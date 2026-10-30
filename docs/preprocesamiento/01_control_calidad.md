# Control de calidad y descarte de archivos dañados (tarea 1301)

| Campo | Valor |
|---|---|
| Sprint | 2 · Preprocesamiento y diseño |
| Responsable | Fernando José Angulo Núñez (Tester) |
| Implementación | Yeison Bolaños Ruiz (`preprocesamiento/control_calidad.py`) |
| Fecha | 27/10/2026 |
| Resultado | **221 de 221 casos aceptados; 0 descartados por daño** |

## 1. Verificaciones por caso

| # | Verificación | Motivo de descarte |
|---|---|---|
| QC-1 | Integridad del archivo: el flujo gzip completo se descomprime; en `.mhd`, el `.raw` tiene el tamaño declarado | «archivo truncado o dañado» |
| QC-2 | Lectura con SimpleITK (imagen y máscara) | «ilegible» |
| QC-3 | Volumen 3D (o 4D con canal T2) con ≥ 8 cortes | «geometría no válida» |
| QC-4 | Sin NaN/Inf; imagen no constante | «valores NaN» / «imagen constante» |
| QC-5 | Máscara presente y con misma geometría (tamaño, espaciado, origen) | «falta la máscara» / «no coincide en geometría» |
| QC-6 | Etiquetas solo en {0, 1, 2} y máscara no vacía | «etiquetas desconocidas» / «máscara vacía» |

## 2. Defecto encontrado durante las pruebas

La prueba `test_archivo_danado_se_descarta` **falló** con la primera versión del control: un `.nii.gz` cortado a 200 bytes se aceptaba como válido. SimpleITK lee la cabecera y rellena con ceros los datos que faltan sin lanzar error.

- Reportado al Desarrollador el 27/10.
- Corregido el 28/10 con la verificación QC-1, que descomprime el archivo completo.
- La prueba pasa desde entonces y queda como prueba de regresión.

## 3. Resultados sobre los datos reales

| Conjunto | Casos | Aceptados | Descartados |
|---|---|---|---|
| MSD_Task05 | 32 | 32 | 0 |
| PROMISE12 | 50 | 50 | 0 |
| Prostate158 | 139 | 139 | 0 |

Detalle: [control_calidad.csv](control_calidad.csv).

## 4. Exclusiones que no son por daño

| Qué | Cantidad | Motivo |
|---|---|---|
| MSD `imagesTs` | 16 casos | Sin máscara (CE-1). Se reservan para pruebas manuales de la aplicación |
| Archivos ocultos `._*` de macOS en el tar del MSD | — | No son imágenes; se omiten al extraer |
| PROMISE12 completo para entrenamiento | 50 casos | Comparte pacientes con el MSD y no es redistribuible (ver [04](04_informe_tester_fuga.md)) |
| Prostate158: máscaras de tumor | — | Fuera de alcance (no se detectan lesiones) |
