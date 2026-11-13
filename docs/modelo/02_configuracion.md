# Configuración de la segmentación 3D e inferencia

Código: `backend/prosta_ai/pipeline/`. Pruebas: `tests/test_metricas.py`, `tests/test_preparacion_modelo.py`, `tests/test_segmentacion.py`.

## 1. Cadena del Ciclo 3 (patrón Template Method)

| Etapa | Módulo | Qué hace | Error controlado |
|---|---|---|---|
| Control de calidad | `io.py`, `validators.py` | Lee NIfTI (canal 0 = T2 si es 4D) o una serie DICOM; exige 3D, valores finitos, no constante, ≥ 8 cortes, ≥ 32×32 y referencia con la misma forma y geometría | `StageError("control de calidad", …)` |
| Preparación | `preparation.py` | `Orientationd(RAS)` → `Spacingd(0,5 mm, bilinear)` → `ScaleIntensityd[0,1]` → `NormalizeIntensityd` | `StageError("preparación", …)` |
| Segmentación | `segmentation.py` | UNet 3D por ventana deslizante; `argmax`; mayor componente conexa por zona; unión de zonas = próstata | `StageError("segmentación", …)` |
| Evaluación | `base.py`, `evaluation.py` | Si hay referencia: Dice e IoU en el espacio preparado (referencia remuestreada por vecino más cercano) | — |

El avance y los tiempos por etapa se notifican a observadores (`progress.py`, patrón Observer); `TimingRecorder` los usa la medición 1408. La ROI y el paso a la rejilla original son del Ciclo 4 (`pipeline/roi.py`); `evaluar.py` ya la usa para la métrica principal.

Patrones: **Strategy** (`SegmentationStrategy`: `PretrainedUNetStrategy`, `NnUNetStrategy` reservada), **Factory Method** (`create_strategy`, `build_pipeline`), **Adapter** (`io.py` sobre SimpleITK/nibabel), **Chain of Responsibility** (validadores), **Template Method** (`BasePipeline.run`), **Observer** (avance).

## 2. Parámetros (`preparacion.json` del modelo)

`scripts/descargar_modelo.py` genera este archivo a partir de `configs/inference.json` del bundle; se comprobó que lo derivado coincide exactamente con el del proyecto de referencia. Entrenamiento, evaluación e inferencia leen el mismo archivo (RF-09).

| Parámetro | Valor |
|---|---|
| Orientación | RAS |
| Espaciado | 0,5 × 0,5 × 0,5 mm, interpolación bilineal (vecino más cercano para etiquetas) |
| Intensidad | Escalado a [0, 1] y normalización media 0 / desviación 1 |
| Ventana deslizante | 96 × 96 × 96, `sw_batch_size` 4, solapamiento 0,5 |
| Red | UNet 3D, 1 → 3 canales, 16-32-64-128-256-512, 4 unidades residuales, BatchNorm, PReLU, dropout 0,15 |
| Posproceso | Mayor componente conexa de las etiquetas 1 y 2; próstata = unión |
| Pesos | `models/model.pt` (se cargan una sola vez por instancia, en la primera inferencia) |

Diferencia con el preprocesamiento del Ciclo 2 (`preprocesamiento/`): aquel remuestrea a 0,625 × 0,625 × 3,6 mm para revisión y control de datos. El modelo exige **su** preparación (0,5 mm isotrópico); por eso la inferencia parte del NIfTI original y no de `datos/preprocesados/`.

## 3. Rutas y entorno

| Qué | Cómo se indica | Por defecto |
|---|---|---|
| Datos Task05 | `--datos` o `PROSTA_DATOS` | `datos/Task05_Prostate` |
| Modelos | `--directorio-modelos` o `PROSTA_MODELOS` | `modelos/` (en `.gitignore`) |
| Dispositivo | `--dispositivo` | `cpu` en evaluación; `auto` en entrenamiento |
| `prosta_ai` importable | `pytest.ini` (`pythonpath = . backend`); los scripts agregan `backend/` a `sys.path` | — |

Entorno probado: Python 3.12.14, torch 2.5.1+cpu, MONAI 1.4.0, numpy 1.26.4, SimpleITK 2.4.0, nibabel 5.3.2.

## 4. Ajuste fino (preparado, no ejecutado)

`entrenamiento/entrenar.py` parte de los pesos del bundle (o de cero con `--desde-cero`) y usa la división del Ciclo 2 (22/5/5). Hiperparámetros: `DiceCELoss`, AdamW (lr 1e-4, decaimiento 1e-5), lote 2, 4 recortes 96³ por caso y época (`RandCropByPosNegLabeld`), volteo y cambios leves de intensidad, 100 épocas, validación cada 5, se guarda la época con mejor Dice de **validación**; precisión mixta solo en CUDA; semilla 2026. Las etiquetas de Task05 se intercambian (1 ↔ 2) para coincidir con las del modelo base.

Se ejecutó solo `--prueba-rapida` en CPU para comprobar que el flujo funciona (ver [README](README.md)). El ajuste real se hace en Colab con GPU (`entrenamiento/Prosta_AI_entrenamiento.ipynb`). **Regla de adopción:** el modelo ajustado reemplaza al preentrenado solo si su Dice medio en los mismos 5 casos de prueba supera 0,8925.
