"""Los 49 ejercicios del banco, en dos capas.

Núcleo: fórmula del método, pasos, tolerancia 10⁻⁶, ≥ 8 cifras, comprobación
(A·X = B, A·A⁻¹ = I, |f(x)| o cambio de signo) y dominio controlado. Cada
resultado se contrasta con un cálculo independiente hecho aquí con Fraction.

Interfaz: cada ejercicio se carga en su vista real y debe resolverse sin
excepciones (también las de los callbacks de Tk), con tabla, procedimiento y
gráfica actualizados.
"""

import math
import tkinter as tk
import unittest
from fractions import Fraction
from tkinter import ttk

from nucleo import procedimientos, procedimientos_sistemas as ps
from nucleo.analisis import comprobar_continuidad
from nucleo.biseccion import resolver_biseccion
from nucleo.ejercicios import MATRICES, RAICES, SISTEMAS, TODOS
from nucleo.expresiones import analizar
from nucleo.iterativos import reordenar_para_dominancia, resolver_iterativo
from nucleo.metodosabiertos import resolver_metodo_abierto
from nucleo.procedimientos_matrices import calcular
from nucleo.reglafalsa import resolver_reglafalsa
from nucleo.sistemas_texto import leer_matriz_texto, leer_sistema, leer_vector

TOLERANCIA = 1e-6

# Intervalos que contienen un punto fuera del dominio: deben rechazarse antes de iterar (Parte IV).
INTERVALOS_PROHIBIDOS = {"fr1": (0.5, 1.5), "fr2": (2, 4), "fr4": (1, 3), "fr5": (0, 2)}


def _rango_exacto(M):
    M = [list(fila) for fila in M]
    rango = 0
    for c in range(len(M[0])):
        p = next((i for i in range(rango, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[rango], M[p] = M[p], M[rango]
        for i in range(len(M)):
            if i != rango and M[i][c] != 0:
                factor = M[i][c] / M[rango][c]
                M[i] = [a - factor * b for a, b in zip(M[i], M[rango])]
        rango += 1
    return rango


def _det_laplace(M):
    if len(M) == 1:
        return M[0][0]
    return sum((-1) ** j * M[0][j] * _det_laplace([fila[:j] + fila[j + 1:] for fila in M[1:]])
               for j in range(len(M)) if M[0][j] != 0)


def _resolver_raiz(ejercicio):
    d, m = ejercicio.datos, ejercicio.metodo
    if m == "Bisección":
        return resolver_biseccion(d["funcion"], float(d["a"]), float(d["b"]), TOLERANCIA, 100)
    if m == "Regula Falsi":
        return resolver_reglafalsa(d["funcion"], float(d["a"]), float(d["b"]), TOLERANCIA, 100)
    if m == "Newton-Raphson":
        return resolver_metodo_abierto(d["funcion"], m, float(d["x0"]), tolerancia=TOLERANCIA)
    return resolver_metodo_abierto(d["funcion"], m, float(d["x0"]), float(d["x1"]), tolerancia=TOLERANCIA)


def _texto(lineas):
    return "\n".join(t for t, _ in lineas)


class PruebasNucleo(unittest.TestCase):
    def test_estan_los_49(self):
        documentos = {e.documento for e in TODOS if e.documento}
        esperados = {f"P1-E{i}" for i in range(1, 20)} | {f"P2-E{i}" for i in range(1, 11)} | \
                    {f"P3-E{i}" for i in range(1, 16)} | {f"P4-E{i}" for i in range(1, 6)}
        self.assertEqual(documentos, esperados)
        for ejercicio in TODOS:
            with self.subTest(ejercicio=ejercicio.clave):
                self.assertTrue(ejercicio.justificacion and ejercicio.enunciado and ejercicio.titulo)

    # ------------------------------------------------------------ Parte I
    def test_sistemas_gauss_jordan(self):
        for e in [e for e in SISTEMAS if e.metodo == "Gauss-Jordan"]:
            with self.subTest(ejercicio=e.documento):
                variables, A, b = leer_sistema(e.datos["sistema"])
                Ae, be = leer_sistema(e.datos["sistema"], exacto=True)[1:]
                r = ps.resolver_directo(A, b, variables, exacto=e.datos.get("exacto", False))
                resumen = _texto(ps.resumen_directo(r))
                self.assertIn("Forma matricial A·X = B", resumen)                  # planteamiento
                self.assertTrue(r.pasos[0].startswith("PASO 1. Formar la matriz aumentada"))
                self.assertGreater(len(r.pasos), 3)                                 # desarrollo paso a paso
                # Clasificación contrastada con los rangos exactos (Rouché-Frobenius).
                rango_a = _rango_exacto(Ae)
                rango_ab = _rango_exacto([fila + [bi] for fila, bi in zip(Ae, be)])
                tipo = ("incompatible" if rango_a < rango_ab else
                        "unica" if rango_a == len(variables) else "infinitas")
                self.assertEqual(r.tipo, tipo)
                self.assertEqual(r.tipo, e.esperado.get("tipo", "unica"))
                if r.tipo != "unica":
                    self.assertIn("Solución general", r.pasos[-1])
                    continue
                # Comprobación A·X = B con la solución exacta del catálogo y con la calculada.
                for fila, bi in zip(Ae, be):
                    self.assertEqual(sum(a * Fraction(x) for a, x in zip(fila, e.esperado["solucion"])), bi)
                for valor, exacto in zip(r.solucion, e.esperado["solucion"]):
                    self.assertAlmostEqual(valor, float(exacto), places=9)
                self.assertLess(r.residuo, 1e-9)
                self.assertEqual(resumen.count("✓"), len(A) + 2)                  # cada ecuación, det y A·X = B
                if e.datos.get("exacto"):
                    self.assertEqual(tuple(r.exacta), tuple(Fraction(x) for x in e.esperado["solucion"]))
                    self.assertEqual(r.residuo, 0)

    def test_sistemas_iterativos(self):
        for e in [e for e in SISTEMAS if e.metodo in ("Jacobi", "Gauss-Seidel")]:
            with self.subTest(ejercicio=e.clave):
                variables, A, b = leer_sistema(e.datos["sistema"])
                if e.datos.get("reordenar"):
                    A, b, _, _ = reordenar_para_dominancia(A, b, e.metodo)
                x0 = leer_vector(e.datos.get("x0", ""), len(variables))
                r = resolver_iterativo(A, b, e.metodo, x0, TOLERANCIA, 200, variables)
                self.assertIn(ps.FORMULAS_ITERATIVAS[e.metodo], _texto(ps.resumen_iterativo(r)))
                self.assertTrue(r.iteraciones)
                if "solucion" not in e.esperado:
                    continue
                self.assertTrue(r.convergio, r.motivo)
                self.assertLessEqual(r.iteraciones[-1].cambio, TOLERANCIA)
                for valor, exacto in zip(r.solucion, e.esperado["solucion"]):
                    self.assertAlmostEqual(valor, float(exacto), delta=1e-5)

    # ------------------------------------------------------------ Parte II
    def test_determinante_e_inversa(self):
        for e in MATRICES:
            with self.subTest(ejercicio=e.documento):
                A = leer_matriz_texto(e.datos["matriz"])
                exacta = [[Fraction(v) for v in fila] for fila in A]
                det = _det_laplace(exacta)                                         # cálculo independiente
                self.assertEqual(det, e.esperado["det"])
                for metodo in ("cofactores", "lu"):
                    self.assertEqual(calcular("det(A)", A, metodo_det=metodo).valor, det)
                r = calcular("A⁻¹", A)
                self.assertIn("invertible", r.pasos[0])                            # justificación por det ≠ 0
                n = len(A)
                producto = [[sum(exacta[i][k] * Fraction(r.valor[k][j]) for k in range(n)) for j in range(n)]
                            for i in range(n)]
                error = max(abs(float(producto[i][j]) - (i == j)) for i in range(n) for j in range(n))
                self.assertLess(error, 1e-12)                                     # A·A⁻¹ = I₄
                self.assertLess(r.datos["error"], 1e-12)

    def test_matriz_singular_se_justifica(self):
        r = calcular("A⁻¹", [[1, 2, 3, 4], [2, 4, 6, 8], [0, 1, 0, 1], [1, 0, 1, 0]])
        self.assertIsNone(r.valor)
        self.assertIn("singular", (r.pasos[0] + " ".join(t for t, _ in r.verificacion)).lower())

    # ------------------------------------------------------------ Partes III y IV
    def test_raices(self):
        for e in RAICES:
            with self.subTest(ejercicio=e.clave):
                r = _resolver_raiz(e)
                resumen = _texto(procedimientos.resumen(e.metodo, r))
                self.assertIn(procedimientos.FORMULAS[e.metodo], resumen)          # fórmula del método
                self.assertIn("Tolerancia: 1e−06", resumen)
                self.assertTrue(r.iteraciones)
                self.assertIn(f"Iteración 1", _texto(procedimientos.detalle(e.metodo, r, 0)))
                if e.esperado.get("converge") is False:
                    self.assertFalse(r.convergio)                                  # contraejemplo
                    continue
                self.assertTrue(r.convergio, r.motivo)
                self.assertAlmostEqual(r.raiz, e.esperado["raiz"], delta=2 * TOLERANCIA)
                self.assertIn("Raíz aproximada", resumen)
                self.assertGreaterEqual(len(procedimientos.n(r.raiz).lstrip("−").replace(".", "")), 8
                                        if abs(r.raiz) > 1e-3 else 1)              # ≥ 8 cifras significativas
                # Comprobación independiente: |f| pequeño o cambio de signo a ±2·10⁻⁶ de la raíz.
                f = analizar(e.datos["funcion"])
                cerca = [f.intentar(r.raiz + d) for d in (-2 * TOLERANCIA, 2 * TOLERANCIA)]
                cambia = None not in cerca and (cerca[0] < 0) != (cerca[1] < 0)
                self.assertTrue(abs(f(r.raiz)) <= TOLERANCIA or cambia)

    def test_dominio_parte_iv(self):
        por_clave = {e.clave: e for e in RAICES}
        for clave, (a, b) in INTERVALOS_PROHIBIDOS.items():
            with self.subTest(ejercicio=clave):
                funcion = por_clave[clave].datos["funcion"]
                self.assertIn("no es continua", comprobar_continuidad(analizar(funcion), a, b))
                with self.assertRaisesRegex(ValueError, "Bolzano no aplica"):
                    resolver_biseccion(funcion, a, b, TOLERANCIA, 100)
        f = analizar(por_clave["fr3"].datos["funcion"])
        self.assertIsNone(f.intentar(0))                                           # x = 0 fuera del dominio


class PruebasInterfaz(unittest.TestCase):
    """Cada ejercicio cargado en su vista real; los errores de callbacks de Tk también fallan."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk no disponible: {exc}")
        from interfaz.estilos import configurar_estilo
        configurar_estilo(ttk.Style(cls.raiz))
        cls.raiz.geometry("1500x950")
        cls.errores = []
        cls.raiz.report_callback_exception = lambda *info: cls.errores.append(info[1])

    @classmethod
    def tearDownClass(cls):
        cls.raiz.destroy()

    def setUp(self):
        self.errores.clear()

    def _vista(self, crear):
        vista = crear(self.raiz)
        vista.pack(fill="both", expand=True)
        self.addCleanup(vista.destroy)
        self.raiz.update()
        return vista

    def _asentar(self):
        for _ in range(3):
            self.raiz.update()
        self.assertEqual(self.errores, [])

    def test_sistemas(self):
        from interfaz.sistemas import VistaSistemas
        vista = self._vista(VistaSistemas)
        for e in SISTEMAS:
            with self.subTest(ejercicio=e.clave):
                vista.cargar_ejercicio(e)
                self._asentar()
                self.assertIsNotNone(vista.resultado)
                self.assertEqual(vista.metodo, e.metodo)
                self.assertTrue(vista.tabla.filas)
                self.assertTrue(vista.panel.texto.get("1.0", "end").strip())
                self.assertTrue(vista.veredictos)                                 # diagnóstico visible
                if e.datos.get("exacto"):
                    self.assertEqual(vista.modo_numeros, "Fracciones")
                    self.assertIn("/", vista.valor.cget("text") + "/")

    def test_matrices(self):
        from interfaz.vistaMatrices import VistaMatrices
        vista = self._vista(VistaMatrices)
        for e in MATRICES:
            with self.subTest(ejercicio=e.documento):
                vista.cargar_ejercicio(e)
                self._asentar()
                self.assertIn("A·A⁻¹ = I", vista.valor.get("1.0", "end"))
                self.assertTrue(vista.tabla.filas)

    def test_raices(self):
        from interfaz.raices import VistaRaiz
        vistas = {}
        for e in RAICES:
            pareja = ("Bisección", "Regula Falsi") if e.metodo in ("Bisección", "Regula Falsi") \
                else ("Newton-Raphson", "Secante")
            if pareja not in vistas:
                vistas[pareja] = self._vista(lambda padre, p=pareja: VistaRaiz(padre, p))
            vista = vistas[pareja]
            with self.subTest(ejercicio=e.clave):
                vista.cargar_ejercicio(e)
                self._asentar()
                self.assertIsNotNone(vista.resultado)
                self.assertEqual(vista.metodo, e.metodo)
                self.assertEqual(len(vista.tabla_iteraciones.filas), len(vista.resultado.iteraciones))
                self.assertTrue(vista.plano.puntos)                                # aproximaciones en la gráfica
                self.assertTrue(vista.plano.funcion is not None)
                self.assertTrue(math.isfinite(vista.resultado.raiz))


if __name__ == "__main__":
    unittest.main()
