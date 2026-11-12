"""Verifica raíces, fallos numéricos y selección de métodos sin pantalla."""

import math
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from interfaz.pestanaMetodosAbiertos import PestanaMetodosAbiertos
from nucleo.metodosabiertos import METODOS_ABIERTOS, resolver_metodo_abierto


class PruebasMetodosAbiertos(unittest.TestCase):
    def test_raices_conocidas(self):
        for ecuacion, derivada, x0, x1, raiz in (
            ("x^2 = 2", "2*x", 1, 2, math.sqrt(2)),
            ("x^3 - x - 2", "3*x^2 - 1", 1.5, 2, 1.5213797068045676),
            ("cos(x) = x", "-sin(x) - 1", 0.5, 1, 0.7390851332151607),
            ("exp(x) = 2", "exp(x)", 0, 1, math.log(2)),
            ("(x-1)^2", "2*(x-1)", 2, 3, 1),
        ):
            for metodo in METODOS_ABIERTOS:
                with self.subTest(ecuacion=ecuacion, metodo=metodo):
                    r = resolver_metodo_abierto(ecuacion, metodo, x0, x1, derivada, 1e-10)
                    self.assertTrue(r.convergio, r.motivo)
                    self.assertAlmostEqual(r.raiz, raiz, places=8)

    def test_pasos_de_newton_y_secante(self):
        newton = resolver_metodo_abierto("x^2 - 2", "Newton-Raphson", 1,
                                        derivada="2*x", max_iteraciones=2)
        secante = resolver_metodo_abierto("x^2 - 2", "Secante", 1, 2, max_iteraciones=2)
        self.assertEqual(newton.iteraciones[0].siguiente, 1.5)
        self.assertAlmostEqual(newton.iteraciones[1].siguiente, 17/12)
        self.assertAlmostEqual(secante.iteraciones[0].siguiente, 4/3)
        self.assertAlmostEqual(secante.iteraciones[1].siguiente, 1.4)
        self.assertFalse(newton.convergio)
        self.assertFalse(secante.convergio)

    def test_secante_no_requiere_cambio_de_signo_ni_orden(self):
        for x0, x1 in ((2, 3), (3, 2)):
            r = resolver_metodo_abierto("x^2 - 2", "Secante", x0, x1)
            self.assertTrue(r.convergio)
            self.assertAlmostEqual(r.raiz, math.sqrt(2), places=6)

    def test_raices_iniciales(self):
        for metodo, x0, x1 in (("Newton-Raphson", 1, None), ("Secante", 1, 2), ("Secante", 2, 1)):
            r = resolver_metodo_abierto("x-1", metodo, x0, x1, "1")
            self.assertTrue(r.convergio)
            self.assertEqual(r.raiz, 1)
            self.assertEqual(r.iteraciones, ())

    def test_denominadores_nulos(self):
        for metodo, x0, x1, derivada in (("Newton-Raphson", 0, None, "2*x"), ("Secante", -1, 1, "")):
            r = resolver_metodo_abierto("x^2+1", metodo, x0, x1, derivada)
            self.assertFalse(r.convergio)
            self.assertIn("cero", r.motivo)

    def test_ciclo_y_paso_pequeno_no_se_declaran_raices(self):
        ciclo = resolver_metodo_abierto("x^3-2*x+2", "Newton-Raphson", 0,
                                       derivada="3*x^2-2", max_iteraciones=10)
        estancado = resolver_metodo_abierto("x^2+1", "Newton-Raphson", 1, derivada="1e30")
        self.assertFalse(ciclo.convergio)
        self.assertEqual(len(ciclo.iteraciones), 10)
        self.assertFalse(estancado.convergio)
        self.assertIn("estancó", estancado.motivo)

    def test_validaciones(self):
        base = dict(ecuacion="x^2-2", metodo="Secante", x0=1, x1=2)
        for cambios in (
            dict(metodo="Otro"), dict(x0=float("nan")), dict(x1=float("inf")),
            dict(x1=1), dict(x1=None), dict(tolerancia=0), dict(tolerancia=-1),
            dict(tolerancia=float("nan")), dict(max_iteraciones=0),
            dict(max_iteraciones=1001), dict(max_iteraciones=True), dict(max_iteraciones=2.5),
            dict(ecuacion="__import__('os')"), dict(ecuacion="sqrt(x)", x0=-1),
            dict(metodo="Newton-Raphson", derivada=""),
            dict(metodo="Newton-Raphson", derivada="__import__('os')"),
        ):
            with self.subTest(cambios=cambios), self.assertRaises(ValueError):
                resolver_metodo_abierto(**{**base, **cambios})

    def test_salida_del_dominio_y_desborde(self):
        with self.assertRaises(ValueError):
            resolver_metodo_abierto("log(x)", "Newton-Raphson", 10, derivada="1/x")
        with self.assertRaises(ValueError):
            resolver_metodo_abierto("x^2+1", "Newton-Raphson", 1, derivada="1e-320")


class PruebasSeleccionMetodos(unittest.TestCase):
    def setUp(self):
        self.tcl = tk.Tcl()
        self.p = PestanaMetodosAbiertos.__new__(PestanaMetodosAbiertos)
        for nombre in ("metodo", "ecuacion", "derivada", "x0", "x1", "tolerancia", "iteraciones"):
            setattr(self.p, "var_" + nombre, tk.StringVar(self.tcl))
        for nombre in ("entrada_derivada", "entrada_x1", "entrada_ecuacion", "txt_resultado"):
            setattr(self.p, nombre, Mock())
        self.p.var_metodo.set("Newton-Raphson")

    @patch("interfaz.pestanaMetodosAbiertos.mostrar_error")
    @patch("interfaz.pestanaMetodosAbiertos.mostrar_texto")
    def test_selector_y_ejemplo_de_ambos_metodos(self, mostrar, error):
        for metodo in METODOS_ABIERTOS:
            self.p.var_metodo.set(metodo)
            self.p._cargar_ejemplo()
            self.p.entrada_x1.configure.assert_called_with(state="normal" if metodo == "Secante" else "disabled")
            self.p.entrada_derivada.configure.assert_called_with(state="disabled" if metodo == "Secante" else "normal")
            # Los campos deshabilitados no intervienen en el cálculo.
            if metodo == "Secante":
                self.p.var_derivada.set("inválida")
            else:
                self.p.var_x1.set("inválido")
            self.p._accion_resolver()
            self.assertTrue(self.p.resultado.convergio)
            self.assertEqual(self.p.resultado.metodo, metodo)
            self.assertIn("ITERACIÓN 1", mostrar.call_args.args[1])
        error.assert_not_called()

    @patch("interfaz.pestanaMetodosAbiertos.mostrar_error")
    @patch("interfaz.pestanaMetodosAbiertos.mostrar_texto")
    def test_entrada_invalida_borra_resultado_previo(self, mostrar, error):
        self.p._cargar_ejemplo()
        self.p._accion_resolver()
        self.p.var_iteraciones.set("1.5")
        self.p._accion_resolver()
        self.assertIsNone(self.p.resultado)
        error.assert_called_once()
        self.assertIn("No se pudo resolver", mostrar.call_args.args[1])

    @patch("interfaz.pestanaMetodosAbiertos.mostrar_texto")
    def test_limpiar_y_cambiar_metodo_descarta_resultado(self, mostrar):
        self.p._cargar_ejemplo()
        self.p._accion_resolver()
        self.p.var_metodo.set("Secante")
        self.p._seleccionar_metodo()
        self.assertIsNone(self.p.resultado)
        self.p._limpiar()
        self.assertEqual(self.p.var_ecuacion.get(), "")
        self.assertEqual(self.p.var_x0.get(), "")
        self.assertEqual(self.p.var_tolerancia.get(), "1e-6")


if __name__ == "__main__":
    unittest.main()
