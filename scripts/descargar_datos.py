"""Descarga los conjuntos públicos elegidos en el Sprint 1 (tareas 1202 y 1204).

Uso (desde la raíz del repositorio):
    python scripts/descargar_datos.py msd            # principal
    python scripts/descargar_datos.py prostate158    # respaldo

PROMISE12 exige registro en https://promise12.grand-challenge.org/ y no permite
redistribución: se descarga a mano y se descomprime en datos/PROMISE12/.

Los datos quedan en `datos/` (ignorado por git). La licencia y la cita de cada
conjunto están en docs/datos/fichas/.
"""
from __future__ import annotations

import argparse
import tarfile
import urllib.request
import zipfile
from pathlib import Path

URLS = {
    "msd": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar",
    "prostate158": "https://zenodo.org/records/6481141/files/prostate158_train.zip",
}
CARPETA = {"msd": "Task05_Prostate", "prostate158": "Prostate158"}


def _dentro(destino: Path, nombre: str) -> bool:
    return str((destino / nombre).resolve()).startswith(str(destino.resolve()))


def _extraer(archivo: Path, destino: Path) -> None:
    """Extrae solo miembros que quedan dentro de `destino` (sin path traversal)."""
    if archivo.suffix == ".zip":
        with zipfile.ZipFile(archivo) as z:
            for m in z.namelist():
                if _dentro(destino, m) and not Path(m).name.startswith("._"):
                    z.extract(m, destino)
    else:
        with tarfile.open(archivo) as t:
            for m in t:
                if _dentro(destino, m.name) and not Path(m.name).name.startswith("._"):
                    t.extract(m, destino, filter="data")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("conjunto", choices=sorted(URLS))
    ap.add_argument("--destino", type=Path, default=Path("datos"))
    args = ap.parse_args()

    destino = args.destino if args.conjunto == "msd" else args.destino / CARPETA[args.conjunto]
    destino.mkdir(parents=True, exist_ok=True)
    if (args.destino / CARPETA[args.conjunto]).is_dir() and any((args.destino / CARPETA[args.conjunto]).iterdir()):
        print(f"Ya existe {args.destino / CARPETA[args.conjunto]}; no se descarga de nuevo.")
        return
    url = URLS[args.conjunto]
    archivo = destino / url.rsplit("/", 1)[-1]
    if not archivo.exists():
        print(f"Descargando {url} ...")
        urllib.request.urlretrieve(url, archivo)
    print(f"Extrayendo {archivo.name} ...")
    _extraer(archivo, destino)
    archivo.unlink()
    print(f"Listo: {args.destino / CARPETA[args.conjunto]}")


if __name__ == "__main__":
    main()
