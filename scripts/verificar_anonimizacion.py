"""Verificación de anonimización en los metadatos de los conjuntos descargados (tarea 1205).

Revisa, archivo por archivo, que los metadatos no contengan datos de persona,
institución o fechas:

- NIfTI: campos de texto de la cabecera (`descrip`, `aux_file`, `db_name`,
  `intent_name`) y extensiones de cabecera (p. ej. DICOM incrustado).
- MetaImage (.mhd): todas las claves de la cabecera; solo se aceptan las claves
  geométricas estándar.
- Nombres de archivo y carpeta: solo identificadores neutros (prostate_00, 020, Case00).

Uso (desde la raíz del repositorio):
    python scripts/verificar_anonimizacion.py --datos datos --salida docs/datos/anonimizacion.csv

Sale con código 1 si encuentra algún hallazgo.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import nibabel as nib

CLAVES_MHD_PERMITIDAS = {
    "ObjectType", "NDims", "BinaryData", "BinaryDataByteOrderMSB", "CompressedData",
    "CompressedDataSize", "TransformMatrix", "Offset", "CenterOfRotation",
    "AnatomicalOrientation", "ElementSpacing", "DimSize", "ElementType",
    "ElementDataFile", "ElementNumberOfChannels",
}
NOMBRE_NEUTRO = re.compile(
    r"^(prostate_\d{2}|Case\d{2}(_segmentation)?|\d{3}|t2|adc|dwi|empty|"
    r"(t2|adc)_(anatomy|tumor)_reader\d)$"
)
# Patrones que delatarían datos personales o institucionales en texto libre.
SOSPECHOSOS = re.compile(
    r"(\d{4}[-/.]\d{2}[-/.]\d{2}|\d{8}|patient|paciente|name|nombre|hospital|clinic|"
    r"radboud|nijmegen|birth|dob|\^)",
    re.IGNORECASE,
)


def _texto(valor) -> str:
    if hasattr(valor, "tobytes"):
        valor = valor.tobytes()
    if isinstance(valor, bytes):
        valor = valor.split(b"\x00", 1)[0].decode("latin-1", "replace")
    return str(valor).strip()


def revisar_nifti(ruta: Path) -> list[str]:
    hallazgos = []
    img = nib.load(str(ruta))
    cab = img.header
    for campo in ("descrip", "aux_file", "db_name", "intent_name"):
        if campo not in cab:
            continue
        txt = _texto(cab[campo])
        if txt and SOSPECHOSOS.search(txt):
            hallazgos.append(f"{campo}='{txt}'")
    for ext in getattr(cab, "extensions", []):
        hallazgos.append(f"extensión de cabecera código {ext.get_code()}")
    return hallazgos


def revisar_mhd(ruta: Path) -> list[str]:
    hallazgos = []
    for linea in ruta.read_text(encoding="latin-1").splitlines():
        if "=" not in linea:
            continue
        clave, valor = (p.strip() for p in linea.split("=", 1))
        if clave not in CLAVES_MHD_PERMITIDAS:
            hallazgos.append(f"clave no estándar {clave}='{valor}'")
    return hallazgos


def revisar_nombre(ruta: Path, raiz: Path) -> list[str]:
    hallazgos = []
    for parte in ruta.relative_to(raiz).parts:
        base = parte.split(".", 1)[0]
        if base in {"imagesTr", "imagesTs", "labelsTr"}:
            continue
        if not NOMBRE_NEUTRO.match(base):
            hallazgos.append(f"nombre no neutro '{parte}'")
    return hallazgos


def archivos(raiz: Path):
    for patron in ("**/*.nii.gz", "**/*.mhd"):
        for ruta in sorted(raiz.glob(patron)):
            if not ruta.name.startswith("."):
                yield ruta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=Path("datos"))
    ap.add_argument("--salida", type=Path, default=Path("docs/datos/anonimizacion.csv"))
    args = ap.parse_args()

    conjuntos = {
        "MSD_Task05": args.datos / "Task05_Prostate",
        "Prostate158": args.datos / "Prostate158" / "train",
        "PROMISE12": args.datos / "PROMISE12" / "training_data",
    }
    filas, total_hallazgos = [], 0
    for nombre, raiz in conjuntos.items():
        if not raiz.is_dir():
            print(f"Omitido (no existe): {raiz}")
            continue
        n = 0
        for ruta in archivos(raiz):
            h = revisar_nombre(ruta, raiz)
            h += revisar_mhd(ruta) if ruta.suffix == ".mhd" else revisar_nifti(ruta)
            filas.append({
                "conjunto": nombre,
                "archivo": str(ruta.relative_to(raiz)),
                "resultado": "OK" if not h else "REVISAR",
                "hallazgos": "; ".join(h),
            })
            total_hallazgos += bool(h)
            n += 1
        print(f"{nombre}: {n} archivos revisados")

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["conjunto", "archivo", "resultado", "hallazgos"])
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} archivos, {total_hallazgos} con hallazgos. Detalle en {args.salida}")
    return 1 if total_hallazgos else 0


if __name__ == "__main__":
    sys.exit(main())
