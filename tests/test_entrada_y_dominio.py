"""Fase 2: el texto del banco se pega tal cual, el dominio se valida antes de iterar y
Gauss-Jordan puede operar con fracciones exactas. Los casos salen del documento."""

import unittest
from fractions import Fraction as F

from nucleo.analisis import comprobar_continuidad, discontinuidades
from nucleo.biseccion import resolver_biseccion
from nucleo.expresiones import analizar
from nucleo.procedimientos import resumen
from nucleo.procedimientos_sistemas import puede_ser_exacto, resolver_directo, resumen_directo
from nucleo.reglafalsa import resolver_reglafalsa
from nucleo.sistemas_texto import leer_sistema

P1_E12 = ("0.5x - 0.75y + 2z – (1/3)w = 181/60\n1.5x + y - 2.5z + (2/3)w = -0.75\n"
          "-x + 0.5y + (3/4)z - 2w = 7/30\n(2/3)x - 2y + 0.5z + 1.25w = 253/120")
P1_E13 = "12x + 6y + 4z + 3w = 9\n30x + 20y + 15z + 12w = 23\n20x + 15y + 12z + 10w = 16\n105x + 84y + 70z + 60w = 87"
P1_E14 = "2x - 3y + z + 4w = 7\n4x - y - 3z + 2w = 5\n-2x + 8y - 6z - 10w = -16\n3x + 2y - 4z + w = 4"
P1_E15 = "(1/2)x₂ + x₃ − x₄ = 3\n2x₁ + x₂ − x₃ + (1/2)x₄ = 5\nx₁ − x₂ + 2x₃ + x₄ = 1\n(1/2)x₁ + 2x₂ + x₃ − x₄ = 4"


class PruebasLecturaDeSistemas(unittest.TestCase):
    def test_coeficientes_entre_parentesis_y_guion_largo(self):
        variables, A, b = leer_sistema(P1_E12, exacto=True)
        self.assertEqual(variables, ["x", "y", "z", "w"])
        self.assertEqual(A[0], [F(1, 2), F(-3, 4), F(2), F(-1, 3)])
        self.assertEqual(b, [F(181, 60), F(-3, 4), F(7, 30), F(253, 120)])
        _, A, _ = leer_sistema(P1_E15)
        self.assertEqual(A[0], [0.0, 0.5, 1.0, -1.0])
        _, A, b = leer_sistema("2x + (−3/4)y = (7/5)\nx - y = 0", exacto=True)
        self.assertEqual((A[0], b[0]), ([F(2), F(-3, 4)], F(7, 5)))

    def test_por_defecto_sigue_en_decimales(self):
        _, A, b = leer_sistema("0.5x + y = 1\nx - y = 0")
        self.assertIsInstance(A[0][0], float)
        self.assertIsInstance(b[0], float)


class PruebasExpresionesDelDocumento(unittest.TestCase):
    def test_superindices_punto_y_seno(self):
        casos = {"eˣ − 3x²": "e^x − 3x²", "cos(x) − x·eˣ": "cos(x) − x·e^x", "x⁴ − 3x² − 3": "x⁴ − 3x² − 3",
                 "x.e^(−x) − 0.2": "x·e^(−x) − 0.2", "e⁻ˣ + x": "e^(−x) + x",
                 "ln(x) + sen(x) = 1.2": "ln(x) + sin(x) − 1.2"}
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(analizar(texto).bonito, esperado)

    def test_igualdad_con_constante_se_simplifica(self):
        self.assertEqual(analizar("x² − 3 sen(x) − ln(x + 2) = 0").bonito, "x² − 3sin(x) − ln(x + 2)")
        self.assertEqual(analizar("ln(x + 1) / (x² − 4) = −0.1").bonito, "ln(x + 1)/(x² − 4) + 0.1")
        self.assertEqual(analizar("x = 2x").bonito, "x − 2x")

    def test_exponente_perdido_avisa_sin_bloquear(self):
        expresion = analizar("e(-x) - x")
        self.assertIn("e^(…)", expresion.aviso)
        self.assertAlmostEqual(expresion(1), -1 * 2.718281828459045 - 1, places=9)
        self.assertEqual(analizar("e^(-x) - x").aviso, "")
        self.assertEqual(analizar("sec(x) - 2").aviso, "")


class PruebasContinuidad(unittest.TestCase):
    def test_parte_iv_rechaza_intervalos_con_polo(self):
        casos = (("sen(x) / ln(x) = 1", 0.5, 1.5, "x = 1"), ("ln(x + 1)/(x² − 4) = −0.1", 1, 3, "x = 2"),
                 ("e^(1/x) + 2x/tan(x) = 2", -1, 1, "x = 0"), ("tan(x) - x", 4, 5, "4.71239"))
        for texto, a, b, punto in casos:
            with self.subTest(texto=texto):
                mensaje = comprobar_continuidad(analizar(texto), a, b)
                self.assertIn("no es continua", mensaje)
                self.assertIn(punto, mensaje)
                for metodo in (resolver_biseccion, resolver_reglafalsa):
                    with self.assertRaisesRegex(ValueError, "Bolzano no aplica"):
                        metodo(texto, a, b, 1e-6, 100)

    def test_intervalos_correctos_de_la_parte_iv(self):
        for texto, a, b, raiz in (("sen(x) / ln(x) = 1", 2, 3, 2.2191076), ("ln(x + 1)/(x² − 4) = −0.1", 0, 1, 0.46051884),
                                  ("(x + 4)/(x − 1) = 0", -5, -3, -4.0)):
            with self.subTest(texto=texto):
                self.assertIsNone(comprobar_continuidad(analizar(texto), a, b))
                self.assertAlmostEqual(resolver_biseccion(texto, a, b, 1e-6, 100).raiz, raiz, places=5)

    def test_dominio_descrito(self):
        self.assertIn("x > 0", comprobar_continuidad(analizar("x ln(x) - 1"), -1, 2))
        self.assertEqual(discontinuidades(analizar("x^3 - 1"), 0, 2), [])


class PruebasGaussJordanExacto(unittest.TestCase):
    def test_fracciones_exactas_del_ejercicio_12(self):
        variables, A, b = leer_sistema(P1_E12)
        self.assertTrue(puede_ser_exacto(A, b))
        r = resolver_directo(A, b, variables, exacto=True)
        self.assertEqual(r.exacta, (F(162683, 104610), F(-16458, 17435), F(96608, 156915), F(-94081, 104610)))
        self.assertEqual(r.residuo, 0)
        texto = "\n".join(l for l, _ in resumen_directo(r))
        self.assertIn("x = 162683/104610 ≈ 1.555138132", texto)
        self.assertIn("fracciones exactas", texto)
        self.assertTrue(any("1/2" in paso for paso in r.pasos))          # los pasos muestran fracciones

    def test_mal_condicionado_sale_exacto(self):
        variables, A, b = leer_sistema(P1_E13)
        self.assertEqual(resolver_directo(A, b, variables, exacto=True).exacta, (1, -2, 3, -1))

    def test_solucion_general_con_nombres_del_sistema(self):
        variables, A, b = leer_sistema(P1_E14)
        r = resolver_directo(A, b, variables, exacto=True)
        self.assertEqual(r.tipo, "infinitas")
        general = r.pasos[-1].split("Solución general:")[1]
        self.assertIn("x = 6 − 3·t₁", general)
        self.assertIn("y = 17/5 − 8/5·t₁", general)
        self.assertIn("w = t₁  (libre)", general)

    def test_ceros_de_redondeo_se_muestran_como_cero(self):
        variables, A, b = leer_sistema("x + 4y -z + 3w = 6\n3x -2y + z + 3w = 22\n-3x + 4y + 6z + 3w = 41\n"
                                       "-x + 3y + 4z + w = 22")
        self.assertEqual(resolver_directo(A, b, variables).solucion[0], 0.0)

    def test_sistemas_grandes_siguen_en_decimales(self):
        n = 11
        A = [[float(n + 1 if i == j else 1) for j in range(n)] for i in range(n)]
        self.assertFalse(puede_ser_exacto(A, [1.0] * n))
        self.assertEqual(resolver_directo(A, [1.0] * n, [f"x{i}" for i in range(n)], exacto=True).exacta, ())


class PruebasResumenDeRaices(unittest.TestCase):
    def test_raiz_y_residuo_en_el_procedimiento(self):
        r = resolver_biseccion("e^(x/2) + sen(2x) = 3", 2, 3, 1e-6, 100)      # P3-E14
        texto = "\n".join(l for l, _ in resumen("Bisección", r))
        self.assertIn("Raíz aproximada: x ≈ 2.673062", texto)
        self.assertIn("|f(x)| =", texto)
        self.assertIn("f es empinada cerca de la raíz", texto)


if __name__ == "__main__":
    unittest.main()
