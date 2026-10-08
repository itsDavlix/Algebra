"""Pruebas de resultados, pivoteo, validación y conservación de la entrada."""

import itertools
import random
import unittest
from fractions import Fraction
from unittest.mock import patch
from nucleo.determinantes import (
    determinante, recomendar_metodo, formatear_determinante,
)


class PruebasDeterminantes(unittest.TestCase):
    """Contrasta ambos métodos con casos conocidos y una fórmula independiente."""

    def test_casos_conocidos(self):
        """Incluye matrices singulares, intercambios y órdenes pequeños."""
        for matriz, esperado in [([[7]], 7), ([[1, 2], [3, 4]], -2),
                                ([[0, 1], [1, 0]], -1), ([[1, 2], [2, 4]], 0),
                                ([[6, 1, 1], [4, -2, 5], [2, 8, 7]], -306),
                                ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], 1)]:
            for metodo in ('cofactores', 'lu'):
                with self.subTest(metodo=metodo, matriz=matriz):
                    copia = [fila[:] for fila in matriz]
                    self.assertEqual(determinante(matriz, metodo), esperado)
                    self.assertEqual(matriz, copia)

    def test_formula_independiente(self):
        """Usa la fórmula de Leibniz para verificar signos y menores."""
        generador = random.Random(19)
        for n in range(1, 6):
            for _ in range(5):
                matriz = [[generador.randint(-5, 5) for _ in range(n)] for _ in range(n)]
                esperado = 0
                for permutacion in itertools.permutations(range(n)):
                    inversiones = sum(permutacion[i] > permutacion[j]
                                      for i in range(n) for j in range(i + 1, n))
                    termino = (-1) ** inversiones
                    for i in range(n):
                        termino *= matriz[i][permutacion[i]]
                    esperado += termino
                for metodo in ('cofactores', 'lu'):
                    self.assertEqual(determinante(matriz, metodo), esperado)

    def test_validaciones(self):
        """Rechaza matrices vacías, irregulares, no cuadradas y no finitas."""
        for matriz in ([], [[1, 2]], [[1], [2, 3]], [[float('inf')]], [[float('nan')]]):
            for metodo in ('cofactores', 'lu'):
                with self.assertRaises(ValueError):
                    determinante(matriz, metodo)
        with self.assertRaises(ValueError):
            determinante([[1]], '')

    def test_magnitudes_extremas(self):
        """Evita convertir determinantes pequeños en cero y permite resultados grandes."""
        for metodo in ('cofactores', 'lu'):
            valor = determinante([[1e-100, 0], [0, 1e-100]], metodo)
            self.assertGreater(valor, 0)
            self.assertNotEqual(formatear_determinante(valor), '0')
            self.assertGreater(determinante([[1e200, 0], [0, 1e200]], metodo), 0)
            self.assertEqual(determinante([[0.5, 0], [0, 0.25]], metodo), Fraction(1, 8))

    def test_recomendaciones_y_limite(self):
        """Comprueba la sugerencia y la salida controlada del cálculo factorial."""
        self.assertEqual(recomendar_metodo([[1]])[0], 'cofactores')
        matriz = [[2 if i == j else 1 for j in range(4)] for i in range(4)]
        self.assertEqual(recomendar_metodo(matriz)[0], 'lu')
        with patch('nucleo.determinantes.MAX_EXPANSIONES', 1):
            with self.assertRaisesRegex(ValueError, 'Seleccioná LU'):
                determinante(matriz, 'cofactores')
        self.assertEqual(determinante(matriz, 'lu'), 5)
