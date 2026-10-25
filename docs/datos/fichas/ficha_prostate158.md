# Ficha de conjunto de datos: Prostate158

| Campo | Valor |
|---|---|
| Nombre | Prostate158 (partición de entrenamiento) |
| Rol en Prosta-AI | Conjunto de **respaldo** y de evaluación externa |
| Fuente | https://github.com/kbressem/prostate158 · Zenodo: https://zenodo.org/records/6481141 |
| Origen de las imágenes | Charité – Universitätsmedizin Berlin, resonadores de 3 T |
| Contenido | 139 pacientes (119 en `train.csv` y 20 en `valid.csv`). Por paciente: `t2`, `adc`, `dwi`, `t2_anatomy_reader1` (PZ = 1, TZ = 2) y máscaras de tumor de uno o dos lectores |
| Formato | NIfTI comprimido, una carpeta numerada por paciente (`020/`, `021/`, …) |
| Tamaño | 844 archivos, 2,6 GiB |
| Licencia | **Creative Commons Attribution 4.0 (CC-BY 4.0)** |
| Desidentificación | De origen; verificada en la tarea 1205 (0 hallazgos) |
| Responsable de la ficha | Juan David Riascos Erazo · 18/10/2026 |

## Qué permite la licencia

| Acción | ¿Permitida? | Condición |
|---|---|---|
| Uso académico | Sí | — |
| Modificar | Sí | Indicar los cambios |
| Redistribuir | Sí | Atribución (no exige compartir igual) |

## Notas de uso

- Solo se usa la máscara anatómica del lector 1 (`t2_anatomy_reader1`). Las máscaras de tumor quedan **fuera del alcance**: Prosta-AI no detecta lesiones ni diagnostica.
- La orientación de origen es LPS y el espaciado es de 0,27 a 0,47 mm en el plano y 3 mm entre cortes. Requiere reorientar y remuestrear (Ciclo 2).

## Cita

Adams, L. C., Makowski, M. R., Engel, G. et al. Prostate158 – An expert-annotated 3T MRI dataset and algorithm for prostate cancer detection. *Computers in Biology and Medicine* 148, 105817 (2022). https://doi.org/10.1016/j.compbiomed.2022.105817
