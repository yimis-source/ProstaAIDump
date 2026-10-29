"""Script de preprocesamiento automatizado (tarea 1305).

Para cada caso de la fuente elegida: control de calidad → T2 en RAS →
remuestreo al espaciado objetivo → normalización → escritura en NIfTI.
Los casos descartados quedan registrados con el motivo.

Uso (desde la raíz del repositorio):
    python -m preprocesamiento.preprocesar --fuente msd
    python -m preprocesamiento.preprocesar --fuente promise12 --salida datos/preprocesados

Salida (no se versiona):
    datos/preprocesados/<fuente>/imagenes/<caso>.nii.gz
    datos/preprocesados/<fuente>/mascaras/<caso>.nii.gz
    datos/preprocesados/<fuente>/manifiesto.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import SimpleITK as sitk

from . import control_calidad, fuentes, transformaciones


def procesar_caso(caso: fuentes.Caso, destino: Path) -> dict:
    qc = control_calidad.revisar(caso)
    fila = {"caso": caso.id, "conjunto": caso.conjunto, "estado": "", "motivo": "",
            "dim_x": "", "dim_y": "", "dim_z": ""}
    if not qc.aceptado:
        fila.update(estado="descartado", motivo="; ".join(qc.errores))
        return fila
    img = transformaciones.preparar_imagen(control_calidad.leer_t2(caso))
    msk = transformaciones.preparar_mascara(sitk.ReadImage(str(caso.mascara)))
    (destino / "imagenes").mkdir(parents=True, exist_ok=True)
    (destino / "mascaras").mkdir(parents=True, exist_ok=True)
    sitk.WriteImage(img, str(destino / "imagenes" / f"{caso.id}.nii.gz"), useCompression=True)
    sitk.WriteImage(msk, str(destino / "mascaras" / f"{caso.id}.nii.gz"), useCompression=True)
    fila.update(estado="ok", dim_x=img.GetSize()[0], dim_y=img.GetSize()[1], dim_z=img.GetSize()[2])
    return fila


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=Path("datos"))
    ap.add_argument("--fuente", choices=sorted(fuentes.FUENTES), default="msd")
    ap.add_argument("--salida", type=Path, default=Path("datos/preprocesados"))
    args = ap.parse_args(argv)

    destino = args.salida / args.fuente
    casos = fuentes.listar(args.datos, args.fuente)
    filas = []
    for i, caso in enumerate(casos, 1):
        fila = procesar_caso(caso, destino)
        filas.append(fila)
        print(f"[{i}/{len(casos)}] {caso.id}: {fila['estado']} {fila['motivo']}".rstrip())

    destino.mkdir(parents=True, exist_ok=True)
    with open(destino / "manifiesto.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    ok = sum(f["estado"] == "ok" for f in filas)
    print(f"{ok} casos preprocesados, {len(filas) - ok} descartados. Manifiesto: {destino / 'manifiesto.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
