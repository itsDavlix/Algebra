"""Pestaña para resolver una ecuación de una variable por bisección."""

import tkinter as tk
from tkinter import ttk

from interfaz.ayudas import crear_area_resultado, mostrar_error, mostrar_texto
from interfaz.estilos import (
    AZUL, AZUL_BORDE, AZUL_CLARO, ROJO, TEXTO, TEXTO_SUAVE, VERDE,
)
from nucleo.biseccion import (
    MAX_ITERACIONES, autoajustar_biseccion, preparar_funcion, resolver_biseccion,
)


def _interpolar_x(a, b, proporcion):
    """Interpola entre a y b sin desbordar cuando el intervalo es muy grande."""
    diferencia = b - a
    if diferencia == float("inf"):
        return a * (1 - proporcion) + b * proporcion
    return a + diferencia * proporcion


def _proporcion_x(x, a, b):
    """Convierte una coordenada x en su posición relativa dentro del intervalo."""
    diferencia = b - a
    if diferencia == float("inf"):
        return (x / 2 - a / 2) / (b / 2 - a / 2)
    return (x - a) / diferencia


def dibujar_grafica_biseccion(canvas, funcion, a, b, resultado=None):
    """Traza f(x), el cambio de signo inicial y el intervalo final de bisección."""
    canvas.delete("all")
    oscuro = str(canvas.cget("background")) == "#111C2E"
    color_texto = "#E5E7EB" if oscuro else TEXTO
    color_suave = "#A8B3C5" if oscuro else TEXTO_SUAVE
    color_verde = "#4ADE80" if oscuro else VERDE
    color_rojo = "#F87171" if oscuro else ROJO
    color_azul = "#C7B5FF" if oscuro else "#6946AD"
    color_eje = "#9A86C7" if oscuro else "#8876A8"
    color_rejilla = "#44516A" if oscuro else "#E2D9EF"
    color_intervalo = "#143B2B" if oscuro else "#ECFDF3"
    color_superficie = "#111C2E" if oscuro else "white"
    ancho = max(canvas.winfo_width(), 420)
    alto = max(canvas.winfo_height(), 210)
    # Define el área de trazado y deja márgenes para las etiquetas de los ejes.
    izquierda, derecha, arriba, abajo = 56, ancho - 16, 40, alto - 54
    ancho_trazo, alto_trazo = derecha - izquierda, abajo - arriba

    # Muestrea el intervalo; los puntos fuera del dominio separan los trazos.
    xs = []
    ys = []
    puntos_fuera_dominio = 0
    cantidad = max(120, min(500, int(ancho_trazo * 1.25)))
    for indice in range(cantidad + 1):
        x = _interpolar_x(a, b, indice / cantidad)
        try:
            y = funcion(x)
        except ValueError:
            xs.append(x)
            ys.append(None)
            puntos_fuera_dominio += 1
        else:
            xs.append(x)
            ys.append(y)

    valores = [y for y in ys if y is not None]
    if not valores:
        canvas.create_text(
            ancho / 2, alto / 2, text="No se pudo representar f(x) en este intervalo.",
        fill=color_suave, width=ancho - 32,
        )
        return

    # Escala los valores para dibujar también funciones con magnitudes grandes.
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
        """Transforma valores de la función en coordenadas visibles del lienzo."""
        proporcion_y = (y / escala_y - minimo) / (maximo - minimo)
        return abajo - min(max(proporcion_y, 0.0), 1.0) * alto_trazo

    def coord_x(x):
        """Transforma valores x usando la escala del intervalo original."""
        return izquierda + _proporcion_x(x, a, b) * ancho_trazo

    expresion = resultado.expresion if resultado is not None else "f(x)"
    canvas.create_text(
        izquierda, 10, anchor="w", text=f"f(x) = {expresion}",
        fill=color_texto, font=("Helvetica", 10, "bold"),
    )
    valores_extremos = None
    intervalo_final = None
    if resultado is not None:
        # Recupera signos e intervalo directamente del cálculo, no de la curva aproximada.
        if resultado.iteraciones:
            primer_paso = resultado.iteraciones[0]
            valores_extremos = primer_paso.fa, primer_paso.fb
            ultimo_paso = resultado.iteraciones[-1]
            intervalo_final = (
                (ultimo_paso.c, ultimo_paso.c)
                if ultimo_paso.fc == 0 else (ultimo_paso.a, ultimo_paso.b)
            )
        else:
            intervalo_final = (resultado.raiz, resultado.raiz)
        if valores_extremos is not None:
            signo_a = "−" if valores_extremos[0] < 0 else "+"
            signo_b = "−" if valores_extremos[1] < 0 else "+"
            estado_extremos = (
                f"Extremos: f(a) {signo_a}   f(b) {signo_b}   "
                "cambio de signo comprobado"
            )
        else:
            extremo = "a" if resultado.raiz == a else "b"
            estado_extremos = f"Raíz exacta en el extremo {extremo}"
        canvas.create_text(
            derecha, 26, anchor="e", text=estado_extremos,
            fill=color_verde, font=("Helvetica", 8, "bold"),
        )

    # Coloca una cuadrícula y etiquetas uniformes para orientar la lectura.
    for indice in range(5):
        proporcion = indice / 4
        x = _interpolar_x(a, b, proporcion)
        y_valor = maximo + (minimo - maximo) * proporcion
        px = izquierda + proporcion * ancho_trazo
        py = arriba + proporcion * alto_trazo
        valor_y = y_valor * escala_y
        etiqueta_y = f"{valor_y:.3g}" if abs(valor_y) != float("inf") else f"{y_valor:.2g}×{escala_y:.1e}"
        canvas.create_line(px, arriba, px, abajo, fill=color_rejilla, width=1)
        canvas.create_line(izquierda, py, derecha, py, fill=color_rejilla, width=1)
        canvas.create_text(px, abajo + 14, text=f"{x:.3g}", fill=color_suave, font=("Helvetica", 9))
        canvas.create_text(izquierda - 7, py, text=etiqueta_y,
                           anchor="e", fill=color_suave, font=("Helvetica", 9))

    # Resalta el último intervalo que todavía acota la raíz.
    if intervalo_final is not None and intervalo_final[0] < intervalo_final[1]:
        x_a, x_b = map(lambda x: coord_x(x), intervalo_final)
        canvas.create_rectangle(
            x_a, arriba, x_b, abajo, fill=color_intervalo, stipple="gray25",
            outline="",
        )
        for x in (x_a, x_b):
            canvas.create_line(x, arriba, x, abajo, fill=color_verde, dash=(2, 3), width=2)

    # Dibuja los ejes, la curva y la aproximación devuelta por bisección.
    cero_y = coord_y(0.0)
    canvas.create_line(izquierda, cero_y, derecha, cero_y, fill=color_eje, width=2)
    canvas.create_line(izquierda, arriba, izquierda, abajo, fill=color_eje, width=2)
    anterior = None
    for x, y in zip(xs, ys):
        if y is None:
            anterior = None
            continue
        punto = (coord_x(x), coord_y(y))
        if anterior is not None:
            canvas.create_line(*anterior, *punto, fill=color_azul, width=3)
        anterior = punto

    if resultado is not None:
        x_raiz = coord_x(resultado.raiz)
        y_raiz = coord_y(resultado.valor_funcion)
        canvas.create_line(x_raiz, arriba, x_raiz, abajo, fill=color_verde, dash=(4, 3))
        canvas.create_oval(x_raiz - 5, y_raiz - 5, x_raiz + 5, y_raiz + 5,
                           fill=color_verde, outline=color_superficie, width=1)
        canvas.create_oval(x_raiz - 4, cero_y - 4, x_raiz + 4, cero_y + 4,
                           fill=color_superficie, outline=color_verde, width=2)
        if valores_extremos is not None:
            for x, y, nombre in ((a, valores_extremos[0], "a"), (b, valores_extremos[1], "b")):
                px, py = coord_x(x), coord_y(y)
                color = color_azul if y < 0 else color_rojo
                canvas.create_oval(
                    px - 3, py - 3, px + 3, py + 3, fill=color, outline=color_superficie,
                )
                canvas.create_text(
                    px, py - 10, text=nombre, fill=color,
                    font=("Helvetica", 9, "bold"),
                )
        canvas.create_text(
            min(max(x_raiz, izquierda + 52), derecha - 52), arriba + 9,
            text=f"raíz ≈ {resultado.raiz:.6g}", fill=color_verde,
            font=("Helvetica", 8, "bold"),
        )

    canvas.create_text(
        izquierda, alto - 27, anchor="w",
        text=(
            f"Dominio: {puntos_fuera_dominio} muestras no evaluables; revisa continuidad en [a,b]."
            if puntos_fuera_dominio else
            "Requisito: f continua en [a,b]. La gráfica no puede certificar continuidad."
        ),
        fill=color_suave, font=("Helvetica", 9),
    )
    canvas.create_text(
        izquierda, alto - 10, anchor="w",
        text="Curva: f(x)   Línea: f(x)=0   Puntos: extremos   Banda verde: intervalo final",
        fill=color_suave, font=("Helvetica", 9),
    )


def _numero_tabla(valor):
    """Acorta la representación numérica sin ocultar cifras significativas útiles."""
    return f"{valor:.7g}"


def _resumen_resultado(resultado):
    """Resume convergencia, raíz y tolerancia antes del detalle por iteración."""
    estado = "convergencia alcanzada" if resultado.convergio else "aproximación sin convergencia"
    return (
        f"{estado}: x ≈ {_numero_tabla(resultado.raiz)}    "
        f"f(x) = {_numero_tabla(resultado.valor_funcion)}\n"
        f"Cota de error: {_numero_tabla(resultado.error)} "
        f"(tolerancia {_numero_tabla(resultado.tolerancia)})    "
        f"Iteraciones: {len(resultado.iteraciones)}\n"
        f"Motivo: {resultado.motivo}\n"
        "La cota indica cuánto puede diferir x de la raíz si f es continua en el intervalo."
    )


class PestanaBiseccion(ttk.Frame):
    """Recibe la ecuación y muestra la aproximación con todo el procedimiento."""

    def __init__(self, padre):
        """Crea las variables de estado y conecta los paneles de la pestaña."""
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=2, minsize=330)
        self.columnconfigure(1, weight=3, minsize=350)
        self.rowconfigure(0, weight=1)
        self.iteraciones_expandidas = False
        self.var_ecuacion = tk.StringVar(self)
        self.var_a = tk.StringVar(self)
        self.var_b = tk.StringVar(self)
        self.var_tolerancia = tk.StringVar(self)
        self.var_iteraciones = tk.StringVar(self)
        self._construir_entrada()
        self._construir_resultado()
        self._cargar_ejemplo()
    def _construir_entrada(self):
        """Crea los campos y las ayudas para ingresar la función y sus parámetros."""
        marco = ttk.LabelFrame(self, text="Resolver f(x) = 0", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self.marco_entrada = marco

        # La expresión acepta una igualdad o una función escrita igualada a cero.
        ttk.Label(marco, text="Ecuación o expresión f(x):").pack(anchor="w")
        self.entrada_ecuacion = ttk.Entry(marco, textvariable=self.var_ecuacion, width=34)
        self.entrada_ecuacion.pack(fill="x", pady=(3, 5))
        self.entrada_ecuacion.bind("<Return>", self._accion_resolver)
        ttk.Label(
            marco, text="Ejemplos: x^3 - x - 2   o   x^2 = 2\nSin igualdad, se interpreta f(x) = 0.",
            style="Ayuda.TLabel", justify="left", wraplength=320,
        ).pack(anchor="w", pady=(0, 12))

        ttk.Label(marco, text="Valores calculados automáticamente al resolver:",
                  style="Ayuda.TLabel").pack(anchor="w")
        # Organiza los parámetros en dos columnas para mantener el panel compacto.
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
            entrada = ttk.Entry(datos, textvariable=variable, width=13, state="readonly")
            entrada.grid(row=fila + 1, column=columna, sticky="ew", padx=margen, pady=(3, 10))

        # Resolver propone los parámetros y calcula la raíz en una sola acción.
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
        """Distribuye el resumen, la gráfica y la tabla dentro del panel de resultados."""
        # Reserva el espacio superior para la gráfica y el inferior para el procedimiento.
        marco = ttk.LabelFrame(self, text="Resultado y procedimiento paso a paso",
                               style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        self.marco_resultado = marco
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)
        self.etiqueta_grafica = ttk.Label(
            marco, text="Gráfica de la función e intersección con el eje x",
            style="Negrita.TLabel",
        )
        self.etiqueta_grafica.grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.canvas_grafica = tk.Canvas(
            marco, height=210, background="white", highlightthickness=0,
        )
        self.canvas_grafica.grid(row=1, column=0, sticky="ew")
        self.canvas_grafica.bind("<Configure>", self._redibujar_grafica)
        self.resultado_biseccion = None
        self.funcion_grafica = None
        area, self.txt_resultado = crear_area_resultado(marco, alto=4)
        self.txt_resultado.configure(width=42)
        area.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        self.area_resumen = area

        marco.rowconfigure(3, weight=1)
        procedimiento = ttk.Frame(marco)
        procedimiento.grid(row=3, column=0, sticky="nsew", pady=(5, 0))
        self.procedimiento = procedimiento
        procedimiento.columnconfigure(0, weight=1)
        procedimiento.rowconfigure(0, weight=0)

        barra_titulo = ttk.Frame(procedimiento)
        barra_titulo.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        barra_titulo.columnconfigure(0, weight=1)
        ttk.Label(
            barra_titulo, text="Iteraciones — expande una fila para ver los cálculos",
            style="Negrita.TLabel",
        ).grid(row=0, column=0, sticky="w")
        self.boton_expandir = ttk.Button(
            barra_titulo, text="Ampliar tabla", command=self._alternar_vista_iteraciones,
        )
        self.boton_expandir.grid(row=0, column=1, sticky="e", padx=(8, 0))

        # Define tipografía, contraste, estados de fila y barras solo para esta tabla.
        estilo_tabla = ttk.Style(self)
        estilo_tabla.configure(
            "Biseccion.Treeview",
            background="#FFFFFF", fieldbackground="#FFFFFF", foreground=TEXTO,
            font=("TkDefaultFont", 10), rowheight=34, borderwidth=0,
            relief="flat",
        )
        estilo_tabla.map(
            "Biseccion.Treeview",
            background=[("selected", "#E8E1F5")],
            foreground=[("selected", TEXTO)],
        )
        estilo_tabla.configure(
            "Biseccion.Treeview.Heading",
            background="#F5F2FA", foreground=TEXTO_SUAVE,
            font=("TkDefaultFont", 10, "bold"), padding=(9, 10), relief="flat",
        )
        estilo_tabla.map(
            "Biseccion.Treeview.Heading",
            background=[("active", AZUL_CLARO)],
        )
        estilo_tabla.configure(
            "Biseccion.Vertical.TScrollbar", width=9, arrowsize=0,
            background="#D8D1E7", troughcolor="#F8F7FB", bordercolor="#F8F7FB",
            relief="flat",
        )
        estilo_tabla.map(
            "Biseccion.Vertical.TScrollbar",
            background=[("active", "#8A77BC")],
        )
        estilo_tabla.configure(
            "Biseccion.Horizontal.TScrollbar", width=9, arrowsize=0,
            background="#D8D1E7", troughcolor="#F8F7FB", bordercolor="#F8F7FB",
            relief="flat",
        )
        estilo_tabla.map(
            "Biseccion.Horizontal.TScrollbar",
            background=[("active", "#8A77BC")],
        )

        tabla_marco = ttk.Frame(procedimiento)
        tabla_marco.grid(row=1, column=0, sticky="nsew")
        procedimiento.rowconfigure(1, weight=1)
        tabla_marco.columnconfigure(0, weight=1)
        tabla_marco.rowconfigure(0, weight=1)
        columnas = ("a", "b", "c", "fc", "error")
        self.tabla_iteraciones = ttk.Treeview(
            tabla_marco, columns=columnas, show="tree headings", height=8,
            selectmode="browse", style="Biseccion.Treeview",
        )
        self.tabla_iteraciones.heading("#0", text="Iteración / detalle")
        self.tabla_iteraciones.column("#0", width=165, minwidth=140, stretch=True)
        encabezados = {
            "a": "a", "b": "b", "c": "Punto medio",
            "fc": "f(c)", "error": "Error (x)",
        }
        for columna in columnas:
            self.tabla_iteraciones.heading(columna, text=encabezados[columna])
            self.tabla_iteraciones.column(
                columna, width=104, minwidth=86, anchor="e", stretch=True,
            )
        self.tabla_iteraciones.bind("<Configure>", self._ajustar_ancho_tabla)
        self.tabla_iteraciones.tag_configure("fila_par", background="#FFFFFF")
        self.tabla_iteraciones.tag_configure("fila_impar", background="#F7F9FC")
        self.tabla_iteraciones.tag_configure(
            "detalle", background="#F8FAFC", foreground=TEXTO_SUAVE,
        )
        self.tabla_iteraciones.tag_configure(
            "decision", background="#F0ECF8", foreground=AZUL, font=("TkDefaultFont", 9, "bold"),
        )
        self.tabla_iteraciones.tag_configure(
            "parada_ok", background="#ECFDF3", foreground=VERDE,
            font=("TkDefaultFont", 9, "bold"),
        )
        self.tabla_iteraciones.tag_configure(
            "parada_no", background="#FEF2F2", foreground=ROJO,
            font=("TkDefaultFont", 9, "bold"),
        )
        barra_y = ttk.Scrollbar(
            tabla_marco, orient="vertical", style="Biseccion.Vertical.TScrollbar",
            command=self.tabla_iteraciones.yview,
        )
        barra_x = ttk.Scrollbar(
            tabla_marco, orient="horizontal", style="Biseccion.Horizontal.TScrollbar",
            command=self.tabla_iteraciones.xview,
        )
        self.barra_horizontal_tabla = barra_x
        self.tabla_iteraciones.configure(
            yscrollcommand=barra_y.set, xscrollcommand=barra_x.set,
        )
        self.barra_vertical_tabla = barra_y
        self.tabla_iteraciones.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        tabla_marco.rowconfigure(1, weight=0)
        self.tabla_iteraciones.bind("<MouseWheel>", self._desplazar_tabla_rueda)
        self.tabla_iteraciones.bind("<Button-4>", self._desplazar_tabla_rueda)
        self.tabla_iteraciones.bind("<Button-5>", self._desplazar_tabla_rueda)

        self.mensaje_grafica = "Resuelve una ecuación para ver su gráfica y la raíz aproximada."
        self._mostrar_mensaje_grafica()

    def _actualizar_tabla_iteraciones(self, resultado):
        """Construye una fila por iteración y agrupa debajo el cálculo que la explica."""
        # Reemplaza el contenido para que siempre corresponda al último cálculo.
        tabla = self.tabla_iteraciones
        elementos = tabla.get_children()
        if elementos:
            tabla.delete(*elementos)

        for paso in resultado.iteraciones:
            iid = f"iteracion-{paso.numero}"
            estilo_fila = "fila_par" if paso.numero % 2 else "fila_impar"
            tabla.insert(
                "", "end", iid=iid, text=f"Iteración {paso.numero}",
                values=(
                    _numero_tabla(paso.a), _numero_tabla(paso.b), _numero_tabla(paso.c),
                    _numero_tabla(paso.fc), _numero_tabla(paso.error),
                ),
                open=False, tags=(estilo_fila,),
            )
            # Los hijos separan las operaciones y hacen visible la decisión numérica.
            tabla.insert(
                iid, "end", text="Punto medio: c = (a+b)/2",
                values=("", "", _numero_tabla(paso.c), "", ""),
                tags=("detalle",),
            )
            tabla.insert(
                iid, "end",
                text=f"Evaluación: f(a) = {_numero_tabla(paso.fa)}",
                values=("", "", "", "", ""),
                tags=("detalle",),
            )
            tabla.insert(
                iid, "end", text=f"Evaluación: f(b) = {_numero_tabla(paso.fb)}",
                values=("", "", "", "", ""),
                tags=("detalle",),
            )
            tabla.insert(
                iid, "end", text=f"Evaluación: f(c) = {_numero_tabla(paso.fc)}",
                values=("", "", "", "", ""),
                tags=("detalle",),
            )
            tabla.insert(
                iid, "end", text="Cota: max(c-a, b-c)",
                values=("", "", "", "", _numero_tabla(paso.error)),
                tags=("detalle",),
            )
            if paso.numero == len(resultado.iteraciones):
                decision = "Parada: " + resultado.motivo
                intervalo = ("", "")
                estilo_decision = "parada_ok" if resultado.convergio else "parada_no"
            elif (paso.fa < 0) != (paso.fc < 0):
                decision = "Decisión: conservar [a, c]"
                intervalo = (_numero_tabla(paso.a), _numero_tabla(paso.c))
                estilo_decision = "decision"
            else:
                decision = "Decisión: conservar [c, b]"
                intervalo = (_numero_tabla(paso.c), _numero_tabla(paso.b))
                estilo_decision = "decision"
            tabla.insert(
                iid, "end", text=decision,
                values=(intervalo[0], intervalo[1], "", "", ""),
                tags=(estilo_decision,),
            )

    def _ajustar_ancho_tabla(self, evento=None):
        """Reparte el ancho disponible y muestra desplazamiento horizontal si hace falta."""
        # Distribuye el ancho real para que los decimales no queden recortados.
        ancho = evento.width if evento is not None else self.tabla_iteraciones.winfo_width()
        disponible = max(ancho - 22, 0)
        ancho_detalle = max(150, min(250, int(disponible * 0.26)))
        ancho_numero = max(90, (disponible - ancho_detalle) // 5)
        self.tabla_iteraciones.column("#0", width=ancho_detalle)
        for columna in ("a", "b", "c", "fc", "error"):
            self.tabla_iteraciones.column(columna, width=ancho_numero)
        requiere_desplazamiento = disponible < ancho_detalle + 5 * 90
        if requiere_desplazamiento and not self.barra_horizontal_tabla.winfo_ismapped():
            self.barra_horizontal_tabla.grid(row=1, column=0, sticky="ew")
            self.tabla_iteraciones.master.rowconfigure(1, weight=0)
        elif not requiere_desplazamiento and self.barra_horizontal_tabla.winfo_ismapped():
            self.barra_horizontal_tabla.grid_remove()

    def _desplazar_tabla_rueda(self, evento):
        """Unifica la rueda de macOS, Windows y Linux para recorrer la tabla."""
        if getattr(evento, "num", None) == 4:
            pasos = -1
        elif getattr(evento, "num", None) == 5:
            pasos = 1
        else:
            delta = evento.delta
            pasos = int(-delta / 120) if abs(delta) >= 120 else -int(delta)
        self.tabla_iteraciones.yview_scroll(pasos, "units")
        return "break"

    def _alternar_vista_iteraciones(self):
        """Oculta temporalmente los otros paneles para ampliar la tabla."""
        # Oculta temporalmente entradas y gráfica para dedicar el ancho a la tabla.
        if not self.iteraciones_expandidas:
            self.marco_entrada.grid_remove()
            self.etiqueta_grafica.grid_remove()
            self.canvas_grafica.grid_remove()
            self.area_resumen.grid_remove()
            self.marco_resultado.grid_configure(
                row=0, column=0, columnspan=2, sticky="nsew", padx=0,
            )
            self.marco_resultado.rowconfigure(0, weight=1)
            self.marco_resultado.rowconfigure(1, weight=0)
            self.marco_resultado.rowconfigure(2, weight=0)
            self.marco_resultado.rowconfigure(3, weight=0)
            self.procedimiento.grid_configure(row=0, sticky="nsew", pady=0)
            self.boton_expandir.configure(text="Volver al resultado")
            self.iteraciones_expandidas = True
        else:
            self.marco_entrada.grid()
            self.marco_resultado.grid_configure(
                row=0, column=1, columnspan=1, sticky="nsew", padx=(7, 0),
            )
            self.marco_resultado.rowconfigure(0, weight=0)
            self.marco_resultado.rowconfigure(1, weight=1)
            self.marco_resultado.rowconfigure(2, weight=0)
            self.marco_resultado.rowconfigure(3, weight=1)
            self.etiqueta_grafica.grid()
            self.canvas_grafica.grid()
            self.area_resumen.grid()
            self.procedimiento.grid_configure(row=3, sticky="nsew", pady=(5, 0))
            self.boton_expandir.configure(text="Ver tabla completa")
            self.iteraciones_expandidas = False
            self._redibujar_grafica()

    def _actualizar_tabla_iteraciones_vacia(self):
        """Retira resultados anteriores cuando se limpia o falla una entrada."""
        elementos = self.tabla_iteraciones.get_children()
        if elementos:
            self.tabla_iteraciones.delete(*elementos)

    def _mostrar_mensaje_grafica(self):
        """Muestra una indicación centrada cuando aún no hay una gráfica disponible."""
        self.canvas_grafica.delete("all")
        oscuro = str(self.canvas_grafica.cget("background")) == "#111C2E"
        self.canvas_grafica.create_text(
            max(self.canvas_grafica.winfo_width(), 420) / 2,
            max(self.canvas_grafica.winfo_height(), 210) / 2,
            text=self.mensaje_grafica,
            fill="#A8B3C5" if oscuro else TEXTO_SUAVE,
            width=380,
        )

    def _accion_resolver(self, _evento=None):
        """Autoajusta los parámetros, resuelve y actualiza las tres vistas."""
        try:
            ajuste = autoajustar_biseccion(self.var_ecuacion.get())
            self._aplicar_autoajuste(ajuste)
            resultado = resolver_biseccion(
                self.var_ecuacion.get(), ajuste.a, ajuste.b,
                ajuste.tolerancia, ajuste.max_iteraciones,
            )
            # Sincroniza el resumen, la tabla desplegable y la gráfica con el resultado.
            mostrar_texto(self.txt_resultado, _resumen_resultado(resultado))
            self.resultado_biseccion = resultado
            self.funcion_grafica, _ = preparar_funcion(self.var_ecuacion.get())
            self._actualizar_tabla_iteraciones(resultado)
            self._redibujar_grafica()
        except ValueError as error:
            mostrar_texto(self.txt_resultado, "No se pudo resolver la ecuación.\n\n" + str(error))
            self._actualizar_tabla_iteraciones_vacia()
            self.resultado_biseccion = None
            self.funcion_grafica = None
            self.mensaje_grafica = "Corrige los datos y vuelve a resolver."
            self._mostrar_mensaje_grafica()
            mostrar_error(error)

    def _aplicar_autoajuste(self, ajuste):
        """Refleja en los campos los parámetros usados para resolver."""
        self.var_a.set(f"{ajuste.a:.12g}")
        self.var_b.set(f"{ajuste.b:.12g}")
        self.var_tolerancia.set(f"{ajuste.tolerancia:.12g}")
        self.var_iteraciones.set(str(ajuste.max_iteraciones))

    def _redibujar_grafica(self, _evento=None):
        """Refresca la gráfica al terminar el cálculo o cambiar el tamaño del lienzo."""
        if self.resultado_biseccion is None or self.funcion_grafica is None:
            self._mostrar_mensaje_grafica()
            return
        a, b = self.resultado_biseccion.intervalo_inicial
        dibujar_grafica_biseccion(
            self.canvas_grafica, self.funcion_grafica, a, b, self.resultado_biseccion,
        )

    def _cargar_ejemplo(self):
        """Rellena un caso conocido en los campos de entrada."""
        self.var_ecuacion.set("x^3 - x - 2 = 0")
        self.var_a.set("1")
        self.var_b.set("2")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        self.resultado_biseccion = None
        self.funcion_grafica = None
        self._actualizar_tabla_iteraciones_vacia()
        self.mensaje_grafica = "Resuelve una ecuación para ver su gráfica y la raíz aproximada."
        self._redibujar_grafica()
        mostrar_texto(self.txt_resultado, "Pulsa «Resolver por bisección» para calcular la raíz del ejemplo.")

    def _limpiar(self):
        """Restablece campos, confirmación y resultados para empezar otro cálculo."""
        for variable in (self.var_ecuacion, self.var_a, self.var_b):
            variable.set("")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        self.resultado_biseccion = None
        self.funcion_grafica = None
        self._actualizar_tabla_iteraciones_vacia()
        self.mensaje_grafica = "Resuelve una ecuación para ver su gráfica y la raíz aproximada."
        self._redibujar_grafica()
        mostrar_texto(self.txt_resultado, "")
        self.entrada_ecuacion.focus_set()
