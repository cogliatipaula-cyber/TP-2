"""src/pipeline.py.

Módulo de procesamiento, validación y métricas para el reporte operativo de
movimientos de Ecobici (TP2 - Problema 7).
"""

from collections import defaultdict
import csv
from datetime import datetime
import os
import re

# Expresiones regulares para validación de formato
PATRON_ID_VIAJE = re.compile(r"^ECO-\d{4}$")
PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


# =====================================================================
# 1. Clase del Dominio: Viaje
# =====================================================================
class Viaje:
  """Representa un recorrido individual en el sistema Ecobici (unidad de análisis)."""

  def __init__(
      self,
      id_viaje: str,
      fecha_inicio: datetime,
      fecha_fin: datetime,
      id_origen: str,
      nombre_origen: str,
      id_destino: str,
      nombre_destino: str,
  ):
    self.id_viaje = id_viaje
    self.fecha_inicio = fecha_inicio
    self.fecha_fin = fecha_fin
    self.id_origen = id_origen
    self.nombre_origen = nombre_origen
    self.id_destino = id_destino
    self.nombre_destino = nombre_destino

  def duracion_segundos(self) -> int:
    diferencia = self.fecha_fin - self.fecha_inicio
    return int(diferencia.total_seconds())

  def duracion_minutos(self) -> float:
    return round(self.duracion_segundos() / 60.0, 2)

  def es_viaje_circular(self) -> bool:
    return self.id_origen == self.id_destino

  def __repr__(self) -> str:
    return (
        f"Viaje({self.id_viaje}: {self.nombre_origen} -> {self.nombre_destino},"
        f" {self.duracion_minutos()} min)"
    )


# =====================================================================
# 2. Funciones de Validación y Limpieza
# =====================================================================
def validar_recorrido(fila: dict) -> tuple[bool, str | None, Viaje | None]:
  """Valida un registro individual del dataset."""
  id_viaje = str(fila.get("id_viaje", "")).strip()
  fecha_inicio_str = str(fila.get("fecha_inicio", "")).strip()
  fecha_fin_str = str(fila.get("fecha_fin", "")).strip()
  est_origen = str(fila.get("nombre_estacion_origen", "")).strip()
  id_origen = str(fila.get("id_estacion_origen", "")).strip()
  est_destino = str(fila.get("nombre_estacion_destino", "")).strip()
  id_destino = str(fila.get("id_estacion_destino", "")).strip()

  if not PATRON_ID_VIAJE.match(id_viaje):
    return False, "Formato de ID de viaje inválido (esperado ECO-XXXX)", None

  if not id_origen or not est_origen:
    return False, "Extremo de origen incompleto o faltante", None
  if not id_destino or not est_destino:
    return False, "Extremo de destino incompleto o faltante", None

  if not PATRON_FECHA.match(fecha_inicio_str):
    return (
        False,
        f"Formato textual de fecha_inicio inválido: '{fecha_inicio_str}'",
        None,
    )
  if not PATRON_FECHA.match(fecha_fin_str):
    return (
        False,
        f"Formato textual de fecha_fin inválido: '{fecha_fin_str}'",
        None,
    )

  formato_dt = "%Y-%m-%d %H:%M:%S"
  try:
    dt_inicio = datetime.strptime(fecha_inicio_str, formato_dt)
  except ValueError as err:
    return False, f"fecha_inicio inexistente en calendario: {err}", None

  try:
    dt_fin = datetime.strptime(fecha_fin_str, formato_dt)
  except ValueError as err:
    return False, f"fecha_fin inexistente en calendario: {err}", None

  if dt_fin < dt_inicio:
    return (
        False,
        "Inconsistencia temporal: fecha_fin es anterior a fecha_inicio",
        None,
    )

  viaje_valido = Viaje(
      id_viaje=id_viaje,
      fecha_inicio=dt_inicio,
      fecha_fin=dt_fin,
      id_origen=id_origen,
      nombre_origen=est_origen,
      id_destino=id_destino,
      nombre_destino=est_destino,
  )

  return True, None, viaje_valido


def validar_recorridos(filas: list[dict]) -> tuple[list[Viaje], list[dict]]:
  """Procesa una lista de filas leídas, separando válidos de rechazados."""
  validos = []
  rechazados = []

  for fila in filas:
    es_valido, motivo, viaje = validar_recorrido(fila)
    if es_valido:
      validos.append(viaje)
    else:
      registro_descartado = dict(fila)
      registro_descartado["motivo_rechazo"] = motivo
      rechazados.append(registro_descartado)

  return validos, rechazados


# =====================================================================
# 3. Transformación y Reporte Operativo
# =====================================================================
def seleccionar_periodo(
    viajes: list[Viaje], fecha_desde: datetime, fecha_hasta: datetime
) -> list[Viaje]:
  return [v for v in viajes if fecha_desde <= v.fecha_inicio <= fecha_hasta]


def generar_balance(viajes: list[Viaje]) -> dict[str, dict[str, int]]:
  reporte = defaultdict(lambda: {"salidas": 0, "llegadas": 0, "balance": 0})

  for v in viajes:
    reporte[v.nombre_origen]["salidas"] += 1
    reporte[v.nombre_destino]["llegadas"] += 1

  for est, datos in reporte.items():
    datos["balance"] = datos["llegadas"] - datos["salidas"]

  return dict(reporte)


def verificar_conservacion_red(
    balance_reporte: dict[str, dict[str, int]],
) -> bool:
  suma_balances = sum(datos["balance"] for datos in balance_reporte.values())
  return suma_balances == 0


# =====================================================================
# 4. Funciones de Exportación de Salidas
# =====================================================================
def exportar_rechazos(rechazos: list[dict], ruta_salida: str) -> None:
  """Exporta los registros descartados a un CSV de auditoría."""
  if not rechazos:
    return
  carpeta = os.path.dirname(ruta_salida)
  if carpeta:
    os.makedirs(carpeta, exist_ok=True)

  columnas = [c for c in rechazos[0].keys() if c != "motivo_rechazo"]
  columnas.append("motivo_rechazo")

  with open(ruta_salida, mode="w", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=columnas)
    escritor.writeheader()
    for fila in rechazos:
      escritor.writerow(fila)


def exportar_balance(
    balance: dict[str, dict[str, int]], ruta_salida: str
) -> None:
  """Exporta el reporte del balance operativo por estación a un CSV."""
  carpeta = os.path.dirname(ruta_salida)
  if carpeta:
    os.makedirs(carpeta, exist_ok=True)

  with open(ruta_salida, mode="w", encoding="utf-8", newline="") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(["estacion", "salidas", "llegadas", "balance_neto"])
    for est, datos in sorted(balance.items()):
      escritor.writerow(
          [est, datos["salidas"], datos["llegadas"], datos["balance"]]
      )