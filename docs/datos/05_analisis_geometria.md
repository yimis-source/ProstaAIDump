# Análisis de tamaños, espaciado y número de casos (tarea 1206)

| Campo | Valor |
|---|---|
| Ciclo | 1 |
| Responsable | Juan David Riascos Erazo (Analista) |
| Apoyo | Yeison Bolaños Ruiz (script) |
| Fecha | 22/10/2026 |

Script: `scripts/analizar_geometria.py`. Resultado por caso: [analisis_geometria.csv](analisis_geometria.csv) (221 filas). El volumen de la próstata se calcula como el número de vóxeles con etiqueta > 0 por el volumen del vóxel.

## 1. Número de casos

| Conjunto | Casos con máscara | Canales | Etiquetas |
|---|---|---|---|
| MSD_Task05 | 32 | 2 (T2, ADC) | 30 casos con {0, 1, 2}; **2 casos sin TZ** (`prostate_18`, `prostate_32`) |
| Prostate158 | 139 | 1 (T2) | {0, 1, 2} en todos |
| PROMISE12 | 50 | 1 (T2) | {0, 1}: glándula completa |

## 2. Dimensiones (vóxeles, x · y · z)

| Conjunto | x/y mín | x/y mediana | x/y máx | z mín | z mediana | z máx |
|---|---|---|---|---|---|---|
| MSD_Task05 | 256 | 320 | 384 | 11 | 20 | 24 |
| Prostate158 | 232 | 270 | 442 | 24 | 25 | 40 |
| PROMISE12 | 256 | 320 | 512 | 15 | 24 | 54 |

## 3. Espaciado del vóxel (mm)

| Conjunto | Plano mín | Plano mediana | Plano máx | Entre cortes mín | Entre cortes mediana | Entre cortes máx |
|---|---|---|---|---|---|---|
| MSD_Task05 | 0,60 | **0,625** | 0,75 | 3,0 | **3,6** | 4,0 |
| Prostate158 | 0,27 | 0,40 | 0,47 | 3,0 | 3,0 | 3,0 |
| PROMISE12 | 0,27 | 0,61 | 0,75 | 2,2 | 3,6 | 4,0 |

Distribución en el MSD: 23 de los 32 casos tienen exactamente 0,625 × 0,625 × 3,6 mm. Los demás se reparten así: 5 casos con 0,6 × 0,6 × 4,0; 2 con 0,75 × 0,75 × 4,0; 1 con 0,75 × 0,75 × 3,0 y 1 con 0,604 × 0,604 × 4,0.

**El espaciado es muy anisótropo** (≈ 6 veces mayor entre cortes que en el plano). El remuestreo del Ciclo 2 debe conservar esa anisotropía: interpolar a vóxeles isótropos inventaría información entre cortes.

## 4. Orientación

| Conjunto | Orientación |
|---|---|
| MSD_Task05 | RAS en los 32 casos |
| Prostate158 | LPS en los 139 casos |
| PROMISE12 | LPS en los 50 casos (`AnatomicalOrientation = RAI` en la cabecera) |

Hay que unificar la orientación antes de mezclar o comparar conjuntos.

## 5. Intensidades (T2, percentiles 1 y 99)

| Conjunto | p99 mín | p99 mediana | p99 máx |
|---|---|---|---|
| MSD_Task05 | 773 | 936,5 | 1324 |
| Prostate158 | 435 | 685 | 1111 |
| PROMISE12 | 201 | 940,5 | 3539 |

La escala no es comparable entre conjuntos (ni siquiera entre casos de PROMISE12), así que hace falta normalizar por caso.

## 6. Volumen de la próstata (ml)

| Conjunto | Mín | Mediana | Media | Máx |
|---|---|---|---|---|
| MSD_Task05 | 16,0 (`prostate_07`) | 62,0 | 74,3 | 315,4 (`prostate_16`) |
| Prostate158 | 14,8 | 52,4 | 56,0 | 197,4 |
| PROMISE12 | 14,9 | 43,3 | 54,7 | 315,4 (`Case23`) |

`prostate_16` es un valor atípico (glándula muy agrandada), pero real: se mantiene.

## 7. Hallazgo: paciente duplicado entre MSD y PROMISE12

`prostate_16` (MSD) y `Case23` (PROMISE12) tienen idénticos tamaño (320 × 320 × 20), espaciado (0,625 × 0,625 × 3,6 mm) y volumen de próstata (315,4 ml). Es el mismo estudio. Ambos conjuntos incluyen casos de Radboud UMC, así que **no se combinan** (criterio CE-3). Se informa al Tester para el control de fuga del Ciclo 2.

## 8. Implicaciones para el Ciclo 2

| Hallazgo | Acción |
|---|---|
| Espaciado mayoritario 0,625 × 0,625 × 3,6 mm en el MSD | Usarlo como espaciado objetivo |
| Orientaciones RAS y LPS | Reorientar todo a RAS |
| Escalas de intensidad distintas | Normalizar con z-score por caso, tras recortar percentiles |
| MSD 4D (T2 + ADC) | Extraer solo el canal 0 (T2) |
| PZ/TZ frente a glándula completa | Binarizar la máscara (etiqueta > 0) |
| Solo 32 casos en el principal | División 70/15/15 por paciente con semilla fija; Prostate158 como evaluación externa |
