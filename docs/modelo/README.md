# Ciclo 3: segmentación 3D, modelo e inferencia (Entregable 4, hito H005)

Prosta-AI es académica y experimental; **no diagnostica**.

## Resumen

| Indicador | Resultado | Meta | Estado |
|---|---|---|---|
| Dice medio, 5 casos de prueba (rejilla original) | **0,8925 ± 0,0340** | ≥ 0,80 (RF-24) | Cumple |
| IoU medio, 5 casos de prueba | **0,8071 ± 0,0534** | Se informa (RF-23) | — |
| Peor tiempo por estudio en CPU, en frío (actividad 1408) | **25,0 s** | ≤ 120 s (RR-01) | Cumple |
| Memoria pico por estudio | **2276 MiB** | — | — |
| Pruebas automatizadas | 69 de 69 en verde (21 de ciclos 1–2, 30 del Ciclo 3, 18 de la ROI del Ciclo 4) | Todas | Cumple |

Modelo: `prostate_mri_anatomy` 0.3.6 (MONAI Model Zoo, Apache 2.0), preentrenado y sin ajuste. Las cifras reproducen exactamente las del proyecto de referencia (mismos pesos, preparación y división).

## Documentos

| Archivo | Contenido |
|---|---|
| [01_ficha_y_licencias.md](01_ficha_y_licencias.md) | Por qué un preentrenado, ficha del modelo, datos con que se entrenó, licencias y obligaciones |
| [02_configuracion.md](02_configuracion.md) | Cadena de etapas y patrones, parámetros de `preparacion.json`, rutas y entorno, ajuste fino preparado |
| [03_resultados_evaluacion.md](03_resultados_evaluacion.md) | Dice e IoU por caso y medios, comparación con la meta y con el proyecto de referencia |
| [04_medicion_1408.md](04_medicion_1408.md) | Tiempo de inferencia y memoria pico en CPU, hardware, decisión sobre el riesgo 1 |
| [05_limitaciones.md](05_limitaciones.md) | Posible solapamiento de datos con el modelo base, tamaño de la muestra, cambio de dominio, rendimiento |

Evidencia generada: `reports/evaluacion/evaluacion_prostate_mri_anatomy_2026-11-12.{md,csv}` y `reports/inferencia/medicion_1408_2026-11-12.{md,csv}`.

## Código del ciclo

| Ubicación | Contenido |
|---|---|
| `backend/prosta_ai/pipeline/` | `io`, `validators`, `preparation`, `segmentation`, `evaluation`, `base`, `factory`, `progress`, `stages`, `errors` (`roi.py` es del Ciclo 4) |
| `entrenamiento/` | `entrenar.py` (ajuste fino), `evaluar.py`, `Prosta_AI_entrenamiento.ipynb` (Colab) y `README.md`; usa la división del Ciclo 2 sin regenerarla |
| `scripts/descargar_modelo.py` | Descarga el bundle (revisión fija), genera `preparacion.json` y `FICHA.md` con el hash |
| `scripts/medir_inferencia.py` | Medición de la actividad 1408 |
| `tests/test_metricas.py`, `test_preparacion_modelo.py`, `test_segmentacion.py` | 30 pruebas; ninguna necesita los pesos reales (estrategia simulada y UNet mínima) |

## Cómo reproducir

```bash
pip install -r requirements.txt
python scripts/descargar_modelo.py --destino modelos        # o export PROSTA_MODELOS=/ruta/modelos
export PROSTA_DATOS=/ruta/Task05_Prostate                   # o --datos
python -m pytest                                            # primero las pruebas (incluidas Dice/IoU)
python -m entrenamiento.evaluar                             # ~75 s en CPU
python scripts/medir_inferencia.py                          # ~2 min en CPU
```

## Estado del ajuste fino

No se ejecutó el ajuste fino real (100 épocas en GPU). Se comprobó el flujo en CPU con `--prueba-rapida` (1 época, 2 casos, 7 s): entrena, valida (Dice de validación 0,26 tras una época con lotes de 2, esperado para esa prueba), guarda la carpeta del modelo y `evaluar.py` la carga. El ajuste real se hace en Colab con `entrenamiento/Prosta_AI_entrenamiento.ipynb` y solo se adopta si supera 0,8925 en los mismos 5 casos.
