"""Pestaña Vectores: operaciones básicas y verificación de combinación lineal."""

import tkinter as tk
from tkinter import ttk

from nucleo.numeros import convertir_numero, limpiar_numero
from nucleo.vectores import (
    leer_vector, vector_a_texto, sumar_vectores, restar_vectores, multiplicar_vector_escalar,
)
from nucleo.sistemas import verificar_combinacion_lineal
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado, AyudaEmergente


class PestanaVectores(ttk.Frame):
    """Agrupa las operaciones vectoriales y la verificación de combinación lineal."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_operaciones()
        self._construir_combinacion_lineal()

    # ---------------- Operaciones básicas ----------------

    def _construir_operaciones(self):
        marco = ttk.LabelFrame(self, text="Operaciones con vectores", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Primer vector (V1):").pack(anchor="w")
        self.ent_v1 = ttk.Entry(marco)
        self.ent_v1.pack(fill="x", pady=(2, 8))
        self.ent_v1.insert(0, "1, 2, 3")
        AyudaEmergente(self.ent_v1, "Separa los valores con comas o espacios. Ejemplo: 1, 2, 3")

        ttk.Label(marco, text="Segundo vector (V2):").pack(anchor="w")
        self.ent_v2 = ttk.Entry(marco)
        self.ent_v2.pack(fill="x", pady=(2, 8))
        self.ent_v2.insert(0, "4, 5, 6")
        AyudaEmergente(self.ent_v2, "Debe tener la misma cantidad de componentes que V1.")

        fila_escalar = ttk.Frame(marco)
        fila_escalar.pack(fill="x", pady=(0, 10))
        ttk.Label(fila_escalar, text="Escalar (k):").pack(side="left")
        self.ent_escalar = ttk.Entry(fila_escalar, width=12)
        self.ent_escalar.pack(side="left", padx=8)
        self.ent_escalar.insert(0, "2")

        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=4)
        ttk.Button(botones, text="Sumar (V1 + V2)", command=self._accion_suma).pack(side="left", padx=(0, 5))
        ttk.Button(botones, text="Restar (V1 − V2)", command=self._accion_resta).pack(side="left", padx=5)
        ttk.Button(botones, text="Multiplicar por escalar (k·V1)", command=self._accion_escalar).pack(side="left", padx=5)
        ttk.Button(botones, text="Limpiar", command=self._limpiar_operaciones).pack(side="right")

        ttk.Label(marco, text="Resultado:").pack(anchor="w", pady=(16, 4))
        marco_resultado, self.txt_resultado = crear_area_resultado(marco, alto=9)
        marco_resultado.pack(fill="both", expand=True)

    def _accion_suma(self):
        self._ejecutar(lambda: sumar_vectores(leer_vector(self.ent_v1.get()), leer_vector(self.ent_v2.get())), "V1 + V2 = ")

    def _accion_resta(self):
        self._ejecutar(lambda: restar_vectores(leer_vector(self.ent_v1.get()), leer_vector(self.ent_v2.get())), "V1 − V2 = ")

    def _accion_escalar(self):
        try:
            v1 = leer_vector(self.ent_v1.get())
            escalar = convertir_numero(self.ent_escalar.get())
            resultado = multiplicar_vector_escalar(v1, escalar)
            mostrar_texto(self.txt_resultado, f"{limpiar_numero(escalar)} · V1 = {vector_a_texto(resultado)}")
        except ValueError as error:
            mostrar_error(error)

    def _ejecutar(self, operacion, etiqueta):
        try:
            resultado = operacion()
            mostrar_texto(self.txt_resultado, etiqueta + vector_a_texto(resultado))
        except ValueError as error:
            mostrar_error(error)

    def _limpiar_operaciones(self):
        for entrada in (self.ent_v1, self.ent_v2, self.ent_escalar):
            entrada.delete(0, "end")
        mostrar_texto(self.txt_resultado, "")

    # ---------------- Combinación lineal ----------------

    def _construir_combinacion_lineal(self):
        marco = ttk.LabelFrame(self, text="¿Es combinación lineal?", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        ttk.Label(marco, text="Vectores generadores (uno por línea):").pack(anchor="w")
        self.txt_generadores = tk.Text(marco, height=8)
        self.txt_generadores.pack(fill="x", pady=(2, 8))
        self.txt_generadores.insert("1.0", "1 0\n0 1")
        AyudaEmergente(self.txt_generadores, "No es necesario conocer la dimensión: agrega tantos vectores como necesites.")

        ttk.Label(marco, text="Vector a comprobar:").pack(anchor="w")
        self.ent_objetivo = ttk.Entry(marco)
        self.ent_objetivo.pack(fill="x", pady=(2, 8))
        self.ent_objetivo.insert(0, "3, 5")

        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=5)
        ttk.Button(botones, text="Comprobar combinación lineal", style="Accion.TButton", command=self._accion_combinacion_lineal).pack(side="left", fill="x", expand=True)
        ttk.Button(botones, text="Limpiar", command=self._limpiar_combinacion).pack(side="left", padx=(6, 0))

        ttk.Label(marco, text="Resultado:").pack(anchor="w", pady=(10, 4))
        marco_resultado, self.txt_resultado_combinacion = crear_area_resultado(marco, alto=11, fuente=("Segoe UI", 10))
        marco_resultado.pack(fill="both", expand=True)

    def _accion_combinacion_lineal(self):
        try:
            lineas = self.txt_generadores.get("1.0", "end").strip().splitlines()
            generadores = [leer_vector(linea) for linea in lineas if linea.strip()]
            objetivo = leer_vector(self.ent_objetivo.get())

            es_combinacion, coeficientes, tipo = verificar_combinacion_lineal(generadores, objetivo)

            if not es_combinacion:
                salida = (
                    "No, el vector no se puede escribir como combinación lineal de los vectores dados.\n\n"
                    "Al plantear el sistema de ecuaciones no se encontró solución para los coeficientes."
                )
            else:
                salida = "Sí, el vector se puede escribir como combinación lineal de los vectores dados.\n\n"
                salida += "Coeficientes encontrados:\n"
                salida += "\n".join(f"c{i + 1} = {limpiar_numero(c)}" for i, c in enumerate(coeficientes))
                salida += "\n\n" + (
                    "La combinación es única."
                    if tipo == "unica"
                    else "Hay más de una combinación posible; se muestran las variables libres en 0."
                )

            mostrar_texto(self.txt_resultado_combinacion, salida)
        except ValueError as error:
            mostrar_error(error)

    def _limpiar_combinacion(self):
        self.txt_generadores.delete("1.0", "end")
        self.ent_objetivo.delete(0, "end")
        mostrar_texto(self.txt_resultado_combinacion, "")