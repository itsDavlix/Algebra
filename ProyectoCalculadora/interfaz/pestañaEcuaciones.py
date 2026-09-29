"""Pestaña Ecuaciones A·X = B: resolución por Gauss-Jordan y comprobación de soluciones."""

import tkinter as tk
from tkinter import ttk

from nucleo.matrices import leer_matriz, matriz_a_texto, multiplicar_matrices, matrices_aproximadamente_iguales
from nucleo.numeros import limpiar_numero
from nucleo.sistemas import resolver_sistema_gauss_jordan
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado, AyudaEmergente


class PestanaEcuaciones(ttk.Frame):
    """Permite resolver A·X = B y comprobar si una matriz X propuesta cumple la igualdad."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_entrada()
        self._construir_resultado()

    def _construir_entrada(self):
        marco = ttk.LabelFrame(self, text="Resolver A · X = B", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Matriz A:").pack(anchor="w")
        self.txt_a = tk.Text(marco, height=7)
        self.txt_a.pack(fill="x", pady=(2, 8))
        self.txt_a.insert("1.0", "2 1\n1 -1")
        AyudaEmergente(self.txt_a, "Matriz de coeficientes del sistema.")

        ttk.Label(marco, text="Matriz B:").pack(anchor="w")
        self.txt_b = tk.Text(marco, height=7)
        self.txt_b.pack(fill="x", pady=(2, 8))
        self.txt_b.insert("1.0", "5\n1")

        ttk.Button(marco, text="Resolver ecuación matricial", style="Accion.TButton", command=self._accion_resolver).pack(fill="x", pady=5)

        ttk.Label(marco, text="Para comprobar una X concreta, escríbela aquí:").pack(anchor="w", pady=(12, 0))
        self.txt_x = tk.Text(marco, height=7)
        self.txt_x.pack(fill="x", pady=(2, 8))
        self.txt_x.insert("1.0", "2\n1")

        fila_botones = ttk.Frame(marco)
        fila_botones.pack(fill="x", pady=5)
        ttk.Button(fila_botones, text="Comprobar A · X = B", command=self._accion_evaluar).pack(side="left", fill="x", expand=True)
        ttk.Button(fila_botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=(6, 0))

    def _construir_resultado(self):
        marco = ttk.LabelFrame(self, text="Resultado", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        marco_resultado, self.txt_resultado = crear_area_resultado(marco, alto=24)
        marco_resultado.pack(fill="both", expand=True)

    def _accion_resolver(self):
        try:
            a = leer_matriz(self.txt_a.get("1.0", "end"))
            b = leer_matriz(self.txt_b.get("1.0", "end"))
            solucion, tipo, pivotes = resolver_sistema_gauss_jordan(a, b)

            salida = "Solución X:\n\n" + matriz_a_texto(solucion)
            salida += (
                "\n\nTipo de solución: única."
                if tipo == "unica"
                else "\n\nTipo de solución: infinitas soluciones (variables libres = 0)."
            )
            salida += "\n\nColumnas con pivote: " + (", ".join(str(i + 1) for i in pivotes) or "ninguna")
            mostrar_texto(self.txt_resultado, salida)

            texto_x = "\n".join(" ".join(limpiar_numero(x) for x in fila) for fila in solucion)
            self.txt_x.delete("1.0", "end")
            self.txt_x.insert("1.0", texto_x)
        except ValueError as error:
            mostrar_error(error)

    def _accion_evaluar(self):
        try:
            a = leer_matriz(self.txt_a.get("1.0", "end"))
            b = leer_matriz(self.txt_b.get("1.0", "end"))
            x = leer_matriz(self.txt_x.get("1.0", "end"))

            producto = multiplicar_matrices(a, x)
            cumple = matrices_aproximadamente_iguales(producto, b)

            salida = "A · X =\n\n" + matriz_a_texto(producto)
            salida += "\n\nB =\n\n" + matriz_a_texto(b)
            salida += "\n\n" + ("Sí, la X escrita cumple A · X = B." if cumple else "No, la X escrita no cumple A · X = B.")
            mostrar_texto(self.txt_resultado, salida)
        except ValueError as error:
            mostrar_error(error)

    def _limpiar(self):
        for caja in (self.txt_a, self.txt_b, self.txt_x):
            caja.delete("1.0", "end")
        mostrar_texto(self.txt_resultado, "")