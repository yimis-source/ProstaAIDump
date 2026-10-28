# División por paciente en entrenamiento, validación y prueba (tarea 1303)

| Campo | Valor |
|---|---|
| Sprint | 2 |
| Responsable | Juan David Riascos Erazo (Analista) |
| Código | `entrenamiento/division.py` |
| Resultado | `entrenamiento/division_task05.json` |
| Fecha | 28/10/2026 |

## 1. Criterio

- **Un caso del MSD = un paciente.** El conjunto no trae un identificador de paciente aparte y cada `prostate_XX` es un estudio distinto. En la tarea 1304 se comprobó que no hay dos casos con la misma imagen.
- Proporciones **70 / 15 / 15**, mezcla con **semilla 2026** (reproducible).
- Solo los 32 casos con máscara. Los 16 de `imagesTs` no entran.
- El archivo guarda una **huella SHA-256** de la división; `cargar_division` la recalcula y rechaza el archivo si alguien lo editó a mano.

## 2. Resultado

| Conjunto | Casos | Identificadores |
|---|---|---|
| Entrenamiento | 22 | 00, 01, 02, 06, 07, 10, 14, 16, 18, 20, 21, 24, 25, 31, 35, 37, 38, 40, 41, 42, 43, 46 |
| Validación | 5 | 04, 29, 32, 39, 47 |
| Prueba | 5 | 13, 17, 28, 34, 44 |

Huella: `728fae869f02e7c7587aab5081d7b12050dd92164c3d52f96c122cd97369da81`

## 3. Cómo regenerarla

```bash
python -m entrenamiento.division            # escribe entrenamiento/division_task05.json
```

Con los mismos 32 casos y la misma semilla se obtiene exactamente la misma división y la misma huella.

## 4. Observaciones

- El conjunto de prueba solo tiene 5 casos: las métricas del Sprint 5 tendrán una varianza alta. Por eso se propone reportar también la evaluación externa en Prostate158.
- `prostate_16` (volumen atípico de 315,4 ml) quedó en entrenamiento. `prostate_32` (sin TZ) quedó en validación. No afecta, porque la máscara se binariza.
