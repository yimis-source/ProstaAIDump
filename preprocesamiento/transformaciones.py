"""Formato unificado (tarea 1302): NIfTI, orientación RAS, mismo espaciado y escala.

- Imagen: canal T2, reorientada a RAS, remuestreada con interpolación B-spline al
  espaciado objetivo y normalizada con z-score sobre los vóxeles > 0, tras recortar
  a los percentiles 0,5 y 99,5.
- Máscara: misma reorientación y remuestreo por vecino más cercano; se binariza
  (próstata completa = zona periférica + zona de transición).
"""
from __future__ import annotations

import numpy as np
import SimpleITK as sitk

# Mediana del conjunto principal (MSD Task05) en el plano y 3,6 mm entre cortes;
# ver docs/datos/05_analisis_geometria.md.
ESPACIADO_OBJETIVO = (0.625, 0.625, 3.6)
ORIENTACION = "RAS"
PERCENTILES_RECORTE = (0.5, 99.5)


def reorientar(img: sitk.Image) -> sitk.Image:
    return sitk.DICOMOrient(img, ORIENTACION)


def remuestrear(img: sitk.Image, espaciado=ESPACIADO_OBJETIVO, mascara: bool = False) -> sitk.Image:
    tam = [
        max(1, int(round(n * e / o)))
        for n, e, o in zip(img.GetSize(), img.GetSpacing(), espaciado)
    ]
    return sitk.Resample(
        img, tam, sitk.Transform(), sitk.sitkNearestNeighbor if mascara else sitk.sitkBSpline,
        img.GetOrigin(), espaciado, img.GetDirection(), 0,
        sitk.sitkUInt8 if mascara else sitk.sitkFloat32,
    )


def normalizar(img: sitk.Image) -> sitk.Image:
    arr = sitk.GetArrayFromImage(img).astype(np.float32)
    lo, hi = np.percentile(arr, PERCENTILES_RECORTE)
    arr = np.clip(arr, lo, hi)
    fondo = arr > lo
    media = arr[fondo].mean() if fondo.any() else arr.mean()
    desv = arr[fondo].std() if fondo.any() else arr.std()
    arr = (arr - media) / (desv if desv > 0 else 1.0)
    out = sitk.GetImageFromArray(arr)
    out.CopyInformation(img)
    return out


def preparar_imagen(img: sitk.Image) -> sitk.Image:
    return normalizar(remuestrear(reorientar(sitk.Cast(img, sitk.sitkFloat32))))


def preparar_mascara(msk: sitk.Image) -> sitk.Image:
    binaria = sitk.Cast(msk > 0, sitk.sitkUInt8)
    return remuestrear(reorientar(binaria), mascara=True)
