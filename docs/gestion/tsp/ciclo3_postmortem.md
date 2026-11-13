# Postmortem del Ciclo 3: segmentación 3D, modelo e inferencia

| Campo | Valor |
|---|---|
| Ciclo | 3 · 31/10/2026 – 12/11/2026 (plan: 13/11) · se cierra con `v0.3-ciclo3` |
| Reunión de postmortem | 12/11/2026, con todo el equipo, junto con el del Ciclo 4 |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |

## 1. Resultado

Las 9 tareas (1401–1409) se completaron. **Valor ganado: 100 %**.

| Tarea | Plan | Real | Resultado |
|---|---|---|---|
| 1401 | 2 h | 2 h | Paquete `prosta_ai` importable desde pytest; torch 2.5.1 y MONAI 1.4.0 |
| 1402 | 12 h | 14 h | Cadena en `backend/prosta_ai/pipeline/` (Template Method + Strategy) |
| 1403 | 8 h | 9 h | `entrenar.py`, cuaderno de Colab y `descargar_modelo.py` (SHA-256 verificado) |
| 1404 | 8 h | 8 h | 30 pruebas nuevas (métricas, preparación, segmentación) |
| 1405 | 6 h | 6 h | Informe `reports/evaluacion/evaluacion_prostate_mri_anatomy_2026-11-12` |
| 1406 | 5 h | 6 h | `docs/modelo/` (ficha, configuración, resultados, limitaciones) |
| 1407 | 3 h | 3,5 h | Prueba rápida en CPU: 1 época, Dice de validación 0,26 (solo verifica que corre) |
| 1408 | 4 h | 4 h | `reports/inferencia/medicion_1408_2026-11-12` |
| 1409 | 3 h | 3,5 h | README e integración |
| **Total** | **51 h** | **56 h** | |

**Desviación de esfuerzo: +9,8 %**, frente a +12,5 % en el ciclo anterior.

| Integrante | Plan | Real |
|---|---|---|
| Yeison | 26 h | 29 h |
| Juan | 11 h | 12 h |
| Fernando | 11 h | 11,5 h |
| Yimis | 3 h | 3,5 h |
| Sergio | 0 h | 0 h |

La mayor desviación fue 1402 (+2 h): adaptar la preparación al espacio RAS y quitar las dependencias de configuración. Las 1,5 h de espera de cómputo de 1408 se registran aparte.

## 2. Resultados técnicos

| Indicador | Resultado | Meta | Estado |
|---|---|---|---|
| Dice medio, 5 casos de prueba | **0,8925 ± 0,0340** | ≥ 0,80 | Cumple |
| IoU medio | 0,8071 ± 0,0534 | Se informa | — |
| Peor caso de Dice | prostate_28: 0,8320 | ≥ 0,80 | Cumple |
| Tiempo por estudio en CPU, en frío | 12,9 – 25,0 s | ≤ 120 s | Cumple |
| Memoria pico | 1736 – 2276 MiB | — | — |

Equipo de medición: AMD Ryzen 5 5600G, 30,7 GiB de RAM, sin GPU. Decisión sobre el riesgo 1: **no hace falta Colab para inferir**; Colab queda solo para el ajuste fino.

Decisión de modelo: se usa `prostate_mri_anatomy` 0.3.6 sin ajuste. El ajuste fino está preparado, pero solo se adopta si supera 0,8925 en el mismo conjunto de prueba.

## 3. Defectos

| ID | Tipo | Introducido | Detectado | Corrección |
|---|---|---|---|---|
| D-05 | 80 Función | DIS (1403, configuración de `--prueba-rapida`) | EJE (1407) | ~20 min |
| D-06 | 10 Documentación | IMP (1405, `evaluar.py`) | REV (informe) | ~5 min |

- D-05: con ventana de 32 vóxeles la UNet de 5 niveles daba siempre Dice de validación 0, así que la prueba rápida no habría detectado una validación rota. Se sube a 64.
- D-06: el informe mostraba «-0.0000» como diferencia frente a la referencia. Se redondea antes de formatear.
- Observación de proceso: el primer informe de evaluación se generó antes de correr pytest. Se regeneró después de 69/69 en verde, como pedía la mejora del Ciclo 2.
- Defectos abiertos al cierre: **0**.

## 4. Calidad

| Criterio del lanzamiento | Resultado |
|---|---|
| Pruebas de métricas antes del informe | Sí (D-06 es de formato, no de cálculo) |
| Pruebas automatizadas | 69 de 69 en verde |
| Conjunto de prueba fuera del entrenamiento | Sí: división del Ciclo 2 (huella `728fae86…`) verificada por el cuaderno |
| Defectos abiertos al cierre | 0 |

## 5. Lecciones aprendidas

1. Un modelo preentrenado con licencia clara redujo el riesgo del ciclo: el Entregable 4 no depende de conseguir GPU.
2. Una «prueba rápida» también se tiene que probar: si siempre da 0, no detecta nada (D-05).
3. Medir temprano (1408) cerró el riesgo 1 del Acta con datos y no con supuestos.

## 6. Mejoras para el Ciclo 4

| Mejora | Responsable |
|---|---|
| Probar la ROI con la máscara **predicha** y no solo con la de referencia | Juan |
| Mantener el aviso no clínico en una sola constante | Yeison |
| Registrar las horas reales el mismo día | Todos |
