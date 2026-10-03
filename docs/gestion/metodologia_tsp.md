# Metodología de desarrollo: TSP con ciclos incrementales

| Campo | Valor |
|---|---|
| Proyecto | Prosta-AI |
| Responsable | Yimis Buenaventura (Director de Proyecto / Líder) |
| Fecha | 03/10/2026 |
| Base | Acta de Constitución v1.0, sección de metodología |

## 1. Enfoque

- **Gestión:** PMBOK 6 con plantillas Open PM/PM².
- **Desarrollo:** **TSP (Team Software Process)**, del SEI (Watts Humphrey), en su forma incremental. El producto se construye en **7 ciclos**; cada uno agrega una parte funcional y verificada sobre lo que dejó el anterior.
- **Requisitos:** ISO/IEC/IEEE 29148.

TSP es un proceso **planificado y medido**. Cada ciclo se estima, se ejecuta contra ese plan y se cierra comparando lo real con lo planeado. Los datos de un ciclo sirven para estimar mejor el siguiente.

## 2. Estructura de cada ciclo

| Paso | Qué se hace | Artefacto | Responsable |
|---|---|---|---|
| 1. Lanzamiento | Objetivos del ciclo, tareas, estimación de horas, plan de calidad y riesgos | `docs/gestion/tsp/cicloN_lanzamiento.md` | Planeación (Fernando), con todo el equipo |
| 2. Requisitos y diseño | Lo que el ciclo necesite precisar o diseñar | `docs/` | Analista / Diseñador / Director |
| 3. Implementación | Código y documentos en la rama de cada rol | Commits | Cada rol |
| 4. Revisión | *Pull request* revisado por otro rol antes de entrar a `desarrollo` | PR en GitHub | Revisor asignado |
| 5. Prueba | Pruebas automatizadas y verificaciones antes de integrar | `tests/`, `scripts/verificar_*.py` | Tester |
| 6. Postmortem | Horas reales frente a las planeadas, defectos, valor ganado y lecciones | `docs/gestion/tsp/cicloN_postmortem.md` | Planeación, con todo el equipo |
| 7. Cierre | `desarrollo` → `main` y etiqueta `v0.N-cicloN` | Etiqueta en GitHub | Director |

Durante todo el ciclo se mantienen dos registros:

- **LOGD (registro de defectos):** cada defecto con su tipo, la fase en que se introdujo, la fase en que se detectó y el tiempo de corrección. Archivo: `docs/gestion/tsp/LOGD_registro_defectos.md`.
- **LOGT (registro de tiempos):** horas por integrante y tarea. Archivo: `docs/gestion/tsp/LOGT_registro_tiempos.md`.

## 3. Ciclos del proyecto

| Ciclo | Fechas | Hito | Contenido | Entregable |
|---|---|---|---|---|
| 1 | 13/10 – 25/10/2026 | H003 | Adquisición y comprensión de datos | E2 (parte) |
| 2 | 26/10 – 30/10/2026 | H004 | Preprocesamiento, división por paciente y diseño | E2, E3 |
| 3 | 31/10 – 13/11/2026 | H005 | Segmentación 3D, modelo e inferencia | E4 |
| 4 | 14/11 – 20/11/2026 | H006 | Región de interés (ROI) | E5 |
| 5 | 21/11 – 25/11/2026 | H007 | Evaluación técnica | Insumo de E7 |
| 6 | 26/11 – 02/12/2026 | H008 | Aplicación web e integración | E6, E7 |
| 7 | 03/12 – 09/12/2026 | H009 | Cierre y lecciones aprendidas | E8 |

La duración de cada ciclo **no es fija**: la define su lanzamiento según el trabajo planeado y las fechas de los hitos.

## 4. Roles TSP en el equipo

Cada integrante tiene un rol de desarrollo, un grupo de procesos de gestión (Acta) y un rol de gestión TSP.

| Integrante | Rol de desarrollo | Grupo de gestión | Rol TSP |
|---|---|---|---|
| Yimis Buenaventura | Director / Líder | Trazabilidad | **Líder del equipo**: coordina, integra, versiona y decide |
| Yeison Bolaños Ruiz | Desarrollador | Inicio | **Gerente de desarrollo**: estrategia técnica y calidad del código |
| Fernando José Angulo Núñez | Tester | Planeación | **Gerente de planeación**: lanzamientos, LOGT, LOGD, valor ganado y postmortems; además ejecuta las pruebas |
| Juan David Riascos Erazo | Analista | Monitoreo y control | **Gerente de calidad y proceso**: criterios de aceptación, métricas e impacto de los cambios |
| Sergio Gabriel Meneses Silva | Diseñador | Cierre | **Gerente de soporte**: herramientas (3D Slicer, diseño), entorno y material de presentación |

## 5. Convenciones en Git

- Una rama por rol (`lider/…`, `analista/…`, `disenador/…`, `desarrollador/…`, `tester/…`).
- Todo cambio entra a `desarrollo` por *pull request* revisado por otro rol.
- Al cerrar el ciclo N: PR de `desarrollo` a `main` y etiqueta **`v0.N-cicloN`**.
- Mensajes de commit: `tipo(ámbito): descripción` (`feat`, `fix`, `docs`, `test`, `chore`).
