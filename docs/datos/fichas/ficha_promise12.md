# Ficha de conjunto de datos: PROMISE12

| Campo | Valor |
|---|---|
| Nombre | PROMISE12 – Prostate MR Image Segmentation 2012 |
| Rol en Prosta-AI | **Referencia local**: no se usa para entrenar ni se redistribuye |
| Fuente | https://promise12.grand-challenge.org/ (requiere cuenta y aceptar los términos del reto) |
| Origen | Cuatro centros (Radboud UMC Nijmegen, Haukeland Bergen, Beth Israel Boston, UCL Londres) |
| Contenido | 50 casos de entrenamiento con máscara de glándula completa (`CaseXX_segmentation`) y 30 de prueba sin máscara |
| Formato | MetaImage (`.mhd` + `.raw`) |
| Tamaño | 200 archivos de entrenamiento, 750,1 MiB |
| Licencia | Términos de uso del reto: solo investigación, **sin redistribución**, citar el artículo |
| Desidentificación | De origen; verificada en la tarea 1205 (0 hallazgos en cabeceras `.mhd`) |
| Responsable de la ficha | Juan David Riascos Erazo · 18/10/2026 |

## Restricciones

- No se suben al repositorio ni la descarga ni archivos derivados (máscaras, volúmenes convertidos).
- **Pacientes compartidos con el MSD**: el MSD Task05 también proviene de Radboud. En la tarea 1206 se identificó `prostate_16` (MSD) ≡ `Case23` (PROMISE12). Mezclar ambos conjuntos produciría fuga entre entrenamiento y prueba (riesgo 4 del Acta).

## Cita

Litjens, G., Toth, R., van de Ven, W. et al. Evaluation of prostate segmentation algorithms for MRI: the PROMISE12 challenge. *Medical Image Analysis* 18(2), 359–373 (2014). https://doi.org/10.1016/j.media.2013.12.002
