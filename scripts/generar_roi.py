"""Genera la ROI superpuesta (PNG) y su resumen (JSON) desde una imagen y una máscara NIfTI.

Uso:
    python scripts/generar_roi.py --imagen img.nii.gz --mascara pred.nii.gz \\
        [--referencia ref.nii.gz] [--canal 0] [--cortes 3] --salida carpeta

    # segmentando con el modelo (pesos en $PROSTA_MODELOS o --directorio-modelos)
    python scripts/generar_roi.py --imagen img.nii.gz --modelo prostate_mri_anatomy \\
        [--referencia ref.nii.gz] --salida carpeta

Con --modelo se ejecuta la cadena completa (control de calidad, preparación,
segmentación, ROI, evaluación) y la máscara predicha se lleva a la rejilla original.

La máscara y la referencia se binarizan (unión de etiquetas > 0). Resultado
experimental con fines académicos; no es un diagnóstico.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import nibabel as nib
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from prosta_ai.pipeline.roi import calcular_roi, dice_iou, seleccionar_cortes  # noqa: E402
from prosta_ai.visualizacion import figura_comparada, normalizar, texto_explicativo  # noqa: E402
from prosta_ai.visualizacion.textos import AVISO_EXPERIMENTAL  # noqa: E402


def _leer(ruta: Path, canal: int | None):
    """Lee un NIfTI en orientación canónica (RAS) y devuelve (datos 3D, espaciado)."""
    img = nib.as_closest_canonical(nib.load(str(ruta)))
    datos = np.asarray(img.dataobj, dtype=np.float32)
    if datos.ndim == 4:
        datos = datos[..., canal or 0]
    if datos.ndim != 3:
        raise ValueError(f"{ruta.name}: se esperaba un volumen 3D o 4D.")
    return datos, tuple(float(z) for z in img.header.get_zooms()[:3])


def _segmentar(a: argparse.Namespace) -> tuple[Path, dict]:
    """Ejecuta la cadena con el modelo; devuelve la máscara en el espacio original y datos de trazabilidad."""
    from prosta_ai.pipeline.base import PipelineInput
    from prosta_ai.pipeline.errors import StageError
    from prosta_ai.pipeline.factory import build_pipeline, directorio_modelos, model_info

    carpeta = a.directorio_modelos or directorio_modelos(RAIZ / "modelos")
    pipeline = build_pipeline(a.modelo, carpeta, a.dispositivo)
    t0 = time.perf_counter()
    try:
        r = pipeline.run(PipelineInput([a.imagen], "NIfTI", [a.referencia] if a.referencia else [], a.salida))
    except StageError as exc:
        print(f"Error en la etapa {exc.stage}: {exc.message}", file=sys.stderr)
        raise SystemExit(1)
    info = model_info(a.modelo, carpeta)
    extra = {
        "modelo": {k: info[k] for k in ("nombre", "version", "hash_pesos")},
        "dispositivo": str(getattr(pipeline.strategy, "device", "")),
        "tiempos_s": {k: round(v, 2) for k, v in r.durations.items()},
        "tiempo_total_s": round(time.perf_counter() - t0, 2),
        "dice_espacio_preparado": r.dice,
        "iou_espacio_preparado": r.iou,
    }
    return a.salida / "mascara_original.nii.gz", extra


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--imagen", type=Path, required=True)
    ap.add_argument("--mascara", type=Path, help="máscara a mostrar (p. ej. la predicha); alternativa a --modelo")
    ap.add_argument("--modelo", help="nombre del modelo con el que segmentar (p. ej. prostate_mri_anatomy)")
    ap.add_argument("--directorio-modelos", type=Path, help="carpeta de modelos (por defecto $PROSTA_MODELOS o ./modelos)")
    ap.add_argument("--dispositivo", help="cpu o cuda (por defecto automático)")
    ap.add_argument("--referencia", type=Path, help="máscara de referencia para Dice e IoU")
    ap.add_argument("--canal", type=int, default=0, help="canal si la imagen es 4D (por defecto 0, T2)")
    ap.add_argument("--cortes", type=int, default=3, help="cantidad de cortes con ROI a exportar")
    ap.add_argument("--salida", type=Path, required=True)
    a = ap.parse_args(argv)

    if bool(a.mascara) == bool(a.modelo):
        print("Error: indique exactamente una de las opciones --mascara o --modelo.", file=sys.stderr)
        return 2
    a.salida.mkdir(parents=True, exist_ok=True)
    extra: dict = {}
    if a.modelo:
        a.mascara, extra = _segmentar(a)
    imagen, esp = _leer(a.imagen, a.canal)
    mascara = _leer(a.mascara, None)[0] > 0
    if mascara.shape != imagen.shape:
        print(f"Error: la máscara {mascara.shape} no coincide con la imagen {imagen.shape}.", file=sys.stderr)
        return 2
    resumen = calcular_roi(mascara, esp)
    metricas = None
    if a.referencia:
        ref = _leer(a.referencia, None)[0] > 0
        if ref.shape != imagen.shape:
            print("Error: la referencia no coincide con la imagen.", file=sys.stderr)
            return 2
        metricas = dice_iou(mascara, ref)

    img8 = normalizar(imagen)
    texto = texto_explicativo(resumen.a_dict(), metricas, incluir_aviso=False)  # la figura imprime el aviso al pie
    cortes = seleccionar_cortes(mascara, a.cortes)
    if not cortes:  # sin ROI: se exporta el corte central con el mensaje
        cortes = [imagen.shape[2] // 2]
    archivos = []
    for z in cortes:
        ruta = a.salida / f"roi_corte_{z + 1:03d}.png"
        figura_comparada(img8, mascara, z, texto).save(ruta)
        archivos.append(ruta.name)

    salida = {
        "imagen": a.imagen.name,
        "mascara": a.mascara.name,
        "referencia": a.referencia.name if a.referencia else None,
        "roi": resumen.a_dict(),
        "metricas": metricas,
        **extra,
        "cortes_exportados": [z + 1 for z in cortes],  # numeración desde 1
        "archivos": archivos,
        "aviso": AVISO_EXPERIMENTAL,
    }
    (a.salida / "resumen_roi.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(resumen.mensaje)
    if metricas:
        print(f"Dice={metricas['dice']}, IoU={metricas['iou']}")
    print(f"Salida en {a.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
