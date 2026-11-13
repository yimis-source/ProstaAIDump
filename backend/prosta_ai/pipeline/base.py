"""Orden fijo del procesamiento (patrón Template Method).

Control de calidad → preparación → segmentación → evaluación.

La evaluación compara la máscara con la referencia **en el espacio preparado**
(orientación RAS y vóxeles isotrópicos del modelo): la referencia se lleva a ese
espacio con vecino más cercano (`prepare_label`). La etapa ROI del Ciclo 4 se
inserta sobrescribiendo `etapas()`.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import stages
from .errors import StageError
from .evaluation import dice, iou
from .io import Volume, load_volume, save_nifti
from .preparation import PreparationConfig, PreparedVolume, prepare_label, prepare_volume
from .progress import PipelineProgress, TimingRecorder
from .segmentation import SegmentationStrategy
from .validators import detailed_validation


@dataclass
class PipelineInput:
    files: list[Path]
    fmt: str = "NIfTI"
    reference_files: list[Path] = field(default_factory=list)
    output_dir: Path | None = None  # si se indica, se guarda la máscara


@dataclass
class PipelineOutput:
    mask: np.ndarray  # máscara binaria en el espacio preparado
    prepared_affine: np.ndarray
    mask_path: Path | None
    dice: float | None
    iou: float | None
    durations: dict[str, float]


@dataclass
class PipelineContext:
    """Estado compartido entre etapas durante una ejecución."""

    volume: Volume | None = None
    reference_volume: Volume | None = None
    prepared: PreparedVolume | None = None
    mask: np.ndarray | None = None  # en el espacio preparado
    mask_path: Path | None = None
    dice: float | None = None
    iou: float | None = None
    extra: dict = field(default_factory=dict)


Etapa = Callable[[PipelineInput, PipelineContext], None]


class BasePipeline(ABC):
    """Define `run`; las subclases implementan cada etapa."""

    def etapas(self) -> list[tuple[str, Etapa]]:
        """Etapas en orden; el Ciclo 4 inserta la ROI entre la segmentación y la evaluación."""
        return [
            (stages.CONTROL_CALIDAD, self.quality_control),
            (stages.PREPARACION, self.prepare),
            (stages.SEGMENTACION, self.segment),
            (stages.EVALUACION, self.evaluate),
        ]

    def run(self, inp: PipelineInput, progress: PipelineProgress | None = None) -> PipelineOutput:
        progress = progress or PipelineProgress()
        ctx = PipelineContext()
        timing = TimingRecorder()
        progress.attach(timing)
        for nombre, funcion in self.etapas():
            progress.notify_start(nombre)
            t0 = time.perf_counter()
            try:
                funcion(inp, ctx)
            except StageError as exc:
                progress.notify_failed(nombre, exc.message)
                raise
            except Exception as exc:  # error no previsto: se informa de forma controlada
                err = StageError(nombre, "Ocurrió un error inesperado durante esta etapa.")
                progress.notify_failed(nombre, err.message)
                raise err from exc
            progress.notify_end(nombre, time.perf_counter() - t0)
        assert ctx.mask is not None and ctx.prepared is not None
        return PipelineOutput(
            mask=ctx.mask,
            prepared_affine=ctx.prepared.affine,
            mask_path=ctx.mask_path,
            dice=ctx.dice,
            iou=ctx.iou,
            durations=dict(timing.durations),
        )

    @abstractmethod
    def quality_control(self, inp: PipelineInput, ctx: PipelineContext) -> None: ...

    @abstractmethod
    def prepare(self, inp: PipelineInput, ctx: PipelineContext) -> None: ...

    @abstractmethod
    def segment(self, inp: PipelineInput, ctx: PipelineContext) -> None: ...

    @abstractmethod
    def evaluate(self, inp: PipelineInput, ctx: PipelineContext) -> None: ...


def _leer_referencia(files: list[Path], fmt: str) -> Volume:
    """La referencia es un NIfTI o, si no, una serie del mismo formato que el estudio."""
    if len(files) == 1 and str(files[0]).lower().endswith((".nii", ".nii.gz")):
        return load_volume(files, "NIfTI")
    return load_volume(files, fmt)


class Segmentation3DPipeline(BasePipeline):
    """Segmentación 3D de la próstata con la estrategia indicada."""

    def __init__(self, strategy: SegmentationStrategy, config: PreparationConfig | None = None):
        self.strategy = strategy
        # por defecto la configuración sale de la propia estrategia (si la tiene)
        self._config = config

    def preparation_config(self) -> PreparationConfig:
        cfg = self._config or getattr(self.strategy, "config", None)
        if cfg is None:
            raise StageError(stages.PREPARACION, "El modelo no tiene configuración de preparación.")
        return cfg

    def quality_control(self, inp: PipelineInput, ctx: PipelineContext) -> None:
        volume = load_volume([Path(f) for f in inp.files], inp.fmt)
        ref_files = [Path(f) for f in inp.reference_files]
        reference = _leer_referencia(ref_files, inp.fmt) if ref_files else None
        detailed_validation(volume, reference)
        ctx.volume = volume
        ctx.reference_volume = reference

    def prepare(self, inp: PipelineInput, ctx: PipelineContext) -> None:
        assert ctx.volume is not None
        ctx.prepared = prepare_volume(ctx.volume, self.preparation_config())

    def segment(self, inp: PipelineInput, ctx: PipelineContext) -> None:
        assert ctx.prepared is not None
        mask = np.asarray(self.strategy.segment(ctx.prepared)).astype(np.uint8)
        esperada = tuple(ctx.prepared.tensor.shape[1:])
        if mask.shape != esperada:
            raise StageError(stages.SEGMENTACION, f"La máscara {mask.shape} no coincide con el volumen {esperada}.")
        ctx.mask = mask
        if inp.output_dir is not None:
            ctx.mask_path = Path(inp.output_dir) / "mascara_preparada.nii.gz"
            save_nifti(mask, ctx.prepared.affine, ctx.mask_path)

    def evaluate(self, inp: PipelineInput, ctx: PipelineContext) -> None:
        if ctx.reference_volume is None or ctx.mask is None:
            return  # sin referencia: dice = iou = None
        referencia = prepare_label(ctx.reference_volume, self.preparation_config()) > 0
        if referencia.shape != ctx.mask.shape:
            raise StageError(stages.EVALUACION, "La referencia preparada no coincide con la máscara.")
        ctx.dice = dice(ctx.mask, referencia)
        ctx.iou = iou(ctx.mask, referencia)
