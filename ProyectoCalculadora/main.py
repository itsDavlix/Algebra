import tkinter as tk
from tkinter import ttk

from interfaz.estilos import configurar_estilo
from interfaz.pestanaInicio import PestanaInicio
from interfaz.pestanaVectores import PestanaVectores
from interfaz.pestanaMatrices import PestanaMatrices
from interfaz.pestanaEcuaciones import PestanaEcuaciones
from interfaz.pestanaRomanos import PestanaRomanos
from interfaz.programaAnterior import PestanaProgramaAnterior

"""PROGRAMA VECTORES - Calculadora de Álgebra Lineal
Universidad Americana (UAM) - Álgebra Lineal (MTM0120)

DAVID ALEJANDRO ESPINOZA LARGAESPADA
ERICK ANTONIO ARANA ESPINOZA
JULIAN ALONSO TORREZ VALDIVIA

Características:
- Operaciones con vectores de dimensión n.
- Verificación de combinación lineal.
- Operaciones con matrices, incluyendo matriz inversa.
- Resolución y evaluación de ecuaciones matriciales A·X = B.
- Operaciones con números romanos.
- Comprobaciones automáticas de resultados con tolerancia numérica.
- Opción para ejecutar un programa .py elaborado anteriormente."""


class CalculadoraAlgebraLineal(tk.Tk):
    """Ventana principal: agrupa cada módulo funcional en una pestaña."""

    def __init__(self):
        super().__init__()
        self.title("Calculadora de Álgebra Lineal")
        self.geometry("1040x720")
        self.minsize(920, 640)
        configurar_estilo(ttk.Style(self))
        self._construir_interfaz()

    def _construir_interfaz(self):
        contenedor = ttk.Frame(self, padding=14)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(contenedor, text="Calculadora de Álgebra Lineal", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            contenedor,
            text="Selecciona una pestaña para trabajar con vectores, matrices, ecuaciones o números romanos.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 12))

        notebook = ttk.Notebook(contenedor)
        notebook.pack(fill="both", expand=True)

        notebook.add(PestanaInicio(notebook), text="Inicio")
        notebook.add(PestanaVectores(notebook), text="Vectores")
        notebook.add(PestanaMatrices(notebook), text="Matrices")
        notebook.add(PestanaEcuaciones(notebook), text="Ecuaciones A·X = B")
        notebook.add(PestanaRomanos(notebook), text="Números romanos")
        notebook.add(PestanaProgramaAnterior(notebook), text="Programa anterior")


if __name__ == "__main__":
    CalculadoraAlgebraLineal().mainloop()