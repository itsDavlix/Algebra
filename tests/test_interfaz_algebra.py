"""Vistas de sistemas, matrices y vectores con una ventana Tk real."""

import tkinter as tk
import unittest
from tkinter import ttk

from interfaz.estilos import configurar_estilo
from interfaz.sistemas import VistaSistemas
from interfaz.vistaMatrices import VistaMatrices
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


if __name__ == "__main__":
    unittest.main()
