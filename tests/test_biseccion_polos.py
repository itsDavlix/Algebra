"""Pruebas para evitar declarar raíz una aproximación cercana a un polo."""

import unittest

from nucleo.biseccion import resolver_biseccion


class PruebasPolosBiseccion(unittest.TestCase):
    """Distingue polos detectables de raíces con residuo grande."""

    def test_polos_no_convergen(self):
        """Marca como discontinuidades posibles los polos pedidos."""
        for expresion, a, b in (("tan(x)", 1, 2), ("1/(x-0.3)", 0, 1)):
            with self.subTest(expresion=expresion):
                resultado = resolver_biseccion(expresion, a, b)
                self.assertFalse(resultado.convergio)
                self.assertIn("discontinuidad", resultado.motivo.lower())

    def test_raices_escalada_y_multiple_si_convergen(self):
        """No rechaza una raíz por tener magnitudes funcionales grandes o pequeñas."""
        for expresion, a, b in (("1e9*(x-0.3)", 0, 1), ("(x-1)^3", 0, 3)):
            with self.subTest(expresion=expresion):
                resultado = resolver_biseccion(expresion, a, b)
                self.assertTrue(resultado.convergio)
                self.assertAlmostEqual(resultado.raiz, 0.3 if "1e9" in expresion else 1, places=5)

