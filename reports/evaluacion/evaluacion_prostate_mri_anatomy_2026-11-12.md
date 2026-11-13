# Evaluación del modelo `prostate_mri_anatomy` (2026-11-12)

Uso académico y experimental; no es una evaluación clínica ni diagnóstica.

## Condiciones

- Modelo: prostate_mri_anatomy, versión 0.3.6; SHA-256 de los pesos `3c18e4c658bb088f551b1d63219ef8340fe6256d016c75fc140d3da49dda696d`.
- Ruta de ejecución: `build_pipeline` (control de calidad, preparación, segmentación, evaluación); imagen = canal 0 (T2) del NIfTI 4D; referencia = etiquetas > 0 (zona periférica + transición).
- **Dice/IoU** (principal): rejilla de la imagen original, con la máscara devuelta por `roi.mask_to_original_space` (vecino más cercano). **Dice/IoU (preparado)**: espacio del modelo (RAS, 0,5 mm), con la etiqueta remuestreada por vecino más cercano.
- Dispositivo: cpu. Hardware: AMD Ryzen 5 5600G with Radeon Graphics; 12 hilos lógicos; 6 hilos de torch; 30.7 GiB de RAM; sin GPU; Linux 7.2.14-arch1-1.
- Software: Python 3.12.14, torch 2.5.1+cpu, MONAI 1.4.0.
- División: `entrenamiento/division_task05.json` (Ciclo 2), semilla 2026, {'entrenamiento': 22, 'validacion': 5, 'prueba': 5}, huella `728fae869f02e7c7…`.
- Conjunto evaluado: prueba (5 casos: prostate_13, prostate_17, prostate_28, prostate_34, prostate_44).
- Tiempo por caso: pipeline completo (lectura, preparación, segmentación, evaluación en espacio preparado). El primer caso incluye la carga de los pesos.
- Desviación: típica muestral (n-1).

## Resultados sobre el conjunto de prueba

| Caso | Dice | IoU | Dice (preparado) | IoU (preparado) | Tiempo (s) |
|---|---:|---:|---:|---:|---:|
| prostate_13 | 0.9012 | 0.8201 | 0.8966 | 0.8125 | 16.2 |
| prostate_17 | 0.9097 | 0.8344 | 0.9035 | 0.8240 | 15.8 |
| prostate_28 | 0.8320 | 0.7123 | 0.8374 | 0.7202 | 10.7 |
| prostate_34 | 0.9105 | 0.8356 | 0.9062 | 0.8285 | 12.0 |
| prostate_44 | 0.9090 | 0.8332 | 0.9010 | 0.8199 | 15.6 |
| **Media ± desv.** | **0.8925 ± 0.0340** | **0.8071 ± 0.0534** | **0.8889 ± 0.0290** | **0.8010 ± 0.0455** | **14.1 ± 2.5** |

## Comparación con la meta (RF-24) y con el proyecto de referencia

Se **cumple** la meta (Dice medio 0.8925 ≥ 0.80).
El caso más bajo es prostate_28 (Dice 0.8320).
Proyecto de referencia (03/11/2026, mismos 5 casos, rejilla original): Dice medio 0.8925; diferencia +0.0000.

## Limitaciones

- **Posible sesgo (sobreestimación) por los datos del modelo base.** Según la documentación del bundle (`configs/metadata.json`, `data_source`: "Prostate158 from 10.5281/zenodo.6481141"), el modelo se entrenó con Prostate158 (solo T2). La documentación no menciona MSD Task05, así que no hay evidencia de solapamiento, pero tampoco se puede descartar: el bundle no publica la lista de casos. Además, la división 22/5/5 de este proyecto es independiente de la de los autores, por lo que los 5 casos de prueba no son 'no vistos' por construcción. Si hubiera solapamiento, las cifras estarían sobreestimadas.
- Con 5 casos de prueba la media tiene mucha incertidumbre; un caso malo mueve mucho el promedio.
- Cambio de dominio: Prostate158 (3 T, Charité) frente a Task05 (cortes de 3,0–4,0 mm, otro protocolo); el remuestreo a 0,5 mm interpola y no añade detalle.
- El modelo segmenta dos zonas; aquí se evalúa solo la unión (próstata completa).
- Un solo conjunto público y un solo anotador por caso; sin métricas de superficie (Hausdorff).
- Los tiempos dependen del equipo. No hay validación clínica.
