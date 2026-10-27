"""Control de calidad de los casos antes de preprocesarlos (tarea 1301).

Un caso se descarta si alguna verificación falla. Las verificaciones son:

1. La imagen y la máscara se pueden leer (archivo no dañado ni truncado).
2. La imagen es 3D (o 4D con canal T2) y tiene al menos 8 cortes.
3. No hay valores NaN/Inf y la imagen no es constante.
4. La máscara tiene la misma geometría (tamaño, espaciado, origen) que la imagen.
5. La máscara solo contiene etiquetas enteras conocidas y no está vacía.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import SimpleITK as sitk

from .fuentes import Caso

MIN_CORTES = 8
ETIQUETAS_VALIDAS = {0, 1, 2}
TOLERANCIA_GEOMETRIA = 1e-3


@dataclass
class ResultadoCalidad:
    caso: Caso
    errores: list[str] = field(default_factory=list)

    @property
    def aceptado(self) -> bool:
        return not self.errores


def leer_t2(caso: Caso) -> sitk.Image:
    img = sitk.ReadImage(str(caso.imagen))
    if img.GetDimension() == 4:
        img = img[:, :, :, caso.canal_t2 or 0]
    return img


def _misma_geometria(a: sitk.Image, b: sitk.Image) -> bool:
    return (
        a.GetSize() == b.GetSize()
        and np.allclose(a.GetSpacing(), b.GetSpacing(), atol=TOLERANCIA_GEOMETRIA)
        and np.allclose(a.GetOrigin(), b.GetOrigin(), atol=TOLERANCIA_GEOMETRIA * 100)
    )


def revisar(caso: Caso) -> ResultadoCalidad:
    r = ResultadoCalidad(caso)
    try:
        img = leer_t2(caso)
    except Exception as exc:  # archivo dañado o formato no reconocido
        r.errores.append(f"imagen ilegible: {exc.__class__.__name__}")
        return r
    if img.GetDimension() != 3 or img.GetSize()[2] < MIN_CORTES:
        r.errores.append(f"geometría no válida: tamaño {img.GetSize()}")
    arr = sitk.GetArrayViewFromImage(img)
    if not np.isfinite(arr).all():
        r.errores.append("la imagen tiene valores NaN o infinitos")
    elif arr.min() == arr.max():
        r.errores.append("la imagen es constante")

    if caso.mascara is None or not caso.mascara.is_file():
        r.errores.append("falta la máscara de referencia")
        return r
    try:
        msk = sitk.ReadImage(str(caso.mascara))
    except Exception as exc:
        r.errores.append(f"máscara ilegible: {exc.__class__.__name__}")
        return r
    if not _misma_geometria(img, msk):
        r.errores.append("la máscara no coincide en geometría con la imagen")
    valores = set(np.unique(sitk.GetArrayViewFromImage(msk)).astype(int).tolist())
    if not valores <= ETIQUETAS_VALIDAS:
        r.errores.append(f"etiquetas desconocidas: {sorted(valores - ETIQUETAS_VALIDAS)}")
    if valores <= {0}:
        r.errores.append("la máscara está vacía")
    return r
