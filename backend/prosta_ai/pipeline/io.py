"""Lectura y escritura de volúmenes (patrón Adapter sobre SimpleITK y nibabel).

Convención interna: `Volume.data` se indexa como en nibabel (x, y, z) y
`Volume.affine` lleva coordenadas RAS+ (mm). Los volúmenes DICOM se convierten
a esa misma convención al leerlos.

La carga de archivos subidos (.zip, desidentificación en la admisión) es del
Ciclo 6; aquí solo se leen archivos que ya están en disco y son públicos.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import nibabel as nib
import numpy as np
import SimpleITK as sitk

from .errors import StageError
from .stages import CONTROL_CALIDAD


@dataclass
class Volume:
    """Volumen 3D en float32 con su geometría."""

    data: np.ndarray
    affine: np.ndarray
    spacing: tuple[float, float, float]


# ---------------------------------------------------------------- lectura

def _sitk_a_volume(img: "sitk.Image") -> Volume:
    """Convierte una imagen de SimpleITK (LPS) a Volume (índices x,y,z y afín RAS)."""
    arr = sitk.GetArrayFromImage(img).astype(np.float32)  # (z, y, x)
    data = np.ascontiguousarray(arr.transpose(2, 1, 0))
    d = np.array(img.GetDirection()).reshape(3, 3)
    s = np.array(img.GetSpacing())
    lps = np.eye(4)
    lps[:3, :3] = d * s  # cada columna = dirección del índice * espaciado
    lps[:3, 3] = img.GetOrigin()
    affine = np.diag([-1.0, -1.0, 1.0, 1.0]) @ lps
    return Volume(data=data, affine=affine, spacing=(float(s[0]), float(s[1]), float(s[2])))


def _leer_serie_dicom(files: list[Path]) -> Volume:
    """Reconstruye un volumen a partir de una serie DICOM (la de más cortes si hay varias)."""
    carpeta = files[0] if files[0].is_dir() else files[0].parent
    try:
        series = sitk.ImageSeriesReader.GetGDCMSeriesIDs(str(carpeta)) or []
        candidatas = [sitk.ImageSeriesReader.GetGDCMSeriesFileNames(str(carpeta), uid) for uid in series]
        if not files[0].is_dir():  # solo los archivos indicados
            pedidos = {str(f.resolve()) for f in files}
            candidatas = [[n for n in c if str(Path(n).resolve()) in pedidos] for c in candidatas]
        candidatas = [c for c in candidatas if c]
        if not candidatas:
            raise StageError(CONTROL_CALIDAD, "No se encontró ninguna serie DICOM legible.")
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(list(max(candidatas, key=len)))
        img = reader.Execute()
    except StageError:
        raise
    except Exception as exc:
        raise StageError(CONTROL_CALIDAD, "No se pudo reconstruir el volumen a partir de los cortes DICOM.") from exc
    if img.GetDimension() != 3:
        raise StageError(CONTROL_CALIDAD, "La serie DICOM no forma un volumen 3D.")
    return _sitk_a_volume(img)


def _leer_nifti(path: Path) -> Volume:
    """Lee un NIfTI. Si es 4D (p. ej. MSD Task05: canal 0 = T2, canal 1 = ADC) usa el canal 0."""
    try:
        img = nib.load(str(path))
        shape = img.shape
        if len(shape) == 4:
            data = np.asarray(img.dataobj[..., 0], dtype=np.float32)
        elif len(shape) == 3:
            data = np.asarray(img.dataobj, dtype=np.float32)
        else:
            raise StageError(CONTROL_CALIDAD, f"El volumen tiene {len(shape)} dimensiones; se esperaba 3D.")
        affine = np.array(img.affine, dtype=np.float64)
    except StageError:
        raise
    except Exception as exc:  # incluye archivos truncados (ver D-04 del Ciclo 2)
        raise StageError(CONTROL_CALIDAD, f"El archivo {path.name} está dañado o no se puede leer.") from exc
    zooms = np.linalg.norm(affine[:3, :3], axis=0)
    return Volume(data=data, affine=affine, spacing=(float(zooms[0]), float(zooms[1]), float(zooms[2])))


def load_volume(files: list[Path], fmt: str) -> Volume:
    """Lee el estudio como un Volume. Lanza StageError("control de calidad", ...) si falla.

    `fmt` es "NIfTI" (un único .nii/.nii.gz) o "DICOM" (archivos .dcm o su carpeta).
    """
    if not files:
        raise StageError(CONTROL_CALIDAD, "No hay archivos para leer.")
    files = [Path(f) for f in files]
    if fmt == "NIfTI":
        if len(files) != 1:
            raise StageError(CONTROL_CALIDAD, "Un estudio NIfTI debe ser un único archivo.")
        return _leer_nifti(files[0])
    if fmt == "DICOM":
        return _leer_serie_dicom(files)
    raise StageError(CONTROL_CALIDAD, f"Formato desconocido: {fmt}")


def detectar_formato(path: Path) -> str:
    """"NIfTI" si la ruta termina en .nii/.nii.gz; "DICOM" en otro caso (archivo .dcm o carpeta)."""
    return "NIfTI" if str(path).lower().endswith((".nii", ".nii.gz")) else "DICOM"


# --------------------------------------------------------------- escritura

def save_nifti(data: np.ndarray, affine: np.ndarray, path: Path) -> None:
    """Guarda un NIfTI sin descripción ni metadatos de persona."""
    arr = np.asarray(data)
    if arr.dtype == np.float64:
        arr = arr.astype(np.float32)
    img = nib.Nifti1Image(arr, np.asarray(affine))
    img.header["descrip"] = b""
    img.header["db_name"] = b""
    img.header["aux_file"] = b""
    img.header.set_qform(img.affine, code=1)
    img.header.set_sform(img.affine, code=1)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, str(path))
