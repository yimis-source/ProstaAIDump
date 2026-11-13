"""Control de calidad del volumen leído (patrón Chain of Responsibility).

Es la validación detallada de la etapa «control de calidad» (RF-10). La
admisión de archivos subidos (formato y tamaño) es del Ciclo 6.
Los umbrales coinciden con `preprocesamiento/control_calidad.py` (Ciclo 2).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from .errors import StageError
from .stages import CONTROL_CALIDAD

if TYPE_CHECKING:  # evita importar io (y sus dependencias) al cargar los validadores
    from .io import Volume

MIN_SLICES = 8
MIN_SIDE = 32


@dataclass
class ValidationContext:
    """Datos que viajan por la cadena de validadores."""

    volume: "Volume | None" = None
    reference: "Volume | None" = None


class Validator(ABC):
    """Eslabón de la cadena: valida y pasa el contexto al siguiente."""

    def __init__(self) -> None:
        self._next: Validator | None = None

    def set_next(self, validator: "Validator") -> "Validator":
        self._next = validator
        return validator

    def handle(self, ctx: ValidationContext) -> None:
        self.check(ctx)
        if self._next is not None:
            self._next.handle(ctx)

    @abstractmethod
    def check(self, ctx: ValidationContext) -> None:
        """Lanza StageError si el contexto no es válido."""


class IntegrityValidator(Validator):
    """El volumen debe ser 3D, finito y no constante."""

    def check(self, ctx: ValidationContext) -> None:
        vol = ctx.volume
        if vol is None:
            raise StageError(CONTROL_CALIDAD, "No se pudo leer el volumen.")
        if vol.data.ndim != 3:
            raise StageError(CONTROL_CALIDAD, "El estudio no es un volumen 3D.")
        if not np.isfinite(vol.data).all():
            raise StageError(CONTROL_CALIDAD, "El volumen contiene valores no numéricos (NaN o infinitos).")
        if float(vol.data.max()) == float(vol.data.min()):
            raise StageError(CONTROL_CALIDAD, "El volumen tiene intensidad constante.")


class MetadataValidator(Validator):
    """Tamaño mínimo, espaciado positivo y referencia compatible."""

    def check(self, ctx: ValidationContext) -> None:
        vol = ctx.volume
        assert vol is not None
        x, y, z = vol.data.shape
        if z < MIN_SLICES:
            raise StageError(CONTROL_CALIDAD, f"El volumen tiene {z} cortes; se necesitan al menos {MIN_SLICES}.")
        if x < MIN_SIDE or y < MIN_SIDE:
            raise StageError(
                CONTROL_CALIDAD, f"Los cortes miden {x}x{y} vóxeles; se necesitan al menos {MIN_SIDE}x{MIN_SIDE}."
            )
        if not all(np.isfinite(s) and s > 0 for s in vol.spacing):
            raise StageError(CONTROL_CALIDAD, "El espaciado entre vóxeles no es positivo.")
        ref = ctx.reference
        if ref is not None:
            if ref.data.shape != vol.data.shape:
                raise StageError(
                    CONTROL_CALIDAD,
                    f"La referencia ({ref.data.shape}) no tiene la misma forma que la imagen ({vol.data.shape}).",
                )
            if not np.allclose(ref.affine, vol.affine, atol=1e-3):
                raise StageError(CONTROL_CALIDAD, "La referencia no tiene la misma geometría que la imagen.")


def detailed_validation(volume: "Volume", reference: "Volume | None" = None) -> None:
    """Cadena IntegrityValidator -> MetadataValidator sobre un volumen ya leído."""
    cadena = IntegrityValidator()
    cadena.set_next(MetadataValidator())
    cadena.handle(ValidationContext(volume=volume, reference=reference))
