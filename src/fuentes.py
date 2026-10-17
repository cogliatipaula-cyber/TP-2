# src/fuentes.py
from abc import ABC, abstractmethod
import csv
import json
import os

# Estructura tabular definida y requerida para el problema
CAMPOS_REQUERIDOS = (
    "id_viaje",
    "fecha_inicio",
    "fecha_fin",
    "id_estacion_origen",
    "nombre_estacion_origen",
    "id_estacion_destino",
    "nombre_estacion_destino",
    "duracion_segundos",
)


class FuenteDatos(ABC):
  """Contrato base para cualquier fuente de datos del flujo."""

  @abstractmethod
  def cargar(self, ruta: str) -> list[dict]:
    """Lee el archivo, valida su estructura definida y retorna una lista de diccionarios."""
    pass

  def verificar_estructura(self, campos_encontrados: set) -> None:
    """Verifica que el archivo contenga todos los campos obligatorios."""
    faltantes = set(CAMPOS_REQUERIDOS) - set(campos_encontrados)
    if faltantes:
      raise ValueError(
          f"Estructura inválida. Faltan las siguientes columnas obligatorias:"
          f" {sorted(list(faltantes))}"
      )


class FuenteCSV(FuenteDatos):
  """Lector de datos tabulares en formato CSV."""

  def cargar(self, ruta: str) -> list[dict]:
    if not os.path.exists(ruta):
      raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    with open(ruta, mode="r", encoding="utf-8") as archivo:
      lector = csv.DictReader(archivo)

      # Validar que los encabezados existan y cumplan la estructura definida
      if not lector.fieldnames:
        raise ValueError(
            f"El archivo CSV '{ruta}' está vacío o no tiene encabezados."
        )

      self.verificar_estructura(set(lector.fieldnames))

      return list(lector)


class FuenteJSON(FuenteDatos):
  """Lector de datos tabulares en formato JSON."""

  def cargar(self, ruta: str) -> list[dict]:
    if not os.path.exists(ruta):
      raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    with open(ruta, mode="r", encoding="utf-8") as archivo:
      datos = json.load(archivo)

    if not isinstance(datos, list) or len(datos) == 0:
      raise ValueError(
          f"El archivo JSON '{ruta}' debe ser una lista con registros."
      )

    # Validar que los objetos cumplan con la estructura definida (inspección del primer registro)
    primer_registro = datos[0]
    if not isinstance(primer_registro, dict):
      raise ValueError("Los elementos del JSON deben ser objetos/diccionarios.")

    self.verificar_estructura(set(primer_registro.keys()))

    return datos