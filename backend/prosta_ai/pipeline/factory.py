"""Construcción del pipeline y datos del modelo para la trazabilidad."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .base import Segmentation3DPipeline
from .segmentation import PretrainedUNetStrategy, create_strategy

# Carpeta de modelos: argumento explícito o variable de entorno. Los pesos no se versionan.
VARIABLE_MODELOS = "PROSTA_MODELOS"


def directorio_modelos(por_defecto: Path) -> Path:
    """`$PROSTA_MODELOS` si está definida; si no, `por_defecto`."""
    valor = os.environ.get(VARIABLE_MODELOS)
    return Path(valor) if valor else Path(por_defecto)


def build_pipeline(model_name: str, model_dir: Path, device: str | None = None) -> Segmentation3DPipeline:
    """Crea el pipeline con la estrategia indicada. Los pesos se cargan al primer uso."""
    return Segmentation3DPipeline(create_strategy(model_name, model_dir, device))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def model_info(model_name: str, model_dir: Path) -> dict:
    """Nombre, versión, rutas y hash SHA-256 de los pesos (o None si no están)."""
    estrategia = create_strategy(model_name, model_dir, device="cpu")
    pesos = estrategia.weights_path
    hay_pesos = pesos is not None and Path(pesos).is_file()
    config = None
    if isinstance(estrategia, PretrainedUNetStrategy):
        config = estrategia.config_path if estrategia.config_path.exists() else None
    return {
        "nombre": estrategia.name or model_name,
        "version": estrategia.version or "desconocida",
        "ruta_pesos": str(pesos) if pesos is not None else None,
        "hash_pesos": sha256(Path(pesos)) if hay_pesos else None,
        "ruta_configuracion": str(config) if config is not None else None,
    }
