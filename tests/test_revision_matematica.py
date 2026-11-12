"""Regresiones y comprobaciones independientes de la revisión matemática."""

import math
import unittest
from unittest.mock import Mock, patch

from nucleo.biseccion import resolver_biseccion
from nucleo.metodosabiertos import resolver_metodo_abierto
from nucleo.reglafalsa import resolver_reglafalsa
from nucleo.matrices import matriz_inversa, multiplicar_matrices, matriz_a_texto
from nucleo.sistemas import ErrorSistemaIncompatible, resolver_sistema_gauss_jordan, solucion_general_texto
from nucleo.vectores import norma_vector, norma_vector_con_pasos


class RevisionMatematica(unittest.TestCase):
    def test_ejercicio_del_usuario_con_cuatro_metodos(self):
        ecuacion = "x^3 - 2*x - 5"
        resultados = (
            resolver_biseccion(ecuacion, 2, 3, 1e-10),
            resolver_reglafalsa(ecuacion, 2, 3, 1e-10),
            resolver_metodo_abierto(ecuacion, "Newton-Raphson", 2, derivada="3*x^2-2", tolerancia=1e-10),
            resolver_metodo_abierto(ecuacion, "Secante", 2, 3, tolerancia=1e-10),
        )
        for r in resultados:
            with self.subTest(metodo=type(r).__name__):
                self.assertTrue(r.convergio, r.motivo)
                self.assertAlmostEqual(r.raiz, 2.0945514815423265, places=8)
                self.assertLess(abs(r.raiz**3 - 2*r.raiz - 5), 2e-9)

    def test_regla_falsa_no_confunde_pasos_pequenos_con_raiz(self):
        r = resolver_reglafalsa("x^10 - 1", 0, 10)
        self.assertFalse(r.convergio)
        self.assertGreater(abs(r.valor_funcion), 0.9)

    def test_inversa_es_invariante_ante_escala_uniforme(self):
        for escala in (1e-12, 1, 1e12):
            a = [[2*escala, escala], [escala, 3*escala]]
            inversa = matriz_inversa(a)
            for producto in (multiplicar_matrices(a, inversa), multiplicar_matrices(inversa, a)):
                for i in range(2):
                    for j in range(2):
                        with self.subTest(escala=escala, i=i, j=j):
                            self.assertAlmostEqual(producto[i][j], float(i == j), places=10)

    def test_sistema_es_invariante_ante_escala_uniforme(self):
        for escala in (1e-12, 1, 1e12):
            a = [[2*escala, escala], [escala, 3*escala]]
            b = [[escala], [-7*escala]]
            x, tipo, _ = resolver_sistema_gauss_jordan(a, b)
            with self.subTest(escala=escala):
                self.assertEqual(tipo, "unica")
                self.assertAlmostEqual(x[0][0], 2)
                self.assertAlmostEqual(x[1][0], -3)

    def test_parametros_no_desaparecen_por_constante_grande(self):
        texto = solucion_general_texto([[1, 1]], [[1e12]])
        self.assertIn("− t1", texto)
        self.assertIn("x2 = t1", texto)

    def test_coeficientes_grandes_no_ocultan_incompatibilidad(self):
        with self.assertRaises(ErrorSistemaIncompatible):
            resolver_sistema_gauss_jordan([[1e12], [1e12]], [[1], [2]])

    def test_raiz_exacta_conserva_el_ultimo_paso_de_regla_falsa(self):
        r = resolver_reglafalsa("x^2 - 1", 0, 2, tolerancia=1e-30)
        self.assertTrue(r.convergio)
        self.assertEqual(r.error, r.iteraciones[-1].error)

    def test_norma_evitar_desborde_y_subdesborde(self):
        for escala in (1e-200, 1, 1e200):
            v = [3*escala, 4*escala]
            with self.subTest(escala=escala):
                self.assertTrue(math.isclose(norma_vector(v), 5*escala, rel_tol=1e-14))
                resultado, pasos = norma_vector_con_pasos(v)
                self.assertTrue(math.isclose(resultado, 5*escala, rel_tol=1e-14))
                self.assertFalse(any("✗" in paso for paso in pasos))

    def test_matriz_mostrada_conserva_componentes_de_distinta_escala(self):
        self.assertEqual(matriz_a_texto([[1e12], [1]]).splitlines()[1], "[ 1 ]")

    @patch("interfaz.pestanaEcuaciones.mostrar_texto")
    def test_solucion_copiada_conserva_precision(self, mostrar):
        from interfaz.pestanaEcuaciones import PestanaEcuaciones
        p = PestanaEcuaciones.__new__(PestanaEcuaciones)
        p.txt_a, p.txt_b, p.txt_x, p.txt_resultado = Mock(), Mock(), Mock(), Mock()
        p.txt_a.get.return_value = "3"
        p.txt_b.get.return_value = "1"
        p._accion_resolver()
        x = float(p.txt_x.insert.call_args.args[1])
        self.assertLess(abs(3*x - 1), 1e-14)


if __name__ == "__main__":
    unittest.main()
