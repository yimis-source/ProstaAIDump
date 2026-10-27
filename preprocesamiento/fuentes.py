"""Lectura uniforme de los conjuntos de datos (MSD Task05, Prostate158, PROMISE12).

Cada fuente devuelve objetos `Caso` con la ruta de la imagen T2 y de la máscara
de referencia, sin importar el formato original (NIfTI 4D, NIfTI o MetaImage).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Caso:
    conjunto: str
    id: str              # identificador neutro del caso (= paciente)
    imagen: Path
    mascara: Path | None
    canal_t2: int | None = None  # MSD trae T2 y ADC en un 4.º eje


def casos_msd(raiz: Path) -> Iterator[Caso]:
    for img in sorted((raiz / "imagesTr").glob("prostate_*.nii.gz")):
        caso = img.name[: -len(".nii.gz")]
        yield Caso("MSD_Task05", caso, img, raiz / "labelsTr" / img.name, canal_t2=0)


def casos_prostate158(raiz: Path) -> Iterator[Caso]:
    for carpeta in sorted(p for p in raiz.iterdir() if p.is_dir()):
        if (carpeta / "t2.nii.gz").is_file():
            yield Caso("Prostate158", f"p158_{carpeta.name}", carpeta / "t2.nii.gz",
                       carpeta / "t2_anatomy_reader1.nii.gz")


def casos_promise12(raiz: Path) -> Iterator[Caso]:
    for img in sorted(raiz.glob("Case??.mhd")):
        yield Caso("PROMISE12", f"promise_{img.stem[4:]}", img,
                   raiz / f"{img.stem}_segmentation.mhd")


FUENTES = {
    "msd": ("Task05_Prostate", casos_msd),
    "prostate158": ("Prostate158/train", casos_prostate158),
    "promise12": ("PROMISE12/training_data", casos_promise12),
}


def listar(datos: Path, fuente: str) -> list[Caso]:
    sub, gen = FUENTES[fuente]
    raiz = Path(datos) / sub
    if not raiz.is_dir():
        raise FileNotFoundError(f"No existe {raiz}; descargue primero el conjunto.")
    return list(gen(raiz))
