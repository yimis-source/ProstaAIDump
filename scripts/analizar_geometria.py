"""Análisis de tamaños, espaciado y número de casos de los conjuntos de datos (tarea 1206).

Recorre los conjuntos descargados en `datos/` y escribe una fila por caso con:
dimensiones, espaciado del vóxel, orientación, número de canales, rango de
intensidades (percentiles 1 y 99) y volumen de la próstata en ml a partir de la
máscara de referencia.

Uso (desde la raíz del repositorio):
    python scripts/analizar_geometria.py --salida docs/datos/analisis_geometria.csv

Conjuntos que reconoce (si no existe la carpeta, se omite):
    datos/Task05_Prostate          MSD Task05 (NIfTI 4D: T2 + ADC)
    datos/Prostate158/train        Prostate158 (NIfTI, una carpeta por paciente)
    datos/PROMISE12/training_data  PROMISE12 (MetaImage .mhd/.raw)
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import SimpleITK as sitk

CAMPOS = [
    "conjunto", "caso", "formato", "canales", "dim_x", "dim_y", "dim_z",
    "esp_x", "esp_y", "esp_z", "orientacion", "p01", "p99",
    "volumen_prostata_ml", "etiquetas",
]


def _orientacion(img: sitk.Image) -> str:
    return sitk.DICOMOrientImageFilter.GetOrientationFromDirectionCosines(img.GetDirection())


def _fila(conjunto: str, caso: str, ruta_img: Path, ruta_lbl: Path | None) -> dict:
    img = sitk.ReadImage(str(ruta_img))
    canales = 1
    arr = sitk.GetArrayFromImage(img)
    if img.GetDimension() == 4:  # MSD guarda T2 y ADC en el 4.º eje
        canales = img.GetSize()[3]
        img3 = img[:, :, :, 0]
        arr = sitk.GetArrayFromImage(img3)
    else:
        img3 = img
    tam = img3.GetSize()
    esp = img3.GetSpacing()
    fila = {
        "conjunto": conjunto, "caso": caso,
        "formato": "MHD" if ruta_img.suffix == ".mhd" else "NIfTI",
        "canales": canales,
        "dim_x": tam[0], "dim_y": tam[1], "dim_z": tam[2],
        "esp_x": round(esp[0], 4), "esp_y": round(esp[1], 4), "esp_z": round(esp[2], 4),
        "orientacion": _orientacion(img3),
        "p01": round(float(np.percentile(arr, 1)), 1),
        "p99": round(float(np.percentile(arr, 99)), 1),
        "volumen_prostata_ml": "", "etiquetas": "",
    }
    if ruta_lbl is not None and ruta_lbl.is_file():
        lbl = sitk.GetArrayFromImage(sitk.ReadImage(str(ruta_lbl)))
        vox_ml = esp[0] * esp[1] * esp[2] / 1000.0
        fila["volumen_prostata_ml"] = round(float((lbl > 0).sum()) * vox_ml, 1)
        fila["etiquetas"] = " ".join(str(int(v)) for v in np.unique(lbl))
    return fila


def casos_msd(raiz: Path):
    for img in sorted((raiz / "imagesTr").glob("prostate_*.nii.gz")):
        yield "MSD_Task05", img.name[:-7], img, raiz / "labelsTr" / img.name


def casos_prostate158(raiz: Path):
    for carpeta in sorted(p for p in raiz.iterdir() if p.is_dir()):
        t2 = carpeta / "t2.nii.gz"
        if t2.is_file():
            yield "Prostate158", carpeta.name, t2, carpeta / "t2_anatomy_reader1.nii.gz"


def casos_promise12(raiz: Path):
    for img in sorted(raiz.glob("Case??.mhd")):
        yield "PROMISE12", img.stem, img, raiz / f"{img.stem}_segmentation.mhd"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=Path("datos"))
    ap.add_argument("--salida", type=Path, default=Path("docs/datos/analisis_geometria.csv"))
    args = ap.parse_args()

    fuentes = [
        (args.datos / "Task05_Prostate", casos_msd),
        (args.datos / "Prostate158" / "train", casos_prostate158),
        (args.datos / "PROMISE12" / "training_data", casos_promise12),
    ]
    filas = []
    for raiz, generador in fuentes:
        if not raiz.is_dir():
            print(f"Omitido (no existe): {raiz}")
            continue
        for conjunto, caso, img, lbl in generador(raiz):
            filas.append(_fila(conjunto, caso, img, lbl))
        print(f"{raiz}: {sum(1 for f in filas if f['conjunto'] == conjunto)} casos")

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(filas)
    print(f"Escrito {args.salida} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
