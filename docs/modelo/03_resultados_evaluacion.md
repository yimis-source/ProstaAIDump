# Resultados de la evaluación (Dice e IoU) sobre el conjunto de prueba

Informe generado: `reports/evaluacion/evaluacion_prostate_mri_anatomy_2026-11-12.md` y `.csv` (comando: `python -m entrenamiento.evaluar`). Uso académico; no es una evaluación clínica.

## 1. Condiciones

| Campo | Valor |
|---|---|
| Fecha | 12/11/2026 |
| Modelo | `prostate_mri_anatomy` 0.3.6, SHA-256 `3c18e4c6…696d`, sin ajuste |
| Datos | MSD Task05_Prostate, canal 0 (T2); referencia = etiquetas > 0 (PZ + TZ) |
| División | `entrenamiento/division_task05.json` del Ciclo 2 (22/5/5, semilla 2026, huella `728fae869f02e7c7…`), verificada antes de evaluar |
| Casos de prueba | `prostate_13`, `prostate_17`, `prostate_28`, `prostate_34`, `prostate_44` |
| Equipo | AMD Ryzen 5 5600G (6 núcleos / 12 hilos), 30,7 GiB de RAM, sin GPU, Arch Linux 7.2.14; torch usa 6 hilos |
| Software | Python 3.12.14, torch 2.5.1+cpu, MONAI 1.4.0 |
| Métrica principal | Dice/IoU en la **rejilla de la imagen original**: la máscara vuelve con `roi.mask_to_original_space` (vecino más cercano) y se compara con la etiqueta sin tocar |
| Métrica secundaria | Dice/IoU en el **espacio preparado** (0,5 mm isotrópico), que es lo que calcula la etapa de evaluación del pipeline del Ciclo 3 |
| Pruebas de las métricas | `tests/test_metricas.py` (10 pruebas: idénticos, disjuntos, vacíos, valores a mano, Dice = 2·IoU/(1+IoU)), en verde **antes** de generar el informe (mejora del postmortem del Ciclo 2) |

## 2. Resultados por caso

| Caso | Dice | IoU | Dice (preparado) | IoU (preparado) | Tiempo (s) |
|---|---:|---:|---:|---:|---:|
| prostate_13 | 0,9012 | 0,8201 | 0,8966 | 0,8125 | 16,2 |
| prostate_17 | 0,9097 | 0,8344 | 0,9035 | 0,8240 | 15,8 |
| prostate_28 | 0,8320 | 0,7123 | 0,8374 | 0,7202 | 10,7 |
| prostate_34 | 0,9105 | 0,8356 | 0,9062 | 0,8285 | 12,0 |
| prostate_44 | 0,9090 | 0,8332 | 0,9010 | 0,8199 | 15,6 |
| **Media ± desv. (n−1)** | **0,8925 ± 0,0340** | **0,8071 ± 0,0534** | **0,8889 ± 0,0290** | **0,8010 ± 0,0455** | **14,1 ± 2,5** |

El tiempo es el del pipeline completo de cada caso; el primero incluye la carga de los pesos.

## 3. Comparación con la meta (RF-24)

- Meta: Dice medio ≥ 0,80. Resultado: **0,8925 → se cumple** con un margen de 0,09.
- Los 5 casos superan 0,80 por separado. El más bajo es `prostate_28` (0,8320).
- Con 5 casos, un intervalo aproximado al 95 % para la media (t de Student, 4 g. l.) es 0,8925 ± 0,042, es decir, entre 0,85 y 0,93: incluso el extremo inferior supera 0,80.

## 4. Comparación con el proyecto de referencia (Dice 0,8925)

| | Proyecto de referencia (03/11/2026) | Prosta-AI, Ciclo 3 (12/11/2026) |
|---|---|---|
| Dice medio (rejilla original) | 0,8925 ± 0,0340 | 0,8925 ± 0,0340 |
| IoU medio | 0,8071 ± 0,0534 | 0,8071 ± 0,0534 |
| Dice por caso | 0,9012 / 0,9097 / 0,8320 / 0,9105 / 0,9090 | idénticos a 4 decimales |
| Tiempo medio por caso | 13,3 ± 5,0 s | 14,1 ± 2,5 s |

**Por qué coinciden:** mismos pesos (mismo SHA-256), misma preparación (`preparacion.json` idéntico), mismos 5 casos (la división del Ciclo 2 es la misma que la del proyecto de referencia: misma semilla y misma huella; solo cambia el campo `fecha`), mismo posproceso y misma forma de volver a la rejilla original. La inferencia en CPU es determinista con estas versiones, así que las cifras se reproducen exactamente. Esto valida que la portación del código no cambió el comportamiento.

**Diferencias que sí hay:**

1. **Espacio de la métrica.** Además de la rejilla original, ahora se informa el Dice en el espacio preparado (0,8889). Es 0,004 menor en promedio porque la etiqueta de Task05 (cortes de 3,6–4 mm) se remuestrea a 0,5 mm con vecino más cercano y queda «escalonada» en z, mientras la predicción de la red es suave; en la rejilla original esa diferencia desaparece al volver a cortes gruesos. La cifra oficial para RF-24 es la de la rejilla original, que no altera la anotación.
2. **Tiempo.** La media es 0,8 s mayor y menos dispersa: ahora cada caso también calcula la métrica en el espacio preparado (≈ 0,5 s) y se lee dos veces la imagen; además, la carga del equipo en el momento de medir no es la misma. El tiempo no es comparable entre ejecuciones con precisión de segundos; la medición formal es la de la actividad 1408 ([04](04_medicion_1408.md)).

## 5. Dato adicional del proyecto de referencia (no repetido aquí)

El proyecto de referencia evaluó también los 32 casos (opción `--todos`, que no se portó porque mezcla entrenamiento y validación con prueba). Allí apareció un caso atípico, `prostate_07` (Dice 0,2255), que está en el conjunto de **entrenamiento**: el modelo predice una región falsa en grasa del borde del campo de visión que desplaza a la glándula al conservar la mayor componente. No afecta las cifras de prueba, pero es un aviso de cambio de dominio (ver [05](05_limitaciones.md)).
