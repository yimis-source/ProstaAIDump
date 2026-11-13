"""Cadena de segmentación 3D de Prosta-AI (Ciclo 3, Entregable 4).

Módulos:

- `io`: lectura de NIfTI/DICOM y escritura de NIfTI (patrón Adapter).
- `validators`: control de calidad del volumen leído (Chain of Responsibility).
- `preparation`: transformaciones del modelo, idénticas en entrenamiento e inferencia (RF-09).
- `segmentation`: estrategias de segmentación intercambiables (Strategy + Factory Method).
- `evaluation`: métricas Dice e IoU.
- `base`: orden fijo de las etapas (Template Method).
- `factory`: construcción del pipeline y datos del modelo.
- `progress`: avance y tiempos por etapa (Observer).

La región de interés (ROI) y el paso de la máscara a la rejilla original son del Ciclo 4.
"""
