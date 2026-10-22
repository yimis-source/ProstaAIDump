# Lanzamiento del Ciclo 1: adquisición y comprensión de datos

| Campo | Valor |
|---|---|
| Ciclo | 1 · 13/10/2026 – 25/10/2026 · hito H003 |
| Reunión de lanzamiento | 13/10/2026, con todo el equipo |
| Elaboró | Fernando José Angulo Núñez (Gerente de planeación) |
| Aprobó | Yimis Buenaventura (Líder del equipo) |

## 1. Objetivos del ciclo

1. Definir qué estudios sirven y elegir los conjuntos de datos públicos (uno principal y uno de respaldo).
2. Verificar licencias y anonimización antes de trabajar con los datos.
3. Conocer los datos: tamaños, espaciado, orientación y número de casos, más una revisión visual.
4. Entregar el informe de datos y cerrar con la etiqueta `v0.1-ciclo1`.

## 2. Plan de tareas

| Tarea | Descripción | Responsable | Horas plan | Fecha plan |
|---|---|---|---|---|
| 1201 | Criterios de selección de estudios | Juan | 4 | 14/10 |
| 1202 | Elegir conjuntos públicos y uno de respaldo | Juan | 6 | 17/10 |
| 1203 | Fichas de licencia por conjunto | Juan | 4 | 18/10 |
| 1204 | Descarga, organización e inventario | Yeison | 6 | 20/10 |
| 1205 | Verificación de anonimización en metadatos | Fernando | 6 | 21/10 |
| 1206 | Análisis de tamaños, espaciado y casos | Juan (análisis 4) + Yeison (script 4) | 8 | 22/10 |
| 1207 | Revisión de muestras en 3D Slicer | Sergio (3) + Juan (3) | 6 | 23/10 |
| 1208 | Informe de datos | Juan | 5 | 23/10 |
| 1209 | Integración y etiqueta `v0.1-ciclo1` | Yimis | 2 | 25/10 |
| — | Coordinación y revisión de PR | Yimis | 4 | continuo |
| | **Total** | | **51** | |

Horas plan por integrante: Juan 26, Yeison 10, Yimis 6, Fernando 6, Sergio 3.

## 3. Plan de calidad

| Criterio | Meta |
|---|---|
| Revisión | Cada PR revisado por un rol distinto al autor |
| Privacidad | 0 hallazgos de datos personales antes de integrar datos (tarea 1205) |
| Datos en Git | Ningún volumen versionado (`.gitignore`) |
| Reproducibilidad | Toda cifra del informe sale de un script versionado con su CSV |
| Defectos | Todo defecto encontrado se anota en el LOGD el mismo día |

## 4. Riesgos del ciclo

| Riesgo | Respuesta |
|---|---|
| Licencias que impidan publicar derivados | Fichas antes de usar los datos; los datos no se suben |
| Descargas grandes (> 2 GiB) | El conjunto de respaldo es opcional; la descarga es reproducible por script |
| Datos con información personal | Verificación automática antes de cualquier uso |
| Curva de aprendizaje con imágenes médicas | Revisión en 3D Slicer en pareja (Sergio y Juan) |
