"""Evaluación del modelo sobre el conjunto de PRUEBA (RF-23, RF-24; Ciclo 3).

Usa `build_pipeline`, la misma ruta que tendrá la aplicación: control de
calidad, preparación, segmentación y evaluación. Se informan Dice e IoU en dos
espacios:

- **Rejilla original** (métrica principal): la máscara se devuelve a la
  rejilla de la imagen con `prosta_ai.pipeline.roi.mask_to_original_space`
  (Ciclo 4) y se compara con la etiqueta tal como viene en Task05.
- **Espacio preparado** (la que calcula el pipeline del Ciclo 3): la etiqueta
  se lleva a 0,5 mm isotrópico con vecino más cercano.

La próstata es la unión de etiquetas > 0. La división es la del Ciclo 2
(`entrenamiento/division_task05.json`, 22/5/5, semilla 2026).

Uso (desde la raíz del repositorio):
    python -m entrenamiento.evaluar --datos /ruta/Task05_Prostate --directorio-modelos /ruta/modelos
    PROSTA_DATOS=... PROSTA_MODELOS=... python -m entrenamiento.evaluar

Escribe `reports/evaluacion/evaluacion_<modelo>_<fecha>.md` y `.csv`.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import time
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _ruta in (RAIZ, RAIZ / "backend"):  # permite ejecutar también como script suelto
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

import monai  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from entrenamiento.division import DATOS_POR_DEFECTO, DIVISION_POR_DEFECTO, cargar_division, rutas_caso  # noqa: E402
from prosta_ai.pipeline.base import PipelineInput  # noqa: E402
from prosta_ai.pipeline.evaluation import dice, iou  # noqa: E402
from prosta_ai.pipeline.factory import build_pipeline, directorio_modelos, model_info  # noqa: E402
from prosta_ai.pipeline.io import load_volume  # noqa: E402
from prosta_ai.pipeline.roi import mask_to_original_space  # noqa: E402

META_DICE = 0.80  # RF-24
LINEA_BASE_REFERENCIA = 0.8925  # Dice medio del proyecto de referencia (03/11/2026, rejilla original)
INFORMES = RAIZ / "reports" / "evaluacion"


def hardware() -> str:
    """Descripción breve del equipo donde se mide (CPU, hilos, RAM, GPU)."""
    cpu = platform.processor() or platform.machine()
    ram = ""
    try:
        for linea in Path("/proc/cpuinfo").read_text().splitlines():
            if linea.startswith("model name"):
                cpu = linea.split(":", 1)[1].strip()
                break
        for linea in Path("/proc/meminfo").read_text().splitlines():
            if linea.startswith("MemTotal"):
                ram = f"{int(linea.split()[1]) / 1024**2:.1f} GiB de RAM"
                break
    except OSError:
        pass
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "sin GPU"
    return (f"{cpu}; {os.cpu_count()} hilos lógicos; {torch.get_num_threads()} hilos de torch; {ram}; {gpu}; "
            f"{platform.system()} {platform.release()}")


def evaluar_casos(pipeline, datos: Path, ids: list[str]) -> list[dict]:
    """Ejecuta el pipeline en cada caso y devuelve una fila por caso."""
    filas = []
    for n, caso in enumerate(ids, 1):
        imagen, etiqueta = rutas_caso(datos, caso)
        t0 = time.perf_counter()
        salida = pipeline.run(PipelineInput(files=[imagen], fmt="NIfTI", reference_files=[etiqueta]))
        segundos = time.perf_counter() - t0
        # métrica principal: rejilla original de la imagen (sin remuestrear la etiqueta)
        vol = load_volume([imagen], "NIfTI")
        ref = load_volume([etiqueta], "NIfTI").data > 0
        original = mask_to_original_space(salida.mask, salida.prepared_affine, vol.data.shape, vol.affine)
        fila = {
            "caso": caso,
            "dice": dice(original, ref), "iou": iou(original, ref),
            "dice_preparado": salida.dice, "iou_preparado": salida.iou,
            "tiempo_s": round(segundos, 1),
        }
        filas.append(fila)
        print(f"[{n}/{len(ids)}] {caso}: Dice={fila['dice']:.4f} IoU={fila['iou']:.4f} "
              f"(preparado {fila['dice_preparado']:.4f}/{fila['iou_preparado']:.4f}; {segundos:.0f} s)", flush=True)
    return filas


def resumen(filas: list[dict], clave: str) -> tuple[float, float]:
    """Media y desviación típica muestral (n-1) de una columna."""
    v = np.array([f[clave] for f in filas], dtype=float)
    return float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0


def tabla(filas: list[dict]) -> str:
    lineas = ["| Caso | Dice | IoU | Dice (preparado) | IoU (preparado) | Tiempo (s) |",
              "|---|---:|---:|---:|---:|---:|"]
    lineas += [f"| {f['caso']} | {f['dice']:.4f} | {f['iou']:.4f} | {f['dice_preparado']:.4f} | "
               f"{f['iou_preparado']:.4f} | {f['tiempo_s']:.1f} |" for f in filas]
    celdas = [" ± ".join(f"{x:.4f}" for x in resumen(filas, k))
              for k in ("dice", "iou", "dice_preparado", "iou_preparado")]
    tm, ts = resumen(filas, "tiempo_s")
    lineas.append("| **Media ± desv.** | " + " | ".join(f"**{c}**" for c in celdas) + f" | **{tm:.1f} ± {ts:.1f}** |")
    return "\n".join(lineas)


def texto_sesgo(carpeta: Path) -> str:
    """Limitación obligatoria sobre el posible solapamiento entre datos del modelo base y Task05."""
    meta_p = carpeta / "configs" / "metadata.json"
    fuente = ""
    if meta_p.exists():
        fuente = json.loads(meta_p.read_text(encoding="utf-8")).get("data_source", "")
    return (
        "- **Posible sesgo (sobreestimación) por los datos del modelo base.** Según la documentación del bundle "
        f"(`configs/metadata.json`, `data_source`: \"{fuente or 'no disponible'}\"), el modelo se entrenó con "
        "Prostate158 (solo T2). La documentación no menciona MSD Task05, así que no hay evidencia de "
        "solapamiento, pero tampoco se puede descartar: el bundle no publica la lista de casos. Además, la "
        "división 22/5/5 de este proyecto es independiente de la de los autores, por lo que los 5 casos de "
        "prueba no son 'no vistos' por construcción. Si hubiera solapamiento, las cifras estarían sobreestimadas."
    )


def construir_informe(info: dict, division: dict, filas: list[dict], equipo: str, sesgo: str) -> str:
    dm, ds = resumen(filas, "dice")
    veredicto = (
        f"Se **cumple** la meta (Dice medio {dm:.4f} ≥ {META_DICE:.2f})." if dm >= META_DICE
        else f"**No se cumple** la meta: Dice medio {dm:.4f} < {META_DICE:.2f} (brecha de {META_DICE - dm:.4f})."
    )
    peor = min(filas, key=lambda f: f["dice"])
    return "\n".join([
        f"# Evaluación del modelo `{info['nombre']}` ({date.today().isoformat()})",
        "",
        "Uso académico y experimental; no es una evaluación clínica ni diagnóstica.",
        "",
        "## Condiciones",
        "",
        f"- Modelo: {info['nombre']}, versión {info['version']}; SHA-256 de los pesos `{info['hash_pesos']}`.",
        "- Ruta de ejecución: `build_pipeline` (control de calidad, preparación, segmentación, evaluación); "
        "imagen = canal 0 (T2) del NIfTI 4D; referencia = etiquetas > 0 (zona periférica + transición).",
        "- **Dice/IoU** (principal): rejilla de la imagen original, con la máscara devuelta por "
        "`roi.mask_to_original_space` (vecino más cercano). **Dice/IoU (preparado)**: espacio del modelo "
        "(RAS, 0,5 mm), con la etiqueta remuestreada por vecino más cercano.",
        f"- Dispositivo: cpu. Hardware: {equipo}.",
        f"- Software: Python {platform.python_version()}, torch {torch.__version__}, MONAI {monai.__version__}.",
        f"- División: `entrenamiento/division_task05.json` (Ciclo 2), semilla {division['semilla']}, "
        f"{division['cantidades']}, huella `{division['huella_sha256'][:16]}…`.",
        f"- Conjunto evaluado: prueba ({len(filas)} casos: {', '.join(f['caso'] for f in filas)}).",
        "- Tiempo por caso: pipeline completo (lectura, preparación, segmentación, evaluación en espacio "
        "preparado). El primer caso incluye la carga de los pesos.",
        "- Desviación: típica muestral (n-1).",
        "",
        "## Resultados sobre el conjunto de prueba",
        "",
        tabla(filas),
        "",
        "## Comparación con la meta (RF-24) y con el proyecto de referencia",
        "",
        veredicto,
        f"El caso más bajo es {peor['caso']} (Dice {peor['dice']:.4f}).",
        f"Proyecto de referencia (03/11/2026, mismos 5 casos, rejilla original): Dice medio {LINEA_BASE_REFERENCIA}; "
        f"diferencia {round(dm - LINEA_BASE_REFERENCIA, 4) + 0.0:+.4f}.",
        "",
        "## Limitaciones",
        "",
        sesgo,
        "- Con 5 casos de prueba la media tiene mucha incertidumbre; un caso malo mueve mucho el promedio.",
        "- Cambio de dominio: Prostate158 (3 T, Charité) frente a Task05 (cortes de 3,0–4,0 mm, otro protocolo); "
        "el remuestreo a 0,5 mm interpola y no añade detalle.",
        "- El modelo segmenta dos zonas; aquí se evalúa solo la unión (próstata completa).",
        "- Un solo conjunto público y un solo anotador por caso; sin métricas de superficie (Hausdorff).",
        "- Los tiempos dependen del equipo. No hay validación clínica.",
        "",
    ])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", default="prostate_mri_anatomy", help="Nombre de la carpeta en --directorio-modelos.")
    ap.add_argument("--directorio-modelos", type=Path, default=directorio_modelos(RAIZ / "modelos"),
                    help="Por defecto $PROSTA_MODELOS o <raíz>/modelos.")
    ap.add_argument("--datos", type=Path, default=Path(os.environ.get("PROSTA_DATOS", DATOS_POR_DEFECTO)),
                    help="Carpeta Task05_Prostate. Por defecto $PROSTA_DATOS o <raíz>/datos/Task05_Prostate.")
    ap.add_argument("--division", type=Path, default=DIVISION_POR_DEFECTO)
    ap.add_argument("--dispositivo", default="cpu", help="cpu o cuda.")
    ap.add_argument("--salida", type=Path, default=INFORMES)
    ap.add_argument("--limite", type=int, default=None, help="Solo los N primeros casos (pruebas).")
    args = ap.parse_args()

    carpeta = args.directorio_modelos / args.modelo
    # create_strategy reconoce por nombre el bundle; un modelo propio entra como "unet" + su carpeta
    estrategia = args.modelo if args.modelo == "prostate_mri_anatomy" else "unet"
    info = model_info(estrategia, carpeta)
    division = cargar_division(args.division)  # verifica RC-04 y la huella antes de evaluar
    ids = division["conjuntos"]["prueba"][: args.limite]
    pipeline = build_pipeline(estrategia, carpeta, args.dispositivo)
    filas = evaluar_casos(pipeline, args.datos, ids)

    informe = construir_informe(info, division, filas, hardware(), texto_sesgo(carpeta))
    args.salida.mkdir(parents=True, exist_ok=True)
    base = f"evaluacion_{args.modelo}_{date.today().isoformat()}"
    (args.salida / f"{base}.md").write_text(informe, encoding="utf-8")
    with open(args.salida / f"{base}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["caso", "conjunto", "dice", "iou", "dice_preparado", "iou_preparado", "tiempo_s"])
        for fila in filas:
            w.writerow([fila["caso"], "prueba", f"{fila['dice']:.6f}", f"{fila['iou']:.6f}",
                        f"{fila['dice_preparado']:.6f}", f"{fila['iou_preparado']:.6f}", fila["tiempo_s"]])
    print(f"Informe escrito en {args.salida / (base + '.md')}")


if __name__ == "__main__":
    main()
