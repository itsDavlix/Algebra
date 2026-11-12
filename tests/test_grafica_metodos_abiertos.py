"""Comprueba que la gráfica representa las evaluaciones reales del método."""

import math
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from interfaz.estilos import actualizar_widgets
from interfaz.graficaMetodosAbiertos import (
    dibujar_metodo, limites_grafica, muestrear_curva, puntos_del_metodo,
)
from interfaz.pestanaMetodosAbiertos import PestanaMetodosAbiertos
from nucleo.biseccion import preparar_funcion
from nucleo.metodosabiertos import resolver_metodo_abierto


class PruebasDatosGrafica(unittest.TestCase):
    def test_puntos_son_las_evaluaciones_del_metodo(self):
        f, _ = preparar_funcion("x^2-2")
        r = resolver_metodo_abierto("x^2-2", "Secante", 1, 2)
        puntos = puntos_del_metodo(f, r, (1, 2))
        self.assertEqual(puntos[:2], [("Inicial x0", 1, -1), ("Inicial x1", 2, 2)])
        self.assertAlmostEqual(puntos[2][1], 4/3)
        self.assertEqual(len(puntos), len(r.iteraciones)+2)
        for _, x, y in puntos:
            self.assertEqual(f(x), y)

    def test_muestras_indican_los_huecos_del_dominio(self):
        f, _ = preparar_funcion("1/x")
        muestras = muestrear_curva(f, -1, 1)
        self.assertEqual(len(muestras), 241)
        self.assertEqual(muestras[120], (0, None))
        for x, y in muestras:
            if y is not None:
                self.assertEqual(y, f(x))

    def test_limites_y_muestras_finitos_en_escalas_extremas(self):
        for xs in ((0, 0), (5e-324, 5e-324), (-1e308, 1e308), (2, 2)):
            with self.subTest(xs=xs):
                a, b = limites_grafica(xs)
                self.assertTrue(math.isfinite(a) and math.isfinite(b))
                self.assertLess(a, b)
                self.assertLessEqual(a, min(xs))
                self.assertGreaterEqual(b, max(xs))
                self.assertTrue(all(math.isfinite(x) for x, _ in muestrear_curva(lambda x: x, a, b)))

    def test_etiqueta_no_afirma_raiz_sin_convergencia(self):
        f, _ = preparar_funcion("x^2+1")
        r = resolver_metodo_abierto("x^2+1", "Newton-Raphson", 0, derivada="2*x")
        canvas = Mock()
        canvas.winfo_width.return_value = 800
        canvas.winfo_height.return_value = 300
        canvas.cget.return_value = "white"
        dibujar_metodo(canvas, r, puntos_del_metodo(f, r, (0,)), muestrear_curva(f, -1, 1))
        textos = [c.kwargs.get("text", "") for c in canvas.create_text.call_args_list]
        self.assertTrue(any("Sin convergencia" in t for t in textos))
        self.assertFalse(any("Raíz aproximada" in t for t in textos))


class PruebasVentanaGrafica(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Tk no disponible: {exc}")
        self.raiz.withdraw()
        self.addCleanup(self.raiz.destroy)
        self.p = PestanaMetodosAbiertos(self.raiz)

    def test_ambos_metodos_pasos_temas_y_limpieza(self):
        for metodo in ("Newton-Raphson", "Secante"):
            with self.subTest(metodo=metodo):
                self.p.var_metodo.set(metodo)
                self.p._cargar_ejemplo()
                self.assertTrue(self.p.boton_grafica.instate(["disabled"]))
                self.p._accion_resolver()
                self.p._abrir_grafica()
                ventana = self.p._ventana_grafica
                self.raiz.update()
                self.assertEqual(len(ventana.tabla_muestras.get_children()), 241)
                self.assertTrue(ventana.canvas.find_withtag("recta_metodo"))
                self.assertTrue(ventana.canvas.find_withtag("corte"))
                self.assertEqual(len(ventana.tabla_puntos.get_children()),
                                 len(self.p.resultado.iteraciones) + (2 if metodo == "Secante" else 1))
                ventana.selector.current(len(self.p.resultado.iteraciones)-1)
                ventana.enfocar.set(True)
                ventana._redibujar_grafica()
                for oscuro in (True, False):
                    actualizar_widgets(self.raiz, oscuro)
                    ventana._redibujar_grafica()
                    self.assertTrue(ventana.canvas.find_withtag("resultado"))
                # Editar campos no cambia la ecuación del cálculo ya representado.
                self.p.var_ecuacion.set("x^2+100")
                self.p._abrir_grafica()
                self.assertIs(self.p._ventana_grafica, ventana)
                self.assertEqual(ventana.funcion(2), 4)
                self.p._limpiar()
                self.assertFalse(ventana.winfo_exists())
                self.assertTrue(self.p.boton_grafica.instate(["disabled"]))

    def test_raiz_inicial_sin_iteraciones_y_semilla_fuera_del_dominio(self):
        self.p.var_metodo.set("Secante")
        self.p._seleccionar_metodo()
        self.p.var_ecuacion.set("log(x)")
        self.p.var_x0.set("1")
        self.p.var_x1.set("-1")
        self.p._accion_resolver()
        self.p._abrir_grafica()
        self.raiz.update()
        v = self.p._ventana_grafica
        self.assertFalse(v.canvas.find_withtag("recta_metodo"))
        self.assertIn("No se construyó ninguna recta", v.explicacion.cget("text"))
        self.assertIsNone(v.puntos[1][2])

    @patch("interfaz.pestanaMetodosAbiertos.mostrar_error")
    def test_error_de_entrada_cierra_grafica_anterior(self, error):
        self.p._accion_resolver()
        self.p._abrir_grafica()
        ventana = self.p._ventana_grafica
        self.p.var_ecuacion.set("x/0")
        self.p._accion_resolver()
        self.assertFalse(ventana.winfo_exists())
        self.assertIsNone(self.p._datos_grafica)
        error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
