"""Pruebas de lectura, control de calidad y preparación del volumen (Ciclo 3)."""
import json

import nibabel as nib
import numpy as np
import pytest

from prosta_ai.pipeline.errors import StageError
from prosta_ai.pipeline.io import Volume, load_volume
from prosta_ai.pipeline.preparation import PreparationConfig, prepare_label, prepare_volume
from prosta_ai.pipeline.validators import detailed_validation


def test_lectura_nifti_4d_usa_canal_t2(tmp_path):
    datos = np.zeros((40, 40, 10, 2), dtype=np.float32)
    datos[..., 0] = 1.0  # T2
    datos[..., 1] = 7.0  # ADC
    ruta = tmp_path / "msd.nii.gz"
    nib.save(nib.Nifti1Image(datos, np.diag([0.625, 0.625, 3.6, 1.0])), str(ruta))
    vol = load_volume([ruta], "NIfTI")
    assert vol.data.shape == (40, 40, 10) and float(vol.data.max()) == 1.0
    assert vol.spacing == pytest.approx((0.625, 0.625, 3.6))


def test_archivo_truncado_es_error_controlado(tmp_path, estudio_nifti):
    imagen, _ = estudio_nifti
    roto = tmp_path / "roto.nii.gz"
    roto.write_bytes(imagen.read_bytes()[:200])
    with pytest.raises(StageError) as e:
        load_volume([roto], "NIfTI")
    assert e.value.stage == "control de calidad"


def test_forma_de_salida_de_la_preparacion(estudio_nifti, config_prep):
    vol = load_volume([estudio_nifti[0]], "NIfTI")  # 40x40x16, vóxel 1x1x2 mm
    prep = prepare_volume(vol, config_prep)  # a 2 mm isotrópico
    assert tuple(prep.tensor.shape) == (1, 20, 20, 16)
    assert prep.tensor.dtype.is_floating_point
    assert np.allclose(np.diag(prep.affine)[:3], (2.0, 2.0, 2.0))
    assert prep.original_shape == (40, 40, 16)
    # NormalizeIntensity: media 0 y desviación 1
    assert float(prep.tensor.mean()) == pytest.approx(0.0, abs=1e-3)
    assert float(prep.tensor.std()) == pytest.approx(1.0, abs=1e-2)


def test_orientacion_lps_se_lleva_a_ras(tmp_path, config_prep):
    datos = np.random.default_rng(0).normal(size=(40, 40, 16)).astype(np.float32)
    ruta = tmp_path / "lps.nii.gz"
    nib.save(nib.Nifti1Image(datos, np.diag([-1.0, -1.0, 2.0, 1.0])), str(ruta))
    prep = prepare_volume(load_volume([ruta], "NIfTI"), config_prep)
    assert np.all(np.diag(prep.affine)[:3] > 0)  # ejes crecientes hacia R, A, S


def test_etiqueta_preparada_coincide_con_la_imagen(estudio_nifti, config_prep):
    vol = load_volume([estudio_nifti[0]], "NIfTI")
    ref = load_volume([estudio_nifti[1]], "NIfTI")
    prep = prepare_volume(vol, config_prep)
    etiqueta = prepare_label(ref, config_prep)
    assert etiqueta.shape == tuple(prep.tensor.shape[1:])
    assert set(np.unique(etiqueta)) <= {0, 1, 2}  # vecino más cercano: sin valores intermedios
    intercambiada = prepare_label(ref, config_prep, mapa={1: 2, 2: 1})
    assert np.array_equal(intercambiada == 1, etiqueta == 2)
    assert np.array_equal(intercambiada > 0, etiqueta > 0)


def test_config_json_ida_y_vuelta(tmp_path, config_prep):
    ruta = tmp_path / "preparacion.json"
    ruta.write_text(json.dumps(config_prep.to_json()))
    assert PreparationConfig.from_json(ruta) == config_prep


def test_config_invalida_es_error_controlado(tmp_path):
    ruta = tmp_path / "preparacion.json"
    ruta.write_text(json.dumps({"nombre": "x"}))
    with pytest.raises(StageError) as e:
        PreparationConfig.from_json(ruta)
    assert e.value.stage == "preparación"


@pytest.mark.parametrize("datos, mensaje", [
    (np.ones((40, 40, 16), dtype=np.float32), "constante"),
    (np.random.default_rng(0).random((40, 40, 4)).astype(np.float32), "cortes"),
    (np.full((40, 40, 16), np.nan, dtype=np.float32), "NaN"),
])
def test_control_de_calidad_rechaza(datos, mensaje):
    with pytest.raises(StageError, match=mensaje):
        detailed_validation(Volume(datos, np.eye(4), (1.0, 1.0, 1.0)))


def test_control_de_calidad_rechaza_referencia_incompatible():
    img = Volume(np.random.default_rng(0).random((40, 40, 16)).astype(np.float32), np.eye(4), (1, 1, 1))
    ref = Volume(np.zeros((40, 40, 15), dtype=np.float32), np.eye(4), (1, 1, 1))
    with pytest.raises(StageError, match="misma forma"):
        detailed_validation(img, ref)
