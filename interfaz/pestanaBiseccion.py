"""Pestaña para resolver una ecuación de una variable por bisección."""

import tkinter as tk
from tkinter import ttk

from interfaz.ayudas import crear_area_resultado, mostrar_error, mostrar_texto
from interfaz.estilos import AZUL, AZUL_BORDE, TEXTO, TEXTO_SUAVE, VERDE
from nucleo.biseccion import (
    MAX_ITERACIONES, formatear_resultado_biseccion, preparar_funcion, resolver_biseccion,
)
from nucleo.numeros import convertir_numero


def _interpolar_x(a, b, proporcion):
    diferencia = b - a
    if diferencia == float("inf"):
        return a * (1 - proporcion) + b * proporcion
    return a + diferencia * proporcion


def _proporcion_x(x, a, b):
    diferencia = b - a
    if diferencia == float("inf"):
        return (x / 2 - a / 2) / (b / 2 - a / 2)
    return (x - a) / diferencia


def dibujar_grafica_biseccion(canvas, funcion, a, b, resultado=None):
    """Traza f(x) en [a, b], omitiendo los puntos fuera de su dominio."""
    canvas.delete("all")
    ancho = max(canvas.winfo_width(), 420)
    alto = max(canvas.winfo_height(), 210)
    izquierda, derecha, arriba, abajo = 56, ancho - 16, 28, alto - 34
    ancho_trazo, alto_trazo = derecha - izquierda, abajo - arriba

    xs = []
    ys = []
    cantidad = max(120, min(500, int(ancho_trazo * 1.25)))
    for indice in range(cantidad + 1):
        x = _interpolar_x(a, b, indice / cantidad)
        try:
            y = funcion(x)
        except ValueError:
            xs.append(x)
            ys.append(None)
        else:
            xs.append(x)
            ys.append(y)

    valores = [y for y in ys if y is not None]
    if not valores:
        canvas.create_text(
            ancho / 2, alto / 2, text="No se pudo representar f(x) en este intervalo.",
            fill=TEXTO_SUAVE, width=ancho - 32,
        )
        return

    escala_y = max(max(abs(y) for y in valores), 1.0)
    minimo = min(min(y / escala_y for y in valores), 0.0)
    maximo = max(max(y / escala_y for y in valores), 0.0)
    if minimo == maximo:
        minimo, maximo = -1.0, 1.0
    else:
        margen = (maximo - minimo) * 0.08
        minimo -= margen
        maximo += margen

    def coord_y(y):
        return abajo - (y / escala_y - minimo) / (maximo - minimo) * alto_trazo

    def coord_x(x):
        return izquierda + _proporcion_x(x, a, b) * ancho_trazo

    expresion = resultado.expresion if resultado is not None else "f(x)"
    canvas.create_text(
        izquierda, 10, anchor="w", text=f"f(x) = {expresion}",
        fill=TEXTO, font=("Helvetica", 9, "bold"),
    )
    for indice in range(5):
        proporcion = indice / 4
        x = _interpolar_x(a, b, proporcion)
        y_valor = maximo + (minimo - maximo) * proporcion
        px = izquierda + proporcion * ancho_trazo
        py = arriba + proporcion * alto_trazo
        valor_y = y_valor * escala_y
        etiqueta_y = f"{valor_y:.3g}" if abs(valor_y) != float("inf") else f"{y_valor:.2g}×{escala_y:.1e}"
        canvas.create_line(px, arriba, px, abajo, fill="#E8EDF4")
        canvas.create_line(izquierda, py, derecha, py, fill="#E8EDF4")
        canvas.create_text(px, abajo + 14, text=f"{x:.3g}", fill=TEXTO_SUAVE, font=("Helvetica", 8))
        canvas.create_text(izquierda - 7, py, text=etiqueta_y,
                           anchor="e", fill=TEXTO_SUAVE, font=("Helvetica", 8))

    cero_y = coord_y(0.0)
    canvas.create_line(izquierda, cero_y, derecha, cero_y, fill=AZUL_BORDE, width=2)
    canvas.create_line(izquierda, arriba, izquierda, abajo, fill=AZUL_BORDE)
    anterior = None
    for x, y in zip(xs, ys):
        if y is None:
            anterior = None
            continue
        punto = (coord_x(x), coord_y(y))
        if anterior is not None:
            canvas.create_line(*anterior, *punto, fill=AZUL, width=2)
        anterior = punto

    if resultado is not None:
        x_raiz = coord_x(resultado.raiz)
        y_raiz = coord_y(resultado.valor_funcion)
        canvas.create_line(x_raiz, arriba, x_raiz, abajo, fill=VERDE, dash=(4, 3))
        canvas.create_oval(x_raiz - 4, y_raiz - 4, x_raiz + 4, y_raiz + 4,
                           fill=VERDE, outline="white", width=1)
        canvas.create_oval(x_raiz - 4, cero_y - 4, x_raiz + 4, cero_y + 4,
                           fill="white", outline=VERDE, width=2)
        canvas.create_text(
            min(max(x_raiz, izquierda + 52), derecha - 52), arriba + 9,
            text=f"raíz ≈ {resultado.raiz:.6g}", fill=VERDE,
            font=("Helvetica", 8, "bold"),
        )

    canvas.create_text(
        izquierda, alto - 7, anchor="w",
        text="Curva: f(x)    Línea: f(x) = 0    Círculo: raíz aproximada",
        fill=TEXTO_SUAVE, font=("Helvetica", 8),
    )


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
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)
        ttk.Label(marco, text="Gráfica de la función e intersección con el eje x",
                  style="Negrita.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.canvas_grafica = tk.Canvas(
            marco, height=210, background="white", highlightthickness=0,
        )
        self.canvas_grafica.grid(row=1, column=0, sticky="ew")
        self.canvas_grafica.bind("<Configure>", self._redibujar_grafica)
        self.resultado_biseccion = None
        self.funcion_grafica = None
        area, self.txt_resultado = crear_area_resultado(marco, alto=12)
        self.txt_resultado.configure(width=42)
        area.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        self.mensaje_grafica = "Resuelve una ecuación para ver su gráfica y la raíz aproximada."
        self._mostrar_mensaje_grafica()

    def _mostrar_mensaje_grafica(self):
        self.canvas_grafica.delete("all")
        self.canvas_grafica.create_text(
            max(self.canvas_grafica.winfo_width(), 420) / 2,
            max(self.canvas_grafica.winfo_height(), 210) / 2,
            text=self.mensaje_grafica, fill=TEXTO_SUAVE, width=380,
        )

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
            self.resultado_biseccion = resultado
            self.funcion_grafica, _ = preparar_funcion(self.var_ecuacion.get())
            self._redibujar_grafica()
        except ValueError as error:
            mostrar_texto(self.txt_resultado, "No se pudo resolver la ecuación.\n\n" + str(error))
            self.resultado_biseccion = None
            self.funcion_grafica = None
            self.mensaje_grafica = "Corrige los datos y vuelve a resolver."
            self._mostrar_mensaje_grafica()
            mostrar_error(error)

    def _redibujar_grafica(self, _evento=None):
        if self.resultado_biseccion is None or self.funcion_grafica is None:
            self._mostrar_mensaje_grafica()
            return
        a, b = self.resultado_biseccion.intervalo_inicial
        dibujar_grafica_biseccion(
            self.canvas_grafica, self.funcion_grafica, a, b, self.resultado_biseccion,
        )

    def _cargar_ejemplo(self):
        self.var_ecuacion.set("x^3 - x - 2 = 0")
        self.var_a.set("1")
        self.var_b.set("2")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        self.resultado_biseccion = None
        self.funcion_grafica = None
        self.mensaje_grafica = "Resuelve una ecuación para ver su gráfica y la raíz aproximada."
        self._redibujar_grafica()
        mostrar_texto(self.txt_resultado, "Pulsa «Resolver por bisección» para calcular la raíz del ejemplo.")

    def _limpiar(self):
        for variable in (self.var_ecuacion, self.var_a, self.var_b):
            variable.set("")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        self.resultado_biseccion = None
        self.funcion_grafica = None
        self.mensaje_grafica = "Resuelve una ecuación para ver su gráfica y la raíz aproximada."
        self._redibujar_grafica()
        mostrar_texto(self.txt_resultado, "")
        self.entrada_ecuacion.focus_set()
