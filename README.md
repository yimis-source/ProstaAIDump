# Prosta-AI

Aplicación web **académica y experimental** que carga estudios de resonancia magnética de próstata públicos y desidentificados (DICOM o NIfTI), los segmenta en 3D con un modelo U-Net (PyTorch/MONAI) y muestra la región de interés (ROI) superpuesta a la imagen, con las métricas Dice e IoU cuando el estudio trae máscara de referencia.

> **Prosta-AI no diagnostica.** No tiene uso clínico, no es un dispositivo médico y no trabaja con datos de pacientes reales.

Proyecto del curso Gestión de Proyectos de TI, Universidad Santiago de Cali, 2026-2. Propietario del Proyecto: Ing. Jair Enrique Sanclemente Castro.

## Estado

| Versión | Fecha | Contenido |
|---|---|---|
| `v0.1-ciclo1` | 25/10/2026 | Datos elegidos, licencias, inventario, anonimización, geometría, revisión en 3D Slicer e informe de datos |
| `v0.2-ciclo2` | 30/10/2026 | Control de calidad, formato unificado NIfTI, división por paciente, verificación de fuga, script de preprocesamiento y diseño (arquitectura, pantallas, módulo de IA y base de datos) |

Siguiente: Ciclo 3 (13/11/2026), segmentación 3D, modelo e inferencia.

## Equipo

| Integrante | Rol de desarrollo | Grupo de gestión | Rama |
|---|---|---|---|
| Yimis Buenaventura | Director de Proyecto / Líder | Trazabilidad | `lider/yimis-buenaventura` |
| Juan David Riascos Erazo | Analista | Monitoreo y control | `analista/juan-riascos` |
| Sergio Gabriel Meneses Silva | Diseñador | Cierre | `disenador/sergio-meneses` |
| Yeison Bolaños Ruiz | Desarrollador | Inicio | `desarrollador/yeison-bolanos` |
| Fernando José Angulo Núñez | Tester | Planeación | `tester/fernando-angulo` |

## Metodología

Desarrollo con **TSP (Team Software Process)** en 7 ciclos incrementales: cada ciclo empieza con un lanzamiento (plan, estimación, calidad y riesgos) y termina con un postmortem (plan frente a real, defectos y lecciones). Registros de cada ciclo en `docs/gestion/tsp/`.

| Ciclo | Plan | Real | Defectos |
|---|---|---|---|
| 1 | 51 h | 60 h | 3 (cerrados) |
| 2 | 64 h | 72 h | 1 (cerrado) |

## Flujo de trabajo

- `main`: protegida. Solo recibe la integración al cierre de cada ciclo, con etiqueta `v0.N-cicloN`.
- `desarrollo`: integración continua. Cada rama de rol entra por *pull request* revisado.
- Los PR que tocan `preprocesamiento/` o la división deben pasar `pytest` y `scripts/verificar_fuga.py` (ver `docs/preprocesamiento/04_informe_tester_fuga.md`).

## Uso rápido

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/descargar_datos.py msd
.venv/bin/python -m preprocesamiento.preprocesar --fuente msd
.venv/bin/python -m entrenamiento.division
.venv/bin/python scripts/verificar_fuga.py
.venv/bin/python -m pytest
```

## Documentación

| Ubicación | Contenido |
|---|---|
| `docs/gestion/` | Acta de Constitución, metodología TSP y registros por ciclo (`tsp/`: lanzamientos, postmortems, LOGD, LOGT) |
| `docs/datos/` | Ciclo 1: criterios, selección, fichas de licencia, inventario, anonimización, geometría, revisión en 3D Slicer e informe de datos |
| `docs/preprocesamiento/` | Ciclo 2: control de calidad, formato unificado, división por paciente e informe de fuga |
| `docs/ejecucion/` | Requisitos (SRS, matriz) y diseño: arquitectura, módulos, pantallas y modelo de datos |

## Datos

Los datos no se versionan (`datos/` está en `.gitignore`). Conjunto principal: MSD Task05_Prostate (CC-BY-SA 4.0). Respaldo: Prostate158 (CC-BY 4.0). Ver `docs/datos/fichas/`.

## Marco legal

Ley 1581 de 2012 y Decreto 1377 de 2013 (protección de datos personales), Ley 23 de 1981 (la decisión médica es del profesional) y CONPES 3975.
