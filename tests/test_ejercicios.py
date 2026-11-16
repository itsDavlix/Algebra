"""Cada ejercicio guardado se resuelve con su método y se compara con su resultado esperado (tol 10⁻⁶)."""

import unittest

from nucleo.biseccion import resolver_biseccion
from nucleo.ejercicios import MATRICES, NIVELES, RAICES, SISTEMAS, TODOS, ejercicios_de
from nucleo.iterativos import reordenar_para_dominancia, resolver_iterativo
from nucleo.metodosabiertos import resolver_metodo_abierto
from nucleo.procedimientos_matrices import calcular
from nucleo.procedimientos_sistemas import resolver_directo
from nucleo.reglafalsa import resolver_reglafalsa
from nucleo.sistemas_texto import leer_matriz_texto, leer_sistema, leer_vector

TOLERANCIA = 1e-6


def resolver_raiz(ejercicio):
    d = ejercicio.datos
    if ejercicio.metodo == "Bisección":
        return resolver_biseccion(d["funcion"], float(d["a"]), float(d["b"]), TOLERANCIA, 100)
    if ejercicio.metodo == "Regula Falsi":
        return resolver_reglafalsa(d["funcion"], float(d["a"]), float(d["b"]), TOLERANCIA, 100)
    if ejercicio.metodo == "Newton-Raphson":
        return resolver_metodo_abierto(d["funcion"], "Newton-Raphson", float(d["x0"]), tolerancia=TOLERANCIA)
    return resolver_metodo_abierto(d["funcion"], "Secante", float(d["x0"]), float(d["x1"]), tolerancia=TOLERANCIA)


class PruebasCatalogo(unittest.TestCase):
    def test_estructura(self):
        claves = [e.clave for e in TODOS]
        self.assertEqual(len(claves), len(set(claves)))
        self.assertEqual(len(RAICES), 10)
        self.assertEqual(len(MATRICES), 10)
        for ejercicio in TODOS:
            self.assertIn(ejercicio.dificultad, NIVELES)
            self.assertTrue(ejercicio.justificacion and ejercicio.fuente)

    def test_orden_por_dificultad(self):
        niveles = [NIVELES.index(e.dificultad) for e in ejercicios_de(("Bisección", "Regula Falsi"))]
        self.assertEqual(niveles, sorted(niveles))


class PruebasRaices(unittest.TestCase):
    def test_cada_ecuacion_del_banco(self):
        for ejercicio in RAICES:
            with self.subTest(ejercicio=ejercicio.clave):
                r = resolver_raiz(ejercicio)
                self.assertTrue(r.convergio, r.motivo)
                self.assertAlmostEqual(r.raiz, ejercicio.esperado["raiz"], delta=TOLERANCIA * 2)
                self.assertLessEqual(len(r.iteraciones), 25)


class PruebasSistemas(unittest.TestCase):
    def test_gauss_jordan_del_banco(self):
        for ejercicio in [e for e in SISTEMAS if e.metodo == "Gauss-Jordan"]:
            with self.subTest(ejercicio=ejercicio.clave):
                variables, A, b = leer_sistema(ejercicio.datos["sistema"])
                r = resolver_directo(A, b, variables)
                self.assertEqual(r.tipo, "unica")
                for valor, esperado in zip(r.solucion, ejercicio.esperado["solucion"]):
                    self.assertAlmostEqual(valor, esperado, places=9)
                self.assertLess(r.residuo, 1e-9)

    def test_iterativos(self):
        for ejercicio in [e for e in SISTEMAS if e.metodo in ("Jacobi", "Gauss-Seidel")]:
            with self.subTest(ejercicio=ejercicio.clave):
                variables, A, b = leer_sistema(ejercicio.datos["sistema"])
                if ejercicio.datos.get("reordenar"):
                    A, b, _, _ = reordenar_para_dominancia(A, b, ejercicio.metodo)
                x0 = leer_vector(ejercicio.datos.get("x0", ""), len(variables))
                r = resolver_iterativo(A, b, ejercicio.metodo, x0, TOLERANCIA, 200, variables)
                if ejercicio.clave == "it_banco1":
                    self.assertFalse(r.convergio)       # guardado para mostrar la divergencia
                    self.assertGreater(r.radio_espectral, 1)
                    continue
                self.assertTrue(r.convergio, r.motivo)
                for valor, esperado in zip(r.solucion, ejercicio.esperado.get("solucion", r.solucion)):
                    self.assertAlmostEqual(valor, esperado, delta=1e-5)

    def test_jacobi_falla_donde_gauss_seidel_converge(self):
        ejercicio = next(e for e in SISTEMAS if e.clave == "it_banco10")
        variables, A, b = leer_sistema(ejercicio.datos["sistema"])
        A, b, _, _ = reordenar_para_dominancia(A, b, "Gauss-Seidel")
        self.assertTrue(resolver_iterativo(A, b, "Gauss-Seidel", tolerancia=TOLERANCIA, max_iteraciones=200).convergio)
        self.assertFalse(resolver_iterativo(A, b, "Jacobi", tolerancia=TOLERANCIA, max_iteraciones=200).convergio)


class PruebasMatrices(unittest.TestCase):
    def test_determinante_inversa_y_verificacion(self):
        for ejercicio in MATRICES:
            with self.subTest(ejercicio=ejercicio.clave):
                A = leer_matriz_texto(ejercicio.datos["matriz"])
                r = calcular("A⁻¹", A)
                self.assertEqual(r.determinante, ejercicio.esperado["det"])
                self.assertLess(r.datos["error"], 1e-12)
                self.assertIn("invertible", r.pasos[0])
                det_cofactores = calcular("det(A)", A, metodo_det="cofactores").valor
                self.assertEqual(det_cofactores, ejercicio.esperado["det"])

    def test_matriz_singular(self):
        r = calcular("A⁻¹", [[1, 2], [2, 4]])
        self.assertIsNone(r.valor)
        self.assertIn("singular", r.pasos[0].lower() + r.verificacion[0][0].lower())


if __name__ == "__main__":
    unittest.main()
