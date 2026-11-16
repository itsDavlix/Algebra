"""Pruebas del evaluador propio: normalización, derivación y escritura."""

import math
import unittest

from nucleo.expresiones import analizar, derivada_numerica, evaluar_valor


class PruebasNormalizacion(unittest.TestCase):
    def test_multiplicacion_implicita_y_funciones_sin_parentesis(self):
        casos = {
            "2x": "2*x", "3(x+1)": "3*(x + 1)", "x(x-1)": "x*(x - 1)",
            "xsin(x)": "x*sin(x)", "2pix": "2*pi*x", "sin x": "sin(x)",
            "sin 2x": "sin(2*x)", "√x": "sqrt(x)", "x²+x³": "x^2 + x^3",
            "2e3x": "2000*x", "sen(x)": "sin(x)", "log(x)": "ln(x)",
            "arccos(x)": "acos(x)", "raiz(x)": "sqrt(x)", "x^2 = 2": "x^2 - 2",
        }
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(analizar(entrada).texto, esperado)

    def test_notacion_legible(self):
        casos = {
            "x^3 - x - 2": "x³ − x − 2", "3*(x+1)^2": "3(x + 1)²",
            "sqrt(x) + abs(x)": "√x + |x|", "2*pi*x": "2πx",
        }
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(analizar(entrada).bonito, esperado)

    def test_errores_explican_la_causa(self):
        with self.assertRaisesRegex(ValueError, "Quisiste decir «sin»"):
            analizar("son(x)")
        with self.assertRaisesRegex(ValueError, "Falta cerrar 1 paréntesis"):
            analizar("(x+1")
        with self.assertRaisesRegex(ValueError, "argumento"):
            analizar("log10(x, 2)")

    def test_raices_impares_de_negativos_son_reales(self):
        self.assertAlmostEqual(analizar("(-8)^(1/3)")(0), -2)
        self.assertAlmostEqual(analizar("cbrt(x)")(-27), -3)
        self.assertAlmostEqual(analizar("raiz(x, 5)")(-32), -2)
        with self.assertRaises(ValueError):
            analizar("(-8)^(1/2)")(0)

    def test_valores_numericos_como_expresion(self):
        self.assertAlmostEqual(evaluar_valor("pi/2"), math.pi / 2)
        self.assertEqual(evaluar_valor("2,5"), 2.5)
        self.assertEqual(evaluar_valor("1e-6"), 1e-6)
        with self.assertRaisesRegex(ValueError, "sin x"):
            evaluar_valor("x + 1")


class PruebasDerivadas(unittest.TestCase):
    CASOS = {
        "x^3 - x - 2": "3x² − 1",
        "x^3 - 2x + ln(x+3)": "3x² − 2 + 1/(x + 3)",
        "sin(2x)": "2cos(2x)",
        "1/(x^2+1)": "−2x/(x² + 1)²",
        "x*sin(x)": "sin(x) + x·cos(x)",
        "e^(2x)": "2e^(2x)",
        "atan(x^2)": "2x/(1 + x⁴)",
    }

    def test_reglas_y_simplificacion(self):
        for entrada, esperado in self.CASOS.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(analizar(entrada).derivada().bonito, esperado)

    def test_coincide_con_diferencias_centradas(self):
        funciones = ("x^x", "sqrt(x^2+1)", "tan(x)*exp(-x)", "log(x, 3)",
                     "cosh(x)/x", "acos(x/2)", "si(x < 1, x^2, 2x - 1)", "cbrt(x - 4)")
        for texto in funciones:
            f = analizar(texto)
            df = f.derivada()
            for x in (0.3, 0.7, 1.4):
                with self.subTest(funcion=texto, x=x):
                    self.assertAlmostEqual(df(x), derivada_numerica(f, x), places=5)


if __name__ == "__main__":
    unittest.main()
