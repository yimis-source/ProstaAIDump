# Verificación de anonimización en metadatos (tarea 1205)

| Campo | Valor |
|---|---|
| Sprint | 1 |
| Responsable | Fernando José Angulo Núñez (Tester) |
| Fecha | 21/10/2026 |
| Resultado | **Aprobado: 0 hallazgos en 1024 archivos** |

## 1. Alcance

Se verifican los metadatos de **todas** las imágenes y máscaras de los tres conjuntos descargados. El objetivo es asegurar que no contienen datos de persona, institución ni fechas (Ley 1581 de 2012, Decreto 1377 de 2013, criterio de éxito «cero datos personales» del Acta).

## 2. Método

Script reproducible: `scripts/verificar_anonimizacion.py`.

| Formato | Qué se revisa |
|---|---|
| NIfTI | Campos de texto libre de la cabecera: `descrip`, `aux_file`, `db_name`, `intent_name`. Además, la presencia de **extensiones de cabecera**, que podrían llevar un DICOM incrustado |
| MetaImage `.mhd` | Todas las claves; solo se aceptan las geométricas estándar (`DimSize`, `ElementSpacing`, `Offset`, `TransformMatrix`, …) |
| Nombres de archivo y carpetas | Deben ser identificadores neutros (`prostate_00`, `020`, `Case00`, `t2`, …) |

En el texto libre se buscan fechas (`aaaa-mm-dd`, `aaaammdd`), palabras como *patient*, *name*, *hospital*, *birth*, nombres de institución y el separador `^` típico de los nombres DICOM.

## 3. Resultados

| Conjunto | Archivos revisados | Con hallazgos |
|---|---|---|
| MSD_Task05 | 80 | 0 |
| Prostate158 | 844 | 0 |
| PROMISE12 | 100 (`.mhd`) | 0 |
| **Total** | **1024** | **0** |

Detalle: [anonimizacion.csv](anonimizacion.csv).

### Incidencia durante la verificación

En la primera ejecución aparecieron **100 hallazgos** de tipo «nombre no neutro `convertidas`». Venían de una carpeta local de conversiones de prueba dentro de `PROMISE12/training_data/`, no del conjunto. Se excluyó la carpeta y se volvió a ejecutar: 0 hallazgos.

## 4. Conclusiones

1. Los tres conjuntos llegan desidentificados de origen. Ninguna cabecera tiene extensiones ni texto libre con datos personales.
2. Los NIfTI no llevan fecha de adquisición ni institución. Que el MSD provenga de Radboud solo consta en `dataset.json`, que es documentación pública del conjunto y no un dato de paciente.
3. **Pendiente para la aplicación (Sprint 6):** los DICOM que suba un usuario sí pueden traer datos personales, así que hay que desidentificarlos al cargarlos. Queda registrado como requisito a probar.

## 5. Cómo repetir

```bash
python scripts/verificar_anonimizacion.py --datos datos --salida docs/datos/anonimizacion.csv
echo $?   # 0 = sin hallazgos, 1 = hay hallazgos
```
