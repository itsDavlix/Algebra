"""Verifica las acciones de la pestaña sin requerir un servidor gráfico."""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from interfaz.pestanaBiseccion import PestanaBiseccion, dibujar_grafica_biseccion
from interfaz.estilos import AZUL
from nucleo.biseccion import preparar_funcion, resolver_biseccion


class PruebasAccionesBiseccion(unittest.TestCase):
    def setUp(self):
        self.tcl = tk.Tcl()
        self.pestana = PestanaBiseccion.__new__(PestanaBiseccion)
        for nombre in ("ecuacion", "a", "b", "tolerancia", "iteraciones"):
            setattr(self.pestana, "var_" + nombre, tk.StringVar(self.tcl))
        self.pestana.txt_resultado = Mock()
        self.pestana.entrada_ecuacion = Mock()
        self.pestana.canvas_grafica = Mock()
        self.pestana.canvas_grafica.winfo_width.return_value = 500
        self.pestana.canvas_grafica.winfo_height.return_value = 210

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
        self.assertEqual(self.pestana.canvas_grafica.create_oval.call_count, 2)

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

    def test_grafica_muestra_curva_y_raiz_aproximada(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 500
        lienzo.winfo_height.return_value = 210
        funcion, _ = preparar_funcion("x^2 - 2")
        resultado = resolver_biseccion("x^2 - 2", 1, 2)

        dibujar_grafica_biseccion(lienzo, funcion, 1, 2, resultado)

        self.assertGreater(lienzo.create_line.call_count, 100)
        self.assertEqual(lienzo.create_oval.call_count, 2)
        textos = [call.kwargs.get("text", "") for call in lienzo.create_text.call_args_list]
        self.assertTrue(any("x**2 - 2" in texto for texto in textos))
        self.assertTrue(any("raíz ≈" in texto for texto in textos))

    def test_grafica_maneja_intervalos_con_salto_de_dominio(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 500
        lienzo.winfo_height.return_value = 210
        funcion, _ = preparar_funcion("sqrt(x)")

        dibujar_grafica_biseccion(lienzo, funcion, -1, 2)

        trazos_curva = [
            llamada for llamada in lienzo.create_line.call_args_list
            if llamada.kwargs.get("fill") == AZUL
        ]
        self.assertGreater(len(trazos_curva), 100)
        self.assertLess(len(trazos_curva), 400)

    def test_grafica_funciona_con_intervalos_que_exceden_el_rango_decimal(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 500
        lienzo.winfo_height.return_value = 210
        funcion, _ = preparar_funcion("x")
        resultado = resolver_biseccion("x", -1.7e308, 1.7e308)

        dibujar_grafica_biseccion(lienzo, funcion, -1.7e308, 1.7e308, resultado)

        self.assertEqual(lienzo.create_oval.call_count, 2)

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
