"""Pruebas de la vista de raíces, el plano y los campos con una ventana Tk real."""

import tkinter as tk
import unittest
from tkinter import ttk

from interfaz.campoMatematico import CampoMatematico, CampoValor
from interfaz.estilos import configurar_estilo
from interfaz.motorGrafica import PlanoCartesiano, formatear_marca, paso_bonito
from interfaz.raices import VistaRaiz


class PruebasMarcas(unittest.TestCase):
    def test_pasos_bonitos(self):
        self.assertEqual([paso_bonito(r) for r in (0.13, 0.3, 0.6, 1.7, 4, 8)], [0.1, 0.2, 0.5, 2, 5, 10])
        self.assertEqual(formatear_marca(-0.2, 0.1), "−0.2")
        self.assertEqual(formatear_marca(2000, 500), "2000")


class PruebasConVentana(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk no disponible: {exc}")
        configurar_estilo(ttk.Style(cls.raiz))
        cls.raiz.geometry("1300x900")

    @classmethod
    def tearDownClass(cls):
        cls.raiz.destroy()

    def _vista(self, metodo):
        vista = VistaRaiz(self.raiz, metodo)
        vista.pack(fill="both", expand=True)
        self.addCleanup(vista.destroy)
        self.raiz.update()
        return vista

    def test_flujo_completo_de_los_cuatro_metodos(self):
        for metodo in ("Bisección", "Regula Falsi", "Newton-Raphson", "Secante"):
            with self.subTest(metodo=metodo):
                vista = self._vista(metodo)
                vista.campo_funcion.establecer("x^3 - x - 2")
                self.raiz.update()
                self.assertTrue(any(p.tipo == "raiz" for p in vista.notables))
                vista.sugerir()
                self.assertTrue(all(c.variable.get() for c in vista.campos.values()))
                vista.resolver()
                self.assertIsNotNone(vista.resultado)
                self.assertTrue(vista.resultado.convergio)
                self.assertAlmostEqual(vista.resultado.raiz, 1.5213797, places=5)
                vista.tabla.selection_set(vista.tabla.get_children()[0])
                self.raiz.update()
                self.assertIn("Iteración 1", vista.detalle.get("1.0", "end"))

    def test_alternar_y_comparar_metodos_abiertos(self):
        vista = self._vista(("Newton-Raphson", "Secante"))
        vista.cargar_ejemplo()
        self.assertEqual(vista.metodo, "Newton-Raphson")
        self.assertTrue(vista.resultado.convergio)
        self.assertNotIn("x1", vista.campos)
        vista.cambiar_metodo("Secante")
        self.raiz.update()
        self.assertIn("x1", vista.campos)
        self.assertEqual(vista.campos["x0"].variable.get(), "2")
        self.assertFalse(vista.campo_derivada.winfo_ismapped())
        self.assertIsNone(vista.resultado)
        vista.comparar()
        self.assertEqual(set(vista.resultados_por_metodo), {"Newton-Raphson", "Secante"})
        self.assertIn("Coinciden", vista.detalle.get("1.0", "end"))
        self.assertEqual(vista.resultado.metodo, "Secante")
        vista.cambiar_metodo("Newton-Raphson")
        self.assertEqual(vista.resultado.metodo, "Newton-Raphson")
        self.assertEqual(len(vista.tabla.get_children()), len(vista.resultado.iteraciones))
        vista.campo_funcion.establecer("x^2 - 3")
        self.assertEqual(vista.resultados_por_metodo, {})

    def test_alternar_y_comparar_metodos_cerrados(self):
        vista = self._vista(("Bisección", "Regula Falsi"))
        vista.cargar_ejemplo()
        self.assertEqual(vista.metodo, "Bisección")
        self.assertTrue(vista.resultado.convergio)
        vista.comparar()
        self.assertEqual(set(vista.resultados_por_metodo), {"Bisección", "Regula Falsi"})
        self.assertIn("Coinciden", vista.detalle.get("1.0", "end"))
        vista.cambiar_metodo("Regula Falsi")
        self.assertIs(vista.resultado, vista.resultados_por_metodo["Regula Falsi"])
        self.assertEqual(vista.tabla.heading("paso")["text"], "|Δc|")
        self.assertEqual(vista.campos["a"].variable.get(), "1")

    def test_ventanas_de_detalle(self):
        vista = self._vista(("Bisección", "Regula Falsi"))
        vista.cargar_ejemplo()
        vista.abrir_tabla_completa()
        ventana = vista.ventanas["tabla"]
        self.raiz.update()
        tabla = next(w for w in ventana.winfo_children()[0].winfo_children() if w.winfo_class() == "Treeview")
        self.assertEqual(len(tabla.get_children()), len(vista.resultado.iteraciones))
        tabla.selection_set("15")
        self.raiz.update()
        self.assertEqual(vista.tabla.selection(), ("15",))
        vista.abrir_procedimiento_completo()
        self.raiz.update()
        texto = next(w for w in vista.ventanas["procedimiento"].winfo_children()[0].winfo_children()
                     if w.winfo_class() == "Text")
        self.assertIn(f"Iteración {len(vista.resultado.iteraciones)}", texto.get("1.0", "end"))
        for ventana in vista.ventanas.values():
            ventana.destroy()

    def test_grafica_primero_y_clic_para_colocar_valores(self):
        vista = self._vista(("Newton-Raphson", "Secante"))
        self.assertIn("disabled", vista.campos["x0"].entrada.state())
        self.assertIn("disabled", vista.boton_resolver.state())
        vista.campo_funcion.establecer("x^3 - x - 2")
        self.raiz.update()
        self.assertIsNotNone(vista.plano.funcion)
        self.assertEqual(vista.campos["x0"].variable.get(), "")
        self.assertNotIn("disabled", vista.campos["x0"].entrada.state())
        vista.plano.encuadrar(-4, 4, -5, 5)
        self.raiz.update()
        vista._al_clic_plano(1.98765, 0)
        colocado = vista.campos["x0"].variable.get()
        pixel = 8 / vista.plano.winfo_width()
        self.assertAlmostEqual(float(colocado), 1.98765, delta=pixel)
        self.assertLessEqual(len(colocado.split(".")[1]), 4)  # redondeado, no 1.98765
        self.assertIn("f′(x₀)", vista.validacion.cget("text"))
        vista.resolver()
        self.assertTrue(vista.resultado.convergio)
        vista.cambiar_metodo("Secante")
        vista._al_clic_plano(1.0, 0)
        vista._al_clic_plano(2.0, 0)
        self.assertEqual((vista.campos["x0"].variable.get(), vista.campos["x1"].variable.get()), ("1", "2"))

    def test_derivada_automatica_visible_y_editable(self):
        vista = self._vista(("Newton-Raphson", "Secante"))
        vista.campo_funcion.establecer("x^3 - x - 2")
        self.raiz.update()
        self.assertEqual(vista.campo_derivada.obtener(), "3x² − 1")
        self.assertIn("readonly", vista.campo_derivada.entrada.state())
        vista.campos["x0"].establecer("1.5")
        vista.resolver()
        self.assertTrue(vista.resultado.derivada_automatica)
        vista._alternar_derivada()  # pasar a manual
        self.assertNotIn("readonly", vista.campo_derivada.entrada.state())
        vista.campo_derivada.establecer("2x")
        vista.resolver()
        self.assertFalse(vista.resultado.derivada_automatica)
        self.assertIn("Revisa f'(x)", vista.resultado.advertencia)
        vista._alternar_derivada()  # volver a automática
        self.assertEqual(vista.campo_derivada.obtener(), "3x² − 1")
        vista.campo_funcion.establecer("sin(x)")
        self.assertEqual(vista.campo_derivada.obtener(), "cos(x)")

    def test_clic_ordena_el_intervalo(self):
        vista = self._vista("Bisección")
        vista.campo_funcion.establecer("x^3 - x - 2")
        vista.plano.encuadrar(-4, 4, -5, 5)
        self.raiz.update()
        vista._al_clic_plano(2.0, 0)
        vista._al_clic_plano(1.0, 0)
        self.assertEqual((vista.campos["a"].variable.get(), vista.campos["b"].variable.get()), ("1", "2"))
        self.assertIn("Bolzano", vista.validacion.cget("text"))

    def test_validacion_previa_de_bolzano(self):
        vista = self._vista("Bisección")
        vista.campo_funcion.establecer("x^2 + 1")
        vista.campos["a"].establecer("-1")
        vista.campos["b"].establecer("1")
        self.raiz.update()
        self.assertIn("no se cumple Bolzano", vista.validacion.cget("text"))
        vista.resolver()
        self.assertIsNone(vista.resultado)

    def test_newton_avisa_derivada_nula(self):
        vista = self._vista("Newton-Raphson")
        vista.campo_funcion.establecer("x^2 - 4")
        vista.campos["x0"].establecer("0")
        self.raiz.update()
        self.assertIn("f′(x₀) = 0", vista.validacion.cget("text"))

    def test_paginacion(self):
        vista = self._vista("Bisección")
        vista.campo_funcion.establecer("x^3 - x - 2")
        vista.campos["a"].establecer("1")
        vista.campos["b"].establecer("2")
        vista.campo_tolerancia.establecer("1e-10")
        vista.resolver()
        total = len(vista.resultado.iteraciones)
        por_pagina = vista.por_pagina
        self.assertGreater(total, por_pagina)
        self.assertEqual(len(vista.tabla.get_children()), por_pagina)
        vista._ir_a_pagina(1)
        self.assertEqual(vista.tabla.get_children()[0], str(por_pagina))
        self.assertIn(f"de {total}", vista.etiqueta_pagina.cget("text"))

    def test_cambiar_la_funcion_descarta_el_resultado(self):
        vista = self._vista("Secante")
        vista.cargar_ejemplo()
        self.assertIsNotNone(vista.resultado)
        vista.campo_funcion.establecer("x^2 - 3")
        self.assertIsNone(vista.resultado)
        self.assertEqual(vista.tabla.get_children(), ())

    def test_campo_matematico_inserta_funciones_y_valida(self):
        cambios = []
        campo = CampoMatematico(self.raiz, al_cambiar=cambios.append)
        campo.pack()
        self.addCleanup(campo.destroy)
        campo.establecer("2x")
        campo.entrada.selection_range(0, "end")
        campo._insertar("sqrt")
        self.assertEqual(campo.obtener(), "sqrt(2x)")
        campo.establecer("son(x)")
        self.assertIsNone(campo.expresion)
        self.assertIn("sin", campo.vista.cget("text"))

    def test_campo_valor_acepta_operaciones(self):
        campo = CampoValor(self.raiz, "x₀")
        campo.pack()
        self.addCleanup(campo.destroy)
        campo.establecer("pi/2")
        self.assertAlmostEqual(campo.obtener(), 1.5707963267948966)
        campo.establecer("2,5")
        self.assertEqual(campo.obtener(), 2.5)

    def test_plano_zoom_en_el_cursor(self):
        plano = PlanoCartesiano(self.raiz, width=400, height=300)
        plano.pack()
        self.addCleanup(plano.destroy)
        self.raiz.update()
        plano.encuadrar(-10, 10, -5, 5)
        x, y = plano.a_plano(100, 75)
        plano.zoom(0.5, 100, 75)
        x2, y2 = plano.a_plano(100, 75)
        self.assertAlmostEqual(x, x2)
        self.assertAlmostEqual(y, y2)
        self.assertAlmostEqual(plano.vista[1] - plano.vista[0], 10)


if __name__ == "__main__":
    unittest.main()
