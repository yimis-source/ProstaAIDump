# LOGD: registro de defectos

| Campo | Valor |
|---|---|
| Responsable | Fernando José Angulo Núñez (Gerente de planeación) |
| Reportan | Todos los integrantes, el mismo día en que encuentran el defecto |

Tipos de defecto (TSP): 10 Documentación · 20 Sintaxis · 30 Construcción · 40 Asignación · 50 Interfaz · 60 Verificación · 70 Datos · 80 Función · 90 Sistema · 100 Entorno.

Fases: REQ requisitos · DIS diseño · IMP implementación · REV revisión · EJE ejecución · PU prueba unitaria · INT integración.

| ID | Fecha | Ciclo | Tipo | Introducido en | Detectado en | Detectó | Corrigió | Tiempo de corrección | Descripción | Corrección | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D-01 | 15/10 | 1 | 10 Documentación | REQ (1201) | REV | Fernando | Juan | 20 min | Los criterios de selección no excluían estudios duplicados entre conjuntos | Se agrega el criterio CE-3 (commit «añadir criterio de exclusión de duplicados entre conjuntos») | Cerrado |
| D-02 | 21/10 | 1 | 70 Datos | IMP (1205) | EJE | Fernando | Fernando | 35 min | La verificación de anonimización revisaba la carpeta local `convertidas/` de PROMISE12 y dio 100 falsos positivos | Se excluyen carpetas locales y archivos `._*` (commit «excluir la carpeta local de conversiones de PROMISE12») | Cerrado |
| D-03 | 21/10 | 1 | 50 Interfaz | IMP (1206) | EJE | Yeison | Yeison | 10 min | `analizar_geometria.py` llamaba a un método inexistente de SimpleITK (`GetOrientationFromDirection`) | Se usa `DICOMOrientImageFilter.GetOrientationFromDirectionCosines`; corregido antes del commit | Cerrado |

## Resumen

| Ciclo | Defectos | Introducidos en REQ / IMP | Detectados antes de integrar | Abiertos |
|---|---|---|---|---|
| 1 | 3 | 1 / 2 | 3 | 0 |
