# Documentación del Conjunto de Datos: Usuarios Ecobici

## 1. Origen y procedencia
- **Conjunto de datos:** Usuarios de Ecobici (2024)
- **Organismo responsable:** Secretaría de Transporte y Obras Públicas. Jefatura de Gabinete de Ministros
- **Fuente primaria:** Secretaría de Transporte y Obras Públicas. Jefatura de Gabinete de Ministros (Gobierno de la Ciudad de Buenos Aires - Buenos Aires Data)
- **Licencia:** Creative Commons Atribución 2.5 Argentina (CC-BY-2.5-AR)
- **Fecha de publicación original:** 10 de Mayo de 2021
- **Fecha de última actualización:** 8 de Octubre de 2026
- **Frecuencia de actualización:** Mensualmente

## 2. Unidad de análisis
Cada fila o registro representa el **alta/registro de un usuario individual** en el sistema de transporte público de bicicletas (Ecobici).

## 3. Diccionario de variables
- `id_usuario` (Numérico entero): Identificador único asignado al usuario en el sistema.
- `genero_usuario` (Texto / Categórico): Género consignado por el usuario al registrarse (`MALE`, `FEMALE`, `OTHER`).
- `edad_usuario` (Numérico entero): Edad del usuario en años al momento de registrarse.
- `fecha_alta` (Fecha / Texto): Fecha en la que se generó el alta del usuario, bajo el formato estándar `AAAA-MM-DD`.
- `hora_alta` (Tiempo / Texto): Hora, minutos y segundos exactos en que se registró el alta, bajo el formato `HH:MM:SS`.

## 4. Limitaciones, sesgos y consideraciones
- **Datos no sensibles:** Los datos se encuentran anonimizados bajo un identificador numérico (`id_usuario`), sin nombres, documentos ni datos de contacto personales.
- **Calidad y validaciones:** Pueden existir inconsistencias en el campo `edad_usuario` (valores nulos o edades biológicamente atípicas) que requieren validación y filtrado.
- **Volumen y muestra:** Al ser un archivo anual extenso, para el repositorio y las pruebas de ejecución reproducible se conserva una muestra que supera ampliamente las 50 observaciones mínimas requeridas por la consigna.