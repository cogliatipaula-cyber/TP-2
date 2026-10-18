"""
tests/test_pipeline.py

Suite de pruebas unitarias automatizadas con unittest (Paso 5 - TP2).
Cubre:
 1. Caso normal (Happy Path).
 2. Entradas inválidas, faltantes, fuera de rango o límites (Calendario, IDs, Fechas).
 3. Propiedades relevantes del resultado:
    - Conservación de cantidades (Suma de balances en la red = 0).
    - Equivalencia de resultados entre fuentes CSV y JSON.
"""

import sys
import os
import unittest
import json
import csv
import tempfile
from datetime import datetime

# Insertar el directorio raíz en sys.path para poder importar los módulos de src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fuentes import FuenteCSV, FuenteJSON
from src.pipeline import (
    Viaje,
    validar_recorrido,
    validar_recorridos,
    generar_balance,
    verificar_conservacion_red
)


class TestPipelineEcobici(unittest.TestCase):

    # =========================================================================
    # 1. CASO NORMAL (Happy Path)
    # =========================================================================
    def test_validar_recorrido_caso_normal(self):
        """1. CASO NORMAL:
        Verifica que un registro con datos válidos se procese correctamente,
        devuelva es_valido=True, cree la instancia de Viaje y calcule sus métodos.
        """
        fila_valida = {
            "id_viaje": "ECO-0001",
            "duracion_segundos": "1800",
            "fecha_inicio": "2024-03-15 08:00:00",
            "fecha_fin": "2024-03-15 08:30:00",
            "id_estacion_origen": "EST-001",
            "nombre_estacion_origen": "Plaza de Mayo",
            "id_estacion_destino": "EST-002",
            "nombre_estacion_destino": "Congreso"
        }

        es_valido, motivo, viaje = validar_recorrido(fila_valida)

        self.assertTrue(es_valido, "El viaje válido debería devolver True.")
        self.assertIsNone(motivo, "Un viaje válido no debe tener motivo de rechazo.")
        self.assertIsInstance(viaje, Viaje, "Debe retornar una instancia de la clase Viaje.")
        self.assertEqual(viaje.id_viaje, "ECO-0001")
        self.assertEqual(viaje.duracion_segundos(), 1800, "La duración calculada debe ser 1800 segundos.")
        self.assertEqual(viaje.duracion_minutos(), 30.0)
        self.assertFalse(viaje.es_viaje_circular())

    # =========================================================================
    # 2. ENTRADAS INVÁLIDAS, VALORES FALTANTES Y CASOS LÍMITE
    # =========================================================================
    def test_validar_recorrido_inconsistencia_temporal(self):
        """2a. ENTRADA INVÁLIDA (Inconsistencia temporal):
        Verifica que un viaje con fecha_fin anterior a fecha_inicio sea rechazado.
        """
        fila_invalida = {
            "id_viaje": "ECO-0002",
            "duracion_segundos": "-3600",
            "fecha_inicio": "2024-03-15 10:00:00",
            "fecha_fin": "2024-03-15 09:00:00",  # Fin anterior a inicio
            "id_estacion_origen": "EST-001",
            "nombre_estacion_origen": "Plaza de Mayo",
            "id_estacion_destino": "EST-002",
            "nombre_estacion_destino": "Congreso"
        }

        es_valido, motivo, viaje = validar_recorrido(fila_invalida)

        self.assertFalse(es_valido, "Un viaje con inconsistencia temporal debe devolver False.")
        self.assertIsNone(viaje, "No debe crearse un objeto Viaje si fue rechazado.")
        self.assertIn("Inconsistencia temporal", motivo)

    def test_validar_recorrido_fecha_inexistente_calendario(self):
        """2b. CASO LÍMITE / INVÁLIDO (Calendario):
        Verifica que el 31 de abril (fecha sintácticamente válida para regex pero inexistente)
        sea descartada con mensaje claro y sin ocultar fallas.
        """
        fila_fecha_imposible = {
            "id_viaje": "ECO-0003",
            "duracion_segundos": "1800",
            "fecha_inicio": "2024-04-31 10:00:00",  # El 31 de abril NO existe
            "fecha_fin": "2024-04-31 10:30:00",
            "id_estacion_origen": "EST-001",
            "nombre_estacion_origen": "Plaza de Mayo",
            "id_estacion_destino": "EST-002",
            "nombre_estacion_destino": "Congreso"
        }

        es_valido, motivo, viaje = validar_recorrido(fila_fecha_imposible)

        self.assertFalse(es_valido, "Una fecha inexistente en el calendario debe devolver False.")
        self.assertIsNone(viaje)
        self.assertIn("inexistente en calendario", motivo)

    def test_validar_recorrido_id_y_campos_faltantes(self):
        """2c. VALORES FALTANTES E ID CORRUPTO:
        Verifica el rechazo explícito cuando falta la estación de origen o el ID no cumple la máscara ECO-XXXX.
        """
        fila_id_malo = {
            "id_viaje": "INVALIDO-123",  # No cumple regex ECO-XXXX
            "duracion_segundos": "900",
            "fecha_inicio": "2024-03-15 10:00:00",
            "fecha_fin": "2024-03-15 10:15:00",
            "id_estacion_origen": "EST-001",
            "nombre_estacion_origen": "Plaza de Mayo",
            "id_estacion_destino": "EST-002",
            "nombre_estacion_destino": "Congreso"
        }
        es_valido_id, motivo_id, _ = validar_recorrido(fila_id_malo)
        self.assertFalse(es_valido_id)
        self.assertIn("Formato de ID de viaje inválido", motivo_id)

        fila_origen_faltante = {
            "id_viaje": "ECO-0004",
            "duracion_segundos": "900",
            "fecha_inicio": "2024-03-15 10:00:00",
            "fecha_fin": "2024-03-15 10:15:00",
            "id_estacion_origen": "",  # Campo faltante
            "nombre_estacion_origen": "",
            "id_estacion_destino": "EST-002",
            "nombre_estacion_destino": "Congreso"
        }
        es_valido_origen, motivo_origen, _ = validar_recorrido(fila_origen_faltante)
        self.assertFalse(es_valido_origen)
        self.assertIn("origen incompleto o faltante", motivo_origen)

    # =========================================================================
    # 3. PROPIEDADES RELEVANTES DEL RESULTADO
    # =========================================================================
    def test_propiedad_conservacion_red_suma_balances_cero(self):
        """3a. PROPIEDAD DEL RESULTADO (Conservación de cantidades):
        Verifica que en toda la red, la suma global de los balances netos (llegadas - salidas)
        sea siempre exactamente igual a cero.
        """
        v1 = Viaje("ECO-0001", datetime(2024, 3, 15, 8, 0), datetime(2024, 3, 15, 8, 15), "E1", "Plaza de Mayo", "E2", "Congreso")
        v2 = Viaje("ECO-0002", datetime(2024, 3, 15, 9, 0), datetime(2024, 3, 15, 9, 20), "E2", "Congreso", "E1", "Plaza de Mayo")
        v3 = Viaje("ECO-0003", datetime(2024, 3, 15, 10, 0), datetime(2024, 3, 15, 10, 10), "E1", "Plaza de Mayo", "E3", "Retiro")

        balance = generar_balance([v1, v2, v3])
        es_conservativo = verificar_conservacion_red(balance)

        self.assertTrue(es_conservativo, "La suma total de balances netos en la red debe ser cero.")
        self.assertEqual(balance["Plaza de Mayo"]["balance"], -1)  # 2 salidas, 1 llegada
        self.assertEqual(balance["Retiro"]["balance"], 1)          # 0 salidas, 1 llegada

    def test_propiedad_equivalencia_lectura_csv_y_json(self):
        """3b. PROPIEDAD DEL RESULTADO (Equivalencia CSV y JSON):
        Verifica que leer una muestra equivalente desde CSV y JSON genere exactamente
        la misma cantidad de registros válidos, rechazados y los mismos balances.
        """
        datos_muestra = [
            {
                "id_viaje": "ECO-0001",
                "duracion_segundos": "1800",
                "fecha_inicio": "2024-03-15 08:00:00",
                "fecha_fin": "2024-03-15 08:30:00",
                "id_estacion_origen": "EST-001",
                "nombre_estacion_origen": "Plaza de Mayo",
                "id_estacion_destino": "EST-002",
                "nombre_estacion_destino": "Congreso"
            },
            {
                "id_viaje": "ECO-0002",
                "duracion_segundos": "-3600",
                "fecha_inicio": "2024-03-15 10:00:00",
                "fecha_fin": "2024-03-15 09:00:00",  # Rechazado por fecha
                "id_estacion_origen": "EST-001",
                "nombre_estacion_origen": "Plaza de Mayo",
                "id_estacion_destino": "EST-002",
                "nombre_estacion_destino": "Congreso"
            }
        ]

        # Crear archivos temporales de prueba CSV y JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            path_csv = os.path.join(tmpdir, "muestra.csv")
            path_json = os.path.join(tmpdir, "muestra.json")

            # Escribir CSV con encabezados correctos
            with open(path_csv, mode="w", encoding="utf-8", newline="") as f_csv:
                writer = csv.DictWriter(f_csv, fieldnames=list(datos_muestra[0].keys()))
                writer.writeheader()
                writer.writerows(datos_muestra)

            # Escribir JSON
            with open(path_json, mode="w", encoding="utf-8") as f_json:
                json.dump(datos_muestra, f_json)

            # Cargar y validar desde ambas fuentes
            fuente_csv = FuenteCSV()
            fuente_json = FuenteJSON()

            filas_csv = fuente_csv.cargar(path_csv)
            filas_json = fuente_json.cargar(path_json)

            validos_csv, rechazados_csv = validar_recorridos(filas_csv)
            validos_json, rechazados_json = validar_recorridos(filas_json)

            balance_csv = generar_balance(validos_csv)
            balance_json = generar_balance(validos_json)

            # Verificar equivalencia estricta
            self.assertEqual(len(validos_csv), len(validos_json), "Los válidos de CSV y JSON deben coincidir.")
            self.assertEqual(len(rechazados_csv), len(rechazados_json), "Los rechazados de CSV y JSON deben coincidir.")
            self.assertEqual(balance_csv, balance_json, "El balance derivado debe ser 100% idéntico.")


if __name__ == "__main__":
    unittest.main()