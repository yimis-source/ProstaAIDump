"""Verificación independiente de fuga entre conjuntos (tarea 1304, Tester).

Comprueba sobre la división versionada (`entrenamiento/division_task05.json`):

1. Estructura: cada caso está en un solo conjunto y la huella SHA-256 coincide.
2. Cobertura: la división cubre exactamente los casos con máscara del MSD.
3. Contenido: ningún par de casos de conjuntos distintos tiene la misma imagen
   (hash del volumen T2), es decir, no hay pacientes repetidos con otro nombre.
4. Cruce externo: si están descargados, busca en PROMISE12 y Prostate158 casos con
   la misma geometría y el mismo volumen de próstata que algún caso del MSD
   (posible mismo paciente) e informa en qué conjunto quedó.

Uso:
    python scripts/verificar_fuga.py --datos datos
Sale con código 1 si encuentra fuga dentro de la división.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import SimpleITK as sitk

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from entrenamiento import division  # noqa: E402
from preprocesamiento import control_calidad, fuentes  # noqa: E402


def firma(caso: fuentes.Caso) -> tuple[str, tuple, float]:
    img = control_calidad.leer_t2(caso)
    arr = sitk.GetArrayFromImage(img)
    h = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    msk = sitk.GetArrayFromImage(sitk.ReadImage(str(caso.mascara)))
    vol = round(float((msk > 0).sum()) * float(np.prod(img.GetSpacing())) / 1000, 1)
    geo = (img.GetSize(), tuple(round(e, 3) for e in img.GetSpacing()))
    return h, geo, vol


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=Path("datos"))
    ap.add_argument("--division", type=Path, default=RAIZ / "entrenamiento" / "division_task05.json")
    args = ap.parse_args()
    fugas = 0

    doc = division.cargar_division(args.division)  # 1. estructura + huella
    conj = {c: n for n, lista in doc["conjuntos"].items() for c in lista}
    print(f"[1] Estructura y huella OK: {doc['cantidades']}")

    casos = {c.id: c for c in fuentes.listar(args.datos, "msd")}  # 2. cobertura
    division.verificar_division(doc["conjuntos"], list(casos))
    print(f"[2] Cobertura OK: {len(casos)} casos del MSD, todos asignados una sola vez")

    firmas = {cid: firma(c) for cid, c in casos.items()}  # 3. contenido
    por_hash: dict[str, list[str]] = {}
    for cid, (h, _, _) in firmas.items():
        por_hash.setdefault(h, []).append(cid)
    for ids in por_hash.values():
        if len(ids) > 1 and len({conj[i] for i in ids}) > 1:
            print(f"    FUGA: misma imagen en {ids} ({[conj[i] for i in ids]})")
            fugas += 1
    print(f"[3] Contenido: {len(por_hash)} imágenes distintas en {len(firmas)} casos; fugas: {fugas}")

    for fuente in ("promise12", "prostate158"):  # 4. cruce externo
        try:
            externos = fuentes.listar(args.datos, fuente)
        except FileNotFoundError:
            print(f"[4] {fuente}: no descargado, se omite")
            continue
        coincidencias = []
        for ext in externos:
            _, geo, vol = firma(ext)
            for cid, (_, g, v) in firmas.items():
                if g == geo and abs(v - vol) <= 0.5:
                    coincidencias.append((cid, ext.id, vol, conj[cid]))
        print(f"[4] {fuente}: {len(externos)} casos, {len(coincidencias)} posibles duplicados del MSD")
        for cid, eid, vol, nombre in coincidencias:
            print(f"    {cid} ≈ {eid} ({vol} ml), en '{nombre}': no usar {fuente} junto con el MSD")

    print("RESULTADO:", "FUGA DETECTADA" if fugas else "sin pacientes repetidos entre conjuntos")
    return 1 if fugas else 0


if __name__ == "__main__":
    sys.exit(main())
