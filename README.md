# TP-2
Problema o necesidad que se aborda

La aplicación busca resolver la necesidad de analizar los movimientos de una red de bicicletas públicas, como Ecobici, para conocer cuántos viajes salen y llegan a cada estación durante un período determinado. Los registros incompletos o inconsistentes pueden generar resultados incorrectos, por lo que es necesario validar los datos antes de procesarlos.

Usuarios y finalidad

El programa está dirigido a personas encargadas de supervisar y analizar el funcionamiento operativo de la red de bicicletas. Les permitirá consultar los movimientos registrados por estación y período, identificar la cantidad de salidas y llegadas y analizar el balance neto de cada estación.

Solución propuesta y operaciones

Se desarrollará una aplicación en Python que procese registros de viajes y permita:
-Validar los datos de los recorridos, rechazando aquellos que tengan fechas incompatibles o estaciones de origen o destino faltantes.
-Seleccionar los viajes cuyo inicio se encuentre dentro del período solicitado.
-Registrar las salidas y llegadas correspondientes a cada estación.
-Calcular el balance neto de cada estación, mediante la diferencia entre llegadas y salidas.
-Generar y exportar un reporte con los resultados obtenidos.

Resultados e interpretación

El programa producirá un reporte por estación que incluirá la cantidad de salidas, la cantidad de llegadas y el balance neto. Un balance positivo indica que se registraron más llegadas que salidas; uno negativo indica que hubo más salidas que llegadas; y un balance igual a cero indica que ambas cantidades fueron iguales.
Este resultado representa únicamente el balance de movimientos registrados durante el período y no la cantidad de bicicletas disponibles en la estación.

Alcance de la primera versión

La primera versión trabajará con los datos de los viajes, incluyendo su identificador, fecha y hora de inicio y fin, y estaciones de origen y destino. La selección de viajes se realizará según su fecha y hora de inicio, contabilizando tanto la salida como la llegada de cada viaje seleccionado.

Quedarán fuera del alcance la consulta de datos en tiempo real, la actualización automática de la información de Ecobici, el cálculo del inventario de bicicletas disponibles, las reposiciones de bicicletas y la construcción de una interfaz gráfica compleja. El objetivo será desarrollar un producto pequeño, funcional y verificable mediante pruebas con datos de ejemplo.

Ningún registro se descarta en silencio
. Todo viaje rechazado se aísla junto con su motivo explícito de rechazo para que el equipo operativo pueda auditar el origen de la falla
