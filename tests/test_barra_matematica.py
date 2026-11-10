"""Pruebas del evaluador por tramos y de inserción en widgets reales de Tk."""

import math
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
import unittest

from interfaz.barraMatematica import BarraMatematica
from nucleo.biseccion import preparar_funcion, resolver_biseccion
from nucleo.reglafalsa import resolver_reglafalsa


class PruebasCondiciones(unittest.TestCase):
    def test_comparaciones_y_limites(self):
        for op, esperado in (("<", 2), (">", 2), ("<=", 1), (">=", 1),
                             ("==", 1), ("!=", 2), ("≤", 1), ("≥", 1), ("≠", 2)):
            with self.subTest(op=op):
                f, _ = preparar_funcion(f"si(x {op} 0, 1, 2)")
                self.assertEqual(f(0), esperado)

    def test_solo_evalua_la_rama_elegida(self):
        f, _ = preparar_funcion("si(x < 0, sqrt(-x), sqrt(x))")
        self.assertEqual(f(-4), 2)
        self.assertEqual(f(9), 3)
        f, _ = preparar_funcion("si(-1 < x <= 1, x, si(x > 1, 2, -2))")
        self.assertEqual([f(x) for x in (-2, 0, 1, 3)], [-2, 0, 1, 2])

    def test_igualdad_con_condicion_en_ambos_metodos(self):
        for resolver in (resolver_biseccion, resolver_reglafalsa):
            resultado = resolver("si(x <= 0, -x, x) = 2", 1, 3)
            self.assertTrue(resultado.convergio)
            self.assertEqual(resultado.raiz, 2)

    def test_rechaza_comparaciones_como_raices_y_codigo_arbitrario(self):
        for texto in ("x < 0", "1 + (x > 0)", "si(x, 1, 2)",
                      "si(x < 0, 1)", "si(x < 0, 1, 2, 3)",
                      "si(x < 0, __import__('os'), 0)",
                      "si(x < 0, x.real, 0)", "si(x is 0, 1, 2)",
                      "si(x < 0, True, 2)", "si(x <= 0, 1, 2) = 1 = 2"):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                preparar_funcion(texto)


class PruebasBarraMatematica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk no disponible: {exc}")
        cls.raiz.geometry("400x200")
        cls.barra = BarraMatematica(cls.raiz)

    @classmethod
    def tearDownClass(cls):
        cls.raiz.destroy()

    def setUp(self):
        self.entrada = ttk.Entry(self.raiz)
        self.entrada.entrada_matematica = True
        self.entrada.pack()
        self.raiz.update()
        self.activar(self.entrada)

    def tearDown(self):
        self.entrada.destroy()
        self.barra.ocultar()

    def activar(self, widget):
        self.barra._recordar_campo(SimpleNamespace(widget=widget))

    def test_funcion_con_cursor_y_constante_procesable(self):
        self.entrada.insert(0, "2")
        self.entrada.icursor("end")
        self.barra.alternar()
        self.barra.insertar("cos(", ")")
        self.assertEqual(self.entrada.get(), "2*cos()")
        self.assertEqual(self.entrada.index("insert"), 6)
        self.barra.insertar("pi")
        f, _ = preparar_funcion(self.entrada.get())
        self.assertEqual(f(0), -2)

    def test_envuelve_seleccion_y_reemplaza_operador(self):
        self.entrada.insert(0, "x+1")
        self.entrada.selection_range(0, 3)
        self.barra.insertar("sqrt(", ")")
        self.assertEqual(self.entrada.get(), "sqrt(x+1)")
        f, _ = preparar_funcion(self.entrada.get())
        self.assertEqual(f(8), 3)
        self.entrada.selection_range(0, 4)
        self.barra.insertar("cos")
        self.assertEqual(self.entrada.index("insert"), 3)

    def test_multiplicacion_a_la_derecha_y_funcion_anidada(self):
        self.entrada.insert(0, "x")
        self.entrada.icursor(0)
        self.barra.insertar("sin(", ")")
        self.barra.insertar("cos(", ")")
        self.barra.insertar("0")
        self.assertEqual(self.entrada.get(), "sin(cos(0))*x")
        f, _ = preparar_funcion(self.entrada.get())
        self.assertAlmostEqual(f(2), 2 * math.sin(1))

    def test_potencia_sobre_expresion_seleccionada(self):
        self.entrada.insert(0, "x+1")
        self.entrada.selection_range(0, "end")
        self.barra.insertar("**2")
        self.assertEqual(self.entrada.get(), "(x+1)**2")
        f, _ = preparar_funcion(self.entrada.get())
        self.assertEqual(f(2), 9)

    def test_no_modifica_campos_bloqueados_destruidos_o_pestanas_ocultas(self):
        self.entrada.insert(0, "123")
        for estado in ("readonly", "disabled"):
            self.entrada.configure(state=estado)
            self.barra.insertar("9")
            self.assertEqual(self.entrada.get(), "123")
        self.entrada.configure(state="normal")
        self.entrada.pack_forget()
        self.raiz.update()
        self.barra.insertar("9")
        self.assertEqual(self.entrada.get(), "123")
        self.entrada.destroy()
        self.barra.insertar("9")

    def test_texto_multilinea_y_cambio_de_destino(self):
        texto = tk.Text(self.raiz)
        texto.pack()
        self.raiz.update()
        try:
            texto.insert("1.0", "1 2\n3 4")
            texto.tag_add("sel", "2.0", "2.3")
            self.activar(texto)
            self.barra.insertar("5 6")
            self.assertEqual(texto.get("1.0", "end-1c"), "1 2\n5 6")
            self.assertEqual(self.entrada.get(), "")
            self.barra._cambiar_pestana()
            self.barra.insertar("9")
            self.assertEqual(texto.get("1.0", "end-1c"), "1 2\n5 6")
        finally:
            texto.destroy()

    def test_paleta_reutilizada_y_botones_segun_campo(self):
        self.barra.alternar()
        ventana = self.barra.ventana
        self.assertTrue(self.barra.visible)
        self.barra.ocultar()
        self.barra.alternar()
        self.assertIs(self.barra.ventana, ventana)
        self.entrada.entrada_matematica = False
        self.activar(self.entrada)
        for boton, tipo, _ in self.barra.botones:
            if tipo in ("expresion", "separador"):
                self.assertTrue(boton.instate(["disabled"]))
        self.barra.ocultar()
        self.assertFalse(self.barra.visible)


class PruebasIntegracionBarra(unittest.TestCase):
    def test_boton_principal_ambas_pestanas_y_tema(self):
        from main import CalculadoraAlgebraLineal
        try:
            app = CalculadoraAlgebraLineal()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk no disponible: {exc}")
        try:
            app.update()
            app.boton_simbolos.invoke()
            app.update()
            self.assertTrue(app.barra_matematica.visible)
            self.assertEqual(app.boton_simbolos.cget("text"), "Ocultar símbolos")
            self.assertLess(app.barra_matematica.ventana.winfo_reqheight(),
                            app.winfo_screenheight())
            app._alternar_tema()
            self.assertTrue(app.modo_oscuro)
            contenedor = app.winfo_children()[0]
            notebook = next(w for w in contenedor.winfo_children() if isinstance(w, ttk.Notebook))
            for pestana in notebook.winfo_children():
                if not hasattr(pestana, "entrada_ecuacion"):
                    continue
                notebook.select(pestana)
                app.update()
                entrada = pestana.entrada_ecuacion
                entrada.focus_force()
                app.update()
                entrada.delete(0, "end")
                boton = next(b for b, _, p in app.barra_matematica.botones if p == "tan(")
                self.assertFalse(boton.instate(["disabled"]))
                boton.invoke()
                self.assertEqual(entrada.get(), "tan()")
            app.barra_matematica.ocultar()
            self.assertEqual(app.boton_simbolos.cget("text"), "Mostrar símbolos")
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
