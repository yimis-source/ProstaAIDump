# Prosta-AI

Aplicación web **académica y experimental** que carga estudios de resonancia magnética de próstata públicos y desidentificados (DICOM o NIfTI), los segmenta en 3D con un modelo U-Net (PyTorch/MONAI) y muestra la región de interés (ROI) superpuesta a la imagen, con las métricas Dice e IoU cuando el estudio trae máscara de referencia.

> **Prosta-AI no diagnostica.** No tiene uso clínico, no es un dispositivo médico y no trabaja con datos de pacientes reales.

Proyecto del curso Gestión de Proyectos de TI, Universidad Santiago de Cali, 2026-2. Propietario del Proyecto: Ing. Jair Enrique Sanclemente Castro.

## Equipo

| Integrante | Rol de desarrollo | Grupo de gestión | Rama |
|---|---|---|---|
| Yimis Buenaventura | Director de Proyecto / Líder | Trazabilidad | `lider/yimis-buenaventura` |
| Juan David Riascos Erazo | Analista | Monitoreo y control | `analista/juan-riascos` |
| Sergio Gabriel Meneses Silva | Diseñador | Cierre | `disenador/sergio-meneses` |
| Yeison Bolaños Ruiz | Desarrollador | Inicio | `desarrollador/yeison-bolanos` |
| Fernando José Angulo Núñez | Tester | Planeación | `tester/fernando-angulo` |

## Metodología

Desarrollo con **TSP (Team Software Process)** en 7 ciclos incrementales: cada ciclo empieza con un lanzamiento (plan, estimación, calidad y riesgos) y termina con un postmortem (plan frente a real, defectos y lecciones). Detalle en `docs/gestion/metodologia_tsp.md`.

## Flujo de trabajo

- `main`: protegida. Solo recibe la integración al cierre de cada ciclo, con etiqueta `v0.N-cicloN`.
- `desarrollo`: integración continua. Cada rama de rol entra por *pull request* revisado.
- Cada integrante trabaja en su rama y la sincroniza con `desarrollo` antes de abrir un PR.
- Mensajes de commit: `tipo(ámbito): descripción` (`feat`, `fix`, `docs`, `test`, `chore`).

## Calendario

| Hito | Fecha | Contenido |
|---|---|---|
| H002 | 12/10/2026 | Plan y especificación de requisitos |
| Ciclo 1 (H003) | 25/10/2026 | Adquisición y comprensión de datos |
| Ciclo 2 (H004) | 30/10/2026 | Preprocesamiento, división por paciente y diseño |
| Ciclos 3–7 | 13/11–09/12/2026 | Modelo, ROI, evaluación, aplicación web y cierre |

## Documentación

- `docs/gestion/`: Acta de Constitución y metodología TSP.
