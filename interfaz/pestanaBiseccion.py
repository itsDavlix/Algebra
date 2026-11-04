"""Pestaña para resolver una ecuación de una variable por bisección."""

import tkinter as tk
from tkinter import ttk

from interfaz.ayudas import crear_area_resultado, mostrar_error, mostrar_texto
from nucleo.biseccion import MAX_ITERACIONES, formatear_resultado_biseccion, resolver_biseccion
from nucleo.numeros import convertir_numero


class PestanaBiseccion(ttk.Frame):
    """Recibe la ecuación y muestra la aproximación con todo el procedimiento."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=2, minsize=330)
        self.columnconfigure(1, weight=3, minsize=350)
        self.rowconfigure(0, weight=1)
        self.var_ecuacion = tk.StringVar(self)
        self.var_a = tk.StringVar(self)
        self.var_b = tk.StringVar(self)
        self.var_tolerancia = tk.StringVar(self)
        self.var_iteraciones = tk.StringVar(self)
        self._construir_entrada()
        self._construir_resultado()
        self._cargar_ejemplo()

    def _construir_entrada(self):
        marco = ttk.LabelFrame(self, text="Resolver f(x) = 0", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Ecuación o expresión f(x):").pack(anchor="w")
        self.entrada_ecuacion = ttk.Entry(marco, textvariable=self.var_ecuacion, width=34)
        self.entrada_ecuacion.pack(fill="x", pady=(3, 5))
        self.entrada_ecuacion.bind("<Return>", self._accion_resolver)
        ttk.Label(
            marco, text="Ejemplos: x^3 - x - 2   o   x^2 = 2\nSin igualdad, se interpreta f(x) = 0.",
            style="Ayuda.TLabel", justify="left", wraplength=320,
        ).pack(anchor="w", pady=(0, 12))

        datos = ttk.Frame(marco)
        datos.pack(fill="x")
        datos.columnconfigure(0, weight=1)
        datos.columnconfigure(1, weight=1)
        campos = (
            ("Extremo a:", self.var_a), ("Extremo b:", self.var_b),
            ("Tolerancia (error en x):", self.var_tolerancia),
            ("Máx. iteraciones:", self.var_iteraciones),
        )
        for indice, (etiqueta, variable) in enumerate(campos):
            fila, columna = (indice // 2) * 2, indice % 2
            margen = (0, 6) if columna == 0 else (6, 0)
            ttk.Label(datos, text=etiqueta).grid(row=fila, column=columna, sticky="w", padx=margen)
            entrada = ttk.Entry(datos, textvariable=variable, width=13)
            entrada.grid(row=fila + 1, column=columna, sticky="ew", padx=margen, pady=(3, 10))
            entrada.bind("<Return>", self._accion_resolver)

        ttk.Button(marco, text="Resolver por bisección", style="Accion.TButton",
                   command=self._accion_resolver).pack(fill="x", pady=(4, 6))
        botones = ttk.Frame(marco)
        botones.pack(fill="x")
        ttk.Button(botones, text="Cargar ejemplo", command=self._cargar_ejemplo).pack(
            side="left", fill="x", expand=True)
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=(6, 0))

        ttk.Label(
            marco, text="La función debe ser continua en [a, b], con a < b y valores de "
            "signos opuestos en los extremos (o una raíz en un extremo).",
            style="Ayuda.TLabel", justify="left", wraplength=320,
        ).pack(anchor="w", pady=(14, 8))
        ttk.Label(
            marco, text="Usa * para multiplicar, ^ o ** para potencias y punto decimal. "
            "Funciones: sin/sen, cos, tan, sqrt/raiz, exp, log/ln (natural), log10 y abs. "
            "Constantes: pi y e. Ángulos en radianes.\n"
            f"Tolerancia > 0; máximo entre 1 y {MAX_ITERACIONES} iteraciones.",
            style="Ayuda.TLabel", justify="left", wraplength=320,
        ).pack(anchor="w")

    def _construir_resultado(self):
        marco = ttk.LabelFrame(self, text="Resultado y procedimiento paso a paso",
                               style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        area, self.txt_resultado = crear_area_resultado(marco, alto=24)
        self.txt_resultado.configure(width=42)
        area.pack(fill="both", expand=True)

    def _accion_resolver(self, _evento=None):
        try:
            a = convertir_numero(self.var_a.get(), "El extremo a")
            b = convertir_numero(self.var_b.get(), "El extremo b")
            tolerancia = convertir_numero(self.var_tolerancia.get(), "La tolerancia")
            texto_iteraciones = self.var_iteraciones.get().strip()
            if (not texto_iteraciones.isascii() or not texto_iteraciones.isdecimal()
                    or len(texto_iteraciones) > 4):
                raise ValueError(f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}.")
            resultado = resolver_biseccion(
                self.var_ecuacion.get(), a, b, tolerancia, int(texto_iteraciones),
            )
            mostrar_texto(self.txt_resultado, formatear_resultado_biseccion(resultado))
        except ValueError as error:
            mostrar_texto(self.txt_resultado, "No se pudo resolver la ecuación.\n\n" + str(error))
            mostrar_error(error)

    def _cargar_ejemplo(self):
        self.var_ecuacion.set("x^3 - x - 2 = 0")
        self.var_a.set("1")
        self.var_b.set("2")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        mostrar_texto(self.txt_resultado, "Pulsa «Resolver por bisección» para calcular la raíz del ejemplo.")

    def _limpiar(self):
        for variable in (self.var_ecuacion, self.var_a, self.var_b):
            variable.set("")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        mostrar_texto(self.txt_resultado, "")
        self.entrada_ecuacion.focus_set()
