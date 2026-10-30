"""Pruebas del control de calidad (tarea 1301)."""
import numpy as np

from preprocesamiento import control_calidad
from preprocesamiento.fuentes import Caso


def test_caso_valido_se_acepta(caso_sintetico):
    assert control_calidad.revisar(caso_sintetico).aceptado


def test_archivo_danado_se_descarta(caso_sintetico, tmp_path):
    roto = tmp_path / "roto.nii.gz"
    roto.write_bytes(caso_sintetico.imagen.read_bytes()[:200])
    r = control_calidad.revisar(Caso("X", "roto", roto, caso_sintetico.mascara))
    assert not r.aceptado and "ilegible" in r.errores[0]


def test_pocos_cortes_se_descarta(tmp_path, guardar):
    img = guardar(np.random.rand(4, 32, 32).astype(np.float32), tmp_path / "i.nii.gz")
    msk = guardar(np.ones((4, 32, 32), np.uint8), tmp_path / "m.nii.gz")
    r = control_calidad.revisar(Caso("X", "c", img, msk))
    assert any("geometría" in e for e in r.errores)


def test_imagen_constante_se_descarta(tmp_path, guardar):
    img = guardar(np.zeros((12, 32, 32), np.float32), tmp_path / "i.nii.gz")
    msk = guardar(np.ones((12, 32, 32), np.uint8), tmp_path / "m.nii.gz")
    assert "la imagen es constante" in control_calidad.revisar(Caso("X", "c", img, msk)).errores


def test_mascara_vacia_o_ausente(caso_sintetico, tmp_path, guardar):
    vacia = guardar(np.zeros((12, 64, 64), np.uint8), tmp_path / "v.nii.gz")
    r = control_calidad.revisar(Caso("X", "c", caso_sintetico.imagen, vacia))
    assert "la máscara está vacía" in r.errores
    r = control_calidad.revisar(Caso("X", "c", caso_sintetico.imagen, tmp_path / "no.nii.gz"))
    assert "falta la máscara de referencia" in r.errores


def test_mascara_con_otra_geometria(caso_sintetico, tmp_path, guardar):
    otra = guardar(np.ones((12, 64, 64), np.uint8), tmp_path / "o.nii.gz", espaciado=(0.4, 0.4, 3.0))
    r = control_calidad.revisar(Caso("X", "c", caso_sintetico.imagen, otra))
    assert any("geometría" in e for e in r.errores)


def test_etiquetas_desconocidas(caso_sintetico, tmp_path, guardar):
    msk = np.zeros((12, 64, 64), np.uint8)
    msk[5, 30:34, 30:34] = 7
    r = control_calidad.revisar(Caso("X", "c", caso_sintetico.imagen, guardar(msk, tmp_path / "e.nii.gz")))
    assert any("desconocidas" in e for e in r.errores)
