"""Pestaña Inicio: guía rápida de uso de la calculadora."""

from tkinter import ttk


class PestanaInicio(ttk.Frame):
    """Explica el formato de entrada y qué operaciones ofrece cada módulo."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self._construir()

    def _construir(self):
        marco = ttk.LabelFrame(self, text="Antes de comenzar", style="Seccion.TLabelframe", padding=18)
        marco.pack(fill="both", expand=True)

        texto = (
            "Escribe los datos en el formato indicado y pulsa la operación que necesitas.\n\n"
            "¿Cómo se escribe un vector?\n"
            "• Los componentes van separados por espacios o comas.\n"
            "• Ejemplo: 1, 2, 3     o     1 2 3\n\n"
            "¿Cómo se escribe una matriz?\n"
            "• Cada línea representa una fila.\n"
            "• Ejemplo:\n"
            "      1  2\n"
            "      3  4\n\n"
            "¿Cómo se escribe un número romano?\n"
            "• Usa letras romanas en su forma estándar.\n"
            "• Ejemplos: IV, XIV, XL, MCMXC.\n\n"
            "Módulos disponibles:\n"
            "• Vectores: suma, resta, producto por escalar y verificación de combinación lineal.\n"
            "• Matrices: suma, resta, producto por escalar, producto de matrices y matriz inversa.\n"
            "• Ecuaciones A·X = B: resolución por Gauss-Jordan y comprobación de una solución propuesta.\n"
            "• Números romanos: suma, resta, multiplicación y división exacta.\n"
            "• Programa anterior: permite ejecutar un archivo .py elaborado previamente.\n\n"
            "El programa usa únicamente Python estándar, sin bibliotecas externas."
        )
        ttk.Label(marco, text=texto, justify="left", font=("Segoe UI", 11)).pack(anchor="nw")
