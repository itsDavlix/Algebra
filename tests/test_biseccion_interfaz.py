"""Verifica las acciones de la pestaña sin requerir un servidor gráfico."""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from interfaz.pestanaBiseccion import PestanaBiseccion


class PruebasAccionesBiseccion(unittest.TestCase):
    def setUp(self):
        self.tcl = tk.Tcl()
        self.pestana = PestanaBiseccion.__new__(PestanaBiseccion)
        for nombre in ("ecuacion", "a", "b", "tolerancia", "iteraciones"):
            setattr(self.pestana, "var_" + nombre, tk.StringVar(self.tcl))
        self.pestana.txt_resultado = Mock()
        self.pestana.entrada_ecuacion = Mock()

    @patch("interfaz.pestanaBiseccion.mostrar_error")
    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_ejemplo_resuelve_desde_los_campos(self, mostrar, error):
        self.pestana._cargar_ejemplo()
        self.pestana._accion_resolver()
        salida = mostrar.call_args.args[1]
        self.assertIn("convergencia alcanzada", salida)
        self.assertIn("x ≈ 1.52138", salida)
        self.assertIn("ITERACIÓN 20", salida)
        error.assert_not_called()

    @patch("interfaz.pestanaBiseccion.mostrar_error")
    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_error_reemplaza_el_resultado_anterior(self, mostrar, error):
        self.pestana._cargar_ejemplo()
        for valor in ("", "1.5", "nan", "0", "1001", "²"):
            with self.subTest(valor=valor):
                self.pestana.var_iteraciones.set(valor)
                self.pestana._accion_resolver()
                self.assertIn("No se pudo resolver", mostrar.call_args.args[1])
                self.assertIn("entero entre 1 y 1000", str(error.call_args.args[0]))

    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_limpiar_y_recargar(self, mostrar):
        self.pestana._cargar_ejemplo()
        self.pestana._limpiar()
        self.assertEqual(self.pestana.var_ecuacion.get(), "")
        self.assertEqual(self.pestana.var_a.get(), "")
        self.assertEqual(self.pestana.var_b.get(), "")
        self.assertEqual(mostrar.call_args.args[1], "")
        self.pestana.entrada_ecuacion.focus_set.assert_called_once()
        self.pestana._cargar_ejemplo()
        self.assertEqual(self.pestana.var_ecuacion.get(), "x^3 - x - 2 = 0")
        self.assertEqual(self.pestana.var_tolerancia.get(), "1e-6")


if __name__ == "__main__":
    unittest.main()
