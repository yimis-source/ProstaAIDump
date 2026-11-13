# Lanzamiento del Ciclo 3: segmentación 3D, modelo e inferencia

| Campo | Valor |
|---|---|
| Ciclo | 3 · 31/10/2026 – 13/11/2026 · hito H005 · Entregable 4 |
| Reunión de lanzamiento | 31/10/2026, después del postmortem del Ciclo 2 |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |
| Aprobó | Yimis Buenaventura (Líder del equipo) |

## 1. Objetivos del ciclo

1. Tener una cadena de segmentación 3D reproducible: control de calidad → preparación → segmentación → evaluación (`backend/prosta_ai/pipeline/`).
2. Elegir y documentar el modelo: configuración, licencias, métricas en el conjunto de prueba y limitaciones (E4).
3. Medir el tiempo de inferencia y la memoria en CPU frente a la meta de 120 s (actividad 1408, riesgo 1 del Acta).
4. Dejar preparado el ajuste fino (script y cuaderno de Colab) para adoptarlo solo si supera al preentrenado.
5. Cerrar con la etiqueta `v0.3-ciclo3`.

## 2. Plan de tareas

Factor 1,15 en tareas con historial y 1,25 en las tareas nuevas de entrenamiento, según el postmortem del Ciclo 2.

| Tarea | Descripción | Responsable | Horas plan | Fecha plan |
|---|---|---|---|---|
| 1401 | Paquete `prosta_ai`, dependencias (torch, MONAI) y entorno de pruebas | Yeison | 2 | 01/11 |
| 1402 | Cadena de segmentación: lectura, validación, preparación, segmentación y evaluación | Yeison | 12 | 05/11 |
| 1403 | Script de ajuste fino, cuaderno de Colab y descarga del modelo base | Yeison | 8 | 07/11 |
| 1404 | Pruebas automatizadas: métricas Dice/IoU, preparación y segmentación | Fernando | 8 | 06/11 |
| 1405 | Evaluación del modelo en el conjunto de prueba (5 casos) e informe | Juan | 6 | 10/11 |
| 1406 | Documentación del modelo: ficha, licencias, configuración y limitaciones | Juan | 5 | 11/11 |
| 1407 | Verificación del ajuste fino (prueba rápida en CPU) | Fernando | 3 | 08/11 |
| 1408 | Medición de tiempo de inferencia y memoria en CPU | Yeison | 4 | 11/11 |
| 1409 | Integración, README y etiqueta | Yimis | 3 | 13/11 |
| | **Total** | | **51** | |

Horas plan por integrante: Yeison 26, Fernando 11, Juan 11, Yimis 3, Sergio 0.

Sergio no tiene tareas de producto en este ciclo; apoya en revisiones. El 03/11 el equipo decidió aprovechar esa capacidad y adelantar el Ciclo 4 en paralelo (ver `ciclo4_lanzamiento.md`).

## 3. Plan de calidad

| Criterio | Meta |
|---|---|
| Pruebas de métricas | Dice e IoU probados con casos calculados a mano **antes** de reportar resultados del modelo (mejora del Ciclo 2) |
| Pruebas automatizadas | 100 % en verde antes de cada PR |
| Dice medio en prueba | ≥ 0,80 (RF-24) |
| Tiempo de inferencia | ≤ 120 s por estudio (RR-01) |
| Conjunto de prueba | No se usa para entrenar ni para elegir época |
| Revisión | Cada PR revisado por otro rol; el Tester revisa todo lo que toque `pipeline/` |
| Defectos abiertos al cierre | 0 |

## 4. Riesgos del ciclo

| Riesgo | Respuesta |
|---|---|
| Sin GPU propia (riesgo 1 del Acta) | Usar el preentrenado `prostate_mri_anatomy` en CPU; ajuste fino en Colab, reservado con anticipación |
| Inferencia > 120 s | Medir en 1408; si se supera: Colab, modelo más ligero o menor resolución |
| Solapamiento entre los datos del modelo base y Task05 | Documentarlo como limitación; evaluar solo en los 5 casos de prueba |
| Métricas mal calculadas | Pruebas de métricas antes del informe (1404 antes de 1405) |
| Dependencia: 1405 y 1408 necesitan la cadena de 1402 | Yeison integra 1402 primero; Juan y Fernando trabajan sobre `desarrollo` |
