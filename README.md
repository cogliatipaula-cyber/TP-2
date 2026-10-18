# Trabajo Práctico N.º 2: Aplicación de Procesamiento de Datos de Ecobici

**Materia:** Programación de Datos en Python  
**Autora:** Paula Cogliati  

---

## 1. Problema o necesidad que se aborda

La aplicación busca resolver la necesidad de analizar los movimientos de una red de bicicletas públicas (como Ecobici) para conocer cuántos viajes salen y llegan a cada estación durante un período determinado. Los registros incompletos o inconsistentes pueden generar resultados incorrectos, por lo que es necesario validar los datos antes de procesarlos.

## 2. Usuarios y finalidad

El programa está dirigido a personas encargadas de supervisar y analizar el funcionamiento operativo de la red de bicicletas. Les permitirá consultar los movimientos registrados por estación y período, identificar la cantidad de salidas y llegadas y analizar el balance neto de cada estación.

## 3. Fuente de datos, licencia y unidad de análisis

* **Fuente de datos:** Muestras tabulares en formato CSV (`data/ecobici-movimientos.csv`) y JSON (`data/ecobici-movimientos.json`) basadas en registros de uso público del sistema Ecobici.
* **Licencia:** Datos de dominio público / acceso abierto para fines educativos.
* **Unidad de análisis:** El **`Viaje`** (recorrido individual realizado por un usuario entre una estación de origen y una de destino con sello de fecha/hora de inicio y fin).

## 4. Solución propuesta y operaciones

Se desarrolló una aplicación en Python que procesa registros de viajes y permite:
* **Validar los datos de los recorridos:** Rechaza registros con formatos inválidos, fechas imposibles en el calendario, inconsistencias temporales o extremos faltantes.
* **Seleccionar viajes por período:** Filtra los recorridos cuyo inicio se encuentre dentro del rango solicitado.
* **Registrar salidas y llegadas:** Contabiliza los movimientos correspondientes a cada estación.
* **Calcular el balance neto:** Evalúa la diferencia entre llegadas y salidas (`balance = llegadas - salidas`).
* **Verificar invariantes del dominio:** Comprueba la conservación de la red (suma total de balances = 0).
* **Generar y exportar reportes:** Exporta los resultados analíticos a la carpeta `outputs/`.

## 5. Decisiones de limpieza, validaciones y supuestos

* **Expresiones Regulares (`re`):** Se utiliza `^ECO-\d{4}$` para validar la máscara de ID de viaje y `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$` para la estructura sintáctica de la fecha.
* **Validación de Calendario:** La sintaxis de fecha se complementa con `datetime.strptime` para detectar y descartar fechas inexistentes en el calendario real (ej. 31 de abril).
* **Inconsistencias Temporales:** Se valida estrictamente que la fecha de fin sea igual o posterior a la fecha de inicio (`fecha_fin >= fecha_inicio`).
* **Política de Transparencia (Sin descarte silencioso):** Ningún registro se descarta en silencio. Todo viaje rechazado se aísla en `outputs/rechazos.csv` detallando la fila original y el motivo explícito de la falla.

## 6. Organización del código

TP-2/
├── data/
│   ├── ecobici-movimientos.csv
│   ├── ecobici-movimientos.json
│   └── README.md
├── outputs/
│   ├── rechazos.csv
│   └── reporte_balance.csv
├── src/
│   ├── __pycache__/
│   ├── fuentes.py
│   └── pipeline.py
├── tests/
│   ├── __pycache__/
│   ├── __init__.py
│   └── test_pipeline.py
├── .gitignore
├── README.md
└── run.py

7. Ejemplo de resultados
Al ejecutar py run.py, la aplicación valida las fuentes, genera los archivos en outputs/ e imprime por consola el consolidado operativo:
======================================================================
REPORTE DE BALANCE OPERATIVO POR ESTACIÓN (CSV vs JSON)
======================================================================
Estación                        Salidas   Llegadas    Balance Neto
----------------------------------------------------------------------
Congreso                             2          2               0
Plaza Italia                         2          2               0
Plaza de Mayo                        2          2               0
----------------------------------------------------------------------
Verificación de conservación de red (Suma de balances): 0 [OK]
======================================================================


8. Interpretación del Balance: 

Un balance positivo indica que la estación recibió más bicicletas de las que salieron; un balance negativo indica mayor flujo de salida; y un balance igual a cero representa un estado de equilibrio operativo.

9. Conservación de la Red: 

La suma global de los balances netos de todas las estaciones es siempre igual a cero, reflejando que cada bicicleta que sale de un origen debe llegar a un destino.

10. Limitaciones: 

El reporte representa únicamente el balance de movimientos registrados en la muestra y no refleja el inventario total de bicicletas físicas disponibles. Quedan fuera del alcance las consultas en tiempo real y la gestión de logística de rebalanceo de flota.