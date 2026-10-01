"""Pestaña Matrices: suma, resta, producto por escalar y producto de matrices."""

import tkinter as tk
from tkinter import ttk

from nucleo.numeros import convertir_numero, limpiar_numero
from nucleo.matrices import (
    leer_matriz, matriz_a_texto, sumar_matrices, restar_matrices,
    multiplicar_matriz_escalar, multiplicar_matrices, matriz_inversa,
)
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado, AyudaEmergente


class PestanaMatrices(ttk.Frame):
    """Agrupa la entrada de matrices A y B, y las operaciones disponibles entre ellas."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_entrada()
        self._construir_operaciones()

    def _construir_entrada(self):
        marco = ttk.LabelFrame(self, text="Matrices A y B", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Matriz A (una fila por línea):").pack(anchor="w")
        self.txt_a = tk.Text(marco, height=9)
        self.txt_a.pack(fill="x", pady=(2, 10))
        self.txt_a.insert("1.0", "1 2\n3 4")
        AyudaEmergente(self.txt_a, "Separa los valores de cada fila con espacios o comas.")

        ttk.Label(marco, text="Matriz B (una fila por línea):").pack(anchor="w")
        self.txt_b = tk.Text(marco, height=9)
        self.txt_b.pack(fill="x", pady=(2, 10))
        self.txt_b.insert("1.0", "5 6\n7 8")

        fila_escalar = ttk.Frame(marco)
        fila_escalar.pack(fill="x", pady=5)
        ttk.Label(fila_escalar, text="Escalar (k):").pack(side="left")
        self.ent_escalar = ttk.Entry(fila_escalar, width=12)
        self.ent_escalar.pack(side="left", padx=8)
        self.ent_escalar.insert(0, "2")
        ttk.Button(fila_escalar, text="Limpiar", command=self._limpiar).pack(side="right")

    def _construir_operaciones(self):
        marco = ttk.LabelFrame(self, text="Elige una operación", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        botones = ttk.Frame(marco)
        botones.pack(fill="x")
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        ttk.Button(botones, text="Sumar (A + B)", command=self._accion_suma).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Restar (A − B)", command=self._accion_resta).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Multiplicar por escalar (k·A)", command=self._accion_escalar).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Multiplicar matrices (A × B)", command=self._accion_producto).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Matriz inversa (A⁻¹)", style="Accion.TButton", command=self._accion_inversa).grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        ttk.Label(marco, text="Resultado:").pack(anchor="w", pady=(16, 4))
        marco_resultado, self.txt_resultado = crear_area_resultado(marco, alto=20)
        marco_resultado.pack(fill="both", expand=True)

    def _obtener_ab(self):
        return leer_matriz(self.txt_a.get("1.0", "end")), leer_matriz(self.txt_b.get("1.0", "end"))

    def _accion_suma(self):
        self._ejecutar(lambda: sumar_matrices(*self._obtener_ab()), "A + B =\n\n")

    def _accion_resta(self):
        self._ejecutar(lambda: restar_matrices(*self._obtener_ab()), "A − B =\n\n")

    def _accion_producto(self):
        self._ejecutar(lambda: multiplicar_matrices(*self._obtener_ab()), "A × B =\n\n")

    def _accion_inversa(self):
        try:
            a = leer_matriz(self.txt_a.get("1.0", "end"))
            resultado = matriz_inversa(a)
            mostrar_texto(self.txt_resultado, "A⁻¹ =\n\n" + matriz_a_texto(resultado))
        except ValueError as error:
            mostrar_error(error)

    def _accion_escalar(self):
        try:
            a = leer_matriz(self.txt_a.get("1.0", "end"))
            escalar = convertir_numero(self.ent_escalar.get())
            resultado = multiplicar_matriz_escalar(a, escalar)
            mostrar_texto(self.txt_resultado, f"{limpiar_numero(escalar)} · A =\n\n" + matriz_a_texto(resultado))
        except ValueError as error:
            mostrar_error(error)

    def _ejecutar(self, operacion, etiqueta):
        try:
            resultado = operacion()
            mostrar_texto(self.txt_resultado, etiqueta + matriz_a_texto(resultado))
        except ValueError as error:
            mostrar_error(error)

    def _limpiar(self):
        self.txt_a.delete("1.0", "end")
        self.txt_b.delete("1.0", "end")
        self.ent_escalar.delete(0, "end")
        mostrar_texto(self.txt_resultado, "")