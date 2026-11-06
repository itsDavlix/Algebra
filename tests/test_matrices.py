"""Pruebas de formato, inversión y condición numérica de matrices."""

import random
import unittest

from nucleo.matrices import (
    matriz_inversa_con_pasos, multiplicar_matrices, norma_1, numero_condicion_1,
)


class PruebasMatrices(unittest.TestCase):
    """Comprueba inversión, pivoteo, escala y advertencias de condición."""

    def test_inversa_conocida_y_pivoteo(self):
        """Calcula inversas conocidas, incluido un intercambio de filas necesario."""
        inversa, _ = matriz_inversa_con_pasos([[4, 7], [2, 6]])
        esperada = [[0.6, -0.7], [-0.2, 0.4]]
        for fila, fila_esperada in zip(inversa, esperada):
            for valor, valor_esperado in zip(fila, fila_esperada):
                self.assertAlmostEqual(valor, valor_esperado)
        inversa, _ = matriz_inversa_con_pasos([[0, 1], [1, 0]])
        self.assertEqual(inversa, [[0.0, 1.0], [1.0, 0.0]])

    def test_inversa_reproduce_identidad_en_matrices_enteras(self):
        """Verifica 80 matrices invertibles generadas de forma reproducible."""
        generador = random.Random(42017)
        for caso in range(80):
            orden = generador.randint(1, 5)
            matriz = [
                [generador.randint(-4, 4) for _ in range(orden)]
                for _ in range(orden)
            ]
            for i in range(orden):
                matriz[i][i] = (
                    sum(abs(valor) for j, valor in enumerate(matriz[i]) if j != i)
                    + generador.randint(1, 4)
                )
            inversa, _ = matriz_inversa_con_pasos(matriz)
            producto = multiplicar_matrices(matriz, inversa)
            for i, fila in enumerate(producto):
                for j, valor in enumerate(fila):
                    with self.subTest(caso=caso, i=i, j=j):
                        self.assertAlmostEqual(valor, 1.0 if i == j else 0.0, places=8)

    def test_matriz_singular_y_no_cuadrada(self):
        """Rechaza matrices sin inversa y matrices rectangulares."""
        with self.assertRaisesRegex(ValueError, "singular"):
            matriz_inversa_con_pasos([[1, 2], [2, 4]])
        with self.assertRaisesRegex(ValueError, "cuadrada"):
            matriz_inversa_con_pasos([[1, 2, 3], [4, 5, 6]])

    def test_matriz_pequena_no_se_declara_singular(self):
        """La tolerancia del pivote sigue la escala de la matriz."""
        inversa, _ = matriz_inversa_con_pasos([[1e-11, 0], [0, 1e-11]])
        self.assertEqual(inversa, [[1e11, 0.0], [0.0, 1e11]])

    def test_numero_condicion_y_aviso(self):
        """Advierte para Hilbert 8×8, pero no para una matriz bien condicionada."""
        hilbert = [[1 / (i + j + 1) for j in range(8)] for i in range(8)]
        inversa_hilbert, pasos_hilbert = matriz_inversa_con_pasos(hilbert)
        self.assertGreater(numero_condicion_1(hilbert, inversa_hilbert), 1e8)
        self.assertTrue(any("ADVERTENCIA" in paso for paso in pasos_hilbert))

        matriz = [[2, 1], [1, 3]]
        inversa, pasos = matriz_inversa_con_pasos(matriz)
        self.assertEqual(norma_1(matriz), 4)
        self.assertFalse(any("ADVERTENCIA" in paso for paso in pasos))
