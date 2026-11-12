"""Gráfica de los métodos abiertos y coordenadas que sustentan el dibujo."""

import math
import sys
import tkinter as tk
from tkinter import ttk

from interfaz.estilos import actualizar_widgets


def limites_grafica(valores):
    """Añade margen sin desbordar ni producir un intervalo de ancho cero."""
    escala = max((abs(x) for x in valores), default=0) or 1.0
    inferior, superior = min(valores) / escala, max(valores) / escala
    margen = max((superior - inferior) * 0.15, 1e-6)
    limite = sys.float_info.max
    a, b = (max(-limite, (inferior - margen) * escala),
            min(limite, (superior + margen) * escala))
    if a == b:
        a, b = math.nextafter(a, -math.inf), math.nextafter(b, math.inf)
    return a, b


def intervalo_zoom(a, b, centro, nivel):
    """Calcula una vista ampliada o reducida alrededor de un punto."""
    if nivel == 0:
        return a, b
    factor = 1.5 ** (-nivel)
    izquierda = centro + (a - centro) * factor
    derecha = centro + (b - centro) * factor
    if not (math.isfinite(izquierda) and math.isfinite(derecha)
            and izquierda < derecha):
        return None
    return izquierda, derecha


def muestrear_curva(funcion, a, b, cantidad=240):
    """Obtiene las mismas muestras que se muestran en la tabla y en el lienzo."""
    muestras = []
    for i in range(cantidad + 1):
        t = i / cantidad
        x = a * (1 - t) + b * t
        try:
            y = funcion(x)
            if not math.isfinite(y):
                y = None
        except ValueError:
            y = None
        muestras.append((x, y))
    return muestras


def detectar_raices(muestras):
    """Detecta cortes con el eje X a partir de muestras consecutivas."""
    raices = []
    anterior = None
    for x, y in muestras:
        if y is None or not math.isfinite(y):
            anterior = None
            continue
        if y == 0:
            raices.append(x)
        elif anterior is not None:
            x_anterior, y_anterior = anterior
            if ((y_anterior < 0 < y) or (y < 0 < y_anterior)):
                proporcion = abs(y_anterior) / (abs(y_anterior) + abs(y))
                raices.append(x_anterior + (x - x_anterior) * proporcion)
        anterior = (x, y)

    # Evita repetir una misma raíz cuando varias muestras caen muy cerca.
    unicas = []
    for raiz in raices:
        if not unicas or not math.isclose(raiz, unicas[-1], rel_tol=1e-8, abs_tol=1e-12):
            unicas.append(raiz)
    return unicas


def puntos_del_metodo(funcion, resultado, iniciales):
    """Conserva las semillas y las evaluaciones reales de cada iteración."""
    puntos = []
    for i, x in enumerate(iniciales):
        try:
            y = funcion(x)
        except ValueError:
            y = None
        puntos.append((f"Inicial x{i}", x, y))
    puntos.extend((f"Iteración {p.numero}", p.siguiente, p.valor_siguiente)
                  for p in resultado.iteraciones)
    return puntos


def dibujar_metodo(canvas, resultado, puntos, muestras, paso=None):
    """Dibuja datos evaluados, ejes y la recta del paso; no recalcula el método."""
    canvas.delete("all")
    oscuro = str(canvas.cget("background")) == "#111C2E"
    texto = "#E5E7EB" if oscuro else "#1E293B"
    suave = "#A8B3C5" if oscuro else "#64748B"
    curva = "#C7B5FF" if oscuro else "#6946AD"
    recta = "#FBBF24" if oscuro else "#B45309"
    inicial = "#60A5FA" if oscuro else "#2563EB"
    final = ("#4ADE80" if oscuro else "#15803D") if resultado.convergio else ("#F87171" if oscuro else "#B91C1C")
    rejilla = "#334155" if oscuro else "#E2E8F0"
    ancho, alto = max(canvas.winfo_width(), 400), max(canvas.winfo_height(), 250)
    izquierda, derecha, arriba, abajo = 82, ancho - 25, 34, alto - 55
    a, b = muestras[0][0], muestras[-1][0]
    raices = detectar_raices(muestras)
    escala_x = max(abs(a), abs(b)) or 1.0
    na, nb = a / escala_x, b / escala_x
    ys = [y for _, y in muestras if y is not None]
    ys.extend(y for _, x, y in puntos if y is not None and a <= x <= b)
    ys.append(0.0)
    escala_y = max(map(abs, ys)) or 1.0
    bajo, alto_y = min(ys) / escala_y, max(ys) / escala_y
    margen = max((alto_y - bajo) * .08, .05)
    bajo, alto_y = bajo - margen, alto_y + margen

    def cx(x):
        return izquierda + (x / escala_x - na) / (nb - na) * (derecha - izquierda)

    def cy(y):
        return abajo - (y / escala_y - bajo) / (alto_y - bajo) * (abajo - arriba)

    def etiqueta_y(y):
        valor = y * escala_y
        return f"{valor:.4g}" if math.isfinite(valor) else f"{y:.3g}×{escala_y:.3g}"

    for i in range(5):
        t = i / 4
        x = a * (1-t) + b*t
        y = bajo * (1-t) + alto_y*t
        px, py = cx(x), abajo - t * (abajo-arriba)
        canvas.create_line(px, arriba, px, abajo, fill=rejilla)
        canvas.create_line(izquierda, py, derecha, py, fill=rejilla)
        canvas.create_text(px, abajo+15, text=f"{x:.6g}", fill=suave, font=("TkDefaultFont", 9))
        canvas.create_text(izquierda-7, py, text=etiqueta_y(y), anchor="e", fill=suave, font=("TkDefaultFont", 9))
    canvas.create_line(izquierda, cy(0), derecha, cy(0), fill=suave, width=2)
    if a <= 0 <= b:
        canvas.create_line(cx(0), arriba, cx(0), abajo, fill=suave, width=2)
    canvas.create_text(derecha, abajo+35, text="x", fill=texto)
    canvas.create_text(izquierda, 15, text="f(x)", fill=texto)
    canvas.create_text(izquierda + 4, arriba + 10, anchor="w",
                       text=f"Raíces detectadas en la vista: {len(raices)}",
                       fill=final, font=("TkDefaultFont", 9, "bold"))

    anterior = None
    for x, y in muestras:
        if y is None:
            anterior = None
            continue
        actual = (cx(x), cy(y))
        # No une un salto vertical grande a través del eje como si fuera una raíz.
        if anterior is not None and abs(actual[1]-anterior[1]) < .65*(abajo-arriba):
            canvas.create_line(*anterior, *actual, fill=curva, width=2, tags="curva")
        anterior = actual

    for raiz in raices:
        px, py = cx(raiz), cy(0.0)
        canvas.create_oval(px-5, py-5, px+5, py+5, fill=final, outline=texto,
                           width=1, tags="raiz_detectada")
        canvas.create_text(px, min(abajo-12, py+18),
                           text=f"({raiz:.6g}, 0)", fill=final,
                           font=("TkDefaultFont", 8, "bold"),
                           tags="raiz_detectada")

    if paso is not None:
        # Segmento de la tangente/secante entre el punto actual y el corte con x.
        extremos = [(paso.actual, paso.valor_actual), (paso.siguiente, 0.0)]
        if resultado.metodo == "Secante":
            previo = next(((x, y) for _, x, y in puntos if x == paso.anterior and y is not None), None)
            if previo is not None:
                extremos.append(previo)
        extremos.sort()
        for (x1, y1), (x2, y2) in zip(extremos, extremos[1:]):
            if a <= x1 <= b and a <= x2 <= b:
                canvas.create_line(cx(x1), cy(y1), cx(x2), cy(y2), fill=recta,
                                   width=2, dash=(6, 3), tags="recta_metodo")
        if a <= paso.siguiente <= b:
            px, py = cx(paso.siguiente), cy(0)
            canvas.create_rectangle(px-4, py-4, px+4, py+4, outline=recta, width=2, tags="corte")
            canvas.create_line(px, py, px, cy(paso.valor_siguiente), fill=recta, dash=(2, 3))

    for nombre, x, y in puntos:
        if y is None or not a <= x <= b:
            continue
        px, py = cx(x), cy(y)
        color = inicial if nombre.startswith("Inicial") else curva
        canvas.create_oval(px-3, py-3, px+3, py+3, fill=color, outline=color, tags="punto_metodo")
    if paso is not None:
        for nombre, x, y in (("Actual", paso.actual, paso.valor_actual),
                             ("Nuevo", paso.siguiente, paso.valor_siguiente)):
            px, py = cx(x), cy(y)
            canvas.create_oval(px-5, py-5, px+5, py+5, outline=recta, width=2)
            canvas.create_text(min(max(px, izquierda+30), derecha-30), max(arriba+10, py-14),
                               text=nombre, fill=recta, font=("TkDefaultFont", 9, "bold"))
    if a <= resultado.raiz <= b:
        px, py = cx(resultado.raiz), cy(resultado.valor_funcion)
        canvas.create_line(px, arriba, px, abajo, fill=final, dash=(3, 4))
        canvas.create_oval(px-5, py-5, px+5, py+5, fill=final, outline=final, tags="resultado")
        estado = "Raíz aproximada" if resultado.convergio else "Sin convergencia"
        canvas.create_text(derecha, 14, anchor="e", fill=final,
                           text=f"{estado}: x ≈ {resultado.raiz:.10g}", font=("TkDefaultFont", 10, "bold"))


class GraficaMetodosAbiertos(tk.Toplevel):
    """Vista del último cálculo con selección de pasos y tablas de coordenadas."""

    def __init__(self, padre, funcion, resultado, iniciales):
        super().__init__(padre)
        self.title(f"Gráfica y puntos · {resultado.metodo}")
        ancho = min(1000, int(self.winfo_screenwidth() * .9))
        alto = min(800, int(self.winfo_screenheight() * .9))
        self.geometry(f"{ancho}x{alto}")
        self.minsize(760, 600)
        self.funcion = funcion
        self.resultado = resultado
        self.puntos = puntos_del_metodo(funcion, resultado, iniciales)
        self.muestras = []
        self._intervalo = None
        self.nivel_zoom = 0
        self.enfocar = tk.BooleanVar(self, value=False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(5, weight=1)
        ttk.Label(self, text=f"f(x) = {resultado.expresion}", style="Negrita.TLabel",
                  wraplength=700).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 3))
        estado = "Convergencia alcanzada" if resultado.convergio else "Aproximación sin convergencia"
        ttk.Label(self, text=f"{estado} · x ≈ {resultado.raiz:.16g} · f(x) = {resultado.valor_funcion:.6g}\n"
                  f"Tolerancia: {resultado.tolerancia:g} · Iteraciones: {len(resultado.iteraciones)}",
                  wraplength=700).grid(row=1, column=0, sticky="w", padx=16, pady=4)
        self.canvas = tk.Canvas(self, height=300, highlightthickness=0, background="white")
        self.canvas.grid(row=2, column=0, sticky="nsew", padx=12)
        self.canvas.bind("<Configure>", self._redibujar_grafica)
        controles = ttk.Frame(self, padding=(16, 4))
        controles.grid(row=3, column=0, sticky="ew")
        ttk.Label(controles, text="Paso:").pack(side="left")
        self.selector = ttk.Combobox(controles, state="readonly", width=17,
            values=[f"Iteración {p.numero}" for p in resultado.iteraciones] or ["Sin iteraciones"])
        self.selector.current(0)
        self.selector.pack(side="left", padx=6)
        self.selector.bind("<<ComboboxSelected>>", self._redibujar_grafica)
        ttk.Checkbutton(controles, text="Enfocar este paso", variable=self.enfocar,
                        command=self._redibujar_grafica).pack(side="left", padx=8)
        ttk.Button(controles, text="+ Acercar",
                   command=lambda: self._cambiar_zoom(1)).pack(side="left", padx=(12, 0))
        ttk.Button(controles, text="- Alejar",
                   command=lambda: self._cambiar_zoom(-1)).pack(side="left", padx=6)
        ttk.Button(controles, text="Restablecer vista",
                   command=self._restablecer_zoom).pack(side="left")
        ttk.Label(controles, text="Azul: iniciales · Morado: curva/pasos · Ámbar: recta",
                  style="Ayuda.TLabel", wraplength=260).pack(side="left", padx=6)
        self.explicacion = ttk.Label(self, wraplength=900, justify="left", style="Ayuda.TLabel")
        self.explicacion.grid(row=4, column=0, sticky="ew", padx=16, pady=6)
        tablas = ttk.Notebook(self)
        tablas.grid(row=5, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self.tabla_puntos = self._crear_tabla(tablas, "Puntos del método")
        self.tabla_muestras = self._crear_tabla(tablas, "Muestras de la curva")
        for nombre, x, y in self.puntos:
            self.tabla_puntos.insert("", "end", values=(nombre, repr(x), "Fuera del dominio" if y is None else repr(y)))
        actualizar_widgets(self, bool(getattr(padre.winfo_toplevel(), "modo_oscuro", False)))
        self.canvas.bind("<MouseWheel>", self._zoom_rueda)
        self.canvas.bind("<Button-4>", self._zoom_rueda)
        self.canvas.bind("<Button-5>", self._zoom_rueda)
        self._redibujar_grafica()

    @staticmethod
    def _crear_tabla(notebook, titulo):
        marco = ttk.Frame(notebook)
        notebook.add(marco, text=titulo)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        tabla = ttk.Treeview(marco, columns=("nombre", "x", "y"), show="headings", height=5)
        for columna, titulo_col in (("nombre", "Punto"), ("x", "x"), ("y", "f(x)")):
            tabla.heading(columna, text=titulo_col)
            tabla.column(columna, width=180, minwidth=100, anchor="w")
        tabla.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        tabla.configure(yscrollcommand=barra.set)
        return tabla

    def _redibujar_grafica(self, _evento=None):
        pasos = self.resultado.iteraciones
        paso = pasos[max(0, self.selector.current())] if pasos else None
        xs = [x for _, x, _ in self.puntos] + [self.resultado.raiz]
        if self.enfocar.get() and paso is not None:
            xs = [paso.actual, paso.siguiente]
            if paso.anterior is not None and self.resultado.metodo == "Secante":
                xs.append(paso.anterior)
        intervalo_base = limites_grafica(xs)
        centro = (paso.siguiente if self.enfocar.get() and paso is not None
                  else self.resultado.raiz)
        intervalo = intervalo_zoom(*intervalo_base, centro, self.nivel_zoom)
        if intervalo is None:
            intervalo = intervalo_base
        if intervalo != self._intervalo:
            self.muestras = muestrear_curva(self.funcion, *intervalo)
            self._intervalo = intervalo
            hijos = self.tabla_muestras.get_children()
            if hijos:
                self.tabla_muestras.delete(*hijos)
            for i, (x, y) in enumerate(self.muestras):
                self.tabla_muestras.insert("", "end", values=(f"Muestra {i}", repr(x),
                    "Fuera del dominio" if y is None else repr(y)))
        dibujar_metodo(self.canvas, self.resultado, self.puntos, self.muestras, paso)
        if paso is None:
            detalle = "No se construyó ninguna recta. " + self.resultado.motivo
        else:
            tipo = "tangente definida por la derivada ingresada" if self.resultado.metodo == "Newton-Raphson" else "secante entre los dos puntos anteriores"
            detalle = (f"Iteración {paso.numero}: la {tipo} corta el eje x en {paso.siguiente:.10g} "
                       f"(cuadrado ámbar). Evaluamos allí f(x) = {paso.valor_siguiente:.6g} para obtener el punto nuevo. "
                       f"Cambio |Δx| = {paso.error:.6g}.")
        fallos = sum(y is None for _, y in self.muestras)
        self.explicacion.configure(text=detalle + f"\nLa curva une {len(self.muestras)} muestras uniformes de la vista; "
            f"{fallos} no se pudieron evaluar. Las tablas muestran sus coordenadas. "
            "El muestreo no demuestra continuidad ni detecta todas las raíces.",
            wraplength=max(self.winfo_width()-40, 650))
        raices = detectar_raices(self.muestras)
        detalle_raices = (
            "Ninguna raíz detectada en la vista."
            if not raices else
            "Raíces detectadas en la vista: " + ", ".join(
                f"({raiz:.8g}, 0)" for raiz in raices
            ) + "."
        )
        self.explicacion.configure(
            text=self.explicacion.cget("text") + " " + detalle_raices,
        )

    def _cambiar_zoom(self, pasos):
        """Cambia el nivel de zoom y vuelve a muestrear la curva."""
        self.nivel_zoom = max(-12, min(12, self.nivel_zoom + pasos))
        self._redibujar_grafica()

    def _restablecer_zoom(self):
        self.nivel_zoom = 0
        self._redibujar_grafica()

    def _zoom_rueda(self, evento):
        numero = getattr(evento, "num", None)
        delta = getattr(evento, "delta", 0)
        if numero == 4 or delta > 0:
            self._cambiar_zoom(1)
        elif numero == 5 or delta < 0:
            self._cambiar_zoom(-1)
        return "break"
