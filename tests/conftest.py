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
