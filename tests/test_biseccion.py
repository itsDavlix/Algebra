"""Pruebas de raíces conocidas, convergencia y entradas de bisección."""

import math
import unittest

from nucleo.biseccion import (
    MAX_ITERACIONES, formatear_resultado_biseccion,
    preparar_funcion, resolver_biseccion,
)


class PruebasBiseccion(unittest.TestCase):
    def test_raices_conocidas_y_cota_del_error(self):
        casos = (
            ("x^2 = 2", 1, 2, math.sqrt(2)),
            ("x^3 - x - 2 = 0", 1, 2, 1.5213797068045676),
            ("cos(x) = x", 0, 1, 0.7390851332151607),
            ("exp(x) = 2", 0, 1, math.log(2)),
            ("x^2 - 2", -2, -1, -math.sqrt(2)),
            ("log(x)", 0.5, 2, 1),
        )
        for ecuacion, a, b, raiz in casos:
            with self.subTest(ecuacion=ecuacion, a=a):
                resultado = resolver_biseccion(ecuacion, a, b, 1e-10)
                self.assertTrue(resultado.convergio)
                self.assertLessEqual(abs(resultado.raiz - raiz), 1e-10)
                self.assertLessEqual(resultado.error, 1e-10)
                self.assertLessEqual(len(resultado.iteraciones), 35)
                for paso in resultado.iteraciones:
                    self.assertLessEqual(paso.a, raiz)
                    self.assertGreaterEqual(paso.b, raiz)
                    self.assertNotEqual(paso.fa < 0, paso.fb < 0)

    def test_conserva_la_mitad_con_cambio_de_signo(self):
        resultado = resolver_biseccion("x^2 - 2", 1, 2)
        for previo, siguiente in zip(resultado.iteraciones, resultado.iteraciones[1:]):
            self.assertAlmostEqual(siguiente.b - siguiente.a, (previo.b - previo.a) / 2)
            self.assertTrue(siguiente.a == previo.c or siguiente.b == previo.c)
            self.assertLessEqual(siguiente.error, previo.error)

    def test_raices_en_extremos(self):
        for a, b, raiz in ((2, 3, 2), (0, 2, 2)):
            with self.subTest(a=a, b=b):
                resultado = resolver_biseccion("x - 2", a, b)
                self.assertTrue(resultado.convergio)
                self.assertEqual(resultado.raiz, raiz)
                self.assertEqual(resultado.error, 0)
                self.assertEqual(resultado.iteraciones, ())

    def test_raiz_en_punto_medio(self):
        resultado = resolver_biseccion("x - 2", 1, 3)
        self.assertEqual(resultado.raiz, 2)
        self.assertEqual(len(resultado.iteraciones), 1)
        self.assertEqual(resultado.valor_funcion, 0)

    def test_mismos_signos_no_afirma_que_no_haya_raices(self):
        for funcion in ("x^2 + 1", "x^2 - 1", "1e-300*(x^2+1)"):
            with self.subTest(funcion=funcion):
                with self.assertRaisesRegex(ValueError, "no significa.*no tenga raíces"):
                    resolver_biseccion(funcion, -2, 2)

    def test_validacion_de_parametros(self):
        casos = (
            (1, 1, 1e-6, 100), (2, 1, 1e-6, 100),
            (1, 2, 0, 100), (1, 2, -1, 100),
            (math.nan, 2, 1e-6, 100), (1, math.inf, 1e-6, 100),
            (1, 2, math.inf, 100), (1, 2, math.nan, 100),
            (1, 2, 1e-6, 0), (1, 2, 1e-6, -1),
            (1, 2, 1e-6, 2.5), (1, 2, 1e-6, True),
            (1, 2, 1e-6, MAX_ITERACIONES + 1),
        )
        for parametros in casos:
            with self.subTest(parametros=parametros), self.assertRaises(ValueError):
                resolver_biseccion("x^2 - 2", *parametros)

    def test_limite_iteraciones_no_se_confunde_con_exito(self):
        resultado = resolver_biseccion("x^2 - 2", 1, 2, 1e-12, 1)
        self.assertFalse(resultado.convergio)
        self.assertEqual(resultado.raiz, 1.5)
        self.assertEqual(len(resultado.iteraciones), 1)
        self.assertIn("máximo de iteraciones", resultado.motivo)

    def test_residuo_pequeno_no_sustituye_error_en_x(self):
        normal = resolver_biseccion("x^2 - 2", 1, 2, 1e-8)
        escalado = resolver_biseccion("1e-200*(x^2 - 2)", 1, 2, 1e-8)
        self.assertEqual(normal.raiz, escalado.raiz)
        self.assertEqual(len(normal.iteraciones), len(escalado.iteraciones))
        self.assertLessEqual(abs(escalado.raiz - math.sqrt(2)), 1e-8)

    def test_dominio_invalido_y_discontinuidad_muestreada(self):
        for funcion, a, b in (("sqrt(x)", -1, 2), ("1/x", -1, 1),
                              ("log(x)", 0, 2), ("exp(x)-1", 1000, 1001)):
            with self.subTest(funcion=funcion), self.assertRaisesRegex(ValueError, "evaluar f"):
                resolver_biseccion(funcion, a, b)

    def test_intervalos_grandes_sin_desbordar_el_punto_medio(self):
        resultado = resolver_biseccion("x", -1.7e308, 1.7e308)
        self.assertTrue(resultado.convergio)
        self.assertEqual(resultado.raiz, 0)
        self.assertTrue(math.isfinite(resultado.iteraciones[0].error))
        resultado = resolver_biseccion("x/1e308 - 1.5", 1e308, 1.7e308, 1e295)
        self.assertTrue(resultado.convergio)
        self.assertLessEqual(abs(resultado.raiz / 1e308 - 1.5), 1e-12)

    def test_precision_insuficiente_no_se_confunde_con_exito(self):
        resultado = resolver_biseccion("x^2 - 2", 1, 2, 1e-30)
        self.assertFalse(resultado.convergio)
        self.assertIn("precisión numérica", resultado.motivo)
        self.assertGreater(resultado.error, resultado.tolerancia)

    def test_formato_incluye_pasos_y_estado_real(self):
        resultado = resolver_biseccion("x^2 - 2", 1, 2, 1e-20, 2)
        salida = formatear_resultado_biseccion(resultado)
        for texto in ("aproximación sin convergencia", "Comprobación: f(x)",
                      "ITERACIÓN 1", "ITERACIÓN 2", "conservar", "continua", "1e-20"):
            self.assertIn(texto, salida)
        resultado = resolver_biseccion("x - 1e-12", 1e-12, 1)
        self.assertIn("x ≈ 1e-12", formatear_resultado_biseccion(resultado))


class PruebasExpresiones(unittest.TestCase):
    def test_operadores_funciones_y_constantes(self):
        casos = (
            ("-x^2 + 2*x + 3", 2, 3), ("x**2 = 9", 3, 0),
            ("sen(pi/2) + cos(0) + tan(0)", 0, 2),
            ("sqrt(4) + raiz(9) + abs(-2)", 0, 7),
            ("ln(e) + log(e) + log10(100)", 0, 4),
            ("exp(0) + 2e-3", 0, 1.002),
            ("2×x − 6÷2", 3, 3), ("sin(π/2)", 0, 1),
        )
        for expresion, x, esperado in casos:
            with self.subTest(expresion=expresion):
                funcion, _ = preparar_funcion(expresion)
                self.assertAlmostEqual(funcion(x), esperado)

    def test_sintaxis_y_codigo_no_permitido(self):
        entradas = (
            "", "  ", "x +", "2x", "x =", "= 0", "x = 1 = 2", "x == 2",
            "y+1", "math.sin(x)", "__import__('os')", "x.__class__", "[x][0]",
            "(lambda: 1)()", "[x for x in range(3)]", "True", "'x'", "x < 0",
            "sqrt(x, 2)", "sin(x=1)", "1e309", "10j", "x % 2", "x // 2",
            "x" * 501, "+" * 60 + "x", " + ".join(["x"] * 60),
        )
        for entrada in entradas:
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                preparar_funcion(entrada)

    def test_valores_reales_finitos_y_limites_de_potencias(self):
        for expresion in ("10^100000000", "(-1)^0.5", "1/0", "sqrt(-1)",
                          "exp(1000)", "10^(10^100000)"):
            with self.subTest(expresion=expresion):
                funcion, _ = preparar_funcion(expresion)
                with self.assertRaises(ValueError):
                    funcion(1)


if __name__ == "__main__":
    unittest.main()
