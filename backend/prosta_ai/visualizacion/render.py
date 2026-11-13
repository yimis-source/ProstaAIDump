"""Superposición de la ROI sobre cortes axiales (RF-13), sin dependencias web ni de BD.

Porta la lógica de dibujo del proyecto original (rendering.py) como funciones puras.
Los arreglos tienen ejes (x, y, z); el corte se muestra con x a la derecha e y arriba.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .textos import AVISO_EXPERIMENTAL, LEYENDA_COLOR, LEYENDA_ORIGINAL, LEYENDA_ROI

COLOR_ROI = (45, 212, 191)  # verde azulado (#2DD4BF) del diseño CU04
ALFA_ROI = 0.45
ANCHO_MINIMO = 512
_RUTA_FUENTE = Path(__file__).resolve().parent.parent / "recursos" / "DejaVuSans.ttf"


def _fuente(tam: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(_RUTA_FUENTE), tam)
    except OSError:
        return ImageFont.load_default(size=tam)


def normalizar(datos: np.ndarray) -> np.ndarray:
    """Intensidad a 0-255 con percentiles 1 y 99 (uint8)."""
    p1, p99 = np.percentile(datos, [1, 99])
    if p99 <= p1:
        return np.zeros(datos.shape, dtype=np.uint8)
    return (np.clip((datos - p1) / (p99 - p1), 0, 1) * 255).astype(np.uint8)


def plano(corte2d: np.ndarray) -> np.ndarray:
    """Corte axial con fila 0 arriba (y hacia arriba, x a la derecha)."""
    return np.rot90(corte2d)


def superponer(
    imagen_u8: np.ndarray,
    mascara: np.ndarray | None,
    indice: int,
    color: tuple[int, int, int] = COLOR_ROI,
    alfa: float = ALFA_ROI,
) -> Image.Image:
    """RGB del corte ``indice`` con la ROI mezclada; solo cambian los vóxeles de la máscara."""
    if mascara is not None and mascara.shape != imagen_u8.shape:
        raise ValueError("La máscara no tiene la misma forma que la imagen.")
    if not 0 <= indice < imagen_u8.shape[2]:
        raise IndexError("Índice de corte fuera de rango.")
    gris = plano(imagen_u8[:, :, indice])
    rgb = np.repeat(gris[:, :, None], 3, axis=2).astype(np.float32)
    if mascara is not None:
        roi = plano(mascara[:, :, indice] > 0)
        rgb[roi] = (1 - alfa) * rgb[roi] + alfa * np.array(color, dtype=np.float32)
    return Image.fromarray(np.rint(rgb).astype(np.uint8), mode="RGB")


def corte_original(imagen_u8: np.ndarray, indice: int) -> Image.Image:
    return superponer(imagen_u8, None, indice)


def _escalar(img: Image.Image, ancho_min: int) -> Image.Image:
    factor = max(1, -(-ancho_min // img.width))
    if factor > 1:
        img = img.resize((img.width * factor, img.height * factor), Image.Resampling.NEAREST)
    return img


def _lineas(texto: str, fuente, ancho: int, dib: ImageDraw.ImageDraw) -> list[str]:
    """Divide el texto (respetando saltos de párrafo) para que quepa en ``ancho``."""
    salida: list[str] = []
    for parrafo in texto.split("\n"):
        n = 220
        lineas = textwrap.wrap(parrafo, width=n) or [""]
        while n > 8 and max(dib.textlength(l, font=fuente) for l in lineas) > ancho:
            n -= 2
            lineas = textwrap.wrap(parrafo, width=n) or [""]
        salida.extend(lineas)
    return salida


def pie_texto(ancho: int, texto: str, tam: int, fondo=(20, 20, 20), color=(255, 255, 255)) -> Image.Image:
    """Franja de texto con ajuste de línea (aviso o explicación)."""
    fuente = _fuente(tam)
    medidor = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lineas = _lineas(texto, fuente, ancho - 20, medidor)
    alto_linea = int(tam * 1.35)
    pie = Image.new("RGB", (ancho, alto_linea * len(lineas) + 16), fondo)
    dib = ImageDraw.Draw(pie)
    for i, linea in enumerate(lineas):
        dib.text((10, 8 + i * alto_linea), linea, fill=color, font=fuente)
    return pie


def con_aviso(img: Image.Image, aviso: str = AVISO_EXPERIMENTAL) -> Image.Image:
    """Imagen con el aviso experimental impreso debajo."""
    img = _escalar(img.convert("RGB"), ANCHO_MINIMO)
    pie = pie_texto(img.width, aviso, max(12, img.width // 38))
    lienzo = Image.new("RGB", (img.width, img.height + pie.height))
    lienzo.paste(img, (0, 0))
    lienzo.paste(pie, (0, img.height))
    return lienzo


def figura_comparada(
    imagen_u8: np.ndarray,
    mascara: np.ndarray | None,
    indice: int,
    explicacion: str | None = None,
    ancho_panel: int = 512,
) -> Image.Image:
    """Paneles «Original» y «Original + ROI» lado a lado, leyenda, explicación y aviso (CU04)."""
    izq = _escalar(corte_original(imagen_u8, indice), ancho_panel)
    der = _escalar(superponer(imagen_u8, mascara, indice), ancho_panel)
    tam = max(14, ancho_panel // 34)
    cab = Image.new("RGB", (izq.width + der.width + 10, int(tam * 2)), (23, 36, 59))
    d = ImageDraw.Draw(cab)
    f = _fuente(tam)
    d.text((10, tam // 2), f"{LEYENDA_ORIGINAL}  (corte {indice + 1}/{imagen_u8.shape[2]})", fill=(223, 230, 238), font=f)
    d.text((izq.width + 20, tam // 2), LEYENDA_ROI, fill=(223, 230, 238), font=f)
    cuerpo = Image.new("RGB", (cab.width, izq.height), (8, 11, 16))
    cuerpo.paste(izq, (0, 0))
    cuerpo.paste(der, (izq.width + 10, 0))
    # leyenda de color
    ley = Image.new("RGB", (cab.width, int(tam * 2)), (17, 25, 35))
    d = ImageDraw.Draw(ley)
    d.rectangle([10, tam // 2, 10 + tam, tam // 2 + tam], fill=COLOR_ROI)
    d.text((22 + tam, tam // 2), LEYENDA_COLOR, fill=(223, 230, 238), font=f)
    trozos = [cab, cuerpo, ley]
    if explicacion:
        trozos.append(pie_texto(cab.width, explicacion, max(12, tam - 3), fondo=(17, 25, 35), color=(214, 222, 232)))
    trozos.append(pie_texto(cab.width, AVISO_EXPERIMENTAL, tam, fondo=(120, 53, 15), color=(255, 255, 255)))
    lienzo = Image.new("RGB", (cab.width, sum(t.height for t in trozos)))
    y = 0
    for t in trozos:
        lienzo.paste(t, (0, y))
        y += t.height
    return lienzo
