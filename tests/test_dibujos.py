"""Dibujos de vectores y sistemas 2×2: la geometría debe coincidir con el cálculo."""

import math
import unittest

from interfaz.dibujos import (
    admite_plano_sistema, admite_plano_vectores, dibujo_sistema, dibujo_vectores, encuadre_proporcional,
)
from nucleo.iterativos import resolver_iterativo


class PruebasVectores(unittest.TestCase):
    def test_solo_r2_y_operaciones_geometricas(self):
        self.assertTrue(admite_plano_vectores("V₁ + V₂", [1, 2], [3, 4]))
        self.assertTrue(admite_plano_vectores("k · V₁", [1, 2], None))
        self.assertFalse(admite_plano_vectores("V₁ + V₂", [1, 2, 3], [3, 4, 5]))
        self.assertFalse(admite_plano_vectores("V₁ × V₂", [1, 2], [3, 4]))
        self.assertFalse(admite_plano_vectores("Independencia", [1, 2], [3, 4]))

    def test_suma_es_la_diagonal_del_paralelogramo(self):
        d = dibujo_vectores("V₁ + V₂", [1, 2], [3, -1])
        resultado = next(p for p in d.puntos if p.clave == "res")
        self.assertEqual((resultado.x, resultado.y), (4, 1))
        flechas = [(c.p, c.q) for c in d.capas if c.tipo == "flecha"]
        self.assertIn(((1, 2), (4, 1)), flechas)      # V₂ trasladado al extremo de V₁
        self.assertIn(((3, -1), (4, 1)), flechas)     # V₁ trasladado al extremo de V₂

    def test_resta_y_escalar(self):
        d = dibujo_vectores("V₁ − V₂", [5, 1], [2, 3])
        self.assertEqual(next((p.x, p.y) for p in d.puntos if p.clave == "res"), (3, -2))
        d = dibujo_vectores("k · V₁", [1, 2], None, -2)
        self.assertEqual(next((p.x, p.y) for p in d.puntos if p.clave == "res"), (-2, -4))
        self.assertIn("contrario", d.nota)

    def test_angulo_entre_vectores(self):
        self.assertIn("90°", dibujo_vectores("V₁ · V₂", [1, 0], [0, 3]).nota)
        self.assertIn("perpendiculares", dibujo_vectores("V₁ · V₂", [1, 0], [0, 3]).nota)
        self.assertIn("45°", dibujo_vectores("V₁ · V₂", [1, 0], [2, 2]).nota)
        self.assertIn("no está definido", dibujo_vectores("V₁ · V₂", [0, 0], [2, 2]).nota)


class PruebasSistemas(unittest.TestCase):
    def test_interseccion_es_la_solucion(self):
        d = dibujo_sistema([[2, 1], [1, -1]], [3, 0])
        sol = next(p for p in d.puntos if p.clave == "sol")
        self.assertAlmostEqual(sol.x, 1)
        self.assertAlmostEqual(sol.y, 1)
        for _color, recta, _ancho in d.curvas:        # el punto está sobre las dos rectas
            self.assertAlmostEqual(recta(sol.x), sol.y)

    def test_paralelas_coincidentes_y_verticales(self):
        self.assertIn("paralelas", dibujo_sistema([[1, 1], [2, 2]], [1, 3]).nota)
        self.assertIn("coincidentes", dibujo_sistema([[1, 1], [2, 2]], [1, 2]).nota)
        d = dibujo_sistema([[1, 0], [0, 1]], [3, 2])
        self.assertEqual([c.tipo for c in d.capas], ["vertical"])
        self.assertEqual((d.capas[0].p[0], next(p.y for p in d.puntos)), (3, 2))

    def test_camino_de_gauss_seidel_llega_a_la_solucion(self):
        A, b = [[4, 1], [1, -3]], [9, -5]
        r = resolver_iterativo(A, b, "Gauss-Seidel", None, 1e-8, 100)
        trayectoria = [(0, r.x0)] + [(p.k, p.x) for p in r.iteraciones]
        d = dibujo_sistema(A, b, trayectoria)
        sol = next(p for p in d.puntos if p.clave == "sol")
        ultimo = next(p for p in d.puntos if p.clave == f"k{r.iteraciones[-1].k}")
        self.assertAlmostEqual(ultimo.x, sol.x, places=6)
        self.assertAlmostEqual(ultimo.y, sol.y, places=6)
        self.assertIn("aproximaciones", d.nota)

    def test_solo_2x2(self):
        self.assertTrue(admite_plano_sistema([[1, 2], [3, 4]]))
        self.assertFalse(admite_plano_sistema([[1, 2, 3], [3, 4, 5], [1, 1, 1]]))


class PruebasEncuadre(unittest.TestCase):
    def test_misma_escala_en_los_dos_ejes(self):
        x0, x1, y0, y1 = encuadre_proporcional((0, 4, 0, 2), 800, 400)
        self.assertAlmostEqual((x1 - x0) / 800, (y1 - y0) / 400)
        self.assertTrue(x0 < 0 and x1 > 4 and y0 < 0 and y1 > 2)     # contiene el dibujo con margen

    def test_solo_el_origen(self):
        vista = encuadre_proporcional((0, 0, 0, 0), 600, 300)
        self.assertTrue(all(math.isfinite(v) for v in vista))


if __name__ == "__main__":
    unittest.main()
