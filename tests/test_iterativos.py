"""Jacobi y Gauss-Seidel contra las tablas de la presentación y los ejemplos paso a paso."""

import unittest

from nucleo import procedimientos_sistemas as ps
from nucleo.ejercicios import GUIA
from nucleo.iterativos import (
    dominancia_diagonal, matriz_iteracion, radio_espectral, reordenar_para_dominancia, resolver_iterativo,
)
from nucleo.sistemas_texto import ecuacion_texto, leer_sistema, leer_vector

# Tablas de los documentos (6 decimales). Las tablas son correctas; algunas
# diapositivas paso a paso no (ver test_errores_de_las_diapositivas).
TABLA_JACOBI = [
    (0.600000, 2.272727, -1.100000, 1.875000),
    (1.047273, 1.715909, -0.805227, 0.885227),
    (0.932636, 2.053306, -1.049341, 1.130881),
    (1.015199, 1.953696, -0.968109, 0.973843),
    (0.988991, 2.011415, -1.010286, 1.021351),
]
TABLA_SEIDEL = [
    (0.600000, 2.327273, -0.987273, 0.878864),
    (1.030182, 2.036938, -1.014456, 0.984341),
    (1.006585, 2.003555, -1.002527, 0.998351),
    (1.000861, 2.000298, -1.000307, 0.999850),
    (1.000091, 2.000021, -1.000031, 0.999988),
]


class PruebasLectura(unittest.TestCase):
    def test_formatos_de_ecuaciones(self):
        variables, A, b = leer_sistema(GUIA)
        self.assertEqual(variables, ["x1", "x2", "x3", "x4"])
        self.assertEqual(A[0], [10, -1, 2, 0])
        self.assertEqual(b, [6, 25, -11, 15])
        variables, A, b = leer_sistema("-3x - y + 4z + 5w = -6\n2y = x + 1")
        self.assertEqual(variables, ["x", "y", "z", "w"])
        self.assertEqual(A[1], [-1, 2, 0, 0])
        self.assertEqual(b[1], 1)
        _, A, b = leer_sistema("1/2a + 0.5b = 1\na - b = 0")
        self.assertEqual(A[0], [0.5, 0.5])
        _, A, b = leer_sistema("2 1 | 3\n1 -1 | 0")
        self.assertEqual((A, b), ([[2, 1], [1, -1]], [3, 0]))

    def test_errores_claros(self):
        for texto, fragmento in (("2x + = 3", "no se entiende"), ("2x + y", "«=»"), ("", "Escribe")):
            with self.subTest(texto=texto), self.assertRaisesRegex(ValueError, fragmento):
                leer_sistema(texto)

    def test_vector_inicial(self):
        self.assertEqual(leer_vector("", 3), [0, 0, 0])
        self.assertEqual(leer_vector("(1, 1/2, -2)", 3), [1, 0.5, -2])
        with self.assertRaises(ValueError):
            leer_vector("1, 2", 3)

    def test_ecuacion_legible(self):
        self.assertEqual(ecuacion_texto([-3, -1, 4, 5], -6, ["x", "y", "z", "w"]), "−3x − y + 4z + 5w = −6")


class PruebasMetodos(unittest.TestCase):
    def setUp(self):
        self.variables, self.A, self.b = leer_sistema(GUIA)

    def test_tablas_de_la_clase(self):
        for metodo, tabla in (("Jacobi", TABLA_JACOBI), ("Gauss-Seidel", TABLA_SEIDEL)):
            r = resolver_iterativo(self.A, self.b, metodo, max_iteraciones=5)
            for paso, esperado in zip(r.iteraciones, tabla):
                for valor, referencia in zip(paso.x, esperado):
                    with self.subTest(metodo=metodo, k=paso.k):
                        self.assertAlmostEqual(valor, referencia, places=6)

    def test_converge_a_la_solucion_exacta(self):
        for metodo in ("Jacobi", "Gauss-Seidel"):
            r = resolver_iterativo(self.A, self.b, metodo, tolerancia=1e-10, max_iteraciones=200)
            self.assertTrue(r.convergio)
            for valor, exacto in zip(r.solucion, (1, 2, -1, 1)):
                self.assertAlmostEqual(valor, exacto, places=9)
            self.assertLessEqual(r.iteraciones[-1].residuo, 1e-10)

    def test_gauss_seidel_usa_valores_nuevos(self):
        r = resolver_iterativo(self.A, self.b, "Gauss-Seidel", max_iteraciones=1)
        sustitucion_x2 = r.iteraciones[0].sustituciones[1]
        usado_x1 = next(t for t in sustitucion_x2.terminos if t[0] == 0)
        self.assertTrue(usado_x1[3])
        self.assertAlmostEqual(usado_x1[2], 0.6)
        jacobi = resolver_iterativo(self.A, self.b, "Jacobi", max_iteraciones=1)
        self.assertFalse(any(t[3] for s in jacobi.iteraciones[0].sustituciones for t in s.terminos))

    def test_dominancia_y_radio_espectral(self):
        self.assertTrue(all(f.cumple for f in dominancia_diagonal(self.A)))
        self.assertLess(radio_espectral(matriz_iteracion(self.A, "Gauss-Seidel")),
                        radio_espectral(matriz_iteracion(self.A, "Jacobi")))
        self.assertAlmostEqual(radio_espectral([[0.5, 0], [0, -0.25]]), 0.5, places=6)

    def test_diagonal_nula_y_divergencia(self):
        with self.assertRaisesRegex(ValueError, "Reordena"):
            resolver_iterativo([[0, 1], [1, 0]], [1, 1], "Jacobi")
        r = resolver_iterativo([[1, 3], [2, 1]], [4, 3], "Jacobi", max_iteraciones=200)
        self.assertFalse(r.convergio)

    def test_reordenar_no_cambia_la_solucion(self):
        A, b = [[1, 10], [10, 1]], [12, 21]
        A2, b2, permutacion, rho = reordenar_para_dominancia(A, b, "Jacobi")
        self.assertEqual(permutacion, (1, 0))
        self.assertLess(rho, 1)
        r = resolver_iterativo(A2, b2, "Jacobi", tolerancia=1e-10, max_iteraciones=200)
        self.assertAlmostEqual(r.solucion[0], 2, places=8)
        self.assertAlmostEqual(r.solucion[1], 1, places=8)


class PruebasProcedimiento(unittest.TestCase):
    def setUp(self):
        self.variables, self.A, self.b = leer_sistema(GUIA)

    def test_despejes_como_en_la_clase(self):
        despejes = [ps.despeje(self.A, self.b, self.variables, i) for i in range(4)]
        self.assertEqual(despejes, ["x₁ = (6 + x₂ − 2x₃) / 10", "x₂ = (25 + x₁ + x₃ − 3x₄) / 11",
                                    "x₃ = (−11 − 2x₁ + x₂ + x₄) / 10", "x₄ = (15 − 3x₂ + x₃) / 8"])

    def test_sustituciones_de_la_iteracion_2(self):
        r = resolver_iterativo(self.A, self.b, "Jacobi", variables=self.variables)
        texto = "\n".join(t for t, _ in ps.detalle_iterativo(r, 2))
        self.assertIn("x₁⁽²⁾ = (6 + 2.272727 − 2(−1.100000)) / 10 = 1.047273", texto)
        self.assertIn("x₂⁽²⁾ = (25 + 0.600000 − 1.100000 − 3(1.875000)) / 11 = 1.715909", texto)

    def test_errores_de_las_diapositivas(self):
        """Las diapositivas 15, 20 y 21 muestran valores que no siguen de sus propias fórmulas."""
        jacobi = resolver_iterativo(self.A, self.b, "Jacobi", max_iteraciones=2).iteraciones[1].x
        self.assertNotAlmostEqual(jacobi[1], 1.704545, places=4)   # diapositiva 15: x₂⁽²⁾
        self.assertNotAlmostEqual(jacobi[3], 0.906818, places=4)   # diapositiva 15: x₄⁽²⁾
        seidel = resolver_iterativo(self.A, self.b, "Gauss-Seidel", max_iteraciones=2).iteraciones
        self.assertNotAlmostEqual(seidel[0].x[3], 0.751591, places=4)  # diapositiva 20: x₄⁽¹⁾
        self.assertNotAlmostEqual(seidel[1].x[0], 0.830182, places=4)  # diapositiva 21: x₁⁽²⁾


class PruebasDiagnostico(unittest.TestCase):
    CINCO = ("2x2 - 3x3 + x4 + 4x5 = -18\n3x1 + 2x3 - 4x4 + x5 = 6\n-2x1 + 5x2 + 3x4 - 2x5 = -2\n"
             "4x1 - x2 + 3x3 - 3x5 = 24\nx1 - 3x2 - 2x3 + 5x4 = 4")

    def test_diagonal_nula_cinco_por_cinco(self):
        """Ejercicio de clase: Gauss-Jordan con 4 intercambios, Jacobi diverge, Gauss-Seidel solo reordenando."""
        from nucleo.diagnostico import FUNCIONA, NO_FUNCIONA, REORDENAR, diagnosticar
        _, A, b = leer_sistema(self.CINCO)
        gj, jacobi, seidel = diagnosticar(A, b)
        self.assertEqual((gj.estado, jacobi.estado, seidel.estado), (FUNCIONA, NO_FUNCIONA, REORDENAR))
        self.assertIn("4 intercambios", gj.detalle)
        self.assertGreater(jacobi.rho, 1)
        self.assertEqual(seidel.permutacion, (1, 2, 0, 4, 3))
        A2 = [A[p] for p in seidel.permutacion]
        b2 = [b[p] for p in seidel.permutacion]
        real = resolver_iterativo(A2, b2, "Gauss-Seidel", tolerancia=1e-6, max_iteraciones=200)
        self.assertTrue(real.convergio)
        self.assertLess(abs(seidel.iteraciones - len(real.iteraciones)), 15)   # la estimación es orientativa
        for valor, exacto in zip(real.solucion, (2, -1, 3, 1, -2)):
            self.assertAlmostEqual(valor, exacto, places=5)

    def test_dominante_y_singular(self):
        from nucleo.diagnostico import FUNCIONA, NO_FUNCIONA, diagnosticar, iteraciones_estimadas
        _, A, b = leer_sistema(GUIA)
        self.assertTrue(all(v.estado == FUNCIONA for v in diagnosticar(A, b)))
        self.assertIn("dominante", diagnosticar(A, b)[1].breve)
        singular = diagnosticar([[1, 1], [2, 2]], [1, 2])
        self.assertEqual([v.estado for v in singular[1:]], [NO_FUNCIONA, NO_FUNCIONA])
        self.assertEqual(iteraciones_estimadas(0.5, 1e-6), 20)    # 0.5²⁰ ≈ 9.5·10⁻⁷
        self.assertIsNone(iteraciones_estimadas(1.2, 1e-6))


class PruebasGaussJordanExplicado(unittest.TestCase):
    CINCO = PruebasDiagnostico.CINCO

    def setUp(self):
        self.variables, self.A, self.b = leer_sistema(self.CINCO)
        self.r = ps.resolver_directo(self.A, self.b, self.variables)

    def test_cada_eliminacion_muestra_su_propio_estado(self):
        """Antes, todos los pasos de una columna mostraban la matriz ya eliminada por completo."""
        eliminaciones = [p for p in self.r.pasos if "Eliminar la entrada" in p.splitlines()[0]]
        matrices = [tuple(l for l in p.splitlines() if l.startswith("[")) for p in eliminaciones]
        self.assertEqual(len(set(matrices)), len(matrices))
        primera = matrices[0]                       # F2 ← F2 − 3F1: F3 aún conserva su −2 inicial
        self.assertTrue(primera[2].replace(" ", "").startswith("[−2"))

    def test_pivotes_intercambios_y_determinante(self):
        self.assertEqual(self.r.intercambios, 4)
        self.assertEqual(len(self.r.pivotes), 5)
        producto = (-1) ** self.r.intercambios
        for _f, _c, valor in self.r.pivotes:
            producto *= valor
        self.assertAlmostEqual(producto, float(self.r.determinante), places=8)
        texto = "\n".join(l for l, _ in ps.resumen_directo(self.r))
        self.assertIn("(−1)⁴", texto)
        self.assertIn("✓ Coincide con det(A)", texto)
        self.assertIn("a₁₁ = 0 no sirve de pivote", self.r.pasos[1])

    def test_verificacion_sustituyendo(self):
        texto = "\n".join(l for l, _ in ps.resumen_directo(self.r))
        self.assertIn("Ec. 1: 2(−1) − 3(3) + 1 + 4(−2) = −18 ✓", texto)
        self.assertIn("Ec. 4: 4(2) − (−1) + 3(3) − 3(−2) = 24 ✓", texto)
        self.assertEqual(ps.sustitucion_ecuacion([0, 0], [1, 2]), "0")


if __name__ == "__main__":
    unittest.main()
