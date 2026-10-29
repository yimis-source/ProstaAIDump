# Preprocesamiento (Sprint 2)

| # | Documento | Tarea | Responsable |
|---|---|---|---|
| 1 | [Control de calidad](01_control_calidad.md) · [control_calidad.csv](control_calidad.csv) | 1301 | Tester |
| 2 | [Formato unificado](02_formato_unificado.md) | 1302 | Desarrollador |
| 3 | [División por paciente](03_division_por_paciente.md) | 1303 | Analista |
| 4 | [Informe de verificación de fuga](04_informe_tester_fuga.md) | 1304 | Tester |
| 5 | Script automatizado (abajo) | 1305 | Desarrollador |

## Script de preprocesamiento (tarea 1305)

```bash
python -m preprocesamiento.preprocesar --fuente msd          # MSD Task05 (principal)
python -m preprocesamiento.preprocesar --fuente prostate158  # respaldo
python -m entrenamiento.division                             # división por paciente
python scripts/verificar_fuga.py                             # verificación del Tester
```

Flujo por caso: control de calidad → canal T2 → orientación RAS → remuestreo a 0,625 × 0,625 × 3,6 mm → z-score → escritura en `datos/preprocesados/<fuente>/{imagenes,mascaras}/<caso>.nii.gz` + `manifiesto.csv` con los aceptados y los descartados (con el motivo).
