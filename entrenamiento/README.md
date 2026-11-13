# Entrenamiento y evaluación de Prosta-AI

Aplicación académica y experimental, **no diagnóstica**. Esta carpeta contiene la división por paciente
(Ciclo 2) y el ajuste fino y la evaluación del modelo de segmentación 3D (Ciclo 3, Entregable 4).

> **Estado (Ciclo 3):** se usa el modelo preentrenado `prostate_mri_anatomy` (MONAI Model Zoo, Apache 2.0)
> sin ajuste. El ajuste fino de esta carpeta **no se ha ejecutado**: solo se comprobó en CPU con
> `--prueba-rapida`. El ajuste real se hace en Google Colab con GPU y solo se adopta si supera el Dice del
> preentrenado en el mismo conjunto de prueba. Ver `docs/modelo/`.

| Archivo | Función |
|---|---|
| `division.py`, `division_task05.json` | División por paciente 22/5/5 (semilla 2026) del Ciclo 2. **Es la única división**: entrenamiento y evaluación la cargan y verifican (RC-04 + huella SHA-256); no se regenera. |
| `entrenar.py` | Ajuste fino (o desde cero) de la UNet 3D con MONAI. Usa `prosta_ai.pipeline.preparation` (las mismas transformaciones que la inferencia, RF-09). |
| `evaluar.py` | Dice e IoU por caso y medios sobre los 5 casos de prueba con `build_pipeline`; escribe `reports/evaluacion/`. |
| `Prosta_AI_entrenamiento.ipynb` | Cuaderno de Google Colab (GPU) con todo el flujo. |

## Requisitos y rutas

Python 3.12 con `requirements.txt` (torch 2.5.1, monai 1.4.0, numpy 1.26, nibabel 5.3, SimpleITK 2.4).
Los comandos se ejecutan desde la **raíz del repositorio**. Ni los datos ni los pesos se versionan; se indican
por argumento o por variable de entorno:

| Variable | Argumento | Por defecto |
|---|---|---|
| `PROSTA_DATOS` | `--datos` | `datos/Task05_Prostate` |
| `PROSTA_MODELOS` | `--directorio-modelos` (evaluar), `--base` / `--salida` (entrenar) | `modelos/` |

```bash
python scripts/descargar_datos.py msd                 # MSD Task05_Prostate (CC BY-SA 4.0)
python scripts/descargar_modelo.py                    # bundle prostate_mri_anatomy (~146 MiB)
```

## Pasos

1. **Evaluación** del modelo sobre el conjunto de prueba (CPU, unos 75 s en total):
   `python -m entrenamiento.evaluar --datos <Task05> --directorio-modelos <modelos>`
2. **Medición de inferencia (actividad 1408)**: tiempo y memoria pico por estudio:
   `python scripts/medir_inferencia.py --datos <Task05> --directorio-modelos <modelos>` → `reports/inferencia/`.
3. **Comprobación rápida del entrenamiento en CPU** (1 época, 2 casos, 1 mm, ventana 32; unos 7 s; el modelo no sirve):
   `python -m entrenamiento.entrenar --prueba-rapida --datos <Task05> --base <modelos>/prostate_mri_anatomy --salida /tmp/prueba`
4. **Ajuste fino real** (GPU, ver el cuaderno):
   `python -m entrenamiento.entrenar --max-epocas 100 --dispositivo cuda`
   Opciones: `--desde-cero`, `--lr`, `--recortes`, `--validar-cada`, `--nombre`, `--version`, `--semilla`.
5. Evaluar el modelo ajustado con `evaluar.py --modelo <nombre>` y compararlo con el preentrenado.

## Qué se guarda al entrenar

`<salida>/<nombre>/`: `models/model.pt`, `preparacion.json` (formato que lee `create_strategy`),
`metadatos.json` (versión, fecha, SHA-256 de los pesos, hiperparámetros, semilla, huella de la división, entorno),
`division.json`, `historial.json` y `FICHA.md`. Se guarda la época con mejor Dice de **validación**.

## Decisiones

- Etiquetas: Task05 usa 1 = zona periférica y 2 = transición; el modelo base usa 1 = glándula central y
  2 = periférica. Al entrenar se intercambian. La próstata completa es la unión de etiquetas > 0.
- Imagen: canal 0 (T2) del NIfTI 4D.
- Semilla 2026 (Python, NumPy, torch y MONAI). En GPU puede haber pequeñas variaciones.
- El conjunto de prueba no se usa durante el entrenamiento ni para elegir la mejor época.
- Las métricas principales se calculan en la rejilla de la imagen original (la máscara vuelve con
  `prosta_ai.pipeline.roi.mask_to_original_space`, Ciclo 4); también se informan en el espacio preparado.
