"""Pruebas de la estrategia de segmentación y del pipeline (Ciclo 3).

No requieren los pesos reales: usan una estrategia simulada (umbral) y una
UNet de MONAI mínima con pesos aleatorios guardados en una carpeta temporal.
"""
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from monai.networks.nets import UNet

from prosta_ai.pipeline import stages
from prosta_ai.pipeline.base import PipelineInput, Segmentation3DPipeline
from prosta_ai.pipeline.errors import StageError
from prosta_ai.pipeline.factory import build_pipeline, model_info
from prosta_ai.pipeline.io import load_volume
from prosta_ai.pipeline.preparation import prepare_volume
from prosta_ai.pipeline.progress import PipelineProgress
from prosta_ai.pipeline.segmentation import (
    NnUNetStrategy,
    PretrainedUNetStrategy,
    SegmentationStrategy,
    create_strategy,
    etiquetas_a_prostata,
    mayor_componente,
)

RAIZ_PRUEBAS = Path(__file__).resolve().parents[1]
RED_MINI = {"spatial_dims": 3, "in_channels": 1, "out_channels": 3, "channels": [4, 8], "strides": [2],
            "num_res_units": 1, "norm": "batch", "act": "prelu", "dropout": 0.0}


class EstrategiaUmbral(SegmentationStrategy):
    """Estrategia simulada: umbraliza el volumen preparado (normalizado)."""

    name, version = "umbral", "prueba"

    def __init__(self, umbral: float = 1.0):
        self.umbral = umbral
        self.llamadas = 0

    def segment(self, prepared):
        self.llamadas += 1
        return (prepared.tensor[0].numpy() > self.umbral).astype(np.uint8)


class Registro:
    """Observador que guarda los eventos del pipeline."""

    def __init__(self):
        self.eventos = []

    def on_stage_start(self, stage):
        self.eventos.append(("inicio", stage))

    def on_stage_end(self, stage, duration_s):
        self.eventos.append(("fin", stage))

    def on_stage_failed(self, stage, message):
        self.eventos.append(("fallo", stage))


@pytest.fixture
def modelo_mini(tmp_path, config_prep):
    """Carpeta de modelo con preparacion.json y una UNet mínima con pesos aleatorios."""
    torch.manual_seed(0)
    carpeta = tmp_path / "modelos" / "mini"
    (carpeta / "models").mkdir(parents=True)
    torch.save(UNet(**RED_MINI).state_dict(), carpeta / "models" / "model.pt")
    cfg = config_prep.to_json() | {"nombre": "mini", "version": "1.0", "red": RED_MINI}
    (carpeta / "preparacion.json").write_text(json.dumps(cfg))
    return carpeta


def test_pipeline_con_estrategia_simulada(estudio_nifti, config_prep, tmp_path):
    imagen, etiqueta = estudio_nifti
    registro = Registro()
    progreso = PipelineProgress()
    progreso.attach(registro)
    estrategia = EstrategiaUmbral()
    salida = Segmentation3DPipeline(estrategia, config_prep).run(
        PipelineInput([imagen], "NIfTI", [etiqueta], output_dir=tmp_path / "salida"), progreso)
    assert estrategia.llamadas == 1
    assert salida.mask.shape == (20, 20, 16) and salida.mask.dtype == np.uint8
    assert set(np.unique(salida.mask)) <= {0, 1}
    assert salida.dice > 0.8 and 0 < salida.iou <= salida.dice  # el umbral encuentra la elipsoide
    assert list(salida.durations) == stages.STAGES
    assert [e for e in registro.eventos if e[0] == "fin"] == [("fin", s) for s in stages.STAGES]
    assert salida.mask_path.is_file()


def test_pipeline_sin_referencia_no_calcula_metricas(estudio_nifti, config_prep):
    salida = Segmentation3DPipeline(EstrategiaUmbral(), config_prep).run(PipelineInput([estudio_nifti[0]]))
    assert salida.dice is None and salida.iou is None and salida.mask_path is None


def test_fallo_de_etapa_se_notifica(tmp_path, config_prep):
    import nibabel as nib

    ruta = tmp_path / "constante.nii.gz"
    nib.save(nib.Nifti1Image(np.ones((40, 40, 16), dtype=np.float32), np.eye(4)), str(ruta))
    registro = Registro()
    progreso = PipelineProgress()
    progreso.attach(registro)
    with pytest.raises(StageError) as e:
        Segmentation3DPipeline(EstrategiaUmbral(), config_prep).run(PipelineInput([ruta]), progreso)
    assert e.value.stage == stages.CONTROL_CALIDAD
    assert registro.eventos[-1] == ("fallo", stages.CONTROL_CALIDAD)


def test_unet_mini_carga_una_vez_y_devuelve_mascara(modelo_mini, estudio_nifti):
    estrategia = create_strategy("mini", modelo_mini.parent, device="cpu")
    assert isinstance(estrategia, PretrainedUNetStrategy) and estrategia.version == "1.0"
    prep = prepare_volume(load_volume([estudio_nifti[0]], "NIfTI"), estrategia.config)
    mascara = estrategia.segment(prep)
    assert mascara.shape == tuple(prep.tensor.shape[1:]) and mascara.dtype == np.uint8
    assert set(np.unique(mascara)) <= {0, 1}
    modelo = estrategia.cargar_modelo()
    estrategia.segment(prep)
    assert estrategia.cargar_modelo() is modelo  # los pesos no se recargan
    assert not modelo.training  # modo evaluación (BatchNorm y dropout fijos)


def test_build_pipeline_con_unet_mini_de_extremo_a_extremo(modelo_mini, estudio_nifti):
    pipeline = build_pipeline("mini", modelo_mini, device="cpu")
    salida = pipeline.run(PipelineInput([estudio_nifti[0]], "NIfTI", [estudio_nifti[1]]))
    assert 0.0 <= salida.dice <= 1.0 and 0.0 <= salida.iou <= salida.dice + 1e-9
    info = model_info("mini", modelo_mini)
    assert info["nombre"] == "mini" and len(info["hash_pesos"]) == 64


def test_sin_pesos_mensaje_claro(tmp_path, estudio_nifti, config_prep):
    estrategia = create_strategy("prostate_mri_anatomy", tmp_path / "vacio")
    prep = prepare_volume(load_volume([estudio_nifti[0]], "NIfTI"), config_prep)
    with pytest.raises(StageError) as e:
        estrategia.segment(prep)
    assert e.value.stage == stages.SEGMENTACION and "descargar_modelo.py" in e.value.message


def test_pesos_incompatibles_error_controlado(modelo_mini, estudio_nifti):
    (modelo_mini / "models" / "model.pt").write_bytes(b"no es un modelo")
    estrategia = create_strategy("mini", modelo_mini.parent, device="cpu")
    with pytest.raises(StageError, match="dañados o no son compatibles"):
        estrategia.cargar_modelo()


def test_fabrica_nombres_desconocidos_y_nnunet(tmp_path, config_prep):
    with pytest.raises(StageError, match="Modelo desconocido"):
        create_strategy("otro", tmp_path)
    nn = create_strategy("nnUNet", tmp_path)
    assert isinstance(nn, NnUNetStrategy)
    with pytest.raises(StageError, match="nnU-Net"):
        nn.segment(None)


def test_mayor_componente_y_union_de_zonas(config_prep):
    etiquetas = np.zeros((20, 20, 20), dtype=np.uint8)
    etiquetas[2:10, 2:10, 2:10] = 1  # zona 1 grande
    etiquetas[15:17, 15:17, 15:17] = 1  # isla falsa de la zona 1
    etiquetas[10:14, 2:10, 2:10] = 2  # zona 2 contigua
    assert mayor_componente(etiquetas == 1).sum() == 8 ** 3
    prostata = etiquetas_a_prostata(etiquetas, config_prep)
    assert prostata.sum() == 8 ** 3 + 4 * 8 * 8 and prostata[16, 16, 16] == 0
