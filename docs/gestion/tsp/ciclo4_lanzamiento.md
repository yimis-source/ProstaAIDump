# Lanzamiento del Ciclo 4: región de interés (ROI)

| Campo | Valor |
|---|---|
| Ciclo | 4 · plan 14/11/2026 – 20/11/2026 · **ejecutado de forma adelantada, en paralelo con el Ciclo 3, del 03/11 al 12/11/2026** · hito H006 · Entregable 5 |
| Reunión de lanzamiento | 03/11/2026, a mitad del Ciclo 3 (Yeison se incorpora el 08/11) |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |
| Aprobó | Yimis Buenaventura (Líder del equipo) |

## Decisión de adelantar el ciclo

El Ciclo 3 concentraba casi todo el trabajo en el Desarrollador (26 de 51 h). Los demás roles tenían capacidad libre: Sergio no tenía tareas de producto en el Ciclo 3, Juan no empezaba la evaluación (1405) hasta el 09/11 y Fernando podía escribir pruebas a partir de criterios antes de tener el código.

Como la ROI se puede especificar, diseñar y probar con las máscaras de referencia de Task05 sin esperar la inferencia final, el equipo decidió el 03/11 adelantar el Ciclo 4 en paralelo con el Ciclo 3, por etapas:

1. **Desde el 03/11, roles sin carga en el Ciclo 3:** Sergio diseña la presentación y los textos (1503); Juan fija los criterios de aceptación (1505, primera parte); Fernando escribe las pruebas a partir de esos criterios (1504, primera parte).
2. **Desde el 08/11, cuando Yeison termina 1403:** código de la ROI y de la superposición (1501, 1502).
3. **Al cierre del Ciclo 3 (11–12/11):** ROI con la máscara predicha (1507), verificación real (1505) y ejemplos (1506).

Aprobó: Yimis Buenaventura.

## 1. Objetivos del ciclo

1. Obtener la ROI a partir de la máscara del modelo, en el espacio de la imagen original: volumen, cortes con ROI, centroide y caja envolvente.
2. Superponer la ROI a la imagen según el diseño de la pantalla CU04 (Ciclo 2).
3. Acompañar cada resultado con una explicación, sus límites y el aviso de uso académico, experimental y no diagnóstico (Necesidades 3 y 4 del Acta).
4. Integrar la ROI como etapa de la cadena del Ciclo 3, sin API ni base de datos (Ciclo 6).
5. Cerrar con la etiqueta `v0.4-ciclo4`.

## 2. Plan de tareas

Factor 1,15 sobre la estimación base.

| Tarea | Descripción | Responsable | Horas plan | Fecha plan |
|---|---|---|---|---|
| 1501 | Cálculo de la ROI: vuelta al espacio original, binarización, volumen, centroide, caja y cortes | Yeison | 6 | 09/11 |
| 1502 | Superposición, figura «Original / Original + ROI» y script `generar_roi.py` | Yeison | 6 | 10/11 |
| 1503 | Presentación: colores, leyenda, textos de explicación, límites y aviso | Sergio | 6 | 05/11 |
| 1504 | Pruebas de ROI y visualización con volúmenes sintéticos | Fernando | 6 | 10/11 |
| 1505 | Criterios de aceptación de la ROI y verificación con casos reales | Juan | 5 | 11/11 |
| 1506 | Ejemplos documentados y README | Yimis | 2 | 12/11 |
| 1507 | Etapa ROI en la cadena y ROI con la máscara predicha del modelo | Yeison | 5 | 12/11 |
| | **Total** | | **36** | |

Horas plan por integrante: Yeison 17, Sergio 6, Fernando 6, Juan 5, Yimis 2.

## 3. Plan de calidad

| Criterio | Meta |
|---|---|
| Pruebas automatizadas | 100 % en verde antes de cada PR |
| Máscara vacía | Mensaje claro, sin error |
| Superposición | Conserva dimensiones y solo colorea vóxeles de la máscara |
| Aviso no clínico | Presente en toda figura y en todo texto de resultado |
| Verificación real | ROI con la máscara **predicha** en casos del conjunto de prueba (mejora del Ciclo 3) |
| Defectos abiertos al cierre | 0 |

## 4. Riesgos del ciclo

| Riesgo | Respuesta |
|---|---|
| ROI desalineada con la imagen (orientación o espaciado) | Volver al espacio original con la afín de la imagen; prueba de remuestreo |
| Cortes poco informativos en la figura | Elegir cortes por área de ROI, no los extremos |
| Que la ROI se lea como diagnóstico | Aviso fijo en la figura y explicación de límites |
| Ciclo adelantado y en paralelo con el Ciclo 3 | Arrancan primero los roles sin carga en el Ciclo 3; todo se prueba con máscaras de referencia; 1507 se integra cuando el Ciclo 3 cierra la inferencia |
| Sobrecarga de Yeison (tareas en los dos ciclos) | Yeison entra al Ciclo 4 solo después de 1403; Sergio, Juan y Fernando dejan listos diseño, criterios y pruebas |
| Pruebas escritas antes que el código | Fernando las ajusta tras integrar 1501–1502 (10/11) |
