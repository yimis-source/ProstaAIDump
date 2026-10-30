# Postmortem del Ciclo 1: adquisición y comprensión de datos

| Campo | Valor |
|---|---|
| Ciclo | 1 · 13/10/2026 – 25/10/2026 · cerrado con `v0.1-ciclo1` |
| Reunión de postmortem | 26/10/2026, con todo el equipo |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |

## 1. Resultado

Las 9 tareas (1201–1209) se completaron y se integraron por PR. **Valor ganado: 100 %** al 25/10.

| Tarea | Plan | Real | Fecha plan | Fecha real |
|---|---|---|---|---|
| 1201 | 4 h | 5 h | 14/10 | 14/10 (ajuste el 15/10) |
| 1202 | 6 h | 7 h | 17/10 | 17/10 |
| 1203 | 4 h | 4 h | 18/10 | 18/10 |
| 1204 | 6 h | 8 h | 20/10 | 20/10 |
| 1205 | 6 h | 7 h | 21/10 | 21/10 |
| 1206 | 8 h | 10 h | 22/10 | 22/10 |
| 1207 | 6 h | 6 h | 23/10 | 23/10 |
| 1208 | 5 h | 6 h | 23/10 | **24/10** (1 día de atraso, sin impacto en el hito) |
| 1209 | 2 h | 2 h | 25/10 | 25/10 |
| Coordinación | 4 h | 5 h | — | — |
| **Total** | **51 h** | **60 h** | | |

**Desviación de esfuerzo: +17,6 %.** Las tareas con más desviación fueron las que dependían de manipular los datos por primera vez (1204 y 1206).

| Integrante | Plan | Real |
|---|---|---|
| Juan | 26 h | 31 h |
| Yeison | 10 h | 12 h |
| Fernando | 6 h | 7 h |
| Yimis | 6 h | 7 h |
| Sergio | 3 h | 3 h |

## 2. Defectos

Detalle en el [LOGD](LOGD_registro_defectos.md).

| ID | Tipo | Fase en que se introdujo | Fase en que se detectó | Corrección |
|---|---|---|---|---|
| D-01 | 10 Documentación | Requisitos (1201) | Revisión | 20 min |
| D-02 | 70 Datos | Implementación (1205) | Prueba (ejecución sobre datos reales) | 35 min |
| D-03 | 50 Interfaz | Implementación (1206) | Ejecución | 10 min |

- **3 defectos**, ninguno llegó a `main`.
- Rendimiento de eliminación antes de integrar: **100 %**.
- Densidad: 3 defectos en 4 scripts (≈ 430 líneas) y 13 documentos.

## 3. Calidad

| Criterio del lanzamiento | Resultado |
|---|---|
| PR revisados por otro rol | 4 de 4 |
| Datos personales | 0 hallazgos en 1024 archivos |
| Volúmenes en Git | 0 |
| Cifras reproducibles por script | Sí (`inventario.csv`, `anonimizacion.csv`, `analisis_geometria.csv`) |

## 4. Lecciones aprendidas

1. Las tareas que tocan los datos por primera vez se subestiman en un ~25 %.
2. La revisión cruzada sirve: D-01 (falta el criterio de duplicados) se detectó en una revisión y luego evitó un error mayor, el paciente duplicado MSD/PROMISE12.
3. Ejecutar los scripts sobre los datos reales antes de documentar resultados (D-02) ahorra rehacer informes.

## 5. Mejoras para el Ciclo 2

| Mejora | Responsable |
|---|---|
| Multiplicar por 1,15 las estimaciones de las tareas con datos | Fernando |
| Pruebas automatizadas (pytest) para el código de preprocesamiento antes de integrarlo | Fernando |
| Verificación de fuga independiente de la división del Analista | Fernando |
| Un PR por bloque de trabajo, no al final del ciclo | Todos |
