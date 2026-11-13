"""Genera la ROI superpuesta (PNG) y su resumen (JSON) desde una imagen y una máscara NIfTI.

Uso:
    python scripts/generar_roi.py --imagen img.nii.gz --mascara pred.nii.gz \\
        [--referencia ref.nii.gz] [--canal 0] [--cortes 3] --salida carpeta

La máscara y la referencia se binarizan (unión de etiquetas > 0). Resultado
experimental con fines académicos; no es un diagnóstico.
"""
from __future__ import annotations

import argparse
import json
import sys
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--imagen", type=Path, required=True)
    ap.add_argument("--mascara", type=Path, required=True, help="máscara a mostrar (p. ej. la predicha)")
    ap.add_argument("--referencia", type=Path, help="máscara de referencia para Dice e IoU")
    ap.add_argument("--canal", type=int, default=0, help="canal si la imagen es 4D (por defecto 0, T2)")
    ap.add_argument("--cortes", type=int, default=3, help="cantidad de cortes con ROI a exportar")
    ap.add_argument("--salida", type=Path, required=True)
    a = ap.parse_args(argv)

    a.salida.mkdir(parents=True, exist_ok=True)
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
