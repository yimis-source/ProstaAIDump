"""Región de interés (ROI) a partir de una máscara de segmentación (Ciclo 4, RF-12).

Funciones puras sobre arreglos NumPy: no leen archivos ni dependen de la API o la
base de datos. La orientación de los ejes es la del arreglo recibido (x, y, z).
Resultado experimental con fines académicos; no es un diagnóstico.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np

MENSAJE_SIN_ROI = (
    "No se encontró región de interés: la máscara está vacía. El modelo no marcó "
    "ningún vóxel como próstata en este estudio."
)


@dataclass
class ResumenROI:
    """Cifras descriptivas de la ROI (todas respecto a la rejilla de la imagen)."""

    hay_roi: bool
    forma: tuple[int, int, int]
    espaciado_mm: tuple[float, float, float]
    n_voxeles: int = 0
    volumen_ml: float = 0.0
    cortes_con_roi: list[int] = field(default_factory=list)  # índices z (base 0)
    centroide_vox: tuple[float, float, float] | None = None
    centroide_mm: tuple[float, float, float] | None = None
    caja_vox: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None  # mín y máx inclusivos
    caja_tamano_mm: tuple[float, float, float] | None = None
    mensaje: str = ""

    def a_dict(self) -> dict:
        return asdict(self)


def binarizar(mascara: np.ndarray, etiquetas: tuple[int, ...] | None = None) -> np.ndarray:
    """Máscara booleana: unión de etiquetas > 0, o solo las indicadas."""
    m = np.asarray(mascara)
    if etiquetas is None:
        return m > 0
    return np.isin(m, etiquetas)


def mask_to_original_space(
    mascara: np.ndarray,
    afin_preparada: np.ndarray,
    forma_original: tuple[int, int, int],
    afin_original: np.ndarray,
) -> np.ndarray:
    """Remuestrea (vecino más cercano) la máscara preparada a la rejilla original.

    Para cada vóxel original se calcula su posición en mundo con la afín original
    y se busca el vóxel correspondiente en el espacio preparado; así la máscara
    sigue siendo binaria. El resultado tiene la forma de la imagen original.
    """
    if mascara.ndim != 3:
        raise ValueError("La máscara debe ser un volumen 3D.")
    a = np.linalg.inv(afin_preparada) @ afin_original
    out = np.zeros(forma_original, dtype=np.uint8)
    ms = np.array(mascara.shape)
    ii, jj = np.meshgrid(np.arange(forma_original[0]), np.arange(forma_original[1]), indexing="ij")
    for k in range(forma_original[2]):  # corte a corte para limitar la memoria
        idx = a[:3, 0, None, None] * ii + a[:3, 1, None, None] * jj + a[:3, 2, None, None] * k + a[:3, 3, None, None]
        idx = np.rint(idx).astype(np.int64)
        dentro = np.all((idx >= 0) & (idx < ms[:, None, None]), axis=0)
        corte = np.zeros(forma_original[:2], dtype=np.uint8)
        corte[dentro] = mascara[idx[0][dentro], idx[1][dentro], idx[2][dentro]] > 0
        out[:, :, k] = corte
    return out


def volumen_ml(mascara: np.ndarray, espaciado_mm: tuple[float, float, float]) -> float:
    """Volumen de la ROI en mililitros (1 mL = 1000 mm³)."""
    return float(np.count_nonzero(mascara)) * float(np.prod(espaciado_mm)) / 1000.0


def calcular_roi(mascara: np.ndarray, espaciado_mm: tuple[float, float, float]) -> ResumenROI:
    """Resume la ROI: volumen, cortes, centroide y caja envolvente.

    Con máscara vacía no falla: devuelve ``hay_roi=False`` y un mensaje claro.
    """
    m = np.asarray(mascara) > 0
    if m.ndim != 3:
        raise ValueError("La máscara debe ser un volumen 3D.")
    if len(espaciado_mm) != 3 or not all(np.isfinite(espaciado_mm)) or min(espaciado_mm) <= 0:
        raise ValueError("El espaciado debe tener 3 valores positivos y finitos.")
    esp = tuple(round(float(e), 4) for e in espaciado_mm)
    forma = tuple(int(n) for n in m.shape)
    n = int(np.count_nonzero(m))
    if n == 0:
        return ResumenROI(False, forma, esp, mensaje=MENSAJE_SIN_ROI)
    coords = np.argwhere(m)
    minimos, maximos = coords.min(axis=0), coords.max(axis=0)
    centroide = coords.mean(axis=0)
    cortes = [int(z) for z in np.flatnonzero(m.any(axis=(0, 1)))]
    return ResumenROI(
        hay_roi=True,
        forma=forma,
        espaciado_mm=esp,
        n_voxeles=n,
        volumen_ml=round(volumen_ml(m, esp), 4),
        cortes_con_roi=cortes,
        centroide_vox=tuple(round(float(c), 2) for c in centroide),
        centroide_mm=tuple(round(float(c * e), 2) for c, e in zip(centroide, esp)),
        caja_vox=(tuple(int(v) for v in minimos), tuple(int(v) for v in maximos)),
        caja_tamano_mm=tuple(round(float((b - a + 1) * e), 2) for a, b, e in zip(minimos, maximos, esp)),
        mensaje=f"ROI con {len(cortes)} cortes y {volumen_ml(m, esp):.1f} mL.",
    )


def dice_iou(prediccion: np.ndarray, referencia: np.ndarray) -> dict[str, float | None]:
    """Dice e IoU entre dos máscaras de igual forma (None si ambas están vacías)."""
    p, r = np.asarray(prediccion) > 0, np.asarray(referencia) > 0
    if p.shape != r.shape:
        raise ValueError("La predicción y la referencia deben tener la misma forma.")
    inter = int(np.count_nonzero(p & r))
    suma = int(np.count_nonzero(p)) + int(np.count_nonzero(r))
    union = suma - inter
    if suma == 0:
        return {"dice": None, "iou": None}
    return {"dice": 2 * inter / suma, "iou": inter / union}


def corte_representativo(mascara: np.ndarray) -> int | None:
    """Índice z del corte con más vóxeles de ROI (None si no hay ROI)."""
    areas = (np.asarray(mascara) > 0).sum(axis=(0, 1))
    return int(areas.argmax()) if areas.max() > 0 else None


def seleccionar_cortes(mascara: np.ndarray, cantidad: int = 3) -> list[int]:
    """Hasta ``cantidad`` cortes con ROI repartidos de forma uniforme.

    Siempre incluye el corte de mayor área (reemplaza al más cercano).
    """
    cortes = [int(c) for c in np.flatnonzero((np.asarray(mascara) > 0).any(axis=(0, 1)))]
    if not cortes or cantidad < 1:
        return []
    if len(cortes) <= cantidad:
        return cortes
    pos = np.linspace(0, len(cortes) - 1, cantidad + 2)[1:-1]  # sin los extremos (bordes poco informativos)
    elegidos = sorted({cortes[int(round(p))] for p in pos})
    mayor = corte_representativo(mascara)
    if mayor not in elegidos:
        elegidos.remove(min(elegidos, key=lambda c: abs(c - mayor)))
        elegidos.append(mayor)
    return sorted(elegidos)
