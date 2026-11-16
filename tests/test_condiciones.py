"""Pruebas del evaluador por tramos si(condición, valor, otro valor)."""

import unittest

from nucleo.biseccion import preparar_funcion, resolver_biseccion
from nucleo.reglafalsa import resolver_reglafalsa


class PruebasCondiciones(unittest.TestCase):
    def test_comparaciones_y_limites(self):
        for op, esperado in (("<", 2), (">", 2), ("<=", 1), (">=", 1),
                             ("==", 1), ("!=", 2), ("≤", 1), ("≥", 1), ("≠", 2)):
            with self.subTest(op=op):
                f, _ = preparar_funcion(f"si(x {op} 0, 1, 2)")
                self.assertEqual(f(0), esperado)

    def test_solo_evalua_la_rama_elegida(self):
        f, _ = preparar_funcion("si(x < 0, sqrt(-x), sqrt(x))")
        self.assertEqual(f(-4), 2)
        self.assertEqual(f(9), 3)
        f, _ = preparar_funcion("si(-1 < x <= 1, x, si(x > 1, 2, -2))")
        self.assertEqual([f(x) for x in (-2, 0, 1, 3)], [-2, 0, 1, 2])

    def test_igualdad_con_condicion_en_ambos_metodos(self):
        for resolver in (resolver_biseccion, resolver_reglafalsa):
            resultado = resolver("si(x <= 0, -x, x) = 2", 1, 3)
            self.assertTrue(resultado.convergio)
            self.assertEqual(resultado.raiz, 2)

    def test_rechaza_comparaciones_como_raices_y_codigo_arbitrario(self):
        for texto in ("x < 0", "1 + (x > 0)", "si(x, 1, 2)",
                      "si(x < 0, 1)", "si(x < 0, 1, 2, 3)",
                      "si(x < 0, __import__('os'), 0)",
                      "si(x < 0, x.real, 0)", "si(x is 0, 1, 2)",
                      "si(x < 0, True, 2)", "si(x <= 0, 1, 2) = 1 = 2"):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                preparar_funcion(texto)


if __name__ == "__main__":
    unittest.main()
