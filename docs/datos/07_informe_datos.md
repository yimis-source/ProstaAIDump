# Informe de datos – Ciclo 1 (tarea 1208)

| Campo | Valor |
|---|---|
| Proyecto | Prosta-AI |
| Documento | Informe_Datos_Prosta-AI_25-10-2026_v1.0 |
| Autor | Juan David Riascos Erazo (Analista, Monitoreo y control) |
| Revisan | Fernando José Angulo Núñez (Tester), Yimis Buenaventura (Director) |
| Hito | H003 · 25/10/2026 · cierre del Ciclo 1 |

## 1. Resumen

El Ciclo 1 cerró con los datos elegidos, descargados, inventariados, verificados y analizados:

| Tarea | Entregable | Estado |
|---|---|---|
| 1201 | [Criterios de selección](01_criterios_seleccion.md) | Cerrada |
| 1202 | [Selección de conjuntos](02_seleccion_datasets.md): MSD Task05 principal, Prostate158 de respaldo | Cerrada |
| 1203 | [Fichas de licencia](fichas/) de MSD, Prostate158 y PROMISE12 | Cerrada |
| 1204 | [Inventario](03_inventario.md): 1125 archivos, 3,6 GiB, SHA-256 por archivo | Cerrada |
| 1205 | [Anonimización](04_verificacion_anonimizacion.md): 0 hallazgos en 1024 archivos | Cerrada |
| 1206 | [Análisis de geometría](05_analisis_geometria.md) de 221 casos | Cerrada |
| 1207 | [Revisión en 3D Slicer](06_revision_3d_slicer.md) de 7 casos | Cerrada |
| 1208 | Este informe | Cerrada |
| 1209 | Etiqueta `v0.1-ciclo1` | Al fusionar en `main` |

## 2. Datos con los que sigue el proyecto

| Uso | Conjunto | Casos | Licencia |
|---|---|---|---|
| Entrenamiento, validación y prueba | MSD Task05 (canal T2, máscara binarizada) | 32 | CC-BY-SA 4.0 |
| Evaluación externa y respaldo | Prostate158 (T2, `t2_anatomy_reader1`) | 139 | CC-BY 4.0 |
| Pruebas manuales de la aplicación | MSD `imagesTs` | 16 | CC-BY-SA 4.0 |
| No se usa | PROMISE12 | 50 | Sin redistribución |

## 3. Características principales

- **MSD:** 256–384 vóxeles en el plano y 11–24 cortes; espaciado mayoritario de 0,625 × 0,625 × 3,6 mm; orientación RAS; volumen de la próstata de 16,0 a 315,4 ml (mediana 62,0).
- **Prostate158:** 0,27–0,47 mm en el plano, 3 mm entre cortes y orientación LPS. Más casos y de otro centro.
- Los conjuntos tienen escalas de intensidad no comparables entre sí.

## 4. Riesgos de datos

| Riesgo | Nivel | Tratamiento |
|---|---|---|
| Pocos casos en el principal (32) | Alto | División por paciente con semilla fija; modelo preentrenado (Ciclo 3); Prostate158 para evaluación externa |
| Sesgo de centro y escáner (todo el MSD viene de Radboud) | Medio | Evaluar en Prostate158 y documentarlo como limitación |
| **Fuga por duplicados entre conjuntos** (`prostate_16` ≡ PROMISE12 `Case23`) | Medio | No mezclar MSD con PROMISE12; el Tester lo comprueba en la tarea 1304 |
| Licencia CC-BY-SA (compartir igual) | Bajo | No redistribuir volúmenes; si se publican derivados, con la misma licencia |
| Máscaras sin TZ (`prostate_18`, `prostate_32`) | Bajo | Se binariza; no afecta a la segmentación de la glándula completa |
| Volumen de descarga de Prostate158 (2,6 GiB) | Bajo | Descarga opcional, solo para quien evalúe |

## 5. Recomendaciones para el Ciclo 2

1. **Control de calidad** automático por caso: lectura completa, geometría imagen-máscara, etiquetas válidas y máscara no vacía (tarea 1301).
2. **Formato unificado:** NIfTI con orientación RAS, espaciado 0,625 × 0,625 × 3,6 mm, z-score por caso y máscara binaria (tarea 1302).
3. **División por paciente** 70/15/15 con semilla 2026 sobre los 32 casos del MSD, con huella SHA-256 para detectar modificaciones (tarea 1303).
4. **Verificación de fuga** por parte del Tester, incluido el cruce con PROMISE12 (tarea 1304).
5. Un **script único** que ejecute todo de forma reproducible (tarea 1305).
