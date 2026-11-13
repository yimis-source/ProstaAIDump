# Ficha del modelo y licencias (Ciclo 3)

| Campo | Valor |
|---|---|
| Ciclo / hito | 3 · H005 · Entregable 4 (segmentación 3D, modelo e inferencia) |
| Decisión | Usar el modelo preentrenado `prostate_mri_anatomy` **sin ajuste** en este ciclo |

## 1. Por qué un modelo preentrenado

- Es la respuesta prevista al **riesgo 1 del Acta** (capacidad de cómputo): «modelos preentrenados con ajustes ligeros» y Google Colab.
- Cumple la meta de RF-24 con margen: Dice medio **0,8925** en los 5 casos de prueba (ver [03](03_resultados_evaluacion.md)).
- Corre en CPU dentro de la meta de 120 s (ver [04](04_medicion_1408.md)).
- El ajuste fino queda preparado en `entrenamiento/` y solo se adopta si mejora ese Dice en el mismo conjunto de prueba.

## 2. Ficha

| Campo | Valor |
|---|---|
| Nombre | Prostate MRI Anatomy (`prostate_mri_anatomy`), versión 0.3.6 |
| Origen | MONAI Model Zoo, https://huggingface.co/MONAI/prostate_mri_anatomy, revisión `2bfceed082de08e9f2b36a50662c99b6243ee794` (fijada en `scripts/descargar_modelo.py`) |
| Autores | Lisa C. Adams y Keno K. Bressem (Charité – Universitätsmedizin Berlin) |
| Licencia | Apache License 2.0, Copyright (c) Keno Bressem |
| SHA-256 de los pesos (`models/model.pt`, 146 MiB) | `3c18e4c658bb088f551b1d63219ef8340fe6256d016c75fc140d3da49dda696d` (verificado el 12/11/2026) |
| Uso previsto por los autores | Ejemplo de investigación; «not to be used for diagnostic purposes» |
| Publicado con | MONAI 1.4.0, PyTorch 2.4.0 (aquí se usa torch 2.5.1, sin problemas de carga) |
| Datos de entrenamiento | Prostate158 (https://doi.org/10.5281/zenodo.6481141): 139 estudios de entrenamiento, resonancia 3 T de la Charité, **solo T2** |
| Tarea original | Fondo (0), glándula central / zona de transición (1), zona periférica (2) |
| Arquitectura | `monai.networks.nets.UNet` 3D: 1 canal de entrada, 3 clases, canales 16-32-64-128-256-512, pasos 2, 4 unidades residuales, BatchNorm, PReLU, dropout 0,15 |
| Pérdida de entrenamiento | *focal soft-Dice* |
| Desempeño publicado (prueba de Prostate158, evaluador 1 / 2) | Dice zona de transición 0,877 / 0,875; zona periférica 0,754 / 0,730 |

Cita:

> Adams, L. C., Makowski, M. R., Engel, G., Rattunde, M., Busch, F., Asbach, P., … & Bressem, K. K. (2022). Prostate158 – An expert-annotated 3T MRI dataset and algorithm for prostate cancer detection. *Computers in Biology and Medicine, 148*, 105817. https://doi.org/10.1016/j.compbiomed.2022.105817

## 3. Licencias

| Componente | Licencia | Cómo se cumple |
|---|---|---|
| Pesos y configuración del bundle | Apache 2.0 | Los pesos **no se versionan** (`/modelos/` y `*.pt` en `.gitignore`). `scripts/descargar_modelo.py` los baja con su `LICENSE` y genera `FICHA.md` con autoría, cita y hash |
| Prostate158 (datos con que se entrenó el modelo) | Acceso abierto en Zenodo; el reto exige un acuerdo de uso para investigación no comercial | Prosta-AI no descarga, no guarda ni redistribuye Prostate158; solo usa los pesos publicados por los mismos autores bajo Apache 2.0 |
| MSD Task05_Prostate (evaluación) | CC BY-SA 4.0 | Datos fuera del repositorio; los informes publican solo métricas. Ver `docs/datos/fichas/ficha_msd_task05.md` |
| MONAI | Apache 2.0 | Dependencia sin modificar |
| PyTorch | BSD 3 cláusulas | Dependencia sin modificar |

Riesgo legal residual: que un modelo entrenado sea «obra derivada» de los datos no está resuelto; los propios autores del conjunto publicaron los pesos con licencia abierta. Se mantiene el uso **académico, no comercial y no clínico**.

## 4. Obligaciones del equipo

1. Conservar `LICENSE` y `FICHA.md` junto a los pesos si alguna vez se redistribuyen.
2. Citar el modelo, Prostate158 y el Medical Segmentation Decathlon en la documentación final y la presentación.
3. No subir pesos, imágenes ni máscaras al repositorio.
4. No presentar Prosta-AI como herramienta de diagnóstico.
