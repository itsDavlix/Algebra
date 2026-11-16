"""Pruebas de puntos notables, valores sugeridos y textos del procedimiento."""

import math
import unittest

from nucleo import procedimientos
from nucleo.analisis import puntos_notables, sugerir_valores
from nucleo.biseccion import resolver_biseccion
from nucleo.expresiones import analizar
from nucleo.metodosabiertos import resolver_metodo_abierto
from nucleo.reglafalsa import resolver_reglafalsa


def _notables(texto, a=-5, b=5):
    f = analizar(texto)
    return f, puntos_notables(f, a, b, f.derivada(), f.derivada().derivada())


class PruebasPuntosNotables(unittest.TestCase):
    def test_cubica_con_todos_los_tipos(self):
        _, puntos = _notables("x^3 - x - 2")
        por_tipo = {p.tipo: p for p in puntos}
        self.assertAlmostEqual(por_tipo["raiz"].x, 1.5213797068045676, places=9)
        self.assertAlmostEqual(por_tipo["maximo"].x, -1 / math.sqrt(3), places=7)
        self.assertAlmostEqual(por_tipo["minimo"].x, 1 / math.sqrt(3), places=7)
        self.assertAlmostEqual(por_tipo["inflexion"].x, 0, places=7)
        self.assertEqual(por_tipo["corte_y"].y, -2)

    def test_polos_no_son_raices(self):
        _, puntos = _notables("1/(x - 1)")
        self.assertFalse([p for p in puntos if p.tipo == "raiz"])
        _, puntos = _notables("tan(x)", -3, 3)
        raices = [p.x for p in puntos if p.tipo == "raiz"]
        self.assertEqual(len(raices), 1)
        self.assertAlmostEqual(raices[0], 0, places=9)

    def test_raiz_doble_se_detecta_sin_cambio_de_signo(self):
        _, puntos = _notables("(x - 1)^2")
        raices = [p for p in puntos if p.tipo == "raiz"]
        self.assertEqual(len(raices), 1)
        self.assertIn("doble", raices[0].explicacion)

    def test_dominio_restringido(self):
        _, puntos = _notables("sqrt(x) - 1", -4, 4)
        raices = [p.x for p in puntos if p.tipo == "raiz"]
        self.assertEqual(len(raices), 1)
        self.assertAlmostEqual(raices[0], 1, places=9)


class PruebasSugerencias(unittest.TestCase):
    def test_intervalo_limpio_con_bolzano(self):
        f, puntos = _notables("x^3 - x - 2")
        raiz = next(p for p in puntos if p.tipo == "raiz")
        for metodo in ("Bisección", "Regula Falsi"):
            sugerencia = sugerir_valores(metodo, f, raiz)
            self.assertEqual(sugerencia.valores, {"a": "1", "b": "2"})
            self.assertIn("Bolzano", sugerencia.explicacion)

    def test_newton_cumple_condicion_de_fourier(self):
        f, puntos = _notables("x^3 - x - 2")
        raiz = next(p for p in puntos if p.tipo == "raiz")
        sugerencia = sugerir_valores("Newton-Raphson", f, raiz, f.derivada(), f.derivada().derivada())
        x0 = float(sugerencia.valores["x0"])
        self.assertGreater(f(x0) * f.derivada().derivada()(x0), 0)
        self.assertTrue(resolver_metodo_abierto("x^3 - x - 2", "Newton-Raphson", x0).convergio)

    def test_raiz_doble_no_se_ofrece_a_metodos_cerrados(self):
        f, puntos = _notables("(x - 1)^2")
        raiz = next(p for p in puntos if p.tipo == "raiz")
        self.assertEqual(sugerir_valores("Bisección", f, raiz).valores, {})


class PruebasProcedimientos(unittest.TestCase):
    def test_filas_y_detalles_de_los_cuatro_metodos(self):
        resultados = {
            "Bisección": resolver_biseccion("x^3 - x - 2", 1, 2),
            "Regula Falsi": resolver_reglafalsa("x^3 - x - 2", 1, 2),
            "Newton-Raphson": resolver_metodo_abierto("x^3 - x - 2", "Newton-Raphson", 2),
            "Secante": resolver_metodo_abierto("x^3 - x - 2", "Secante", 1, 2),
        }
        for metodo, resultado in resultados.items():
            with self.subTest(metodo=metodo):
                columnas = procedimientos.COLUMNAS[metodo]
                for paso in resultado.iteraciones:
                    self.assertEqual(len(procedimientos.fila(metodo, paso)), len(columnas))
                ultimo = procedimientos.detalle(metodo, resultado, len(resultado.iteraciones) - 1)
                self.assertTrue(any(estilo == "ok" for _, estilo in ultimo))
                texto = "\n".join(t for t, _ in procedimientos.resumen(metodo, resultado))
                self.assertIn(procedimientos.FORMULAS[metodo], texto)

    def test_newton_sustituye_los_valores(self):
        resultado = resolver_metodo_abierto("x^2 - 2", "Newton-Raphson", 1)
        texto = "\n".join(t for t, _ in procedimientos.detalle("Newton-Raphson", resultado, 0))
        self.assertIn("x₁ = x₀ − f(x₀) / f′(x₀)", texto)
        self.assertIn("= 1 − (−1) / 2", texto)
        self.assertIn("= 1.5", texto)

    def test_secante_numera_desde_x2(self):
        resultado = resolver_metodo_abierto("x^2 - 2", "Secante", 1, 2)
        texto = "\n".join(t for t, _ in procedimientos.detalle("Secante", resultado, 0))
        self.assertIn("x₀ = 1 y x₁ = 2", texto)
        self.assertIn("x₂ = x₁", texto)

    def test_orden_de_convergencia_observado(self):
        newton = resolver_metodo_abierto("x^2 - 2", "Newton-Raphson", 1, tolerancia=1e-12)
        secante = resolver_metodo_abierto("x^2 - 2", "Secante", 1, 2, tolerancia=1e-12)
        self.assertAlmostEqual(procedimientos.estimar_orden(newton), 2, delta=0.1)
        self.assertAlmostEqual(procedimientos.estimar_orden(secante), 1.618, delta=0.2)
        texto = "\n".join(t for t, _ in procedimientos.comparacion({"Newton-Raphson": newton, "Secante": secante}))
        self.assertIn("Coinciden", texto)

    def test_comparacion_detecta_raices_distintas(self):
        newton = resolver_metodo_abierto("x^2 - 4", "Newton-Raphson", 3)
        secante = resolver_metodo_abierto("x^2 - 4", "Secante", -3, -1)
        estilos = [e for _, e in procedimientos.comparacion({"Newton-Raphson": newton, "Secante": secante})]
        self.assertIn("aviso", estilos)

    def test_comparacion_de_metodos_cerrados(self):
        biseccion = resolver_biseccion("x^3 - x - 2", 1, 2)
        falsa = resolver_reglafalsa("x^3 - x - 2", 1, 2)
        lineas = procedimientos.comparacion({"Bisección": biseccion, "Regula Falsi": falsa})
        texto = "\n".join(t for t, _ in lineas)
        self.assertIn("Coinciden", texto)
        self.assertIn("razón ½", texto)
        self.assertEqual(procedimientos.evaluaciones("Bisección", biseccion), 2 + len(biseccion.iteraciones))

    def test_biseccion_decide_el_subintervalo(self):
        resultado = resolver_biseccion("x^2 - 2", 1, 2)
        texto = "\n".join(t for t, _ in procedimientos.detalle("Bisección", resultado, 0))
        self.assertIn("c = (a + b) / 2 = (1 + 2) / 2 = 1.5", texto)
        self.assertIn("la raíz está en [a, c]", texto)


if __name__ == "__main__":
    unittest.main()
