# Ciclo 4: Generación de mapa / Región de interés (ROI)

Entregable 5, hito H006. La máscara o ROI se superpone a la imagen junto con una explicación del resultado y sus límites, con el aviso de uso académico, experimental y no diagnóstico (Necesidades 3 y 4; RF-12, RF-13, RF-15, RF-16, RF-17).

> Resultado experimental con fines académicos. No es un diagnóstico ni sustituye la valoración de un profesional de la salud.

## Contenido

| Archivo | Qué es |
|---|---|
| `backend/prosta_ai/pipeline/roi.py` | Funciones puras: ROI en el espacio original, volumen en mL, cortes con ROI, centroide, caja envolvente, Dice/IoU, selección de cortes |
| `backend/prosta_ai/visualizacion/render.py` | Superposición de la máscara sobre cortes, figura «Original / Original + ROI», leyenda y pie de aviso (sin FastAPI ni BD) |
| `backend/prosta_ai/visualizacion/textos.py` | Aviso, explicación, límites y mensaje de «sin ROI» |
| `backend/prosta_ai/recursos/` | Fuente DejaVu Sans (tildes y eñes) y su licencia |
| `scripts/generar_roi.py` | CLI: imagen NIfTI + máscara (`--mascara`) o segmentación con el modelo (`--modelo`) -> PNG + `resumen_roi.json` |
| `backend/prosta_ai/pipeline/base.py` | Etapa ROI dentro de la cadena (`build_roi`) |
| `tests/test_roi.py`, `tests/test_visualizacion.py`, `tests/test_segmentacion.py` | Pruebas con volúmenes sintéticos; la etapa ROI se prueba con la estrategia simulada y una UNet mínima, sin pesos reales |
| `docs/roi/ejemplos/` | Dos PNG con máscara predicha de casos de prueba de Task05_Prostate |

Uso (con `--mascara` en lugar de `--modelo` se muestra una máscara ya existente):

```
python scripts/generar_roi.py --imagen img.nii.gz --modelo prostate_mri_anatomy \
    [--referencia ref.nii.gz] [--canal 0] [--cortes 3] --salida carpeta
```

## Cómo se calcula la ROI

1. La máscara (predicha o de referencia) se binariza: unión de etiquetas > 0.
2. Si viene del espacio preparado del modelo, `mask_to_original_space` la devuelve a la rejilla de la imagen original con vecino más cercano (sigue siendo binaria) usando las afines de ambos espacios.
3. `calcular_roi` obtiene, con el espaciado en mm de la imagen:
   - **Volumen** (mL) = vóxeles de la ROI x volumen del vóxel (mm³) / 1000.
   - **Cortes con ROI** (índices z, base 0) y cantidad.
   - **Centroide** en vóxeles y en mm (respecto al origen de la rejilla, orientación canónica RAS).
   - **Caja envolvente** (mínimo y máximo por eje) y su tamaño en mm.
4. Si hay máscara de referencia, `dice_iou` calcula Dice e IoU; si ambas están vacías devuelve `None`.
5. **Máscara vacía:** no falla. Devuelve `hay_roi = false` y el mensaje «No se encontró región de interés...», que también aparece en el texto explicativo (y aclara que no indica ausencia ni presencia de enfermedad).

La imagen se lee en orientación canónica y se normaliza a 0-255 con los percentiles 1 y 99 (canal 0 = T2 en Task05).

## Qué muestra la superposición

Sigue el diseño CU04 aprobado en el Ciclo 2 (paneles «Original» y «Original + ROI» lado a lado con el mismo corte):

- Dos paneles con el mismo corte axial; la ROI se mezcla en el derecho con el color verde azulado `#2DD4BF` y opacidad 0,45 (la paleta del diseño). Solo cambian los vóxeles de la máscara; la forma del corte se conserva.
- Leyenda de color y número de corte (n/total).
- Panel de explicación («¿Qué estoy viendo?»), con cifras y límites.
- Franja de aviso experimental siempre al pie (RF-15).

El script exporta por defecto 3 cortes con ROI repartidos de forma uniforme, incluyendo el de mayor área. Sin ROI exporta el corte central con el mensaje.

## Texto de explicación y límites

Explicación: la ROI es el área que el modelo estima como próstata, dibujada en color sobre el corte T2, para ver qué zona segmentó el programa y compararla con la original.

Límites (resumen): es una estimación automática que puede incluir tejido que no es próstata o dejar fuera parte de ella (base y ápice); se probó con pocos estudios de un solo conjunto de datos; no está validada clínicamente; Dice e IoU solo existen con máscara de referencia; el volumen depende del espaciado; no debe usarse para decisiones médicas. El texto completo está en `textos.py` y es la fuente única para la pantalla CU04 del Ciclo 6.

## Resultados reales con la máscara predicha

La etapa ROI ya forma parte de la cadena (`Segmentation3DPipeline.etapas()`: control de calidad, preparación, segmentación, **ROI**, evaluación). Lleva la máscara predicha del espacio preparado a la rejilla de la imagen con `mask_to_original_space` y calcula `calcular_roi`; con referencia, la evaluación añade `dice_original` e `iou_original`. Sin API, BD ni frontend (Ciclo 6).

Ejecución real con `scripts/generar_roi.py --modelo prostate_mri_anatomy` (UNet preentrenado v0.3.6, CPU) sobre dos casos del conjunto de **prueba** de la división (`entrenamiento/division_task05.json`), imagen T2 (canal 0) y referencia de `labelsTr` (unión de etiquetas > 0). Los dos casos son los de menor y de mayor Dice de este subconjunto de la evaluación del Ciclo 3 ([docs/modelo/03](../modelo/03_resultados_evaluacion.md)), y las cifras coinciden con ella.

```
PROSTA_MODELOS=/ruta/modelos python scripts/generar_roi.py --imagen imagesTr/prostate_28.nii.gz \
    --referencia labelsTr/prostate_28.nii.gz --modelo prostate_mri_anatomy --salida carpeta
```

| Caso | Forma | Espaciado (mm) | Volumen predicho | Volumen de referencia | Dice / IoU (rejilla original) | Dice / IoU (preparado) | Cortes con ROI (pred.) | Cortes con ROI (ref.) |
|---|---|---|---|---|---|---|---|---|
| prostate_28 | 384x384x11 | 0,60 x 0,60 x 4,0 | 40,7 mL (27 858 vóx.) | 47,3 mL (32 363 vóx.) | 0,8320 / 0,7123 | 0,8374 / 0,7202 | 10 de 11 (z 0-9) | 10 |
| prostate_34 | 320x320x15 | 0,6 x 0,6 x 4,0 | 64,2 mL (44 562 vóx.) | 63,1 mL (43 792 vóx.) | 0,9105 / 0,8356 | 0,9062 / 0,8285 | 15 de 15 (z 0-14) | 13 |

- prostate_28: el modelo subestima el volumen en 6,6 mL (14 %); es el peor Dice de la prueba. prostate_34: sobreestima 1,1 mL (1,8 %) y marca 2 cortes más que la referencia.
- Tiempo de la cadena completa en CPU, con carga de pesos incluida (una ejecución por caso, no es la medición formal de la actividad 1408; ver [docs/modelo/04](../modelo/04_medicion_1408.md)): prostate_28 11,5 s (segmentación 9,9 s, ROI 0,06 s); prostate_34 13,1 s (segmentación 11,6 s, ROI 0,07 s).
- Dice/IoU de dos casos ilustran el flujo; **no son una evaluación**. La evaluación técnica completa (todo el conjunto de prueba, criterios de aceptación, comparación con la línea base) es del Ciclo 5.

Imágenes con la máscara predicha: `ejemplos/prostate_28_prediccion_corte_005.png` (corte 5 de 11) y `ejemplos/prostate_34_prediccion_corte_009.png` (corte 9 de 15), reducidas y cuantizadas para el repositorio. Las salidas completas (NIfTI, JSON, otros cortes) se generaron fuera del repositorio. El script guarda además en el JSON el modelo, su hash de pesos y los tiempos por etapa.

Antes de tener inferencia (primer borrador del ciclo) el flujo se había validado con la máscara de referencia, donde Dice = IoU = 1,0 era trivial; esos ejemplos se reemplazaron por los de arriba.

## Relación con el diseño CU04

| Elemento del diseño | Estado |
|---|---|
| Paneles «Original» y «Original + ROI» con mismo corte | Hecho (`figura_comparada`) |
| Color verde azulado y opacidad | Hecho (0,45; el control de opacidad y el zoom interactivos son del Ciclo 6) |
| Navegación por cortes | Parcial: PNG por corte; el visor interactivo es del Ciclo 6 |
| Métricas Dice/IoU o «no disponible» | Hecho en texto y JSON |
| Panel explicativo y aviso no clínico | Hecho (`textos.py`) |
| Exportar imagen con aviso impreso | Hecho (`con_aviso`, pie en `figura_comparada`) |

## Criterios de aceptación verificados

- Volumen en mL correcto según espaciado (pruebas con cubo y esfera, esfera a menos de 3 % del valor teórico).
- Cortes, centroide y caja exactos en el cubo sintético.
- Máscara vacía: mensaje claro, sin excepción.
- La superposición conserva dimensiones y no modifica vóxeles fuera de la máscara.
- Todo texto de explicación incluye el aviso no diagnóstico.

## Dependencias

NumPy, Pillow (dibujo y fuente), nibabel (solo el script de línea de comandos).
