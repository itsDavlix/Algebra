"""Pruebas de clasificación y tolerancias relativas de sistemas lineales."""

import unittest

from nucleo.matrices import multiplicar_matrices
from nucleo.sistemas import (
    ErrorSistemaIncompatible, resolver_sistema_gauss_jordan_con_pasos,
)


class PruebasSistemas(unittest.TestCase):
    """Verifica soluciones únicas, particulares e incompatibilidad."""

    def test_solucion_unica(self):
        """Resuelve un sistema cuadrado de rango completo."""
        solucion, tipo, pivotes, pasos = resolver_sistema_gauss_jordan_con_pasos(
            [[2, 1], [1, -1]], [[5], [1]]
        )
        self.assertEqual(tipo, "unica")
        self.assertEqual(pivotes, [0, 1])
        self.assertAlmostEqual(solucion[0][0], 2)
        self.assertAlmostEqual(solucion[1][0], 1)
        self.assertTrue(pasos)

    def test_solucion_particular_valida_para_sistema_infinito(self):
        """La solución particular devuelta satisface un sistema subdeterminado."""
        a, b = [[1, 1, 1]], [[3]]
        solucion, tipo, _, pasos = resolver_sistema_gauss_jordan_con_pasos(a, b)
        self.assertEqual(tipo, "infinitas")
        self.assertEqual(multiplicar_matrices(a, solucion), b)
        self.assertTrue(pasos)

    def test_incompatibilidad_conserva_pasos(self):
        """La excepción de incompatibilidad expone el procedimiento parcial."""
        with self.assertRaises(ErrorSistemaIncompatible) as contexto:
            resolver_sistema_gauss_jordan_con_pasos([[1], [1]], [[1], [2]])
        self.assertTrue(contexto.exception.pasos)
        self.assertIn("incompatible", contexto.exception.pasos[-1])

    def test_sistema_pequeno_con_solucion_unica(self):
        """No confunde pivotes pequeños con cero."""
        a = [[1e-11, 0], [0, 1e-11]]
        b = [[1e-11], [2e-11]]
        solucion, tipo, _, _ = resolver_sistema_gauss_jordan_con_pasos(a, b)
        self.assertEqual(tipo, "unica")
        self.assertEqual(solucion, [[1.0], [2.0]])

    def test_incompatibilidad_pequena_se_detecta_con_escala_aumentada(self):
        """Detecta términos independientes relevantes en una matriz pequeña."""
        a = [[1e-11, 1e-11], [1e-11, 1e-11]]
        b = [[1e-11], [2e-11]]
        with self.assertRaises(ErrorSistemaIncompatible):
            resolver_sistema_gauss_jordan_con_pasos(a, b)

