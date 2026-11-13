# Actividad 1408: tiempo de inferencia y memoria en CPU

Riesgo 1 del Acta (capacidad de cómputo) y control de factibilidad de la arquitectura (`docs/ejecucion/02_arquitectura.md`): medir con estudios representativos y comparar con la meta de **120 s por estudio** (RR-01). Informe generado: `reports/inferencia/medicion_1408_2026-11-12.md` y `.csv` (comando: `python scripts/medir_inferencia.py`).

## 1. Equipo

| Campo | Valor (`lscpu`, `/proc/meminfo`) |
|---|---|
| CPU | AMD Ryzen 5 5600G with Radeon Graphics, 6 núcleos / 12 hilos, hasta 4,47 GHz, L2 3 MiB |
| Hilos usados por torch | 6 (valor por defecto de torch = núcleos físicos) |
| RAM | 30,7 GiB (≈ 19 GiB disponibles al medir) + 4 GiB de intercambio |
| GPU | Ninguna (la gráfica integrada no se usa) |
| Sistema | Arch Linux, núcleo 7.2.14 |
| Software | Python 3.12.14, torch 2.5.1+cpu, MONAI 1.4.0 |

## 2. Método

- Modelo `prostate_mri_anatomy` 0.3.6 con su configuración (0,5 mm isotrópico, ventana 96³, `sw_batch_size` 4, solapamiento 0,5).
- Estudios: los 5 casos de prueba y `prostate_02`, el caso de Task05 con más vóxeles tras remuestrear (26,7 millones), como peor caso.
- Cada estudio se procesa en un **proceso nuevo**, así la memoria pico (`ru_maxrss`) es la de ese estudio.
- Se mide: importar librerías, cargar pesos, primera ejecución del pipeline completo (control de calidad, preparación, segmentación, evaluación), y una segunda ejecución con el modelo ya en memoria (régimen de una aplicación que mantiene el modelo cargado).
- «Arranque + 1.ª ejecución» es el tiempo en frío desde que arranca el proceso hasta tener la máscara y las métricas.

## 3. Resultados (12/11/2026)

| Caso | Vóxeles preparados (M) | Importar (s) | Cargar pesos (s) | Preparación (s) | Segmentación (s) | Arranque + 1.ª (s) | 2.ª, modelo cargado (s) | RSS pico (MiB) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| prostate_13 | 22,1 | 1,55 | 0,25 | 1,05 | 14,07 | 17,67 | 16,64 | 2021 |
| prostate_17 | 22,1 | 1,70 | 0,27 | 1,14 | 14,43 | 18,26 | 16,42 | 1974 |
| prostate_28 | 17,4 | 1,68 | 0,27 | 0,82 | 9,60 | 12,91 | 10,77 | 1779 |
| prostate_34 | 16,7 | 1,68 | 0,26 | 0,78 | 10,86 | 14,09 | 12,12 | 1736 |
| prostate_44 | 22,1 | 1,64 | 0,26 | 1,04 | 14,14 | 17,77 | 15,67 | 1995 |
| prostate_02 (peor caso) | 26,7 | 1,66 | 0,27 | 1,27 | 20,97 | 25,02 | 23,17 | 2276 |

Memoria por fases (igual en todos los casos): 358 MiB tras importar torch/MONAI, 656 MiB tras cargar el modelo; el resto hasta el pico corresponde al volumen preparado, la salida de 3 canales de la ventana deslizante y el posproceso.

## 4. Conclusión frente a la meta

| Indicador | Resultado | Meta | Estado |
|---|---|---|---|
| Peor tiempo en frío por estudio | **25,0 s** (`prostate_02`) | ≤ 120 s | Cumple (21 % de la meta) |
| Tiempo medio en frío, 5 casos de prueba | 16,1 s | ≤ 120 s | Cumple |
| Tiempo medio con modelo cargado, 5 casos de prueba | 14,3 s | — | — |
| Memoria pico máxima | **2276 MiB (≈ 2,2 GiB)** | — (no fijada en el SRS) | Cabe con holgura en 30,7 GiB |

- La **segmentación** (ventana deslizante) es el 74–84 % del tiempo en frío y crece con el número de vóxeles tras remuestrear (0,55–0,79 s por millón de vóxeles).
- Cargar los pesos cuesta ≈ 0,26 s; importar las librerías ≈ 1,7 s. Mantener el modelo cargado (Ciclo 6) ahorra entre 1 y 2 s por estudio.
- **Decisión para el riesgo 1:** en CPU no hace falta Colab, un modelo más ligero ni bajar la resolución para la inferencia. Colab queda solo para el ajuste fino.
- No hay evidencia de que la inferencia necesite un proceso aparte por tiempo; si la API se bloquea mientras corre (25 s), se revisa en el Ciclo 6.

## 5. Lo que no se midió

- **GPU:** no hay GPU en el equipo de medición; la medición en Colab queda pendiente (no es necesaria para la meta).
- Equipos con menos RAM o menos núcleos: no se probaron. Con 4 GiB libres el pico de 2,2 GiB debería caber, pero no se verificó.
- Estudios DICOM reales de otro tamaño: la medición usa NIfTI de Task05; un campo de visión mayor aumenta tiempo y memoria de forma aproximadamente proporcional al número de vóxeles a 0,5 mm.
