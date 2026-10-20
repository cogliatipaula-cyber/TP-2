# Documentación Técnica del Código Fuente (`src/`)

Este directorio contiene la lógica nuclear de la aplicación de procesamiento de datos de Ecobici. El código está diseñado siguiendo principios de programación orientada a objetos (POO), modularidad y responsabilidad única.

---

## 1. Solución Propuesta y Operaciones

La solución se compone de un pipeline reproducible que realiza las siguientes operaciones:

1. **Lectura e Ingesta Polimórfica:** Ingesta registros de movimientos desde archivos CSV o JSON garantizando una estructura de campos homogénea.
2. **Validación Sintáctica y Semántica:** Filtra cada fila verificando formato de identificadores, coherencia de fechas en el calendario, secuencia temporal y completitud de datos.
3. **Aislamiento de Rechazos:** Separa los viajes no válidos y genera un registro de auditoría con la causa explícita del descarte.
4. **Instanciación del Modelo de Dominio:** Transforma los registros válidos en objetos de la clase `Viaje`.
5. **Filtrado por Período Operativo:** Permite seleccionar viajes cuya fecha/hora de inicio corresponda a un rango específico.
6. **Cálculo de Balances Operativos:** Consolida las salidas y llegadas por estación para determinar el flujo neto (`balance = llegadas - salidas`).
7. **Verificación de Invariante (Conservación de Red):** Evalúa que la suma global de los balances netos en la red sea estrictamente cero.
8. **Exportación de Reportes:** Escribe los resultados procesados en la carpeta `outputs/`.

---

## 2. Arquitectura de Módulos y Clases

### `src/fuentes.py` — Abstracción de Fuentes de Datos
Implementa la jerarquía de clases para la lectura e ingesta de archivos:

* **`FuenteDatos` (Clase Abstracta / ABC):** Define la interfaz común mediante el método abstracto `@abstractmethod def cargar(self, ruta_archivo)`. Incluye la función auxiliar `verificar_estructura()` para validar la presencia de los campos requeridos antes de procesar el archivo.
* **`FuenteCSV` (Clase Concreta):** Utiliza `csv.DictReader` para procesar archivos tabulares CSV codificados en UTF-8.
* **`FuenteJSON` (Clase Concreta):** Emplea `json.load()` para deserializar colecciones de objetos JSON.

---

### `src/pipeline.py` — Modelo de Dominio y Pipeline de Procesamiento

#### Clase `Viaje`
Modela la unidad fundamental del análisis. Encapsula los atributos del recorrido (`id_viaje`, `fecha_inicio`, `fecha_fin`, `id_estacion_origen`, `nombre_estacion_origen`, `id_estacion_destino`, `nombre_estacion_destino`).

**Métodos destacados:**
* `duracion_segundos()`: Calcula la diferencia en segundos entre `fecha_fin` y `fecha_inicio`.
* `duracion_minutos()`: Devuelve la duración expresada en minutos (`float`).
* `es_viaje_circular()`: Retorna `True` si la estación de origen y destino son la misma.

#### Funciones Principales
* `validar_recorrido(fila)`: Evalúa una fila individual y devuelve `(es_valido, motivo_error, objeto_viaje)`.
* `validar_recorridos(filas)`: Procesa la lista completa de registros, retornando la tupla `(viajes_validos, rechazados)`.
* `filtrar_por_periodo(viajes, inicio, fin)`: Filtra la lista de objetos `Viaje` dentro del rango temporal.
* `generar_balance(viajes)`: Construye un diccionario acumulador por estación con conteo de salidas, llegadas y balance neto.
* `verificar_conservacion_red(balance)`: Comprueba que la suma de balances de toda la red sea igual a `0`.
* `exportar_reporte_csv(balance, ruta)` y `exportar_rechazos_csv(rechazados, ruta)`: Manejan la salida en disco.

---

## 3. Decisiones de Limpieza, Validaciones y Supuestos

### Expresiones Regulares (`re`)
Se definieron patrones compilados al inicio del módulo:
* **`PATRON_ID_VIAJE = re.compile(r"^ECO-\d{4}$")`**: Garantiza que el identificador del viaje respete la máscara estándar (`ECO-` seguido de exactamente 4 dígitos).
* **`PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")`**: Verifica la estructura sintáctica de fecha y hora (`YYYY-MM-DD HH:MM:SS`).

### Validación de Calendario (Complemento a la Regex)
Debido a que una expresión regular no puede verificar si un día existe en el calendario real (por ejemplo, aceptaría sintácticamente `"2024-04-31"`), la regex se complementa con `datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")`. Si la fecha es inexistente, Python lanza un `ValueError` que es capturado limpiamente para clasificar el registro como rechazado por fecha fuera de rango.

### Inconsistencias Temporales
Se valida que `fecha_fin >= fecha_inicio`. Si la fecha de finalización es anterior a la de partida, se registra el motivo `"Inconsistencia temporal: fecha_fin es anterior a fecha_inicio"`.

### Campos Obligatorios
Se comprueba que los identificadores y los nombres de las estaciones de origen y destino no estén vacíos o compuestos únicamente por espacios.

### Política de Transparencia (Sin Descarte Silencioso)
Ninguna fila defectuosa se elimina sin dejar traza. Todas las filas no válidas se guardan junto con el diccionario original y el mensaje de error explicativo para permitir su auditoría posterior.