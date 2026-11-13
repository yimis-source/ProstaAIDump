import sys
from pathlib import Path

import numpy as np
import pytest
import SimpleITK as sitk

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def _guardar(arr, ruta, espaciado=(0.6, 0.6, 3.6), dtype=None):
    img = sitk.GetImageFromArray(arr.astype(dtype or arr.dtype))
    img.SetSpacing(espaciado)
    sitk.WriteImage(img, str(ruta))
    return ruta


@pytest.fixture
def caso_sintetico(tmp_path):
    """Imagen 3D (z=12) con una 'próstata' esférica y su máscara."""
    from preprocesamiento.fuentes import Caso

    z, y, x = np.mgrid[:12, :64, :64]
    esfera = ((x - 32) ** 2 + (y - 32) ** 2 + ((z - 6) * 6) ** 2) < 15 ** 2
    rng = np.random.default_rng(0)
    img = (rng.normal(300, 40, esfera.shape) + 400 * esfera).clip(0)
    msk = esfera.astype(np.uint8)
    msk[esfera & (x > 32)] = 2
    ri = _guardar(img, tmp_path / "img.nii.gz", dtype=np.float32)
    rm = _guardar(msk, tmp_path / "msk.nii.gz")
    return Caso("SINTETICO", "caso_00", ri, rm)


@pytest.fixture
def guardar():
    return _guardar


# ------------------------------------------------- Ciclo 3: segmentación 3D

sys.path.insert(0, str(RAIZ / "backend"))  # prosta_ai (también lo agrega pytest.ini)


def elipsoide(shape=(40, 40, 16), centro=(20, 20, 8), radios=(9, 9, 5)) -> np.ndarray:
    """Máscara booleana de una elipsoide en índices (x, y, z)."""
    x, y, z = np.indices(shape)
    d = sum(((c - o) / r) ** 2 for c, o, r in zip((x, y, z), centro, radios))
    return d <= 1


@pytest.fixture
def estudio_nifti(tmp_path):
    """Imagen T2 sintética (x, y, z) = 40x40x16, vóxel 1x1x2 mm, y su etiqueta (1 = PZ, 2 = TZ)."""
    import nibabel as nib

    rng = np.random.default_rng(0)
    obj = elipsoide()
    img = rng.normal(100, 5, obj.shape).astype(np.float32)
    img[obj] += 400
    etiqueta = np.zeros(obj.shape, dtype=np.uint8)
    etiqueta[obj] = 2
    etiqueta[obj & (np.indices(obj.shape)[0] > 20)] = 1
    afin = np.diag([1.0, 1.0, 2.0, 1.0])
    ri, rl = tmp_path / "imagen.nii.gz", tmp_path / "etiqueta.nii.gz"
    nib.save(nib.Nifti1Image(img, afin), str(ri))
    nib.save(nib.Nifti1Image(etiqueta, afin), str(rl))
    return ri, rl


@pytest.fixture
def config_prep():
    """Configuración de preparación pequeña (2 mm isotrópico) para pruebas rápidas."""
    from prosta_ai.pipeline.preparation import PreparationConfig

    return PreparationConfig(nombre="prueba", version="0", espaciado=(2.0, 2.0, 2.0), roi_size=(16, 16, 16),
                             sw_batch_size=2, overlap=0.25)
