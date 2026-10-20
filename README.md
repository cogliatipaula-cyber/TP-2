# Trabajo Práctico N.º 2: Aplicación de Procesamiento de Datos de Ecobici

**Materia:** Programación de Datos en Python  
**Autora:** Paula Cogliati 

---

## Problema o necesidad que se aborda

La aplicación busca resolver la necesidad de analizar los movimientos de una red de bicicletas públicas, como Ecobici, para conocer cuántos viajes salen y llegan a cada estación durante un período determinado. Los registros incompletos o inconsistentes pueden generar resultados incorrectos, por lo que es necesario validar los datos antes de procesarlos.

## Usuarios y finalidad

El programa está dirigido a personas encargadas de supervisar y analizar el funcionamiento operativo de la red de bicicletas. Les permitirá consultar los movimientos registrados por estación y período, identificar la cantidad de salidas y llegadas y analizar el balance neto de cada estación.

## Fuente de datos, licencia y unidad de análisis

* **Fuente de datos:** Muestras tabulares en formato CSV y JSON estructuradas a partir de la inspiración del dataset abierto de bicicletas públicas del Gobierno de la Ciudad de Buenos Aires ([BA Data - Ecobici](https://data.buenosaires.gob.ar/dataset/estaciones-bicicletas-publicas)).
* **Licencia:** Datos de dominio público / acceso abierto para uso educativo.
* **Unidad de análisis:** El **`Viaje`** (recorrido individual realizado por un usuario entre una estación de origen y una de destino con sellos de fecha/hora de inicio y fin).

## Organización del código

El proyecto está estructurado en módulos y carpetas funcionales para mantener el código ordenado y mantenible:

La carpeta `data` contiene las fuentes de datos de entrada en formato CSV (`ecobici-movimientos.csv`) y JSON (`ecobici-movimientos.json`), acompañadas por un archivo `README.md` interno que describe el formato de las muestras.

La carpeta `src` alberga la lógica principal del programa. Dentro de ella, el archivo `fuentes.py` define la abstracción base y las clases encargadas de la lectura de archivos, mientras que `pipeline.py` implementa la clase `Viaje`, las funciones de validación, filtrado por fecha y el cálculo de balances operativos por estación.

La carpeta `tests` resguarda la suite de pruebas unitarias automatizadas (`test_pipeline.py`) desarrolladas con el módulo `unittest` para verificar el correcto funcionamiento del sistema.

La carpeta `outputs` almacena los archivos generados automáticamente por la aplicación, incluyendo `reporte_balance.csv` con el resumen consolidado por estación y `rechazos.csv` con las filas descartadas y sus motivos de auditoría.

En la raíz del proyecto se encuentra el archivo `run.py`, que actúa como el punto de entrada ejecutable que coordina todo el flujo. Además, se incluye el archivo `.gitignore` para evitar la subida de archivos temporales de Python, el archivo `requirements.txt` que detalla las dependencias (Biblioteca Estándar de Python) y este archivo `README.md` con la documentación general.

## Limitaciones

* El reporte producido representa únicamente el balance de los movimientos registrados dentro de las muestras procesadas y no refleja la cantidad ni el stock total de bicicletas físicas disponibles en cada estación.
* La aplicación procesa archivos de forma local y batch, por lo que no realiza consultas en tiempo real ni actualizaciones automáticas a través de servicios externos.
* Quedan fuera del alcance la gestión de logística de rebalanceo de flota mediante camiones de traslado y la construcción de interfaces gráficas de usuario.

## Manual simple para el usuario

### 1. Requisitos previos
Para utilizar esta aplicación solo necesitás tener instalado **Python 3** en tu computadora. No hace falta instalar librerías externas ni configurar entornos virtuales complejos, ya que el programa funciona exclusivamente con la biblioteca estándar de Python.

### 2. Cómo ejecutar la aplicación
1. Abrí la terminal o consola de comandos de tu sistema operativo.
2. Navegá hasta la carpeta raíz del proyecto (`TP-2`).
3. Ejecutá el siguiente comando:

```powershell
py run.py

3. Qué esperar al ejecutar
En la consola: Verás una tabla comparativa limpia con el nombre de cada estación, su cantidad de salidas, llegadas y el balance neto final (llegadas - salidas), seguida de la verificación automatizada que confirma que la suma global de balances en la red es igual a cero.
En la carpeta outputs: Se generarán o actualizarán automáticamente dos archivos CSV:
outputs/reporte_balance.csv: Contiene el reporte consolidado listo para abrir en Excel o compartir.
outputs/rechazos.csv: Muestra los registros que tenían errores en los datos originales, indicando la fila y la causa explícita del descarte.

4. Cómo ejecutar las pruebas automatizadas
Si querés verificar que el código funciona correctamente y cumple con todos los controles de calidad, podés correr la suite de tests ejecutando:
py -m unittest discover -s tests
Si todo está en orden, la terminal te devolverá un mensaje indicando que se ejecutaron los 6 tests con resultado OK.