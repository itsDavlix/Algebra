"""Pruebas de Regula Falsi, sus estimaciones y su interfaz sin pantalla."""

import math
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from interfaz.pestanaReglaFalsa import PestanaReglaFalsa
from nucleo.biseccion import MAX_ITERACIONES, resolver_biseccion
from nucleo.reglafalsa import (
    formatear_resultado_reglafalsa, nota_estancamiento, punto_falsa_posicion,
    resolver_reglafalsa,
)


class PruebasReglaFalsa(unittest.TestCase):
    def test_raices_conocidas(self):
        casos = (
            ("x^2 = 2", 1, 2, math.sqrt(2)),
            ("x^3 - x - 2 = 0", 1, 2, 1.5213797068045676),
            ("cos(x) = x", 0, 1, 0.7390851332151607),
            ("exp(x) = 2", 0, 1, math.log(2)),
            ("log(x)", 0.5, 5, 1),
        )
        for ecuacion, a, b, raiz in casos:
            with self.subTest(ecuacion=ecuacion):
                resultado = resolver_reglafalsa(ecuacion, a, b, 1e-10)
                self.assertTrue(resultado.convergio, resultado.motivo)
                self.assertLessEqual(abs(resultado.raiz - raiz), 1e-8)

    def test_primeras_iteraciones_y_error_relativo(self):
        resultado = resolver_reglafalsa("x^2 - 2", 1, 2, max_iteraciones=3)
        pasos = resultado.iteraciones
        self.assertAlmostEqual(pasos[0].c, 4 / 3)
        self.assertAlmostEqual(pasos[1].c, 1.4)
        self.assertAlmostEqual(pasos[2].c, 1.4117647, places=7)
        self.assertIsNone(pasos[0].error)
        self.assertIsNone(pasos[0].error_relativo)
        self.assertAlmostEqual(pasos[2].error_relativo, 0.8333333, places=5)

    def test_formula_es_equivalente_a_la_secante(self):
        a, b, fa, fb = 1.0, 2.0, -1.0, 2.0
        esperado = b - fb * (a - b) / (fa - fb)
        self.assertAlmostEqual(punto_falsa_posicion(a, b, fa, fb), esperado)

    def test_iteraciones_conservan_intervalo_y_cambio_de_signo(self):
        resultado = resolver_reglafalsa("x^2 - 2", 1, 2, 1e-8)
        for paso in resultado.iteraciones:
            with self.subTest(iteracion=paso.numero):
                self.assertLess(paso.a, paso.c)
                self.assertLess(paso.c, paso.b)
                self.assertNotEqual(paso.fa < 0, paso.fb < 0)

    def test_estancamiento_y_caso_sin_estancamiento(self):
        resultado = resolver_reglafalsa("x^10 - 1", 0, 1.3, 1e-6, 1000)
        biseccion = resolver_biseccion("x^10 - 1", 0, 1.3, 1e-6, 1000)
        self.assertEqual(resultado.extremo_estancado, "b")
        self.assertIn("El extremo b no cambió", nota_estancamiento(resultado))
        self.assertGreater(len(resultado.iteraciones), len(biseccion.iteraciones))

        casi_lineal = resolver_reglafalsa("x - 3", 0, 10)
        self.assertEqual(nota_estancamiento(casi_lineal), "")
        self.assertEqual(casi_lineal.extremo_estancado, "")

    def test_polos_y_raiz_de_tangente(self):
        polo = resolver_reglafalsa("tan(x)", 1, 2, 1e-6, 1000)
        self.assertFalse(polo.convergio)
        self.assertIn("discontinuidad", polo.motivo.lower())

        raiz = resolver_reglafalsa("tan(x) - 1", 0, 1.5, 1e-10, 500)
        self.assertTrue(raiz.convergio, raiz.motivo)
        self.assertAlmostEqual(raiz.raiz, math.pi / 4, places=4)

    def test_raiz_en_extremo_limite_y_una_iteracion(self):
        extremo = resolver_reglafalsa("x - 2", 2, 3)
        self.assertTrue(extremo.convergio)
        self.assertEqual(extremo.raiz, 2)
        self.assertEqual(extremo.iteraciones, ())
        otro_extremo = resolver_reglafalsa("x - 2", 1, 2)
        self.assertTrue(otro_extremo.convergio)
        self.assertEqual(otro_extremo.raiz, 2)
        self.assertEqual(otro_extremo.iteraciones, ())

        raiz_exacta = resolver_reglafalsa("x", -1, 1)
        self.assertTrue(raiz_exacta.convergio)
        self.assertEqual(raiz_exacta.valor_funcion, 0)
        self.assertIsNone(raiz_exacta.error)  # No hay aproximación anterior para comparar.
        self.assertIsNone(raiz_exacta.iteraciones[0].error_relativo)

        limite = resolver_reglafalsa("x^10 - 1", 0, 1.3, 1e-12, 5)
        self.assertFalse(limite.convergio)
        self.assertIn("máximo de iteraciones", limite.motivo)

        una = resolver_reglafalsa("x^2 - 2", 1, 2, 1e-30, 1)
        self.assertIsNone(una.error)
        self.assertIsNone(una.iteraciones[0].error)
        self.assertIn("no disponible", formatear_resultado_reglafalsa(una))

    def test_entradas_invalidas(self):
        for parametros in (
            ("x^2 - 2", 2, 1, 1e-6, 100),
            ("x^2 - 2", 1, 2, 0, 100),
            ("x^2 - 2", 1, 2, 1e-6, 0),
            ("x^2 - 2", 1, 2, 1e-6, 2.5),
            ("x^2 - 2", 1, 2, 1e-6, True),
            ("x^2 - 2", 1, 2, 1e-6, MAX_ITERACIONES + 1),
            ("x^2 - 2", math.nan, 2, 1e-6, 100),
            ("x^2 - 2", 1, math.inf, 1e-6, 100),
            ("x^2 - 2", 1, 2, math.inf, 100),
        ):
            with self.subTest(parametros=parametros), self.assertRaises(ValueError):
                resolver_reglafalsa(*parametros)

        for ecuacion in ("x^2 + 1", "", "__import__('os')"):
            with self.subTest(ecuacion=ecuacion), self.assertRaises(ValueError):
                resolver_reglafalsa(ecuacion, -1, 1)

    def test_magnitudes_extremas_sin_desbordar(self):
        resultado = resolver_reglafalsa(
            "x - 1e300", -1e308, 1e308, tolerancia=1e290, max_iteraciones=100,
        )
        self.assertTrue(resultado.convergio, resultado.motivo)
        self.assertLessEqual(abs(resultado.raiz - 1e300), 1e290)
        self.assertTrue(all(math.isfinite(paso.c) for paso in resultado.iteraciones))

    def test_ejemplo_de_aceptacion(self):
        resultado = resolver_reglafalsa("x^3 - x - 2 = 0", 1, 2, 1e-6)
        self.assertTrue(resultado.convergio)
        self.assertAlmostEqual(resultado.raiz, 1.52138, places=5)
        self.assertEqual(len(resultado.iteraciones), 13)
        self.assertLessEqual(abs(resultado.valor_funcion), resultado.tolerancia)
        self.assertEqual(resultado.extremo_estancado, "b")


class PruebasInterfazReglaFalsa(unittest.TestCase):
    def setUp(self):
        self.tcl = tk.Tcl()
        self.pestana = PestanaReglaFalsa.__new__(PestanaReglaFalsa)
        for nombre in ("ecuacion", "a", "b", "tolerancia", "iteraciones"):
            setattr(self.pestana, "var_" + nombre, tk.StringVar(self.tcl))
        self.pestana.txt_resultado = Mock()
        self.pestana.tabla_iteraciones = Mock()
        self.pestana.tabla_iteraciones.get_children.return_value = ()
        self.pestana.canvas_grafica = Mock()
        self.pestana.canvas_grafica.winfo_width.return_value = 500
        self.pestana.canvas_grafica.winfo_height.return_value = 210
        self.pestana._redibujar_grafica = Mock()
        self.pestana._mostrar_mensaje_grafica = Mock()

    @patch("interfaz.pestanaReglaFalsa.mostrar_error")
    @patch("interfaz.pestanaReglaFalsa.mostrar_texto")
    def test_resumen_tabla_y_mensaje_de_error(self, mostrar, error):
        self.pestana.var_ecuacion.set("x^3 - x - 2")
        self.pestana.var_a.set("1")
        self.pestana.var_b.set("2")
        self.pestana.var_tolerancia.set("1e-6")
        self.pestana.var_iteraciones.set("100")

        self.pestana._accion_resolver()

        resumen = mostrar.call_args.args[1]
        self.assertAlmostEqual(self.pestana.resultado_biseccion.raiz, 1.52138, places=5)
        self.assertIn("AVISO:", resumen)
        self.assertEqual(self.pestana.tabla_iteraciones.insert.call_count,
                         len(self.pestana.resultado_biseccion.iteraciones) * 8)
        textos = [
            llamada.kwargs.get("text", "")
            for llamada in self.pestana.tabla_iteraciones.insert.call_args_list
        ]
        self.assertTrue(any(texto.startswith("Decisión:") for texto in textos))
        self.assertTrue(any(texto.startswith("Parada:") for texto in textos))
        error.assert_not_called()

        self.pestana.var_ecuacion.set("x^2 + 1")
        self.pestana._accion_resolver()
        self.assertIsNone(self.pestana.resultado_biseccion)
        self.pestana._mostrar_mensaje_grafica.assert_called_once()
        error.assert_called_once()

    @patch("interfaz.pestanaReglaFalsa.mostrar_error")
    @patch("interfaz.pestanaReglaFalsa.mostrar_texto")
    def test_resolver_autoajusta_y_usa_cien_iteraciones(self, mostrar, error):
        self.pestana.var_ecuacion.set("x^2 = 2")
        self.pestana._accion_resolver()
        self.assertEqual(self.pestana.var_iteraciones.get(), "100")
        texto = mostrar.call_args.args[1]
        self.assertIn("convergencia alcanzada", texto)
        self.assertAlmostEqual(self.pestana.resultado_biseccion.raiz, math.sqrt(2), places=5)
        error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
