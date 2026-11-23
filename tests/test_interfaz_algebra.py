"""Vistas de sistemas, matrices y vectores con una ventana Tk real."""

import tkinter as tk
import unittest
from tkinter import ttk

from interfaz.estilos import configurar_estilo
from interfaz.sistemas import VistaSistemas
from interfaz.vistaMatrices import VistaMatrices
from interfaz.vistaRomanos import VistaRomanos
from interfaz.vistaVectores import VistaVectores
from nucleo.ejercicios import MATRICES, SISTEMAS


class PruebasVistas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk no disponible: {exc}")
        configurar_estilo(ttk.Style(cls.raiz))
        cls.raiz.geometry("1500x950")

    @classmethod
    def tearDownClass(cls):
        cls.raiz.destroy()

    def _vista(self, clase):
        vista = clase(self.raiz)
        vista.pack(fill="both", expand=True)
        self.addCleanup(vista.destroy)
        self.raiz.update()
        return vista

    def test_sistemas_flujo_y_comparacion(self):
        vista = self._vista(VistaSistemas)
        vista.cargar_ejemplo()
        self.assertEqual(vista.resultado.tipo, "unica")
        self.assertIn("det(A)", vista.analisis.cget("text"))
        vista.cambiar_metodo("Jacobi")
        self.assertIn("Estrictamente dominante", vista.validacion.cget("text"))
        vista.resolver()
        self.raiz.update()
        self.assertTrue(vista.resultado.convergio)
        vista.tabla.seleccionar(2)
        self.raiz.update()
        self.assertIn("x₂⁽²⁾ = (25 + 0.600000 − 1.100000 − 3(1.875000)) / 11", vista.panel.texto.get("1.0", "end"))
        vista.comparar()
        self.assertEqual(set(vista.resultados), {"Jacobi", "Gauss-Seidel"})
        self.assertIn("Coinciden", vista.panel.texto.get("1.0", "end"))
        self.assertTrue(vista.plano.capas)

    def test_diagnostico_y_matriz_con_diagonal(self):
        vista = self._vista(VistaSistemas)
        vista.establecer_texto("2x2 - 3x3 + x4 + 4x5 = -18\n3x1 + 2x3 - 4x4 + x5 = 6\n"
                               "-2x1 + 5x2 + 3x4 - 2x5 = -2\n4x1 - x2 + 3x3 - 3x5 = 24\nx1 - 3x2 - 2x3 + 5x4 = 4")
        self.raiz.update()
        self.assertEqual(len(vista.vista_previa.tag_ranges("cero")), 10)      # los cinco aᵢᵢ = 0
        self.assertIn("0 ≤ 10 ✗", vista.vista_previa.get("1.0", "end"))
        marcas = [f[1].cget("text")[0] for f in vista.filas_diagnostico.values()]
        self.assertEqual(marcas, ["✓", "✗", "↻"])
        vista.usar_metodo_recomendado("Jacobi")
        self.assertIn("Usa Gauss-Jordan o Gauss-Seidel", vista.validacion.cget("text"))
        vista.usar_metodo_recomendado("Gauss-Seidel")                         # reordena solo
        self.assertEqual(vista.reordenado, (1, 2, 0, 4, 3))
        self.assertEqual(vista.vista_previa.tag_ranges("cero"), ())
        vista.resolver()
        self.assertTrue(vista.resultado.convergio)

    def test_sistemas_reordenar_y_ejercicios(self):
        vista = self._vista(VistaSistemas)
        ejercicio = next(e for e in SISTEMAS if e.clave == "it_banco9")
        vista.cargar_ejercicio(ejercicio)
        self.assertEqual(vista.reordenado, (2, 1, 0, 3))
        self.assertTrue(vista.resultado.convergio)
        vista.establecer_texto("2x + y = 3\nx - y = 0")
        self.assertEqual(vista.reordenado, ())
        vista.establecer_texto("2x + = 3")
        self.assertIn("✗", vista.estado_entrada.cget("text"))

    def test_matrices_inversa_y_operaciones(self):
        vista = self._vista(VistaMatrices)
        vista.cargar_ejercicio(MATRICES[0])
        self.assertIn("invertible", vista.estado.cget("text"))
        self.assertIn("A·A⁻¹ = I", vista.valor.get("1.0", "end"))
        vista.fracciones.set(False)
        vista._refrescar()
        self.assertNotIn("/", vista.valor.get("1.0", "end").split("A·A⁻¹")[0])
        vista.cambiar_operacion("det(A)")
        vista._cambiar_metodo_det("Cofactores")
        vista.calcular()
        self.assertIn("= −54", vista.valor.get("1.0", "end"))
        vista.cambiar_operacion("A · B")
        vista._escribir("B", "1 0\n0 1")
        vista.calcular()
        self.assertIn("columnas de A", vista.validacion.cget("text"))

    def test_vectores(self):
        vista = self._vista(VistaVectores)
        vista.cargar_ejemplo()
        self.assertEqual(vista.valor.cget("text"), "V₁ · V₂ = 12")
        vista.cambiar_operacion("V₁ × V₂")
        vista.calcular()
        self.assertIn("(27, 6, −13)", vista.valor.cget("text"))
        vista.cambiar_operacion("Independencia")
        vista.texto_conjunto.insert("1.0", "1, 2\n2, 4")
        vista.calcular()
        self.assertEqual(vista.valor.cget("text"), "Linealmente dependientes")

    def test_plano_de_vectores_y_de_sistemas(self):
        vista = self._vista(VistaVectores)
        vista.cargar_ejemplo()                                        # V₁ · V₂ en R³: sin plano
        self.assertTrue(vista.boton_plano.instate(["disabled"]))
        vista.v1.set("1, 2")
        vista.v2.set("3, −1")
        vista.cambiar_operacion("V₁ + V₂")
        vista.calcular()
        self.assertTrue(vista.boton_plano.instate(["!disabled"]))
        vista.ver_plano()
        self.raiz.update()
        self.assertEqual(len(vista.ventanas["plano"].plano.puntos), 3)
        vista.ventanas["plano"].destroy()
        vista = self._vista(VistaSistemas)
        vista.cambiar_metodo("Gauss-Seidel")
        vista.establecer_texto("4x + y = 9\nx - 3y = -5")
        vista.variable_x0.set("0, 0")
        vista.resolver()
        vista._cambiar_grafica("Plano")
        self.raiz.update()
        claves = {p.clave for p in vista.plano.puntos}
        self.assertTrue({"sol", "k0", "k1"} <= claves)
        self.assertEqual(len(vista.plano.curvas_extra), 2)
        vista.establecer_texto("x + y + z = 3\nx - y = 0\ny + z = 2")
        vista.resolver()
        self.raiz.update()
        self.assertEqual(vista.plano.puntos, [])
        self.assertIn("2 ecuaciones", vista.aviso_grafica.cget("text"))

    def test_romanos_en_vivo_sin_ventanas_de_error(self):
        vista = self._vista(VistaRomanos)
        self.assertEqual(vista.valor.cget("text"), "XX")              # ejemplo XIV + VI
        vista.cambiar_operacion("A × B")
        self.assertEqual(vista.valor.cget("text"), "LXXXIV")
        vista.a.set("IIII")                                           # no canónico: aviso en línea
        self.assertIn("✗", vista.nota_a.cget("text"))
        self.assertIsNone(vista.resultado)
        vista.a.set("MM")
        vista.b.set("MM")                                             # 4000 000 > 3999
        self.assertIn("3999", vista.validacion.cget("text"))
        vista.cambiar_operacion("A ÷ B")
        vista.a.set("XX")
        vista.b.set("IV")
        self.assertEqual(vista.valor.cget("text"), "V")
        self.assertIn("COMPROBACIÓN", vista.panel.completo()[-1][0] + "".join(t for t, _ in vista.panel.completo()))
        vista.b.set("")
        self.assertIsNone(vista.resultado)

    def test_copiar_tabla_y_procedimiento(self):
        vista = self._vista(VistaSistemas)
        vista.cargar_ejemplo()
        vista.cambiar_metodo("Jacobi")
        vista.resolver()
        self.raiz.update()
        vista.tabla.copiar()
        copiado = self.raiz.clipboard_get().split("\n")
        self.assertEqual(len(copiado), len(vista.resultado.iteraciones) + 2)   # encabezado + fila k = 0
        self.assertTrue(all(len(f.split("\t")) == len(vista.tabla.columnas) for f in copiado))
        self.assertEqual(vista.tabla.boton_copiar.cget("text"), "✓ Copiado")
        vista.panel.copiar()
        texto = self.raiz.clipboard_get()
        self.assertIn("Jacobi", texto)
        self.assertGreater(texto.count("Iteración"), 5)   # todo el desarrollo, no solo la fila elegida

    def test_encabezados_de_tarjetas_sin_recortes(self):
        """Con la ventana al mínimo (1000 px) los botones pasan a icono y nada queda cortado."""
        self.raiz.geometry("1000x850")
        self.addCleanup(self.raiz.geometry, "1500x950")
        for _ in range(3):
            self.raiz.update()
        for clase in (VistaSistemas, VistaMatrices, VistaVectores):
            vista = self._vista(clase)
            if hasattr(vista, "cargar_ejemplo"):
                vista.cargar_ejemplo()
            for _ in range(5):
                self.raiz.update()
            for tarjeta in (vista.tabla, vista.panel):
                cabecera = next(c for c in tarjeta.winfo_children() if c.winfo_class() == "TFrame")
                for hijo in cabecera.winfo_children():
                    with self.subTest(vista=clase.__name__, widget=str(hijo)):
                        self.assertGreaterEqual(hijo.winfo_width(), 10)
                        self.assertLessEqual(hijo.winfo_x() + hijo.winfo_width(), cabecera.winfo_width())
            vista.destroy()   # cada vista debe tener la ventana para ella sola


if __name__ == "__main__":
    unittest.main()
