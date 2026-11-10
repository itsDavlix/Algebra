"""Verifica las acciones de la pestaña sin requerir un servidor gráfico."""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from interfaz.pestanaBiseccion import PestanaBiseccion, dibujar_grafica_biseccion, _intervalo_zoom
from interfaz.estilos import AZUL
from nucleo.biseccion import preparar_funcion, resolver_biseccion


class PruebasAccionesBiseccion(unittest.TestCase):
    def setUp(self):
        self.tcl = tk.Tcl()
        self.pestana = PestanaBiseccion.__new__(PestanaBiseccion)
        for nombre in ("ecuacion", "a", "b", "tolerancia", "iteraciones"):
            setattr(self.pestana, "var_" + nombre, tk.StringVar(self.tcl))
        self.pestana._cargando_ejemplo = False
        self.pestana.txt_resultado = Mock()
        self.pestana.entrada_ecuacion = Mock()
        self.pestana.tabla_iteraciones = Mock()
        self.pestana.tabla_iteraciones.get_children.return_value = ()
        self.pestana.iteraciones_expandidas = False
        self.pestana.grafica_expandida = False
        self.pestana.canvas_grafica = Mock()
        self.pestana.canvas_grafica.winfo_width.return_value = 500
        self.pestana.canvas_grafica.winfo_height.return_value = 210

    @patch("interfaz.pestanaBiseccion.mostrar_error")
    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_resolver_autoajusta_campos_y_calcula_raiz(self, mostrar, error):
        self.pestana.var_ecuacion.set("x^2 = 2")
        self.pestana._accion_resolver()

        self.assertLess(float(self.pestana.var_a.get()), float(self.pestana.var_b.get()))
        self.assertGreater(float(self.pestana.var_tolerancia.get()), 0)
        self.assertGreater(int(self.pestana.var_iteraciones.get()), 0)
        salida = mostrar.call_args.args[1]
        for texto in ("convergencia alcanzada", "Iteraciones", "tolerancia"):
            self.assertIn(texto, salida)
        error.assert_not_called()

    @patch("interfaz.pestanaBiseccion.mostrar_error")
    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_ejemplo_resuelve_desde_los_campos(self, mostrar, error):
        self.pestana._cargar_ejemplo()
        self.pestana._accion_resolver()
        salida = mostrar.call_args.args[1]
        self.assertIn("convergencia alcanzada", salida)
        self.assertIn("x ≈ 1.52138", salida)
        self.assertIn("Iteraciones: 20", salida)
        error.assert_not_called()
        self.assertEqual(self.pestana.canvas_grafica.create_oval.call_count, 4)
        self.assertEqual(self.pestana.tabla_iteraciones.insert.call_count, 20 * 7)
        for llamada in self.pestana.tabla_iteraciones.insert.call_args_list:
            if "values" in llamada.kwargs:
                self.assertEqual(len(llamada.kwargs["values"]), 5)

    @patch("interfaz.pestanaBiseccion.mostrar_error")
    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_tabla_despliega_calculos_y_decision_de_cada_iteracion(self, mostrar, error):
        self.pestana._cargar_ejemplo()
        self.pestana._accion_resolver()

        inserts = self.pestana.tabla_iteraciones.insert.call_args_list
        raiz = next(
            llamada for llamada in inserts
            if llamada.kwargs.get("iid") == "iteracion-1"
        )
        detalles = [
            llamada.kwargs["text"] for llamada in inserts
            if llamada.args and llamada.args[0] == "iteracion-1"
        ]
        self.assertFalse(raiz.kwargs["open"])
        self.assertEqual(
            detalles,
            [
                "Punto medio: c = (a+b)/2",
                "Evaluación: f(a) = -0.125",
                "Evaluación: f(b) = 1.609375",
                "Evaluación: f(c) = 0.6660156",
                "Cota: max(c-a, b-c)",
                "Decisión: conservar [a, c]",
            ],
        )
        self.assertIn("fila_par", raiz.kwargs["tags"])
        ultima_decision = next(
            llamada for llamada in inserts
            if llamada.kwargs.get("text", "").startswith("Parada:")
        )
        self.assertIn("parada_ok", ultima_decision.kwargs["tags"])
        error.assert_not_called()

    def test_vista_completa_oculta_y_restaura_el_resto_del_panel(self):
        for nombre in (
            "marco_entrada", "marco_resultado", "barra_grafica", "area_resumen",
            "procedimiento", "boton_expandir",
        ):
            setattr(self.pestana, nombre, Mock())
        self.pestana._redibujar_grafica = Mock()

        self.pestana._alternar_vista_iteraciones()

        self.assertTrue(self.pestana.iteraciones_expandidas)
        self.pestana.marco_entrada.grid_remove.assert_called_once()
        self.pestana.barra_grafica.grid_remove.assert_called_once()
        self.pestana.area_resumen.grid_remove.assert_called_once()
        self.pestana.marco_resultado.grid_configure.assert_called_once()
        self.pestana.boton_expandir.configure.assert_called_with(text="Volver al resultado")

        self.pestana._alternar_vista_iteraciones()

        self.assertFalse(self.pestana.iteraciones_expandidas)
        self.pestana.marco_entrada.grid.assert_called_once()
        self.pestana.barra_grafica.grid.assert_called_once()
        self.pestana.area_resumen.grid.assert_called_once()
        self.pestana._redibujar_grafica.assert_called_once()
        self.pestana.boton_expandir.configure.assert_called_with(text="Ver tabla completa")

    @patch("interfaz.pestanaBiseccion.mostrar_error")
    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_error_de_autoajuste_reemplaza_el_resultado_anterior(self, mostrar, error):
        self.pestana._cargar_ejemplo()
        for ecuacion in ("", "x^2 + 1", "ecuacion invalida"):
            with self.subTest(ecuacion=ecuacion):
                self.pestana.var_ecuacion.set(ecuacion)
                self.pestana._accion_resolver()
                self.assertIn("No se pudo resolver", mostrar.call_args.args[1])
                self.assertIsNone(self.pestana.resultado_biseccion)
                error.assert_called()

    @patch("interfaz.pestanaBiseccion.mostrar_error")
    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_resuelve_sin_casilla_de_confirmacion(self, mostrar, error):
        self.pestana._cargar_ejemplo()
        self.pestana._accion_resolver()

        self.assertIn("convergencia alcanzada", mostrar.call_args.args[1])
        error.assert_not_called()

    def test_editar_ecuacion_o_intervalo_no_requiere_confirmacion(self):
        self.pestana._cargar_ejemplo()
        self.pestana.var_ecuacion.set("x^2 - 2")
        self.pestana.var_a.set("1.1")
        self.pestana.var_b.set("2")
        self.assertNotIn("var_continuidad", vars(self.pestana))

    def test_grafica_muestra_curva_y_raiz_aproximada(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 500
        lienzo.winfo_height.return_value = 210
        funcion, _ = preparar_funcion("x^2 - 2")
        resultado = resolver_biseccion("x^2 - 2", 1, 2)

        dibujar_grafica_biseccion(lienzo, funcion, 1, 2, resultado)

        self.assertGreater(lienzo.create_line.call_count, 100)
        self.assertEqual(lienzo.create_oval.call_count, 4)
        self.assertEqual(lienzo.create_rectangle.call_count, 1)
        textos = [call.kwargs.get("text", "") for call in lienzo.create_text.call_args_list]
        self.assertTrue(any("x**2 - 2" in texto for texto in textos))
        self.assertTrue(any("raíz ≈" in texto for texto in textos))
        self.assertTrue(any("cambio de signo comprobado" in texto for texto in textos))
        self.assertTrue(any("no puede certificar continuidad" in texto for texto in textos))

    def test_grafica_indica_raiz_exacta_en_extremo(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 500
        lienzo.winfo_height.return_value = 210
        funcion, _ = preparar_funcion("x - 2")
        resultado = resolver_biseccion("x - 2", 2, 3)

        dibujar_grafica_biseccion(lienzo, funcion, 2, 3, resultado)

        textos = [call.kwargs.get("text", "") for call in lienzo.create_text.call_args_list]
        self.assertTrue(any("Raíz exacta en el extremo a" in texto for texto in textos))
        self.assertEqual(lienzo.create_rectangle.call_count, 0)

    def test_zoom_amplia_rango_y_conserva_la_raiz(self):
        for nivel in (-12, -1, 0, 1, 12):
            with self.subTest(nivel=nivel):
                a, b = _intervalo_zoom(1, 2, 1.5, nivel)
                self.assertLess(a, 1.5)
                self.assertGreater(b, 1.5)
                self.assertAlmostEqual(b - a, 1.5 ** (-nivel))
        self.assertEqual(_intervalo_zoom(1, 2, 1.5, 0), (1, 2))
        self.assertIsNone(_intervalo_zoom(-1.7e308, 1.7e308, 0, -1))
        a, b = _intervalo_zoom(-1.7e308, 1.7e308, 0, 1)
        self.assertAlmostEqual(a / 1.7e308, -1 / 1.5)
        self.assertAlmostEqual(b / 1.7e308, 1 / 1.5)

    def test_zoom_dibuja_mas_funcion_sin_mover_extremos_originales(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 800
        lienzo.winfo_height.return_value = 500
        funcion, _ = preparar_funcion("x^2 - 2")
        resultado = resolver_biseccion("x^2 - 2", 1, 2)
        muestreo = Mock(wraps=funcion)
        dibujar_grafica_biseccion(lienzo, muestreo, 1, 2, resultado, intervalo_vista=(0, 3))
        self.assertEqual(muestreo.call_args_list[0].args[0], 0)
        self.assertEqual(muestreo.call_args_list[-1].args[0], 3)
        extremos = [c for c in lienzo.create_text.call_args_list
                    if c.kwargs.get("text") in ("a", "b")]
        self.assertEqual(len(extremos), 2)
        for llamada, x in zip(extremos, (1, 2)):
            self.assertAlmostEqual(llamada.args[0], 56 + x / 3 * (800 - 16 - 56))
        self.assertEqual(resultado.intervalo_inicial, (1, 2))

    def test_zoom_oculta_extremos_fuera_de_la_vista(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 800
        lienzo.winfo_height.return_value = 500
        funcion, _ = preparar_funcion("x^2 - 2")
        resultado = resolver_biseccion("x^2 - 2", 1, 2)
        dibujar_grafica_biseccion(lienzo, funcion, 1, 2, resultado, intervalo_vista=(1.4, 1.5))
        textos = [c.kwargs.get("text") for c in lienzo.create_text.call_args_list]
        self.assertNotIn("a", textos)
        self.assertNotIn("b", textos)
        self.assertEqual(lienzo.create_oval.call_count, 2)

    def test_grafica_maneja_intervalos_con_salto_de_dominio(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 500
        lienzo.winfo_height.return_value = 210
        funcion, _ = preparar_funcion("sqrt(x)")

        dibujar_grafica_biseccion(lienzo, funcion, -1, 2)

        trazos_curva = [
            llamada for llamada in lienzo.create_line.call_args_list
            if llamada.kwargs.get("fill") == AZUL
        ]
        self.assertGreater(len(trazos_curva), 100)
        self.assertLess(len(trazos_curva), 400)
        textos = [call.kwargs.get("text", "") for call in lienzo.create_text.call_args_list]
        self.assertTrue(any("muestras no evaluables" in texto for texto in textos))

    def test_grafica_funciona_con_intervalos_que_exceden_el_rango_decimal(self):
        lienzo = Mock()
        lienzo.winfo_width.return_value = 500
        lienzo.winfo_height.return_value = 210
        funcion, _ = preparar_funcion("x")
        resultado = resolver_biseccion("x", -1.7e308, 1.7e308)

        dibujar_grafica_biseccion(lienzo, funcion, -1.7e308, 1.7e308, resultado)

        self.assertEqual(lienzo.create_oval.call_count, 4)

    @patch("interfaz.pestanaBiseccion.mostrar_texto")
    def test_limpiar_y_recargar(self, mostrar):
        self.pestana._cargar_ejemplo()
        self.pestana._limpiar()
        self.assertEqual(self.pestana.var_ecuacion.get(), "")
        self.assertEqual(self.pestana.var_a.get(), "")
        self.assertEqual(self.pestana.var_b.get(), "")
        self.assertEqual(mostrar.call_args.args[1], "")
        self.pestana.entrada_ecuacion.focus_set.assert_called_once()
        self.pestana._cargar_ejemplo()
        self.assertEqual(self.pestana.var_ecuacion.get(), "x^3 - x - 2 = 0")
        self.assertEqual(self.pestana.var_tolerancia.get(), "1e-6")


if __name__ == "__main__":
    unittest.main()
