"""Fase 3: la interfaz refleja lo nuevo del motor sin romper el ajuste a la ventana."""

import tkinter as tk
import unittest
from tkinter import ttk

from interfaz.componentes import MenuEjercicios
from interfaz.estilos import configurar_estilo
from interfaz.raices import VistaRaiz
from interfaz.sistemas import VistaSistemas
from nucleo.ejercicios import ejercicios_de

P1_E12 = ("0.5x - 0.75y + 2z – (1/3)w = 181/60\n1.5x + y - 2.5z + (2/3)w = -0.75\n"
          "-x + 0.5y + (3/4)z - 2w = 7/30\n(2/3)x - 2y + 0.5z + 1.25w = 253/120")
P1_E11 = ("2x2 - 3x3 + x4 + 4x5 = -18\n3x1 + 2x3 - 4x4 + x5 = 6\n-2x1 + 5x2 + 3x4 - 2x5 = -2\n"
          "4x1 - x2 + 3x3 - 3x5 = 24\nx1 - 3x2 - 2x3 + 5x4 = 4")


class PruebasInterfazBanco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk no disponible: {exc}")
        configurar_estilo(ttk.Style(cls.raiz))

    @classmethod
    def tearDownClass(cls):
        cls.raiz.destroy()

    def _vista(self, crear, geometria="1500x950"):
        self.raiz.geometry(geometria)
        for _ in range(3):
            self.raiz.update()
        vista = crear(self.raiz)
        vista.pack(fill="both", expand=True)
        self.addCleanup(vista.destroy)
        self.raiz.update()
        return vista

    def _asentar(self):
        for _ in range(4):
            self.raiz.update()

    # ------------------------------------------------------------ sistemas
    def test_fracciones_o_decimales_en_gauss_jordan(self):
        vista = self._vista(VistaSistemas)
        vista.establecer_texto(P1_E12)
        vista.resolver()
        self._asentar()
        self.assertTrue(vista.selector_numeros.winfo_ismapped())
        self.assertIn("x = 1.555138132", vista.valor.cget("text"))
        vista.cambiar_modo_numeros("Fracciones")                      # rehace el cálculo
        self.assertIn("x = 162683/104610", vista.valor.cget("text"))
        self.assertIn("162683/104610 ≈ 1.555138132", "\n".join(t for t, _ in vista._lineas_completas()))
        vista.cambiar_metodo("Jacobi")
        self._asentar()
        self.assertFalse(vista.selector_numeros.winfo_ismapped())     # solo aplica a Gauss-Jordan

    def test_tarjeta_de_resultado_cabe_en_la_ventana_minima(self):
        """Ventana mínima de la app (1180 px) con el menú compacto: ~1115 px para la vista."""
        for texto, modo in ((P1_E12, "Fracciones"), (P1_E11, "Decimales")):
            with self.subTest(modo=modo):
                vista = self._vista(VistaSistemas, "1115x700")
                vista.establecer_texto(texto)
                vista.cambiar_modo_numeros(modo)
                vista.resolver()
                self._asentar()
                tarjeta = vista.valor.master
                self.assertLessEqual(tarjeta.winfo_reqheight(), tarjeta.winfo_height())
                self.assertLessEqual(tarjeta.winfo_reqwidth(), tarjeta.winfo_width())
                vista.destroy()

    # ------------------------------------------------------------ raíces
    def test_vista_previa_de_igualdad_y_aviso(self):
        vista = self._vista(lambda padre: VistaRaiz(padre, ("Bisección", "Regula Falsi")))
        campo = vista.campo_funcion
        campo.establecer("ln(x) + sen(x) = 1.2")
        campo._validar()
        self.assertIn("f(x) = ln(x) + sin(x) − 1.2 = 0", campo.vista.cget("text"))
        campo.establecer("e(-x) - x")
        campo._validar()
        self.assertTrue(campo.vista.cget("text").startswith("⚠"))
        self.assertIsNotNone(campo.expresion)                       # avisa, pero no bloquea

    def test_aviso_de_polo_antes_de_resolver(self):
        vista = self._vista(lambda padre: VistaRaiz(padre, ("Bisección", "Regula Falsi")))
        vista.campo_funcion.establecer("sen(x) / ln(x) = 1")
        vista.campo_funcion._validar()
        for clave, valor in (("a", "0.5"), ("b", "1.5")):
            vista.campos[clave].establecer(valor)
        self._asentar()
        self.assertIn("no es continua", vista.validacion.cget("text"))

    def test_vista_previa_larga_no_ensancha(self):
        vista = self._vista(lambda padre: VistaRaiz(padre, ("Newton-Raphson", "Secante")), "1115x700")
        antes = vista.winfo_reqwidth()
        vista.campo_funcion.establecer("e(-x) + " + " + ".join(f"sin({k}x)" for k in range(1, 9)))
        vista.campo_funcion._validar()
        self._asentar()
        self.assertLessEqual(vista.winfo_reqwidth(), antes)

    def test_cambiar_de_funcion_reencuadra_la_grafica(self):
        """Antes, el aviso diferido del plano marcaba la vista como «manual» y no se reencuadraba."""
        vista = self._vista(lambda padre: VistaRaiz(padre, ("Newton-Raphson", "Secante")))
        vista.campo_funcion.establecer("e^(1/x) + 2x / tan(x) = 2")
        vista.campo_funcion._validar()
        for _ in range(8):
            self.raiz.update()
            self.raiz.after(60)
        self.assertFalse(vista._vista_manual)
        vista.campo_funcion.establecer("e(-x) - x")
        vista.campo_funcion._validar()
        self._asentar()
        _, _, y0, y1 = vista.plano.vista
        self.assertLess(y1 - y0, 20)                                        # la recta se ve, no queda plana
        self.assertFalse([p for p in vista.notables if p.tipo == "inflexion"])  # una recta no tiene inflexiones

    def test_tabla_ensancha_columnas_y_ofrece_barra(self):
        vista = self._vista(lambda padre: VistaRaiz(padre, ("Newton-Raphson", "Secante")), "1115x700")
        from nucleo.ejercicios import TODOS
        vista.cargar_ejercicio(next(e for e in TODOS if e.clave == "fr3"))
        self._asentar()
        tabla = vista.tabla_iteraciones.tabla
        self.assertGreaterEqual(int(tabla.column("fx", "minwidth")), 120)    # «−2.4581966e−07» completo

    # ------------------------------------------------------------ menú
    def test_menu_agrupado_por_parte(self):
        menu = MenuEjercicios(self.raiz, ejercicios_de(("Gauss-Jordan", "Jacobi", "Gauss-Seidel")), print)
        self.addCleanup(menu.destroy)
        etiquetas = [menu.menu.entrycget(i, "label") for i in range(menu.menu.index("end") + 1)]
        self.assertTrue(etiquetas[0].startswith("Parte I · Sistemas lineales"))
        self.assertTrue(any(e.startswith("Clase Jacobi") for e in etiquetas))
        parte_i = self.raiz.nametowidget(menu.menu.entrycget(0, "menu"))
        items = [parte_i.entrycget(i, "label") for i in range(parte_i.index("end") + 1)
                 if parte_i.type(i) == "command"]
        self.assertIn("   P1-E9 · 2w = 2 da w directo · Gauss-Jordan", items)     # repetido: se aclara el método
        self.assertIn("   P1-E9 · Diagonal con ceros (reordenar) · Gauss-Seidel", items)
        un_grupo = MenuEjercicios(self.raiz, ejercicios_de(("Inversa", "Determinante")), print)
        self.addCleanup(un_grupo.destroy)
        self.assertEqual(un_grupo.menu.type(0), "command")                 # una sola Parte: lista directa
        raices = MenuEjercicios(self.raiz, ejercicios_de(("Bisección", "Regula Falsi")), print)
        self.addCleanup(raices.destroy)
        self.assertEqual([raices.menu.entrycget(i, "label").split("  (")[0] for i in range(2)],
                         ["Parte III · Ecuaciones no lineales", "Parte IV · Fraccionarias y compuestas"])


if __name__ == "__main__":
    unittest.main()
