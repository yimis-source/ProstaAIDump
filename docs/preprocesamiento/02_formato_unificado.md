# Formato unificado: NIfTI, mismo espaciado y escala (tarea 1302)

| Campo | Valor |
|---|---|
| Ciclo | 2 |
| Responsable | Yeison Bolaños Ruiz (Desarrollador) |
| Revisa | Juan David Riascos Erazo (Analista) |
| Código | `preprocesamiento/transformaciones.py` |
| Fecha | 28/10/2026 |

## 1. Decisiones

| Aspecto | Decisión | Justificación |
|---|---|---|
| Formato de salida | NIfTI comprimido (`.nii.gz`), float32 la imagen y uint8 la máscara | Lo leen MONAI, nibabel y 3D Slicer; PROMISE12 (`.mhd`) se convierte |
| Canal | Solo T2 (canal 0 del MSD) | El modelo del Ciclo 3 es monocanal T2 (CI-1) |
| Orientación | **RAS** | La del MSD; Prostate158 y PROMISE12 vienen en LPS |
| Espaciado | **0,625 × 0,625 × 3,6 mm** | Es el de 23 de los 32 casos del MSD (tarea 1206). Se conserva la anisotropía |
| Interpolación | B-spline para la imagen y vecino más cercano para la máscara | Evita valores intermedios en la máscara |
| Escala de intensidades | Recorte a los percentiles 0,5–99,5 y **z-score** sobre los vóxeles por encima del recorte inferior | Las escalas de cada conjunto no son comparables (p99 de 201 a 3539) |
| Máscara | Binaria: etiqueta > 0 = próstata (PZ + TZ) | PROMISE12 solo trae la glándula completa; 2 casos del MSD no tienen TZ |

## 2. Resultado sobre los datos reales

| Conjunto | Casos convertidos | Tamaño resultante x/y (mín–máx) | Cortes z (mín–máx) |
|---|---|---|---|
| MSD_Task05 | 32 | 307–371 | 12–24 |
| PROMISE12 | 50 | 224–320 | 17–35 |
| Prostate158 | 139 | 174–193 | 20–33 |

Todos los volúmenes resultantes comparten orientación, espaciado y escala. La prueba `test_volumen_de_la_mascara_se_conserva` comprueba que el remuestreo no altera el volumen de la próstata en más del 10 %.

## 3. Pendiente para el Ciclo 3

- El tamaño en x/y sigue variando entre casos. El recorte o relleno a un tamaño fijo (*patch*) lo decide quien entrene, según el modelo.
- La corrección de inhomogeneidad N4 (observada en la tarea 1207) queda como opción, no activada por defecto.
