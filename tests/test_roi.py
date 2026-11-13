"""Pruebas de la ROI (tarea 1503): volumen, cortes, centroide, caja, vacía, Dice/IoU."""
import numpy as np
import pytest

from prosta_ai.pipeline.roi import (
    MENSAJE_SIN_ROI, binarizar, calcular_roi, dice_iou, mask_to_original_space,
    seleccionar_cortes, volumen_ml,
)


def cubo(forma=(20, 20, 10), lo=(5, 6, 2), hi=(15, 14, 7)):
    m = np.zeros(forma, dtype=np.uint8)
    m[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]] = 1
    return m


def test_volumen_en_ml_segun_espaciado():
    m = cubo()  # 10*8*5 = 400 vóxeles
    assert volumen_ml(m, (1.0, 1.0, 1.0)) == pytest.approx(0.4)
    r = calcular_roi(m, (0.5, 0.5, 3.0))
    assert r.n_voxeles == 400 and r.volumen_ml == pytest.approx(400 * 0.75 / 1000)


def test_cortes_centroide_y_caja():
    r = calcular_roi(cubo(), (1.0, 2.0, 3.0))
    assert r.hay_roi and r.cortes_con_roi == [2, 3, 4, 5, 6]
    assert r.centroide_vox == (9.5, 9.5, 4.0)
    assert r.centroide_mm == (9.5, 19.0, 12.0)
    assert r.caja_vox == ((5, 6, 2), (14, 13, 6))
    assert r.caja_tamano_mm == (10.0, 16.0, 15.0)


def test_esfera_volumen_cercano_al_teorico():
    z, y, x = np.mgrid[:60, :60, :60]
    esf = ((x - 30) ** 2 + (y - 30) ** 2 + (z - 30) ** 2) <= 15 ** 2
    r = calcular_roi(esf, (1, 1, 1))
    assert r.volumen_ml == pytest.approx(4 / 3 * np.pi * 15 ** 3 / 1000, rel=0.03)
    assert r.centroide_vox == (30.0, 30.0, 30.0)


def test_mascara_vacia_no_falla():
    r = calcular_roi(np.zeros((8, 8, 8)), (1, 1, 1))
    assert not r.hay_roi and r.volumen_ml == 0 and r.cortes_con_roi == []
    assert r.centroide_vox is None and r.caja_vox is None
    assert r.mensaje == MENSAJE_SIN_ROI and "no se encontró" in r.mensaje.lower()
    assert seleccionar_cortes(np.zeros((8, 8, 8))) == []


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        calcular_roi(np.zeros((4, 4)), (1, 1, 1))
    with pytest.raises(ValueError):
        calcular_roi(cubo(), (1, 0, 1))
    with pytest.raises(ValueError):
        calcular_roi(cubo(), (1, np.nan, 1))


def test_binarizar_union_de_etiquetas():
    m = np.array([[[0, 1, 2]]])
    assert binarizar(m).tolist() == [[[False, True, True]]]
    assert binarizar(m, (2,)).tolist() == [[[False, False, True]]]


def test_dice_iou():
    a = cubo()
    assert dice_iou(a, a) == {"dice": 1.0, "iou": 1.0}
    b = cubo(lo=(5, 6, 2), hi=(15, 14, 4))  # 160 vóxeles dentro de a (400)
    d = dice_iou(b, a)
    assert d["dice"] == pytest.approx(2 * 160 / 560) and d["iou"] == pytest.approx(160 / 400)
    assert dice_iou(np.zeros((3, 3, 3)), np.ones((3, 3, 3)))["dice"] == 0.0
    assert dice_iou(np.zeros((3, 3, 3)), np.zeros((3, 3, 3))) == {"dice": None, "iou": None}
    with pytest.raises(ValueError):
        dice_iou(np.zeros((3, 3, 3)), np.zeros((3, 3, 4)))


def test_seleccionar_cortes_incluye_el_de_mayor_area():
    m = np.zeros((20, 20, 30), dtype=np.uint8)
    m[8:12, 8:12, 5:25] = 1
    m[5:15, 5:15, 20] = 1  # mayor área
    cortes = seleccionar_cortes(m, 3)
    assert len(cortes) == 3 and 20 in cortes and all(5 <= c < 25 for c in cortes)
    assert seleccionar_cortes(cubo(), 10) == [2, 3, 4, 5, 6]


def test_mask_to_original_space_identidad_y_submuestreo():
    m = cubo()
    afin = np.eye(4)
    assert np.array_equal(mask_to_original_space(m, afin, m.shape, afin), m)
    # original con vóxeles de la mitad de tamaño: forma doble, misma región física
    afin_o = np.diag([0.5, 0.5, 0.5, 1.0])
    o = mask_to_original_space(m, afin, (40, 40, 20), afin_o)
    assert o.shape == (40, 40, 20) and set(np.unique(o)) <= {0, 1}
    assert o.sum() == pytest.approx(m.sum() * 8, rel=0.2)
    with pytest.raises(ValueError):
        mask_to_original_space(m[0], afin, m.shape, afin)
