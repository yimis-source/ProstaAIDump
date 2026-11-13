"""Textos de aviso, explicación y límites de la ROI (RF-15, RF-16, RF-17; N3 y N4)."""
from __future__ import annotations

AVISO_EXPERIMENTAL = (
    "Resultado experimental con fines académicos. No es un diagnóstico ni "
    "sustituye la valoración de un profesional de la salud."
)

LEYENDA_ORIGINAL = "Original"
LEYENDA_ROI = "Original + ROI"
LEYENDA_COLOR = "Región de interés (ROI) estimada por el modelo"

EXPLICACION = (
    "La región de interés (ROI) es el área que el modelo estima como próstata, "
    "dibujada en color sobre el corte de la imagen de resonancia T2. Sirve para "
    "ver qué zona segmentó el programa y compararla con la imagen original."
)

LIMITES = (
    "La ROI es una estimación automática y puede equivocarse: incluir tejido que "
    "no es próstata o dejar fuera parte de ella, sobre todo en la base y el ápice. "
    "Se probó con pocos estudios de un solo conjunto de datos y no se validó "
    "clínicamente. Dice e IoU solo se calculan si existe una máscara de referencia. "
    "El volumen en mL depende del espaciado de la imagen. No use este resultado "
    "para decisiones médicas."
)

SIN_ROI = (
    "No se encontró región de interés: el modelo no marcó ninguna zona en este "
    "estudio. Esto no indica ausencia ni presencia de enfermedad."
)


def texto_explicativo(resumen: dict | None = None, metricas: dict | None = None, incluir_aviso: bool = True) -> str:
    """Texto completo: explicación, cifras (si hay ROI), límites y aviso (omitible si la figura ya lo imprime)."""
    partes = [EXPLICACION]
    if resumen is not None:
        if resumen.get("hay_roi"):
            partes.append(
                f"En este estudio la ROI ocupa {len(resumen['cortes_con_roi'])} cortes y "
                f"tiene un volumen aproximado de {resumen['volumen_ml']:.1f} mL."
            )
        else:
            partes.append(SIN_ROI)
    if metricas and metricas.get("dice") is not None:
        partes.append(
            f"Frente a la referencia: Dice {metricas['dice']:.3f}, IoU {metricas['iou']:.3f}."
        )
    elif metricas is not None:
        partes.append("Dice e IoU no disponibles para este estudio.")
    partes.append(LIMITES)
    if incluir_aviso:
        partes.append(AVISO_EXPERIMENTAL)
    return "\n\n".join(partes)
