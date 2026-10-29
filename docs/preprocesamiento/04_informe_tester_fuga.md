# Informe del Tester: verificación de pacientes repetidos (tarea 1304)

| Campo | Valor |
|---|---|
| Sprint | 2 |
| Responsable | Fernando José Angulo Núñez (Tester, Planeación) |
| Objeto verificado | `entrenamiento/division_task05.json` (huella `728fae86…69da81`) |
| Herramientas | `scripts/verificar_fuga.py`, `tests/test_division.py` |
| Fecha | 29/10/2026 |
| Veredicto | **APROBADO: no hay pacientes repetidos entre entrenamiento, validación y prueba** |

## 1. Verificaciones realizadas

| # | Verificación | Resultado |
|---|---|---|
| V1 | Cada identificador aparece en un solo conjunto; ningún conjunto vacío | OK: 22 / 5 / 5 |
| V2 | La huella SHA-256 del archivo coincide con su contenido | OK |
| V3 | La división cubre exactamente los 32 casos con máscara del MSD (ni faltan ni sobran) | OK |
| V4 | **Por contenido**: hash del volumen T2 de cada caso; ningún par de conjuntos distintos comparte imagen | OK: 32 imágenes distintas en 32 casos |
| V5 | Reproducibilidad: misma semilla, misma división | OK (prueba automatizada) |
| V6 | Las pruebas detectan una fuga provocada (caso copiado de entrenamiento a prueba) y un archivo editado a mano | OK |
| V7 | Cruce con conjuntos externos (misma geometría y volumen de próstata con diferencia ≤ 0,5 ml) | Ver sección 2 |

## 2. Hallazgo: casos del MSD presentes en PROMISE12

| Caso MSD | Conjunto en la división | Probable duplicado | Volumen |
|---|---|---|---|
| `prostate_16` | entrenamiento | PROMISE12 `Case23` | 315,4 ml (idéntico) |
| `prostate_01` | entrenamiento | PROMISE12 `Case14` | ≈ 71,6 ml |
| `prostate_17` | **prueba** | PROMISE12 `Case20` | ≈ 34,5 ml |
| `prostate_44` | **prueba** | PROMISE12 `Case19` | ≈ 43,9 ml |

**Implicación:** si se entrenara con PROMISE12, dos casos de prueba (`prostate_17`, `prostate_44`) habrían sido vistos en el entrenamiento. Eso sería fuga y daría métricas infladas.

**Decisión registrada (con el Analista y el Director):** PROMISE12 **no** se usa para entrenar ni validar mientras se use el MSD como conjunto de prueba. Esto ya estaba en la tarea 1202 por licencia y ahora queda confirmado también por fuga.

Prostate158: 0 coincidencias con el MSD (otro centro), así que se puede usar como evaluación externa sin riesgo de fuga.

## 3. Pruebas automatizadas

```
$ python -m pytest -q
.....................                                                    [100%]
21 passed
```

| Archivo | Pruebas | Qué cubre |
|---|---|---|
| `tests/test_division.py` | 9 | Proporciones, reproducibilidad, fuga, cobertura y huella |
| `tests/test_control_calidad.py` | 7 | QC-1 a QC-6, incluido el archivo truncado (defecto corregido el 28/10) |
| `tests/test_transformaciones.py` | 5 | Espaciado, RAS, z-score, máscara binaria, conservación del volumen y script completo |

## 4. Condición para próximas integraciones

Toda solicitud de *pull request* que modifique `entrenamiento/division_task05.json`, `entrenamiento/division.py` o `preprocesamiento/` debe:

1. Pasar `python -m pytest`.
2. Pasar `python scripts/verificar_fuga.py`, que debe terminar con código 0.
3. Contar con la revisión del Tester.
