# Limitaciones del modelo y de la evaluación (Ciclo 3)

## 1. Posible solapamiento de datos con el modelo base (sobreestimación)

- Según su documentación (`configs/metadata.json`: `data_source` = «Prostate158 from 10.5281/zenodo.6481141»; `docs/README.md`: «trained in the prostate158 training data … Only T2w images»), el modelo se entrenó con Prostate158 (Charité, Berlín). MSD Task05 procede de Radboud UMC (Nijmegen). La documentación no menciona Task05 ni como entrenamiento ni como validación.
- **No hay evidencia de solapamiento, pero tampoco se puede descartar:** el bundle no publica la lista de casos ni las semillas, y no se puede verificar con los datos disponibles.
- La división 22/5/5 de este proyecto es independiente de la de los autores: los 5 casos de prueba no son «no vistos» por construcción, solo lo son si Task05 nunca entró al entrenamiento del modelo base.
- Si hubiera solapamiento, el Dice 0,8925 estaría **sobreestimado**. Por eso el resultado se presenta como evidencia de factibilidad, no como estimación de generalización.
- Relacionado (Ciclo 2): MSD y PROMISE12 comparten al menos un estudio (`prostate_16` = `Case23`); por eso no se combinan. Ese hallazgo no afecta al modelo base, pero muestra que los conjuntos públicos de próstata pueden reutilizar estudios.

## 2. Tamaño y alcance de la evaluación

- Solo 5 casos de prueba: la media tiene mucha incertidumbre (intervalo aproximado al 95 %: 0,85–0,93).
- Un solo conjunto público y un anotador por caso; no hay variabilidad entre observadores ni validación externa o clínica.
- Solo Dice e IoU; no se calculan métricas de superficie (Hausdorff, distancia media de superficie), que son más sensibles a errores en base y ápex.
- La evaluación formal y ampliada es del Ciclo 5 (H007).

## 3. Cambio de dominio

- Prostate158 (3 T, T2 de 0,47 × 0,47 × 3 mm) frente a Task05 (cortes de 3,0–4,0 mm, otro protocolo y escáner). El remuestreo a 0,5 mm interpola y no añade detalle.
- El modelo segmenta dos zonas (glándula central y periférica); aquí se usa solo la unión. Los criterios de delimitación de los anotadores pueden diferir, sobre todo en base y ápex.
- El posproceso conserva la mayor componente de cada zona: si el modelo marca una región falsa más grande que la zona real (caso `prostate_07` en el proyecto de referencia, Dice 0,23), la glándula se pierde. Mejora propuesta: ajuste fino con Task05 o preferir la componente más cercana al centro; si se adopta, aplicarla igual en entrenamiento, evaluación e inferencia.

## 4. Rendimiento

- Los tiempos y la memoria dependen del equipo (AMD Ryzen 5 5600G, 30,7 GiB, sin GPU). No representan otro hardware; en un equipo con 4 GiB de RAM libres o menos la inferencia podría no caber (pico ≈ 2 GiB).
- No se midió en GPU ni en Colab (no hay GPU en el equipo de medición).

## 5. Ajuste fino

- No se ejecutó el ajuste fino real (100 épocas): requiere GPU (Colab). Solo se comprobó que el flujo arranca con `--prueba-rapida` en CPU.
- Con 22 casos de entrenamiento, una mejora pequeña frente al preentrenado puede ser ruido.

## 6. Uso

Prosta-AI es académica y experimental. El modelo no está aprobado para uso clínico y sus autores lo excluyen expresamente para diagnóstico.
