"""Visualización de la ROI superpuesta y textos de explicación (Ciclo 4)."""
from .render import COLOR_ROI, con_aviso, figura_comparada, normalizar, superponer
from .textos import AVISO_EXPERIMENTAL, EXPLICACION, LIMITES, texto_explicativo

__all__ = [
    "AVISO_EXPERIMENTAL", "COLOR_ROI", "EXPLICACION", "LIMITES", "con_aviso",
    "figura_comparada", "normalizar", "superponer", "texto_explicativo",
]
