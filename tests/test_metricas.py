"""Pruebas de las métricas Dice e IoU (mejora del postmortem del Ciclo 2).

Se verifican antes de reportar resultados del modelo: casos límite y valores
calculados a mano.
"""
import numpy as np
import pytest

from prosta_ai.pipeline.evaluation import dice, iou


def _cubo(shape=(10, 10, 10), desde=(2, 2, 2), hasta=(6, 6, 6)):
    m = np.zeros(shape, dtype=np.uint8)
    m[desde[0]:hasta[0], desde[1]:hasta[1], desde[2]:hasta[2]] = 1
    return m


def test_mascaras_identicas_valen_uno():
    m = _cubo()
    assert dice(m, m) == 1.0
    assert iou(m, m) == 1.0


def test_mascaras_disjuntas_valen_cero():
    a = _cubo(desde=(0, 0, 0), hasta=(3, 3, 3))
    b = _cubo(desde=(5, 5, 5), hasta=(8, 8, 8))
    assert dice(a, b) == 0.0
    assert iou(a, b) == 0.0


def test_ambas_vacias_valen_uno():
    vacia = np.zeros((4, 4, 4), dtype=np.uint8)
    assert dice(vacia, vacia) == 1.0
    assert iou(vacia, vacia) == 1.0


@pytest.mark.parametrize("prediccion_vacia", [True, False])
def test_una_vacia_vale_cero(prediccion_vacia):
    vacia, llena = np.zeros((4, 4, 4)), _cubo((4, 4, 4), (0, 0, 0), (2, 2, 2))
    p, r = (vacia, llena) if prediccion_vacia else (llena, vacia)
    assert dice(p, r) == 0.0
    assert iou(p, r) == 0.0


def test_valores_calculados_a_mano():
    # P = 4 vóxeles, R = 6 vóxeles, intersección = 3, unión = 7
    p = np.zeros((1, 1, 10), dtype=np.uint8)
    r = np.zeros((1, 1, 10), dtype=np.uint8)
    p[0, 0, 0:4] = 1  # vóxeles 0..3
    r[0, 0, 1:7] = 1  # vóxeles 1..6
    assert dice(p, r) == pytest.approx(2 * 3 / (4 + 6))  # 0,6
    assert iou(p, r) == pytest.approx(3 / 7)


def test_cubos_desplazados_a_mano():
    # dos cubos 4x4x4 (64 vóxeles) desplazados 2 en x: intersección 2x4x4 = 32
    a = _cubo(desde=(2, 2, 2), hasta=(6, 6, 6))
    b = _cubo(desde=(4, 2, 2), hasta=(8, 6, 6))
    assert dice(a, b) == pytest.approx(64 / 128)  # 0,5
    assert iou(a, b) == pytest.approx(32 / 96)  # 1/3


def test_etiquetas_multiples_se_binarizan():
    """La próstata es la unión de etiquetas > 0 (PZ = 1, TZ = 2)."""
    ref = np.array([[[0, 1, 2, 2]]])
    pred = np.array([[[0, 1, 1, 1]]], dtype=bool)
    assert dice(pred, ref) == 1.0 and iou(pred, ref) == 1.0


def test_simetria_y_relacion_entre_dice_e_iou():
    rng = np.random.default_rng(1)
    a = rng.random((8, 8, 8)) > 0.5
    b = rng.random((8, 8, 8)) > 0.5
    assert dice(a, b) == pytest.approx(dice(b, a))
    assert iou(a, b) == pytest.approx(iou(b, a))
    j = iou(a, b)
    assert dice(a, b) == pytest.approx(2 * j / (1 + j))  # Dice = 2·IoU / (1 + IoU)
    assert 0.0 <= iou(a, b) <= dice(a, b) <= 1.0


def test_formas_distintas_lanzan_error():
    with pytest.raises(ValueError, match="formas distintas"):
        dice(np.zeros((2, 2, 2)), np.zeros((2, 2, 3)))
    with pytest.raises(ValueError):
        iou(np.zeros((2, 2, 2)), np.zeros((3, 2, 2)))
