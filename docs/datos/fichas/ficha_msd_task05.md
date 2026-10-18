# Ficha de conjunto de datos: MSD Task05_Prostate

| Campo | Valor |
|---|---|
| Nombre | Medical Segmentation Decathlon, Task05_Prostate |
| Rol en Prosta-AI | Conjunto **principal** |
| Fuente | http://medicaldecathlon.com/ · copia de MONAI: https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar |
| Origen de las imágenes | Radboud University, Nijmegen Medical Centre (según `dataset.json`) |
| Versión | 1.0 · 04/05/2018 (`dataset.json`) |
| Contenido | 32 casos con máscara (`imagesTr`/`labelsTr`) y 16 sin máscara (`imagesTs`). Imagen 4D: canal 0 = T2, canal 1 = ADC. Etiquetas: 0 fondo, 1 zona periférica (PZ), 2 zona de transición (TZ) |
| Formato | NIfTI comprimido (`.nii.gz`) |
| Tamaño | 81 archivos, 228,7 MiB |
| Licencia | **Creative Commons Attribution-ShareAlike 4.0 (CC-BY-SA 4.0)**, https://creativecommons.org/licenses/by-sa/4.0/ |
| Desidentificación | De origen; verificada en la tarea 1205 (0 hallazgos) |
| Responsable de la ficha | Juan David Riascos Erazo · 18/10/2026 |

## Qué permite la licencia

| Acción | ¿Permitida? | Condición |
|---|---|---|
| Uso académico | Sí | — |
| Modificar (preprocesar, recortar, unir etiquetas) | Sí | Indicar que hubo cambios |
| Redistribuir los datos o derivados | Sí | Atribución y **misma licencia** (CC-BY-SA 4.0) |
| Uso comercial | Sí por licencia | No aplica a Prosta-AI |

## Obligaciones para el equipo

1. No subir los datos al repositorio: se descargan con `scripts/descargar_datos.py`.
2. Citar el conjunto en todo informe, cartel o presentación que muestre imágenes.
3. Si algún día se publican volúmenes preprocesados, deben ir con CC-BY-SA 4.0.

## Cita

Antonelli, M., Reinke, A., Bakas, S. et al. The Medical Segmentation Decathlon. *Nat Commun* 13, 4128 (2022). https://doi.org/10.1038/s41467-022-30695-9

Simpson, A. L. et al. A large annotated medical image dataset for the development and evaluation of segmentation algorithms. arXiv:1902.09063 (2019).
