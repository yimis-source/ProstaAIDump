# Selección de conjuntos de datos (tarea 1202)

| Campo | Valor |
|---|---|
| Ciclo | 1 |
| Responsable | Juan David Riascos Erazo (Analista) |
| Aprueba | Yimis Buenaventura (Director) |
| Versión | 1.0 · 17/10/2026 |

## 1. Candidatos evaluados

Cada candidato se evaluó contra los criterios de [01_criterios_seleccion.md](01_criterios_seleccion.md).

| Conjunto | Casos con máscara | Secuencias | Máscara | Formato | Licencia | Cumple | Decisión |
|---|---|---|---|---|---|---|---|
| **Medical Segmentation Decathlon, Task05_Prostate** | 32 (+16 sin máscara) | T2 + ADC (4D) | PZ (1) y TZ (2) | NIfTI | CC-BY-SA 4.0 | CI-1 a CI-7 | **Principal** |
| **Prostate158** | 139 (119 entrenamiento + 20 validación) | T2, ADC, DWI | Anatomía PZ/TZ (lector 1) y tumor | NIfTI | CC-BY 4.0 | CI-1 a CI-7 | **Respaldo** |
| PROMISE12 | 50 (+30 de prueba sin máscara) | T2 | Glándula completa | MetaImage (.mhd/.raw) | Términos del reto: registro obligatorio, sin redistribución | CI-1 a CI-4, CI-6; CI-5 parcial | Solo **referencia local**, no se redistribuye |
| NCI-ISBI 2013 | 60 | T2 | PZ y glándula central | DICOM | TCIA, uso con atribución | Sí, pero requiere conversión y emparejar máscaras | Descartado por tiempo |
| PI-CAI | 1500 | bpMRI | Lesión (no glándula completa en todos) | MHA | CC-BY-NC 4.0 | CI-3 parcial | Descartado: la máscara es de lesión y el volumen excede el cómputo disponible (riesgo 1 del Acta) |
| Datos de una institución local | — | — | — | DICOM | — | CI-4 no | Descartado: implicaría datos de pacientes reales (Ley 1581) |

## 2. Justificación de la elección

**MSD Task05 como principal:**
- Es el conjunto que usan los tutoriales y modelos de MONAI, que es el stack fijado por el Acta (RC-01).
- Licencia CC-BY-SA 4.0: permite publicar derivados con atribución y compartir igual.
- Tamaño manejable en CPU (228,7 MiB descargados).
- Limitación: solo 32 casos con máscara, todos de un mismo centro (Radboud UMC, Nijmegen).

**Prostate158 como respaldo:**
- Mismo tipo de anotación (PZ/TZ) que el MSD, lo que permite unir etiquetas igual que en el principal.
- 139 casos de otro centro (Charité, Berlín) y escáneres de 3 T: sirve para medir sesgo y, si hace falta, ampliar el entrenamiento.
- Contras: 2,6 GiB y espaciado distinto (0,4 mm en el plano y 3 mm entre cortes) que obliga a remuestrear.

**PROMISE12 solo como referencia:** su licencia no permite redistribuir. Además, en la tarea 1206 se comprobó que **comparte al menos un paciente con el MSD** (`prostate_16` ≡ `Case23`: misma geometría y 315,4 ml de volumen). Por eso no se mezcla con el MSD (criterio CE-3).

## 3. Decisión

| Uso | Conjunto |
|---|---|
| Entrenamiento, validación y prueba (Ciclos 2–5) | MSD Task05 (32 casos) |
| Respaldo y evaluación externa | Prostate158 (139 casos) |
| Pruebas manuales de la aplicación | MSD `imagesTs` (16 casos sin máscara) |
| No se usa para entrenar | PROMISE12 |

Si en el Ciclo 3 el modelo no alcanza Dice ≥ 0,80 con el MSD, se abre una solicitud de cambio para ampliar el entrenamiento con Prostate158.
