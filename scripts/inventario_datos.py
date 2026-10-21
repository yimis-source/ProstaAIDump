"""Inventario de los datos descargados (tarea 1204).

Escribe un CSV con una fila por archivo (conjunto, ruta relativa, tamaño y SHA-256)
y muestra un resumen por conjunto. Sirve para comprobar que todos tenemos la misma
copia de los datos sin versionarlos en git.

Uso (desde la raíz del repositorio):
    python scripts/inventario_datos.py --datos datos --salida docs/datos/inventario.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

CONJUNTOS = {
    "MSD_Task05": "Task05_Prostate",
    "Prostate158": "Prostate158/train",
    "PROMISE12": "PROMISE12/training_data",
}
EXTENSIONES = (".nii.gz", ".mhd", ".raw", ".json", ".csv")


def sha256(ruta: Path, bloque: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while chunk := f.read(bloque):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=Path("datos"))
    ap.add_argument("--salida", type=Path, default=Path("docs/datos/inventario.csv"))
    args = ap.parse_args()

    filas = []
    resumen = defaultdict(lambda: [0, 0])
    for nombre, sub in CONJUNTOS.items():
        raiz = args.datos / sub
        if not raiz.is_dir():
            print(f"Omitido (no existe): {raiz}")
            continue
        for ruta in sorted(raiz.rglob("*")):
            rel = ruta.relative_to(raiz)
            if (not ruta.is_file() or ruta.name.startswith(".")
                    or not ruta.name.endswith(EXTENSIONES) or "convertidas" in rel.parts):
                continue
            tam = ruta.stat().st_size
            filas.append({"conjunto": nombre, "archivo": str(rel), "bytes": tam, "sha256": sha256(ruta)})
            resumen[nombre][0] += 1
            resumen[nombre][1] += tam

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["conjunto", "archivo", "bytes", "sha256"])
        w.writeheader()
        w.writerows(filas)
    for nombre, (n, tam) in resumen.items():
        print(f"{nombre}: {n} archivos, {tam / 2**20:.1f} MiB")
    print(f"Inventario escrito en {args.salida}")


if __name__ == "__main__":
    main()
