"""PROGRAMA VECTORES - Calculadora de Álgebra Linealgit fet
Universidad Americana (UAM) - Álgebra Lineal (MTM0120)

DAVID ALEJANDRO ESPINOZA LARGAESPADA
ERICK ANTONIO ARANA ESPINOZA
JULIAN ALONSO TORREZ VALDIVIA

Características:
- Operaciones con vectores de dimensión n.
- Verificación de combinación lineal.
- Operaciones con matrices, incluyendo matriz inversa.
- Resolución y evaluación de ecuaciones matriciales A·X = B.
- Resolución de ecuaciones de una variable por el método de bisección.
- Resolución de ecuaciones de una variable por Regula Falsi (falsa posición).
- Operaciones con números romanos.
- Comprobaciones automáticas de resultados con tolerancia numérica.
- Opción para ejecutar un programa .py elaborado anteriormente."""

import os
import sys
import tkinter as tk
from tkinter import ttk


# Permite encontrar los módulos locales también al iniciar main.py directamente.
if __package__ is None or __package__ == "":
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from interfaz.estilos import actualizar_widgets, configurar_estilo
from interfaz.pestanaInicio import PestanaInicio
from interfaz.pestanaVectores import PestanaVectores
from interfaz.pestanaMatrices import PestanaMatrices
from interfaz.pestanaEcuaciones import PestanaEcuaciones
from interfaz.pestanaBiseccion import PestanaBiseccion
from interfaz.pestanaReglaFalsa import PestanaReglaFalsa
from interfaz.pestanaRomanos import PestanaRomanos
from interfaz.programaAnterior import PestanaProgramaAnterior

class CalculadoraAlgebraLineal(tk.Tk):
    """Ventana principal: agrupa cada módulo funcional en una pestaña."""

    def __init__(self):
        super().__init__()
        # Adapta el tamaño inicial a la pantalla y mantiene espacio para las pestañas.
        self.title("CalcuMaxing")
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        ancho = min(1440, max(700, int(ancho_pantalla * 0.88)))
        alto = min(980, max(560, int(alto_pantalla * 0.93)))
        self.minsize(min(920, ancho), min(640, alto))
        posicion_x = max(0, (ancho_pantalla - ancho) // 2)
        posicion_y = max(0, (alto_pantalla - alto) // 2)
        self.geometry(f"{ancho}x{alto}+{posicion_x}+{posicion_y}")
        self.modo_oscuro = False
        configurar_estilo(ttk.Style(self))
        self._construir_interfaz()
        actualizar_widgets(self, self.modo_oscuro)

    def _construir_interfaz(self):
        # Crea el encabezado y agrega cada módulo como una pestaña.
        contenedor = ttk.Frame(self, padding=14)
        contenedor.pack(fill="both", expand=True)

        encabezado = ttk.Frame(contenedor)
        encabezado.pack(fill="x", pady=(2, 0))
        ttk.Label(
            encabezado, text="CalcuMaxing", style="Titulo.TLabel",
        ).pack(side="left", anchor="w")
        self.boton_tema = ttk.Button(
            encabezado, text="Activar modo oscuro", command=self._alternar_tema,
        )
        self.boton_tema.pack(side="right", anchor="e")
        ttk.Label(
            contenedor,
            text="Herramientas de álgebra lineal, sistemas y raíces de ecuaciones.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(2, 8))
        ttk.Separator(contenedor).pack(fill="x", pady=(0, 10))

        notebook = ttk.Notebook(contenedor)
        notebook.pack(fill="both", expand=True)

        notebook.add(PestanaInicio(notebook), text="Inicio")
        notebook.add(PestanaVectores(notebook), text="Vectores")
        notebook.add(PestanaMatrices(notebook), text="Matrices")
        notebook.add(PestanaEcuaciones(notebook), text="Ecuaciones A·X = B")
        notebook.add(PestanaBiseccion(notebook), text="Bisección")
        notebook.add(PestanaReglaFalsa(notebook), text="Regula Falsi")
        notebook.add(PestanaRomanos(notebook), text="Números romanos")
        notebook.add(PestanaProgramaAnterior(notebook), text="Programa anterior")

    def _alternar_tema(self):
        """Cambia la paleta de toda la aplicación y actualiza las gráficas."""
        self.modo_oscuro = not self.modo_oscuro
        configurar_estilo(ttk.Style(self), self.modo_oscuro)
        actualizar_widgets(self, self.modo_oscuro)
        self.boton_tema.configure(
            text="Activar modo claro" if self.modo_oscuro else "Activar modo oscuro",
        )
        def redibujar_graficas(padre):
            for widget in padre.winfo_children():
                redibujar = getattr(widget, "_redibujar_grafica", None)
                if redibujar is not None:
                    redibujar()
                redibujar_graficas(widget)

        redibujar_graficas(self)


if __name__ == "__main__":
    CalculadoraAlgebraLineal().mainloop()