# Postmortem del Ciclo 2: preprocesamiento, división por paciente y diseño

| Campo | Valor |
|---|---|
| Ciclo | 2 · 26/10/2026 – 30/10/2026 · se cierra con `v0.2-ciclo2` |
| Reunión de postmortem | 30/10/2026, con todo el equipo |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |

## 1. Resultado

Las 10 tareas (1301–1310) y las pruebas automatizadas se completaron. **Valor ganado: 100 %.**

| Tarea | Plan | Real | Fecha plan | Fecha real |
|---|---|---|---|---|
| 1301 | 8 h | 11 h | 27/10 | **28/10** (corrección de D-04) |
| 1302 | 8 h | 8 h | 27/10 | 27/10 |
| 1303 | 4 h | 4 h | 28/10 | 28/10 |
| 1304 | 5 h | 7 h | 29/10 | 29/10 |
| 1305 | 4 h | 4 h | 28/10 | 28/10 |
| 1306 | 6 h | 6 h | 26/10 | 26/10 |
| 1307 | 10 h | 12 h | 29/10 | 29/10 |
| 1308 | 5 h | 5 h | 29/10 | 29/10 |
| 1309 | 5 h | 5 h | 29/10 | 29/10 |
| 1310 | 3 h | 4 h | 30/10 | 30/10 |
| Pruebas (pytest) | 6 h | 6 h | 29/10 | 29/10 |
| **Total** | **64 h** | **72 h** | | |

**Desviación de esfuerzo: +12,5 %**, frente a +17,6 % en el Ciclo 1. El factor 1,15 mejoró la estimación.

| Integrante | Plan | Real |
|---|---|---|
| Yeison | 20 h | 22 h |
| Fernando | 16 h | 19 h |
| Sergio | 10 h | 12 h |
| Yimis | 9 h | 10 h |
| Juan | 9 h | 9 h |

## 2. Defectos

| ID | Tipo | Fase en que se introdujo | Fase en que se detectó | Corrección |
|---|---|---|---|---|
| D-04 | 80 Función | Implementación (1301, control de calidad) | **Prueba unitaria** (`test_archivo_danado_se_descarta`) | 95 min |

- D-04: un `.nii.gz` truncado pasaba el control de calidad, porque SimpleITK lo rellena con ceros sin error. Lo detectó una prueba del Tester **antes de llegar a `main`** y quedó como prueba de regresión.
- Defectos abiertos al cierre: **0**.

## 3. Calidad

| Criterio del lanzamiento | Resultado |
|---|---|
| Pruebas automatizadas | 21 de 21 en verde |
| Verificación de fuga | Código 0: sin pacientes repetidos. Hallazgo: 4 casos del MSD también están en PROMISE12, por lo que este no se usa |
| PR revisados por otro rol | 9 de 9 |
| Defectos abiertos al cierre | 0 |
| Aviso de uso no clínico en pantallas de resultados | Sí |

## 4. Lecciones aprendidas

1. La mejora del Ciclo 1 funcionó: con pruebas automatizadas, D-04 se detectó en la fase de prueba y no en la integración.
2. Leer un archivo sin error no garantiza que esté completo: hay que verificar la integridad explícitamente.
3. Un ciclo de 5 días con 10 tareas solo funcionó porque el diseño avanzó en paralelo con el código.

## 5. Mejoras para el Ciclo 3

| Mejora | Responsable |
|---|---|
| Mantener el factor 1,15; aplicar 1,25 a las tareas nuevas de entrenamiento (sin historial) | Fernando |
| Reservar la GPU de Colab con anticipación (riesgo 1 del Acta) | Yeison |
| Agregar pruebas de métricas (Dice e IoU) antes de reportar resultados del modelo | Fernando |
| Registrar en el LOGT las horas de espera de cómputo por separado | Todos |
