"""Pruebas de la superposición y los textos de la ROI (tarea 1504)."""
import numpy as np
import pytest

from prosta_ai.visualizacion import (
    AVISO_EXPERIMENTAL, COLOR_ROI, LIMITES, con_aviso, figura_comparada, normalizar,
    superponer, texto_explicativo,
)
from prosta_ai.visualizacion.render import plano


@pytest.fixture
def datos():
    rng = np.random.default_rng(0)
    img = normalizar(rng.normal(300, 50, (30, 24, 8)).astype(np.float32))
    m = np.zeros(img.shape, dtype=bool)
    m[10:20, 8:16, 2:6] = True
    return img, m


def test_superposicion_conserva_dimensiones(datos):
    img, m = datos
    r = superponer(img, m, 3)
    assert r.size == (img.shape[0], img.shape[1]) and r.mode == "RGB"  # plano() rota 90 grados
    assert np.asarray(r).shape[:2] == plano(img[:, :, 3]).shape


def test_solo_colorea_voxeles_de_la_mascara(datos):
    img, m = datos
    base = np.asarray(superponer(img, None, 3))
    con = np.asarray(superponer(img, m, 3))
    roi = plano(m[:, :, 3])
    assert np.array_equal(base[~roi], con[~roi])           # fuera de la máscara no cambia nada
    assert not np.array_equal(base[roi], con[roi])         # dentro sí
    esperado = 0.55 * base[roi].astype(float) + 0.45 * np.array(COLOR_ROI)
    assert np.abs(con[roi].astype(float) - esperado).max() <= 1


def test_corte_sin_roi_queda_igual(datos):
    img, m = datos
    assert np.array_equal(np.asarray(superponer(img, m, 0)), np.asarray(superponer(img, None, 0)))


def test_mascara_vacia_o_ausente_no_falla(datos):
    img, _ = datos
    assert superponer(img, np.zeros(img.shape, bool), 1).size
    assert superponer(img, None, 1).size


def test_errores(datos):
    img, m = datos
    with pytest.raises(ValueError):
        superponer(img, m[:, :, :4], 0)
    with pytest.raises(IndexError):
        superponer(img, m, 99)


def test_figura_comparada_y_aviso(datos):
    img, m = datos
    fig = figura_comparada(img, m, 3, texto_explicativo({"hay_roi": True, "cortes_con_roi": [2, 3], "volumen_ml": 1.2}))
    assert fig.mode == "RGB" and fig.width > 2 * 512 and fig.height > fig.width // 2 * 0.5
    assert con_aviso(superponer(img, m, 3)).height > superponer(img, m, 3).height


def test_texto_incluye_aviso_y_limites():
    t = texto_explicativo({"hay_roi": True, "cortes_con_roi": [1, 2, 3], "volumen_ml": 40.25}, {"dice": 0.9, "iou": 0.8})
    assert AVISO_EXPERIMENTAL in t and LIMITES in t
    assert "No es un diagnóstico" in t and "40.2 mL" in t
    assert "Dice 0.900" in t and "IoU 0.800" in t


def test_texto_sin_roi_y_sin_referencia():
    t = texto_explicativo({"hay_roi": False}, {"dice": None, "iou": None})
    assert "No se encontró región de interés" in t and "no disponibles" in t
    assert AVISO_EXPERIMENTAL in t
    assert AVISO_EXPERIMENTAL in texto_explicativo()


def test_texto_sin_aviso_opcional():
    assert AVISO_EXPERIMENTAL not in texto_explicativo(incluir_aviso=False)
