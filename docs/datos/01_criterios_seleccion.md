# Criterios de selección de estudios (tarea 1201)

| Campo | Valor |
|---|---|
| Ciclo | 1 · Adquisición y comprensión de datos |
| Responsable | Juan David Riascos Erazo (Analista) |
| Revisa | Fernando José Angulo Núñez (Tester), Yimis Buenaventura (Director) |
| Versión | 1.1 · 15/10/2026 |

Define qué estudios de resonancia magnética de próstata sirven para Prosta-AI. Se aplica a cada conjunto candidato (tarea 1202) y luego a cada caso dentro del conjunto elegido (tarea 1301).

## 1. Criterios de inclusión

| # | Criterio | Motivo | Cómo se verifica |
|---|---|---|---|
| CI-1 | Secuencia **T2 ponderada (T2w) axial** | Es la secuencia en la que se delimita la glándula; el modelo del Ciclo 3 trabaja con T2w | Metadatos del conjunto (`modality`) y revisión visual (tarea 1207) |
| CI-2 | Volumen **3D** con al menos 8 cortes | La segmentación es volumétrica (RF del SRS) | `dim_z` en `analisis_geometria.csv` |
| CI-3 | Trae **máscara de referencia** de la próstata (glándula completa o zonas PZ/TZ) | Sin máscara no se puede entrenar ni calcular Dice/IoU | Existe archivo de etiqueta con la misma geometría |
| CI-4 | Datos **públicos y desidentificados** en origen | RC-03 del Acta y Ley 1581 de 2012: no se trabaja con pacientes reales identificables | Ficha del conjunto + verificación de metadatos (tarea 1205) |
| CI-5 | **Licencia** que permita uso académico y, de preferencia, redistribución de derivados | Los informes y modelos se publican en GitHub | Ficha de licencia (tarea 1203) |
| CI-6 | Formato legible con herramientas libres: **NIfTI, DICOM o MetaImage** | Se unifica a NIfTI en el Ciclo 2 | Lectura con SimpleITK/nibabel |
| CI-7 | Un identificador de caso por **paciente** | Permite dividir por paciente sin fuga (RC-04) | Documentación del conjunto |

## 2. Criterios de exclusión

| # | Criterio |
|---|---|
| CE-1 | Estudios sin máscara (p. ej. `imagesTs` del MSD): solo sirven para pruebas manuales de la aplicación, no para entrenar ni evaluar |
| CE-2 | Archivos dañados, truncados o con geometría incoherente entre imagen y máscara |
| CE-3 | Estudios duplicados entre conjuntos (el mismo paciente publicado en dos repositorios) |
| CE-4 | Conjuntos que exigen acuerdo de uso con datos clínicos identificables o aprobación de comité de ética |
| CE-5 | Conjuntos con licencia que prohíbe trabajos derivados o uso fuera del reto original, salvo como referencia |

## 3. Criterios deseables (no excluyentes)

- Más de 30 casos con máscara.
- Espaciado en el plano ≤ 0,8 mm y entre cortes ≤ 4 mm.
- Varias fuentes de adquisición (escáneres o centros) para medir sesgo.
- Documentación publicada (artículo con DOI) para poder citar.

## 4. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 14/10/2026 | Primera versión |
| 1.1 | 15/10/2026 | Se agrega CE-3 (duplicados entre conjuntos) por observación del Tester |
