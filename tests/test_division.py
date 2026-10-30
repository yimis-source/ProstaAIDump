"""Pruebas de la división por paciente (tareas 1303 y 1304)."""
import json
from pathlib import Path

import pytest

from entrenamiento import division

RAIZ = Path(__file__).resolve().parents[1]
CASOS = [f"prostate_{i:02d}" for i in range(32)]


def test_proporciones_70_15_15():
    c = division.dividir(CASOS)
    assert {k: len(v) for k, v in c.items()} == {"entrenamiento": 22, "validacion": 5, "prueba": 5}


def test_reproducible_con_la_misma_semilla():
    assert division.dividir(CASOS) == division.dividir(list(reversed(CASOS)))


def test_semilla_distinta_cambia_la_division():
    assert division.dividir(CASOS, 1) != division.dividir(CASOS, 2)


def test_sin_pacientes_repetidos_entre_conjuntos():
    c = division.dividir(CASOS)
    todos = [x for v in c.values() for x in v]
    assert len(todos) == len(set(todos)) == len(CASOS)


def test_verificar_detecta_fuga():
    c = division.dividir(CASOS)
    c["prueba"].append(c["entrenamiento"][0])
    with pytest.raises(ValueError, match="está en"):
        division.verificar_division(c)


def test_verificar_detecta_casos_faltantes():
    c = division.dividir(CASOS)
    with pytest.raises(ValueError, match="no cubre"):
        division.verificar_division(c, CASOS + ["prostate_99"])


def test_menos_de_tres_casos():
    with pytest.raises(ValueError):
        division.dividir(["a", "b"])


def test_archivo_versionado_es_valido_y_su_huella_coincide():
    doc = division.cargar_division(RAIZ / "entrenamiento" / "division_task05.json")
    assert doc["total_casos"] == 32
    assert doc["semilla"] == division.SEMILLA


def test_huella_detecta_archivo_modificado(tmp_path):
    doc = json.loads((RAIZ / "entrenamiento" / "division_task05.json").read_text())
    a, b = doc["conjuntos"]["prueba"][0], doc["conjuntos"]["validacion"][0]
    doc["conjuntos"]["prueba"][0], doc["conjuntos"]["validacion"][0] = b, a
    ruta = tmp_path / "division.json"
    ruta.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="huella"):
        division.cargar_division(ruta)
