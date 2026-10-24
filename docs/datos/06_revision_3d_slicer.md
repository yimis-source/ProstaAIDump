# Revisión visual de muestras en 3D Slicer (tarea 1207)

| Campo | Valor |
|---|---|
| Sprint | 1 |
| Revisores | Sergio Gabriel Meneses Silva (Diseñador), Juan David Riascos Erazo (Analista) |
| Herramienta | 3D Slicer 5.6 (módulos *Volumes*, *Segment Editor*, *Segment Statistics*) |
| Fecha | 23/10/2026 |

## 1. Muestra

Se eligieron casos que cubren los extremos encontrados en la tarea 1206, más uno típico de cada conjunto.

| Caso | Conjunto | Motivo de la elección |
|---|---|---|
| `prostate_00` | MSD | Caso típico (0,625 × 0,625 × 3,6 mm, 47,3 ml) |
| `prostate_07` | MSD | Volumen mínimo (16,0 ml) |
| `prostate_16` | MSD | Volumen máximo (315,4 ml); duplicado de PROMISE12 `Case23` |
| `prostate_18` | MSD | Máscara sin TZ y espaciado 0,75 × 0,75 × 4,0 |
| `prostate_32` | MSD | Máscara sin TZ |
| `020` | Prostate158 | Caso típico de otro centro (LPS, 0,4 mm en el plano) |
| `Case00` | PROMISE12 | Mayor resolución en el plano (512 × 512, 0,27 mm) |

## 2. Lista de verificación

| Verificación | Resultado |
|---|---|
| El volumen se abre sin errores y la máscara se superpone alineada | Sí, en los 7 casos |
| El MSD en Slicer muestra 2 volúmenes por caso (T2 y ADC) | Sí: hay que elegir el canal 0 para ver la T2 |
| La máscara cubre la glándula de la base al ápex | Sí. En los cortes extremos la delimitación es menos precisa, como es esperable con 3,6–4 mm entre cortes |
| `prostate_18` y `prostate_32` sin TZ | La glándula está completa con etiqueta 1. **No falta tejido**: toda la próstata se etiquetó como PZ. Binarizando, la máscara completa es válida |
| `prostate_16` | Hiperplasia evidente que ocupa casi todo el campo. La máscara es coherente con la imagen |
| Orientación | El MSD y Prostate158 se ven correctos en Slicer, que maneja RAS/LPS. Al exportar a NumPy, los ejes quedan invertidos entre conjuntos |
| Artefactos | Inhomogeneidad de campo (más brillo cerca de la bobina) en `prostate_07` y en `Case00`. Se recomienda normalizar intensidades y, opcionalmente, corrección N4 |
| Recorte | La glándula ocupa ~10–20 % del campo en x/y. Un recorte centrado reduciría el cómputo |

## 3. Observaciones para el diseño de la interfaz (Sprint 2)

- La T2 se ve bien en escala de grises con ventana entre los percentiles 1 y 99. Se adoptará esa ventana por defecto en el visor de la aplicación.
- La máscara se lee mejor como contorno o con relleno semitransparente (opacidad 0,4) en un color que no se confunda con la escala de grises.
- Con tan pocos cortes en z (11–24), el visor debe permitir moverse corte a corte en el plano axial. Las vistas sagital y coronal se ven muy pixeladas.

## 4. Evidencias

Las capturas de pantalla se guardan en la carpeta compartida del equipo (no en el repositorio, por la licencia y el tamaño). Los nombres siguen el formato `slicer_<caso>_<vista>.png`.
