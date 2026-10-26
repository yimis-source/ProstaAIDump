# Lanzamiento del Ciclo 2: preprocesamiento, división por paciente y diseño

| Campo | Valor |
|---|---|
| Ciclo | 2 · 26/10/2026 – 30/10/2026 · hito H004 |
| Reunión de lanzamiento | 26/10/2026, después del postmortem del Ciclo 1 |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |
| Aprobó | Yimis Buenaventura (Líder del equipo) |

## 1. Objetivos del ciclo

1. Dejar los datos listos para entrenar: control de calidad, formato unificado y división por paciente sin fuga.
2. Automatizar el preprocesamiento en un solo script reproducible.
3. Cerrar el diseño de la solución: arquitectura, pantallas, módulo de IA y base de datos.
4. Cerrar con la etiqueta `v0.2-ciclo2`.

## 2. Plan de tareas

Las estimaciones de las tareas con datos ya incluyen el factor 1,15 del postmortem del Ciclo 1.

| Tarea | Descripción | Responsable | Horas plan | Fecha plan |
|---|---|---|---|---|
| 1301 | Control de calidad y descarte de archivos dañados | Yeison (código 3) + Fernando (pruebas e informe 5) | 8 | 27/10 |
| 1302 | Formato unificado: NIfTI, espaciado y escala | Yeison | 8 | 27/10 |
| 1303 | División por paciente | Juan | 4 | 28/10 |
| 1304 | Informe del Tester: sin pacientes repetidos | Fernando | 5 | 29/10 |
| 1305 | Script de preprocesamiento automatizado | Yeison | 4 | 28/10 |
| 1306 | Arquitectura del sistema y de software | Yimis | 6 | 26/10 |
| 1307 | Pantallas e interfaz | Sergio | 10 | 29/10 |
| 1308 | Módulo de IA y patrones | Yeison | 5 | 29/10 |
| 1309 | Modelo de base de datos | Juan | 5 | 29/10 |
| 1310 | Índice, inconsistencias, README y etiqueta | Yimis | 3 | 30/10 |
| — | Pruebas automatizadas (pytest) | Fernando | 6 | 29/10 |
| | **Total** | | **64** | |

Horas plan por integrante: Yeison 20, Fernando 16, Sergio 10, Juan 9, Yimis 9.

## 3. Plan de calidad

| Criterio | Meta |
|---|---|
| Pruebas automatizadas | 100 % en verde antes de cada PR que toque `preprocesamiento/` o la división |
| Fuga | `scripts/verificar_fuga.py` con código 0 |
| Revisión | Cada PR revisado por otro rol; el Tester revisa todo lo de datos |
| Defectos abiertos al cierre | 0 |
| Diseño | Aviso de uso no clínico en todas las pantallas de resultados |

## 4. Riesgos del ciclo

| Riesgo | Respuesta |
|---|---|
| Ciclo corto (5 días) con 10 tareas | Diseño (1306–1309) en paralelo con el preprocesamiento; PR pequeños |
| Fuga entre entrenamiento y prueba | Verificación independiente por contenido (1304) |
| Archivos dañados que pasen sin detectarse | Pruebas con volúmenes sintéticos corruptos |
| Dependencia: las pruebas necesitan el código de Yeison | Yeison integra primero (27/10) y Fernando prueba sobre `desarrollo` |
