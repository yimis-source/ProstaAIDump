"""Pruebas del formato unificado y del script de preprocesamiento (tareas 1302 y 1305)."""
import csv

import numpy as np
import SimpleITK as sitk

from preprocesamiento import preprocesar, transformaciones
from preprocesamiento.control_calidad import leer_t2


def test_espaciado_y_orientacion_objetivo(caso_sintetico):
    img = transformaciones.preparar_imagen(leer_t2(caso_sintetico))
    assert np.allclose(img.GetSpacing(), transformaciones.ESPACIADO_OBJETIVO)
    assert sitk.DICOMOrientImageFilter.GetOrientationFromDirectionCosines(img.GetDirection()) == "RAS"


def test_normalizacion_z_score(caso_sintetico):
    arr = sitk.GetArrayFromImage(transformaciones.preparar_imagen(leer_t2(caso_sintetico)))
    assert arr.dtype == np.float32
    assert abs(arr.mean()) < 0.5 and 0.5 < arr.std() < 1.5


def test_mascara_binaria_y_alineada(caso_sintetico):
    img = transformaciones.preparar_imagen(leer_t2(caso_sintetico))
    msk = transformaciones.preparar_mascara(sitk.ReadImage(str(caso_sintetico.mascara)))
    assert msk.GetSize() == img.GetSize()
    assert set(np.unique(sitk.GetArrayFromImage(msk))) == {0, 1}


def test_volumen_de_la_mascara_se_conserva(caso_sintetico):
    original = sitk.ReadImage(str(caso_sintetico.mascara))
    vol_o = (sitk.GetArrayFromImage(original) > 0).sum() * np.prod(original.GetSpacing())
    nueva = transformaciones.preparar_mascara(original)
    vol_n = sitk.GetArrayFromImage(nueva).sum() * np.prod(nueva.GetSpacing())
    assert abs(vol_n - vol_o) / vol_o < 0.1


def test_procesar_caso_escribe_nifti_y_descarta_malos(caso_sintetico, tmp_path):
    fila = preprocesar.procesar_caso(caso_sintetico, tmp_path)
    assert fila["estado"] == "ok"
    assert (tmp_path / "imagenes" / "caso_00.nii.gz").is_file()
    assert (tmp_path / "mascaras" / "caso_00.nii.gz").is_file()

    roto = tmp_path / "roto.nii.gz"
    roto.write_bytes(b"no es un nifti")
    malo = type(caso_sintetico)("X", "roto", roto, caso_sintetico.mascara)
    assert preprocesar.procesar_caso(malo, tmp_path)["estado"] == "descartado"
