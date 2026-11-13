"""Medición del tiempo de inferencia y la memoria en CPU (actividad 1408, riesgo 1).

Cada estudio se procesa en un proceso hijo nuevo, para que la memoria pico
(`ru_maxrss`) sea la de ese estudio y no se acumule entre casos. En el hijo se mide:

- importación de librerías y carga de los pesos (costo de arranque, una vez);
- primera ejecución del pipeline (control de calidad, preparación, segmentación,
  evaluación) con los tiempos por etapa;
- segunda ejecución del mismo estudio con el modelo ya cargado (régimen estable,
  como en una aplicación que mantiene el modelo en memoria);
- memoria residente pico del proceso.

Se compara con la meta de 120 s por estudio (RR-01, sección 5.1 del SRS).

Uso (desde la raíz del repositorio):
    python scripts/medir_inferencia.py --datos /ruta/Task05_Prostate --directorio-modelos /ruta/modelos
    (también lee $PROSTA_DATOS y $PROSTA_MODELOS)

Por defecto mide los 5 casos de prueba de la división y el caso de mayor tamaño
en el espacio preparado (peor caso). Escribe `reports/inferencia/medicion_1408_<fecha>.md` y `.csv`.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

T_INICIO = time.perf_counter()
RAIZ = Path(__file__).resolve().parents[1]
for _ruta in (RAIZ, RAIZ / "backend"):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

META_S = 120.0
SALIDA = RAIZ / "reports" / "inferencia"


def _rss_pico_mib() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # Linux: KiB


def medir_en_hijo(args: argparse.Namespace) -> None:
    """Se ejecuta en el proceso hijo: mide un caso e imprime un JSON."""
    import torch

    from entrenamiento.division import rutas_caso
    from prosta_ai.pipeline.base import PipelineInput
    from prosta_ai.pipeline.factory import build_pipeline

    t_import = time.perf_counter() - T_INICIO
    rss_import = _rss_pico_mib()
    if args.hilos:
        torch.set_num_threads(args.hilos)
    pipeline = build_pipeline(args.modelo, args.directorio_modelos, "cpu")
    t0 = time.perf_counter()
    pipeline.strategy.cargar_modelo()
    t_pesos = time.perf_counter() - t0
    rss_modelo = _rss_pico_mib()

    imagen, etiqueta = rutas_caso(args.datos, args.caso)
    entrada = PipelineInput(files=[imagen], fmt="NIfTI", reference_files=[etiqueta])
    t0 = time.perf_counter()
    primera = pipeline.run(entrada)
    t_primera = time.perf_counter() - t0
    t0 = time.perf_counter()
    segunda = pipeline.run(entrada)
    t_segunda = time.perf_counter() - t0
    print(json.dumps({
        "caso": args.caso,
        "forma_preparada": list(primera.mask.shape),
        "megavoxeles_preparados": round(float(primera.mask.size) / 1e6, 1),
        "hilos_torch": torch.get_num_threads(),
        "t_importacion_s": round(t_import, 2),
        "t_carga_pesos_s": round(t_pesos, 2),
        "t_primera_s": round(t_primera, 2),
        "t_segunda_s": round(t_segunda, 2),
        "t_arranque_mas_primera_s": round(time.perf_counter() - T_INICIO - t_segunda, 2),
        "etapas_primera_s": {k: round(v, 2) for k, v in primera.durations.items()},
        "etapas_segunda_s": {k: round(v, 2) for k, v in segunda.durations.items()},
        "rss_tras_importar_mib": round(rss_import),
        "rss_tras_cargar_modelo_mib": round(rss_modelo),
        "rss_pico_mib": round(_rss_pico_mib()),
        "dice_preparado": round(primera.dice, 4),
    }))


def caso_mas_grande(datos: Path, casos: list[str], espaciado: float) -> str:
    """Caso con más vóxeles tras remuestrear al espaciado del modelo (según la cabecera)."""
    import nibabel as nib
    import numpy as np

    from entrenamiento.division import rutas_caso

    def voxeles(caso: str) -> float:
        img = nib.load(str(rutas_caso(datos, caso)[0]))
        extension_mm = np.array(img.shape[:3]) * np.array(img.header.get_zooms()[:3])
        return float(np.prod(extension_mm / espaciado))

    return max(casos, key=voxeles)


def hardware() -> dict:
    info = {"cpu": platform.processor() or platform.machine(), "ram_gib": None}
    try:
        for linea in Path("/proc/cpuinfo").read_text().splitlines():
            if linea.startswith("model name"):
                info["cpu"] = linea.split(":", 1)[1].strip()
                break
        for linea in Path("/proc/meminfo").read_text().splitlines():
            if linea.startswith("MemTotal"):
                info["ram_gib"] = round(int(linea.split()[1]) / 1024**2, 1)
    except OSError:
        pass
    info["hilos_logicos"] = os.cpu_count()
    info["so"] = f"{platform.system()} {platform.release()}"
    info["python"] = platform.python_version()
    return info


def informe(filas: list[dict], hw: dict, versiones: dict, peor: str) -> str:
    peor_t = max(f["t_arranque_mas_primera_s"] for f in filas)
    peor_rss = max(f["rss_pico_mib"] for f in filas)
    lineas = [
        f"# Medición de inferencia en CPU (actividad 1408), {date.today().isoformat()}",
        "",
        "Uso académico y experimental. Riesgo 1 del Acta (capacidad de cómputo); meta RR-01: resultado en ≤ 120 s.",
        "",
        "## Equipo y software",
        "",
        f"- CPU: {hw['cpu']}, {hw['hilos_logicos']} hilos lógicos; torch usa {filas[0]['hilos_torch']} hilos.",
        f"- RAM: {hw['ram_gib']} GiB. Sin GPU (no se midió GPU).",
        f"- {hw['so']}; Python {hw['python']}; torch {versiones['torch']}; MONAI {versiones['monai']}.",
        "- Modelo: `prostate_mri_anatomy` 0.3.6, ventana deslizante 96³, `sw_batch_size` 4, solapamiento 0,5, "
        "espaciado 0,5 mm.",
        "- Cada caso en un proceso nuevo; memoria = RSS pico del proceso (`ru_maxrss`).",
        "",
        "## Resultados",
        "",
        "| Caso | Vóxeles preparados (M) | Importar (s) | Cargar pesos (s) | Preparación (s) | Segmentación (s) "
        "| Arranque + 1.ª ejecución (s) | 2.ª ejecución, modelo cargado (s) | RSS pico (MiB) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for f in filas:
        e = f["etapas_primera_s"]
        marca = " (peor caso por tamaño)" if f["caso"] == peor else ""
        lineas.append(
            f"| {f['caso']}{marca} | {f['megavoxeles_preparados']} | {f['t_importacion_s']} | {f['t_carga_pesos_s']} "
            f"| {e.get('preparación', 0)} | {e.get('segmentación', 0)} | {f['t_arranque_mas_primera_s']} "
            f"| {f['t_segunda_s']} | {f['rss_pico_mib']} |"
        )
    veredicto = "cumple" if peor_t <= META_S else "NO cumple"
    lineas += [
        "",
        f"Peor tiempo (arranque en frío + primera ejecución): **{peor_t:.1f} s** → {veredicto} la meta de {META_S:.0f} s. "
        f"Memoria pico máxima: **{peor_rss} MiB**.",
        "",
    ]
    return "\n".join(lineas)


def main() -> None:
    from prosta_ai.pipeline.factory import directorio_modelos

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", default="prostate_mri_anatomy")
    ap.add_argument("--directorio-modelos", type=Path, default=directorio_modelos(RAIZ / "modelos"))
    ap.add_argument("--datos", type=Path,
                    default=Path(os.environ.get("PROSTA_DATOS", RAIZ / "datos" / "Task05_Prostate")))
    ap.add_argument("--division", type=Path, default=RAIZ / "entrenamiento" / "division_task05.json")
    ap.add_argument("--casos", nargs="*", help="Casos a medir (por defecto: prueba + el más grande).")
    ap.add_argument("--hilos", type=int, default=None, help="Hilos de torch (por defecto, los de torch).")
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--hijo", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--caso", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.hijo:
        medir_en_hijo(args)
        return

    from entrenamiento.division import cargar_division

    division = cargar_division(args.division)
    todos = [c for v in division["conjuntos"].values() for c in v]
    peor = caso_mas_grande(args.datos, todos, 0.5)
    casos = args.casos or list(dict.fromkeys(division["conjuntos"]["prueba"] + [peor]))
    filas = []
    for caso in casos:
        cmd = [sys.executable, str(Path(__file__).resolve()), "--hijo", "--caso", caso, "--modelo", args.modelo,
               "--directorio-modelos", str(args.directorio_modelos), "--datos", str(args.datos)]
        if args.hilos:
            cmd += ["--hilos", str(args.hilos)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        fila = json.loads(res.stdout.strip().splitlines()[-1])
        filas.append(fila)
        print(f"{caso}: arranque+1.ª {fila['t_arranque_mas_primera_s']} s, 2.ª {fila['t_segunda_s']} s, "
              f"RSS pico {fila['rss_pico_mib']} MiB", flush=True)

    import monai
    import torch

    args.salida.mkdir(parents=True, exist_ok=True)
    base = args.salida / f"medicion_1408_{date.today().isoformat()}"
    base.with_suffix(".md").write_text(
        informe(filas, hardware(), {"torch": torch.__version__, "monai": monai.__version__}, peor), encoding="utf-8")
    columnas = ["caso", "megavoxeles_preparados", "hilos_torch", "t_importacion_s", "t_carga_pesos_s",
                "t_preparacion_s", "t_segmentacion_s", "t_arranque_mas_primera_s", "t_segunda_s",
                "rss_tras_importar_mib", "rss_tras_cargar_modelo_mib", "rss_pico_mib", "dice_preparado"]
    with open(base.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({**fila, "t_preparacion_s": fila["etapas_primera_s"].get("preparación"),
                        "t_segmentacion_s": fila["etapas_primera_s"].get("segmentación")})
    print(f"Informe escrito en {base.with_suffix('.md')}")


if __name__ == "__main__":
    main()
