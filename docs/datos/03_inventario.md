# Descarga, organización e inventario de datos (tarea 1204)

| Campo | Valor |
|---|---|
| Sprint | 1 |
| Responsable | Yeison Bolaños Ruiz (Desarrollador) |
| Revisa | Juan David Riascos Erazo (Analista) |
| Fecha | 20/10/2026 |

## 1. Cómo se descarga

```bash
python scripts/descargar_datos.py msd           # MSD Task05 → datos/Task05_Prostate
python scripts/descargar_datos.py prostate158   # Prostate158 → datos/Prostate158/train
# PROMISE12: descarga manual (requiere registro) → datos/PROMISE12/training_data
python scripts/inventario_datos.py              # regenera docs/datos/inventario.csv
```

`datos/` está en `.gitignore`: **ningún volumen se versiona**. El repositorio solo guarda el inventario con el SHA-256 de cada archivo, que sirve para comprobar que todos los integrantes trabajan con la misma copia.

## 2. Estructura de carpetas

```
datos/
├── Task05_Prostate/          # principal
│   ├── dataset.json
│   ├── imagesTr/prostate_XX.nii.gz   (32, 4D: T2 + ADC)
│   ├── labelsTr/prostate_XX.nii.gz   (32, PZ = 1, TZ = 2)
│   └── imagesTs/prostate_XX.nii.gz   (16, sin máscara)
├── Prostate158/train/        # respaldo
│   └── 020/ … 158/  t2, adc, dwi, t2_anatomy_reader1, tumor…
├── PROMISE12/training_data/  # referencia local, no redistribuible
│   └── CaseXX.mhd/.raw, CaseXX_segmentation.mhd/.raw
└── preprocesados/            # salida del Sprint 2 (se genera)
```

## 3. Resumen del inventario

| Conjunto | Archivos | Tamaño | Casos con máscara |
|---|---|---|---|
| MSD_Task05 | 81 | 228,7 MiB | 32 |
| Prostate158 | 844 | 2655,5 MiB | 139 |
| PROMISE12 | 200 | 750,1 MiB | 50 |
| **Total** | **1125** | **3,6 GiB** | **221** |

Detalle por archivo: [inventario.csv](inventario.csv) (conjunto, ruta, bytes, SHA-256).

## 4. Observaciones

- El tar del MSD trae archivos ocultos de macOS (`._prostate_XX.nii.gz`). El script de descarga los omite al extraer.
- La carpeta de PROMISE12 tenía una subcarpeta `convertidas/` de una prueba local de conversión. Se excluye del inventario porque no es parte del conjunto original.
- La extracción valida las rutas para que ningún miembro del tar/zip escriba fuera de `datos/`.
