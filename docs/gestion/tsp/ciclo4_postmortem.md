# Postmortem del Ciclo 4: región de interés (ROI)

| Campo | Valor |
|---|---|
| Ciclo | 4 · plan 14/11 – 20/11/2026 · **real 03/11 – 12/11/2026, en paralelo con el Ciclo 3 (cierre adelantado 8 días)** · se cierra con `v0.4-ciclo4` |
| Reunión de postmortem | 12/11/2026, con todo el equipo, junto con el del Ciclo 3 |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |

## 1. Resultado

Las 7 tareas (1501–1507) se completaron. **Valor ganado: 100 %**.

| Tarea | Plan | Real | Resultado |
|---|---|---|---|
| 1501 | 6 h | 7 h | `pipeline/roi.py`: espacio original, volumen, centroide, caja, cortes; máscara vacía sin error |
| 1502 | 6 h | 6 h | `visualizacion/render.py` y `scripts/generar_roi.py` (PNG + `resumen_roi.json`) |
| 1503 | 6 h | 7 h | `visualizacion/textos.py`: aviso, explicación y límites; colores de CU04 (`#2DD4BF`, 45 %) |
| 1504 | 6 h | 6 h | 18 pruebas de ROI y visualización con cubo y esfera sintéticos |
| 1505 | 5 h | 5 h | `docs/roi/README.md`: criterios de aceptación y verificación real |
| 1506 | 2 h | 2,5 h | Ejemplos en `docs/roi/ejemplos/` y README |
| 1507 | 5 h | 5,5 h | Etapa `build_roi` en la cadena; `generar_roi.py --modelo`; 3 pruebas nuevas |
| **Total** | **36 h** | **39 h** | |

**Desviación de esfuerzo: +8,3 %**, frente a +9,8 % en el ciclo anterior.

| Integrante | Plan | Real |
|---|---|---|
| Yeison | 17 h | 18,5 h |
| Sergio | 6 h | 7 h |
| Fernando | 6 h | 6 h |
| Juan | 5 h | 5 h |
| Yimis | 2 h | 2,5 h |

Las desviaciones se concentran en las tareas con defectos (1501, 1503, 1506).

## 2. Resultados técnicos

ROI con la máscara **predicha** en dos casos del conjunto de prueba (modelo `prostate_mri_anatomy` 0.3.6, CPU):

| Caso | Volumen predicho | Volumen referencia | Dice / IoU (rejilla original) | Cortes con ROI (pred. / ref.) | Tiempo total |
|---|---|---|---|---|---|
| prostate_28 | 40,7 mL | 47,3 mL | 0,8320 / 0,7123 | 10 / 10 | 11,5 s |
| prostate_34 | 64,2 mL | 63,1 mL | 0,9105 / 0,8356 | 15 / 13 | 13,1 s |

- El cálculo de la ROI tarda menos de 0,1 s; casi todo el tiempo es la segmentación.
- Los Dice coinciden con la evaluación del Ciclo 3, lo que confirma que la ROI está en el mismo espacio que la referencia.
- prostate_28 (el peor caso) subestima el volumen en 6,6 mL (−14 %). La evaluación técnica completa es del Ciclo 5.

## 3. Defectos

| ID | Tipo | Introducido | Detectado | Corrección |
|---|---|---|---|---|
| D-07 | 80 Función | DIS (1501, selección de cortes) | EJE (primera figura) | Excluir bordes e incluir el corte de mayor área |
| D-08 | 10 Documentación | IMP (1503, textos) | EJE (primera figura) | El aviso aparecía duplicado; queda solo en el pie (`incluir_aviso`) |
| D-09 | 10 Documentación | IMP (1506, ejemplos) | REV | PNG de 500 KB, sobre el límite de 300 KB; se reduce y cuantiza |

Defectos abiertos al cierre: **0**. Los tres se detectaron antes de integrar.

## 4. Calidad

| Criterio del lanzamiento | Resultado |
|---|---|
| Pruebas automatizadas | 72 de 72 en verde |
| Máscara vacía | Mensaje claro, sin error (probado) |
| Superposición | Conserva dimensiones y solo colorea la máscara (probado) |
| Aviso no clínico | En el pie de toda figura y en el texto de resultado |
| ROI con máscara predicha | Sí, en prostate_28 y prostate_34 |
| Defectos abiertos al cierre | 0 |

## 5. Lecciones aprendidas

1. Trabajar primero con la máscara de referencia permitió avanzar en paralelo al Ciclo 3; pero un Dice de 1,0 con la propia referencia no prueba nada, y por eso hizo falta 1507.
2. Adelantar el ciclo en paralelo funcionó porque los roles con capacidad libre (Sergio, Juan, Fernando) arrancaron primero con diseño, criterios y pruebas, y la ROI no dependía de la inferencia final salvo en 1507. El costo fue la carga de Yeison en dos ciclos a la vez, que se contuvo haciéndolo entrar solo después de 1403.
3. Mirar la figura generada encontró dos defectos (D-07, D-08) que las pruebas no cubrían.

## 6. Mejoras para el Ciclo 5

| Mejora | Responsable |
|---|---|
| Evaluar la ROI (volumen y Dice) en los 5 casos de prueba, con criterios de aceptación | Juan |
| Unificar el aviso no clínico en una sola constante antes de la API (Ciclo 6) | Yeison |
| Mantener el factor 1,15; las tareas con revisión visual necesitan holgura | Fernando |
