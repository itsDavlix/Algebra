"""Pruebas básicas del núcleo. Ejecutar: python -m unittest discover -s tests -v"""

import unittest

from nucleo.matrices import leer_matriz, matriz_inversa, multiplicar_matrices
from nucleo.numeros import convertir_numero
from nucleo.romanos import operar_romanos
from nucleo.sistemas import resolver_sistema_gauss_jordan_con_pasos
from nucleo.vectores import leer_vector, multiplicar_vector_escalar
from nucleo.comprobaciones import (
    numeros_aproximadamente_iguales,
    vectores_aproximadamente_iguales,
    matrices_aproximadamente_iguales,
    matriz_identidad,
)


class ValidacionesTest(unittest.TestCase):
    def test_vector_valido(self):
        self.assertEqual(leer_vector("1, 2, -3.5"), [1.0, 2.0, -3.5])

    def test_vector_con_coma_vacia(self):
        with self.assertRaises(ValueError):
            leer_vector("1,,2")

    def test_numero_no_finito(self):
        for texto in ("nan", "inf", "-inf"):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                convertir_numero(texto)

    def test_matriz_no_rectangular(self):
        with self.assertRaises(ValueError):
            leer_matriz("1 2\n3")

    def test_producto_incompatible(self):
        with self.assertRaises(ValueError):
            multiplicar_matrices([[1, 2]], [[1, 2]])

    def test_matriz_singular(self):
        with self.assertRaises(ValueError):
            matriz_inversa([[1, 2], [2, 4]])

    def test_desbordamiento(self):
        with self.assertRaises(ValueError):
            multiplicar_vector_escalar([1e308], 1e308)

    def test_sistema_valido(self):
        solucion, tipo, _, _ = resolver_sistema_gauss_jordan_con_pasos(
            [[2, 1], [1, -1]], [[5], [1]]
        )
        self.assertEqual(tipo, "unica")
        self.assertAlmostEqual(solucion[0][0], 2.0)
        self.assertAlmostEqual(solucion[1][0], 1.0)

    def test_romano_no_canonico(self):
        with self.assertRaises(ValueError):
            operar_romanos("IIII", "I", "+")

    def test_resultado_romano_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            operar_romanos("V", "X", "-")

    def test_comprobacion_numerica_con_tolerancia(self):
        self.assertTrue(numeros_aproximadamente_iguales(0.1 + 0.2, 0.3))
        self.assertFalse(numeros_aproximadamente_iguales(1, 1.1))

    def test_comprobacion_vectores(self):
        self.assertTrue(vectores_aproximadamente_iguales([1, 2], [1.0, 2.0]))
        self.assertFalse(vectores_aproximadamente_iguales([1, 2], [1, 3]))
        self.assertFalse(vectores_aproximadamente_iguales([1, 2], [1, 2, 3]))

    def test_comprobacion_matrices(self):
        self.assertTrue(
            matrices_aproximadamente_iguales(
                [[1, 0], [0, 1]],
                matriz_identidad(2),
            )
        )
        self.assertFalse(
            matrices_aproximadamente_iguales(
                [[1, 0], [0, 2]],
                matriz_identidad(2),
            )
        )

    def test_comprobacion_inversa(self):
        inversa = matriz_inversa([[2, 0], [0, 4]])
        producto = multiplicar_matrices([[2, 0], [0, 4]], inversa)
        self.assertTrue(matrices_aproximadamente_iguales(producto, matriz_identidad(2)))


if __name__ == "__main__":
    unittest.main()
