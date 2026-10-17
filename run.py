"""run.py.

Punto de entrada principal para la ejecución reproducible del reporte de
movimientos de Ecobici (TP2 - Paso 3).
"""

import csv
import json
import os
from src.fuentes import FuenteCSV, FuenteJSON
from src.pipeline import (
    exportar_balance,
    exportar_rechazos,
    generar_balance,
    validar_recorridos,
    verificar_conservacion_red,
)


def asegurar_archivo_json(ruta_csv: str, ruta_json: str) -> None:
  """Si el archivo JSON no existe en data/, lo genera automáticamente a partir del CSV."""
  if not os.path.exists(ruta_json) and os.path.exists(ruta_csv):
    with open(ruta_csv, mode="r", encoding="utf-8") as f_csv:
      filas = list(csv.DictReader(f_csv))
    with open(ruta_json, mode="w", encoding="utf-8") as f_json:
      json.dump(filas, f_json, indent=2, ensure_ascii=False)
    print(
        f" [AUTO] Se creó '{ruta_json}' automáticamente a partir del CSV para"
        " la prueba."
    )


def ejecutar_flujo(fuente, ruta_archivo, nombre_formato):
  print(f"\n---> Procesando fuente {nombre_formato}: '{ruta_archivo}'")
  filas = fuente.cargar(ruta_archivo)
  validos, rechazados = validar_recorridos(filas)
  balance = generar_balance(validos)
  es_conservativo = verificar_conservacion_red(balance)

  print(
      f"     Leídos: {len(filas)} | Válidos: {len(validos)} | Rechazados:"
      f" {len(rechazados)}"
  )
  print(
      "     Conservación de red (Suma balances = 0):"
      f" {'✓ CORRECTA' if es_conservativo else '✗ ERROR'}"
  )

  return validos, rechazados, balance


def main():
  print("=" * 70)
  print(" PROCESAMIENTO Y VALIDACIÓN DE MOVIMIENTOS ECOBICI (TP2)")
  print("=" * 70)

  # Generar el archivo JSON en data/ si todavía no existe
  asegurar_archivo_json(
      "data/ecobici-movimientos.csv", "data/ecobici-movimientos.json"
  )

  # 1. Demostrar lectura y equivalencia de ambos formatos (CSV y JSON)
  fuente_csv = FuenteCSV()
  validos_csv, rechazados_csv, balance_csv = ejecutar_flujo(
      fuente_csv, "data/ecobici-movimientos.csv", "CSV"
  )

  fuente_json = FuenteJSON()
  validos_json, rechazados_json, balance_json = ejecutar_flujo(
      fuente_json, "data/ecobici-movimientos.json", "JSON"
  )

  # Comprobación de equivalencia entre formatos
  assert len(validos_csv) == len(validos_json), (
      "Error: discrepancia en registros válidos entre CSV y JSON"
  )
  assert len(rechazados_csv) == len(rechazados_json), (
      "Error: discrepancia en rechazados entre CSV y JSON"
  )
  assert balance_csv == balance_json, (
      "Error: los balances calculados difieren entre CSV y JSON"
  )

  print(
      "\n [VERIFICACIÓN] ¡Los resultados entre las muestras CSV y JSON son 100%"
      " EQUIVALENTES!"
  )

  # 2. Exportar archivos de salida útiles
  exportar_rechazos(rechazados_csv, "outputs/rechazos.csv")
  exportar_balance(balance_csv, "outputs/reporte_balance.csv")
  print("\n [SALIDAS] Archivos generados en carpeta 'outputs/':")
  print("   • outputs/rechazos.csv (auditoría con motivos de descarte)")
  print("   • outputs/reporte_balance.csv (métricas por estación)")

  # 3. Mostrar resumen en pantalla
  print("\n" + "-" * 70)
  print("FILAS RECHAZADAS Y MOTIVOS DETECTADOS:")
  print("-" * 70)
  for r in rechazados_csv:
    print(f"• ID: {r.get('id_viaje', 'S/D'):<10} | Motivo: {r['motivo_rechazo']}")

  print("\n" + "-" * 70)
  print(
      f"{'ESTACIÓN':<25} | {'SALIDAS':<8} | {'LLEGADAS':<8} | {'BALANCE NETO'}"
  )
  print("-" * 70)
  for est, datos in sorted(balance_csv.items()):
    print(
        f"{est:<25} | {datos['salidas']:<8} | {datos['llegadas']:<8} |"
        f" {datos['balance']:+d}"
    )
  print("=" * 70)


if __name__ == "__main__":
  main()