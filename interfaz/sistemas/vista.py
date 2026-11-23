"""Vista de sistemas lineales A·X = B: Gauss-Jordan, Jacobi y Gauss-Seidel.

Flujo, como en la clase: ① escribir el sistema (se muestra su forma matricial)
→ análisis previo (det(A), dominancia diagonal, ρ(T)) → ② parámetros →
resolver → resultado verificado, tabla paginada y paso a paso.
"""

import tkinter as tk
from tkinter import ttk

from interfaz.campoMatematico import CampoValor
from interfaz.ayudas import AyudaEmergente
from interfaz.componentes import (
    MenuEjercicios, PanelProcedimiento, SelectorSegmentado, TablaPaginada, tarjeta,
)
from interfaz.dibujos import admite_plano_sistema, dibujo_sistema, encuadre_proporcional
from interfaz.estilos import PALETA, fuente
from interfaz.motorGrafica import PlanoCartesiano
from interfaz.sistemas import convergencia
from nucleo import procedimientos_sistemas as ps
from nucleo.determinantes import determinante
from nucleo.diagnostico import (
    FUNCIONA, NO_FUNCIONA, REORDENAR, anotar_dominancia, diagnosticar,
)
from nucleo.ejercicios import GUIA, ejercicios_de
from nucleo.iterativos import (
    dominancia_diagonal, matriz_iteracion, radio_espectral, reordenar_para_dominancia, resolver_iterativo,
)
from nucleo.sistemas_texto import ecuacion_texto, leer_sistema, leer_vector, nombre_bonito

METODOS = ("Gauss-Jordan", "Jacobi", "Gauss-Seidel")
ITERATIVOS = ("Jacobi", "Gauss-Seidel")
FORMULAS = {
    "Gauss-Jordan": "[A | B] → [I | X] mediante operaciones elementales de fila",
    **ps.FORMULAS_ITERATIVAS,
}
DESCRIPCIONES = {
    "Gauss-Jordan": "Método directo: elimina por columnas con pivoteo parcial hasta leer X; da la solución exacta "
                    "salvo redondeo.",
    "Jacobi": "Método iterativo: despeja cada incógnita y la actualiza solo con los valores de la iteración anterior.",
    "Gauss-Seidel": "Método iterativo: como Jacobi, pero usa de inmediato los valores recién calculados.",
}
COLORES_NIVEL = {"pendiente": "texto_suave", "ok": "exito", "aviso": "aviso", "error": "error"}
COLOR_VEREDICTO = {FUNCIONA: "exito", REORDENAR: "aviso", NO_FUNCIONA: "error"}
FILAS_VISTA_PREVIA = 8
ETIQUETA_NUMEROS = {"Decimales": "0.25", "Fracciones": "1/4"}
MODO_POR_ETIQUETA = {etiqueta: modo for modo, etiqueta in ETIQUETA_NUMEROS.items()}


class VistaSistemas(ttk.Frame):
    ALTO_MINIMO = 680

    def __init__(self, padre):
        super().__init__(padre, padding=(22, 18, 22, 14))
        self.metodo = "Gauss-Jordan"
        self.variables, self.A, self.b = (), None, None
        self.reordenado = ()
        self.resultado = None
        self.resultados = {}
        self.comparacion = None
        self.modo_grafica = "Componentes"
        self.modo_numeros = "Decimales"
        self._programado = None
        self._escribiendo = False
        self.ventanas = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=58, uniform="zonas")
        self.rowconfigure(2, weight=42, uniform="zonas")
        self._construir_encabezado()
        self._construir_cuerpo()
        self._construir_resultados()
        self._aplicar_metodo()
        self._analizar()

    # ================================================================ diseño
    def _construir_encabezado(self):
        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        encabezado.columnconfigure(1, weight=1)
        ttk.Label(encabezado, text="Sistemas lineales A·X = B", style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
        info = ttk.Frame(encabezado)
        info.grid(row=0, column=1, sticky="ew", padx=(16, 12))
        self.etiqueta_formula = ttk.Label(info, style="Formula.TLabel")
        self.etiqueta_formula.pack(anchor="w")
        self.etiqueta_descripcion = ttk.Label(info, style="Tenue.TLabel", justify="left")
        self.etiqueta_descripcion.pack(anchor="w", fill="x")
        info.bind("<Configure>", lambda e: self.etiqueta_descripcion.configure(wraplength=max(160, e.width - 4)))
        acciones = ttk.Frame(encabezado)
        acciones.grid(row=0, column=2, sticky="e")
        self.selector = SelectorSegmentado(acciones, METODOS, self.cambiar_metodo)
        self.selector.pack(side="left", padx=(0, 12))
        ttk.Button(acciones, text="Comparar J / GS", command=self.comparar).pack(side="left", padx=(0, 6))
        MenuEjercicios(acciones, ejercicios_de(METODOS), self.cargar_ejercicio).pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Limpiar", command=self.limpiar).pack(side="left")

    def _construir_cuerpo(self):
        cuerpo = ttk.Frame(self)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.rowconfigure(0, weight=1)
        cuerpo.columnconfigure(0, weight=2, uniform="cuerpo")
        cuerpo.columnconfigure(1, weight=3, uniform="cuerpo")
        cuerpo.columnconfigure(2, minsize=330)

        entrada = tarjeta(cuerpo, padding=(14, 10), row=0, column=0, sticky="nsew", padx=(0, 12))
        entrada.columnconfigure(0, weight=1)
        entrada.rowconfigure(1, weight=1)
        ttk.Label(entrada, text="① SISTEMA · una ecuación por línea", style="Panel.Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6))
        self.texto = tk.Text(entrada, height=5, width=28, wrap="none", font=fuente(12, mono=True),
                             background=PALETA["campo"], foreground=PALETA["texto"], insertbackground=PALETA["acento_hover"],
                             highlightthickness=1, highlightbackground=PALETA["borde"], highlightcolor=PALETA["acento"],
                             relief="flat", padx=10, pady=8, undo=True)
        self.texto.colores_propios = True
        self.texto.grid(row=1, column=0, sticky="nsew")
        self.texto.bind("<<Modified>>", self._al_modificar)
        # Matriz aumentada con la diagonal resaltada y, a la derecha, |aᵢᵢ| frente a Σ|aᵢⱼ|.
        self.vista_previa = tk.Text(entrada, height=1, width=1, wrap="none", font=fuente(10, mono=True),
                                    background=PALETA["tarjeta"], foreground=PALETA["texto"], relief="flat",
                                    borderwidth=0, highlightthickness=0, padx=0, pady=0, cursor="arrow",
                                    state="disabled")
        self.vista_previa.colores_propios = True
        self.vista_previa.tag_configure("diagonal", foreground=PALETA["acento_hover"], font=fuente(10, "bold", mono=True))
        self.vista_previa.tag_configure("cero", foreground=PALETA["error"], font=fuente(10, "bold", mono=True),
                                        background=PALETA["error_suave"])
        self.vista_previa.tag_configure("cumple", foreground=PALETA["exito"])
        self.vista_previa.tag_configure("falla", foreground=PALETA["error"])
        self.vista_previa.tag_configure("tenue", foreground=PALETA["texto_tenue"], font=fuente(9))
        self.vista_previa.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.estado_entrada = ttk.Label(entrada, style="Panel.Ayuda.TLabel", justify="left", wraplength=320)
        self.estado_entrada.grid(row=3, column=0, sticky="ew", pady=(4, 0))
        ttk.Label(entrada, text="Variables: x, y, z, w o x₁, x₂… · coeficientes: 3, −2.5, 1/3 · "
                                "también filas «a b c | d»", style="Panel.Tenue.TLabel",
                  wraplength=320).grid(row=4, column=0, sticky="w", pady=(4, 0))

        grafica = tarjeta(cuerpo, padding=(14, 10), row=0, column=1, sticky="nsew", padx=(0, 12))
        grafica.columnconfigure(0, weight=1)
        grafica.rowconfigure(1, weight=1)
        cabecera = ttk.Frame(grafica, style="Panel.TFrame")
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        cabecera.columnconfigure(0, weight=1)
        ttk.Label(cabecera, text="GRÁFICA", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.selector_grafica = SelectorSegmentado(cabecera, ("Componentes", "Error log₁₀", "Plano"), self._cambiar_grafica)
        self.selector_grafica.grid(row=0, column=1)
        self.selector_grafica.marcar(self.modo_grafica)
        self.plano = PlanoCartesiano(grafica, height=160)
        self.plano.grid(row=1, column=0, sticky="nsew")
        self.plano.bind("<Configure>", lambda _e: self._reencuadrar_plano(), add="+")
        # La nota va sobre el plano (place), no en la cuadrícula: así no altera el tamaño de la tarjeta.
        self.nota_grafica = tk.Label(self.plano, text="", font=fuente(9), justify="left", wraplength=300,
                                     background=PALETA["plano"], foreground=PALETA["texto_suave"], padx=6)
        self.nota_grafica.colores_propios = True
        self.nota_grafica.place(x=8, y=6, anchor="nw")
        self.aviso_grafica = ttk.Label(grafica, style="Panel.Tenue.TLabel", justify="center")
        self.aviso_grafica.place(in_=self.plano, relx=0.5, rely=0.5, anchor="center")

        lateral = tarjeta(cuerpo, padding=(14, 10), row=0, column=2, sticky="nsew")
        lateral.columnconfigure((0, 1, 2), weight=1, uniform="p")
        ttk.Label(lateral, text="② PARÁMETROS Y ANÁLISIS", style="Panel.Seccion.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
        marco_x0 = ttk.Frame(lateral, style="Panel.TFrame")
        marco_x0.grid(row=1, column=0, sticky="new", padx=(0, 6))
        ttk.Label(marco_x0, text="x⁽⁰⁾", style="Panel.Formula.TLabel").pack(anchor="w")
        self.variable_x0 = tk.StringVar()
        self.entrada_x0 = ttk.Entry(marco_x0, textvariable=self.variable_x0, width=1, font=fuente(11, mono=True))
        self.entrada_x0.pack(fill="x", pady=(3, 0))
        self.variable_x0.trace_add("write", lambda *_: self._descartar())
        self.campo_tolerancia = CampoValor(lateral, "Tolerancia", "La tolerancia", al_cambiar=self._descartar,
                                           al_enter=self.resolver)
        self.campo_tolerancia.grid(row=1, column=1, sticky="new", padx=(0, 6))
        self.campo_iteraciones = CampoValor(lateral, "Máx. iter.", "El máximo de iteraciones",
                                            al_cambiar=self._descartar, al_enter=self.resolver)
        self.campo_iteraciones.grid(row=1, column=2, sticky="new")
        self.campo_tolerancia.establecer("1e-6")
        self.campo_iteraciones.establecer("100")
        self.analisis = ttk.Label(lateral, style="Panel.Formula.TLabel", justify="left")
        self.analisis.grid(row=2, column=0, columnspan=3, sticky="nw", pady=(10, 4))
        self._construir_diagnostico(lateral)
        self.validacion = ttk.Label(lateral, style="Panel.Pendiente.TLabel", justify="left", wraplength=300)
        self.validacion.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(4, 8))
        lateral.rowconfigure(4, weight=1)
        botones = ttk.Frame(lateral, style="Panel.TFrame")
        botones.grid(row=5, column=0, columnspan=3, sticky="ew")
        botones.columnconfigure((0, 1), weight=1)
        self.boton_reordenar = ttk.Button(botones, text="Reordenar filas", style="Panel.TButton",
                                          command=self.reordenar)
        self.boton_reordenar.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(botones, text="Resolver", style="Panel.Accion.TButton", command=self.resolver).grid(
            row=0, column=1, sticky="ew")

    def _construir_diagnostico(self, padre):
        """Una fila por método: veredicto, motivo y estimación de iteraciones. Clic para usarlo."""
        self.diagnostico = tk.Frame(padre, background=PALETA["tarjeta"])
        self.diagnostico.colores_propios = True
        self.diagnostico.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.diagnostico.columnconfigure(0, weight=1)
        self.veredictos = []
        self.filas_diagnostico = {}
        for indice, metodo in enumerate(METODOS):
            fila = tk.Frame(self.diagnostico, background=PALETA["tarjeta"], cursor="hand2", padx=6, pady=1)
            fila.grid(row=indice, column=0, sticky="ew", pady=(0, 1))
            fila.columnconfigure(1, weight=1)
            titulo = tk.Label(fila, anchor="w", font=fuente(10, "bold"), background=PALETA["tarjeta"])
            titulo.grid(row=0, column=0, sticky="w")
            estimacion = tk.Label(fila, anchor="e", font=fuente(9, mono=True), background=PALETA["tarjeta"],
                                  foreground=PALETA["texto_tenue"])
            estimacion.grid(row=0, column=1, sticky="e")
            detalle = tk.Label(fila, anchor="w", justify="left", font=fuente(9),
                               background=PALETA["tarjeta"], foreground=PALETA["texto_suave"])
            detalle.grid(row=1, column=0, columnspan=2, sticky="w", padx=(14, 0))
            ayuda = AyudaEmergente(fila, "")
            for widget in (fila, titulo, estimacion, detalle):
                widget.colores_propios = True
                widget.bind("<Button-1>", lambda _e, m=metodo: self.usar_metodo_recomendado(m))
                if widget is not fila:
                    widget.bind("<Enter>", ayuda._mostrar)
                    widget.bind("<Leave>", ayuda._ocultar)
            self.filas_diagnostico[metodo] = (fila, titulo, estimacion, detalle, ayuda)

    def _pintar_diagnostico(self):
        """Colorea cada veredicto y marca el método activo."""
        por_metodo = {v.metodo: v for v in self.veredictos}
        for metodo, (fila, titulo, estimacion, detalle, ayuda) in self.filas_diagnostico.items():
            veredicto = por_metodo.get(metodo)
            fondo = PALETA["acento_suave"] if metodo == self.metodo and veredicto else PALETA["tarjeta"]
            for widget in (fila, titulo, estimacion, detalle):
                widget.configure(background=fondo)
            if veredicto is None:
                titulo.configure(text="")
                estimacion.configure(text="")
                detalle.configure(text="")
                fila.grid_remove()
                continue
            fila.grid()
            titulo.configure(text=f"{veredicto.marca} {metodo}",
                             foreground=PALETA[COLOR_VEREDICTO.get(veredicto.estado, "texto_suave")])
            estimacion.configure(text=f"≈ {veredicto.iteraciones} iter." if veredicto.iteraciones else "")
            detalle.configure(text=veredicto.breve or veredicto.detalle)
            accion = {REORDENAR: "Clic: reordena y usa este método.", FUNCIONA: "Clic: usar este método."}.get(
                veredicto.estado, "Clic: ver este método.")
            ayuda.texto = f"{veredicto.detalle}\n{accion}"

    def _diagnosticar(self):
        try:
            tolerancia = self.campo_tolerancia.obtener()
        except ValueError:
            tolerancia = 1e-6
        try:
            self.veredictos = diagnosticar(self.A, self.b, tolerancia if tolerancia > 0 else 1e-6)
        except (ValueError, ZeroDivisionError, OverflowError):
            self.veredictos = []
        self._pintar_diagnostico()

    def usar_metodo_recomendado(self, metodo):
        """Clic en una fila del diagnóstico: cambia al método y, si hace falta, reordena las ecuaciones."""
        veredicto = next((v for v in self.veredictos if v.metodo == metodo), None)
        if veredicto is None:
            return
        self.cambiar_metodo(metodo)
        if veredicto.estado == REORDENAR:
            self.reordenar()

    def cambiar_modo_numeros(self, modo):
        """Fracciones exactas o decimales en Gauss-Jordan; si ya hay resultado, se rehace."""
        self.modo_numeros = modo
        self.selector_numeros.marcar(ETIQUETA_NUMEROS[modo])
        if self.metodo == "Gauss-Jordan" and self.resultado is not None:
            self.resolver()

    def _actualizar_selector_numeros(self):
        disponible = (self.metodo == "Gauss-Jordan" and self.A is not None
                      and ps.puede_ser_exacto(self.A, self.b))
        if disponible:
            self.selector_numeros.grid()
        else:
            self.selector_numeros.grid_remove()

    def _construir_resultados(self):
        zona = ttk.Frame(self, padding=(0, 10, 0, 0))
        zona.grid(row=2, column=0, sticky="nsew")
        zona.rowconfigure(0, weight=1)
        zona.columnconfigure(0, minsize=250)
        zona.columnconfigure(1, weight=3)
        zona.columnconfigure(2, weight=2, minsize=320)
        tarjeta_resultado = tarjeta(zona, row=0, column=0, sticky="nsew", padx=(0, 12))
        cabecera_resultado = ttk.Frame(tarjeta_resultado, style="Panel.TFrame")
        cabecera_resultado.pack(fill="x")
        cabecera_resultado.columnconfigure(0, weight=1)
        ttk.Label(cabecera_resultado, text="RESULTADO", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        # Gauss-Jordan con fracciones exactas o con decimales; solo aparece si los datos lo permiten.
        # Etiquetas cortas («0.25» / «1/4») para no ensanchar ni alargar la tarjeta; la ayuda dice qué hacen.
        self.selector_numeros = SelectorSegmentado(
            cabecera_resultado, tuple(ETIQUETA_NUMEROS.values()),
            lambda etiqueta: self.cambiar_modo_numeros(MODO_POR_ETIQUETA[etiqueta]))
        self.selector_numeros.grid(row=0, column=1, sticky="e")
        self.selector_numeros.marcar(ETIQUETA_NUMEROS[self.modo_numeros])
        for etiqueta, ayuda in zip(self.selector_numeros.opciones.values(),
                                   ("Gauss-Jordan con decimales", "Gauss-Jordan con fracciones exactas")):
            AyudaEmergente(etiqueta, ayuda)
        self.selector_numeros.grid_remove()
        self.estado = ttk.Label(tarjeta_resultado, text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.estado.pack(anchor="w", pady=(6, 4))
        self.valor = ttk.Label(tarjeta_resultado, text="", style="Panel.Formula.TLabel", justify="left",
                               font=fuente(13, "bold", mono=True))
        self.valor.pack(anchor="w")
        self.datos = ttk.Label(tarjeta_resultado, style="Panel.Ayuda.TLabel", justify="left", wraplength=220)
        self.datos.pack(anchor="w", pady=(8, 0))
        self.tabla = TablaPaginada(zona, "ITERACIONES", al_elegir=self._al_elegir_fila,
                                   titulo_ventana=lambda: f"{self.metodo} · tabla completa")
        self.tabla.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        self.panel = PanelProcedimiento(zona, self._lineas_completas,
                                        titulo_ventana=lambda: f"Procedimiento · {self.metodo}")
        self.panel.grid(row=0, column=2, sticky="nsew")

    # ================================================================ método
    def _aplicar_metodo(self):
        self.selector.marcar(self.metodo)
        if hasattr(self, "selector_numeros"):
            self._actualizar_selector_numeros()
        self.etiqueta_formula.configure(text=FORMULAS[self.metodo])
        self.etiqueta_descripcion.configure(text=DESCRIPCIONES[self.metodo])
        iterativo = self.metodo in ITERATIVOS
        for widget in (self.entrada_x0, self.campo_tolerancia.entrada, self.campo_iteraciones.entrada,
                       self.boton_reordenar):
            widget.state(["!disabled"] if iterativo else ["disabled"])
        if iterativo:
            self.tabla.configurar_columnas(ps.columnas_iterativas(self.variables or ("x1",)))
        else:
            self.tabla.configurar_columnas((("n", "Paso", 54), ("operacion", "Operación de filas", 420, "w")))

    def cambiar_metodo(self, metodo):
        if metodo == self.metodo:
            return
        if self.resultado is not None:
            self.resultados[self.metodo] = self.resultado
        self.metodo = metodo
        self._aplicar_metodo()
        if self.A is not None:
            if metodo in ITERATIVOS:
                self.tabla.configurar_columnas(ps.columnas_iterativas(self.variables))
            self._mostrar_analisis()
        self.resultado = self.resultados.get(metodo)
        if self.resultado is not None:
            self._mostrar_resultado()
        else:
            self._reiniciar_resultado()

    # ================================================================ entrada y análisis
    def _al_modificar(self, _evento=None):
        if not self.texto.edit_modified():
            return
        self.texto.edit_modified(False)
        if self._escribiendo:
            return
        self.reordenado = ()  # la persona editó el sistema: ya no es el orden reordenado
        if self._programado is not None:
            self.after_cancel(self._programado)
        self._programado = self.after(250, self._analizar)

    def obtener_texto(self):
        return self.texto.get("1.0", "end").strip()

    def establecer_texto(self, texto, reordenado=()):
        self.reordenado = tuple(reordenado)
        self._escribiendo = True
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self.texto.edit_modified(False)
        self._escribiendo = False
        self._analizar()

    def _analizar(self):
        self._analizar_texto()
        self._actualizar_selector_numeros()
        if self.modo_grafica == "Plano":      # el plano depende de A: se rehace con el sistema nuevo
            self._dibujar_grafica()

    def _analizar_texto(self):
        """Lee el sistema y muestra su forma matricial, det(A), dominancia y ρ(T)."""
        self._programado = None
        self._descartar()
        texto = self.obtener_texto()
        if not texto:
            self.variables, self.A, self.b = (), None, None
            self._pintar_matriz()
            self.veredictos = []
            self._pintar_diagnostico()
            self.estado_entrada.configure(text="Escribe el sistema o carga un ejercicio.", foreground=PALETA["texto_suave"])
            self.analisis.configure(text="")
            self._validar("Paso ①: escribe el sistema a la izquierda.", "pendiente")
            return
        try:
            variables, A, b = leer_sistema(texto)
        except ValueError as exc:
            self.variables, self.A, self.b = (), None, None
            self._pintar_matriz()
            self.veredictos = []
            self._pintar_diagnostico()
            self.estado_entrada.configure(text=f"✗ {exc}", foreground=PALETA["error"])
            self.analisis.configure(text="")
            self._validar(str(exc), "error")
            return
        self.variables, self.A, self.b = tuple(variables), A, b
        n, m = len(A), len(variables)
        self.estado_entrada.configure(
            text=f"✓ {n} ecuaciones · {m} incógnitas ({', '.join(nombre_bonito(v) for v in variables)})"
                 + (f" · reordenado {', '.join(str(p + 1) for p in self.reordenado)}" if self.reordenado else ""),
            foreground=PALETA["exito"])
        self._pintar_matriz()
        self._diagnosticar()
        if self.metodo in ITERATIVOS:
            self.tabla.configurar_columnas(ps.columnas_iterativas(self.variables))
        self._mostrar_analisis()

    def _pintar_matriz(self):
        """[A | B] con la diagonal en color (ceros en rojo) y la dominancia por fila a la derecha."""
        texto = self.vista_previa
        texto.configure(state="normal")
        texto.delete("1.0", "end")
        if self.A is None:
            texto.configure(state="disabled", width=1, height=1)
            return
        A, b = self.A, self.b
        cuadrada = len(A) == len(A[0])
        signo = lambda v: ps.coef(v).replace("-", "−")
        ancho = max(len(signo(v)) for fila in A for v in fila + [0])
        ancho_b = max(len(signo(v)) for v in b)
        dominancia = anotar_dominancia(A) if cuadrada else []
        visibles = min(len(A), FILAS_VISTA_PREVIA)
        lineas = 0
        largo = 0
        for i in range(visibles):
            inicio = int(texto.index("end-1c").split(".")[1])
            texto.insert("end", "[ ")
            for j, valor in enumerate(A[i]):
                celda = signo(valor).rjust(ancho)
                etiqueta = ("cero" if valor == 0 else "diagonal") if cuadrada and i == j else ()
                texto.insert("end", celda, etiqueta)
                texto.insert("end", " ")
            texto.insert("end", "| " + signo(b[i]).rjust(ancho_b) + " ]")
            if dominancia:
                diagonal, suma, cumple = dominancia[i]
                texto.insert("end", f"  {signo(diagonal)} {'>' if cumple else '≤'} {signo(suma)} "
                                    f"{'✓' if cumple else '✗'}", "cumple" if cumple else "falla")
            largo = max(largo, int(texto.index("end-1c").split(".")[1]) - inicio)
            texto.insert("end", "\n")
            lineas += 1
        if len(A) > visibles:
            texto.insert("end", f"⋮  {len(A) - visibles} filas más\n", "tenue")
            lineas += 1
        if dominancia:
            leyenda = "diagonal en color · ceros en rojo · |aᵢᵢ| vs Σ|aᵢⱼ|"
            texto.insert("end", leyenda, "tenue")
            largo = max(largo, len(leyenda))
            lineas += 1
        else:
            texto.delete("end-2c", "end-1c")
        texto.configure(state="disabled", width=largo, height=lineas)

    def _mostrar_analisis(self):
        A, n, m = self.A, len(self.A), len(self.variables)
        lineas = []
        self._pintar_diagnostico()
        if n != m:
            lineas.append(f"Sistema {n}×{m}: no es cuadrado.")
            self.analisis.configure(text="\n".join(lineas))
            if self.metodo in ITERATIVOS:
                return self._validar("Jacobi y Gauss-Seidel necesitan tantas ecuaciones como incógnitas.", "error")
            return self._validar("Gauss-Jordan clasificará el sistema (única, infinitas o incompatible).", "ok")
        det = determinante(A, "lu")
        lineas.append(f"det(A) = {ps.coef(float(det)).replace('-', '−')}"
                      + ("  ≠ 0 → solución única" if det != 0 else "  = 0 → sin solución única"))
        if self.metodo == "Gauss-Jordan":
            self.analisis.configure(text="\n".join(lineas))
            return self._validar("✓ Listo para Gauss-Jordan." if det != 0 else
                                 "det(A) = 0: Gauss-Jordan indicará si hay infinitas soluciones o ninguna.",
                                 "ok" if det != 0 else "aviso")
        dominante = all(f.cumple for f in dominancia_diagonal(A))
        if any(A[i][i] == 0 for i in range(n)):
            self.analisis.configure(text="\n".join(lineas))
            veredicto = next((v for v in self.veredictos if v.metodo == self.metodo), None)
            if veredicto is not None and veredicto.estado == NO_FUNCIONA:
                otros = [v.metodo for v in self.veredictos if v.estado in (FUNCIONA, REORDENAR)]
                consejo = f" Usa {' o '.join(otros)}." if otros else ""
                return self._validar(f"{veredicto.detalle}{consejo}", "error")
            return self._validar("Hay ceros en la diagonal: no se puede despejar. Pulsa «Reordenar filas».", "error")
        rho = radio_espectral(matriz_iteracion(A, self.metodo))
        self.analisis.configure(text="\n".join(lineas))
        if dominante:
            return self._validar("✓ Estrictamente dominante: la convergencia está garantizada.", "ok")
        if rho < 1:
            return self._validar("No es dominante, pero ρ(T) < 1: converge (la dominancia es suficiente, "
                                 "no necesaria).", "ok")
        mejora = reordenar_para_dominancia(A, self.b, self.metodo)
        consejo = (f" Reordenando se obtiene ρ ≈ {mejora[3]:.3f}: pulsa «Reordenar filas»." if mejora and mejora[3] < 1
                   else " Ningún orden de ecuaciones lo arregla: usa Gauss-Jordan.")
        return self._validar(f"ρ(T) ≥ 1: {self.metodo} no converge con este orden.{consejo}", "aviso")

    def _validar(self, mensaje, nivel):
        self.validacion.configure(text=mensaje, foreground=PALETA[COLORES_NIVEL[nivel]])
        self._nivel = nivel

    def reordenar(self):
        """Reescribe las ecuaciones en el orden con menor ρ(T) (no cambia la solución)."""
        if self.A is None or self.metodo not in ITERATIVOS:
            return
        mejora = reordenar_para_dominancia(self.A, self.b, self.metodo)
        if mejora is None:
            self._validar("El orden actual ya es el más favorable para este método.", "aviso")
            return
        A, b, permutacion, _rho = mejora
        compuesta = tuple(self.reordenado[p] for p in permutacion) if self.reordenado else permutacion
        texto = "\n".join(ecuacion_texto(fila, bi, self.variables) for fila, bi in zip(A, b))
        self.establecer_texto(texto, compuesta)

    # ================================================================ resolver
    def _parametros(self):
        x0 = leer_vector(self.variable_x0.get(), len(self.variables))
        tolerancia = self.campo_tolerancia.obtener()
        iteraciones = self.campo_iteraciones.obtener()
        if not float(iteraciones).is_integer():
            raise ValueError("El máximo de iteraciones debe ser un número entero.")
        return x0, tolerancia, int(iteraciones)

    def _resolver(self, metodo):
        if metodo == "Gauss-Jordan":
            return ps.resolver_directo(self.A, self.b, self.variables, exacto=self.modo_numeros == "Fracciones")
        x0, tolerancia, iteraciones = self._parametros()
        return resolver_iterativo(self.A, self.b, metodo, x0, tolerancia, iteraciones, self.variables,
                                  self.reordenado)

    def resolver(self):
        if self.A is None:
            self._validar("Escribe un sistema válido antes de resolver.", "error")
            return
        try:
            resultado = self._resolver(self.metodo)
        except ValueError as exc:
            self._validar(str(exc), "error")
            return
        self.resultado = resultado
        self.resultados = {self.metodo: resultado}
        self.comparacion = None
        self._mostrar_resultado()

    def comparar(self):
        """Resuelve con Jacobi y Gauss-Seidel sobre el mismo sistema y compara."""
        if self.A is None:
            self._validar("Escribe un sistema válido antes de comparar.", "error")
            return
        try:
            self.resultados = {m: self._resolver(m) for m in ITERATIVOS}
        except ValueError as exc:
            self._validar(str(exc), "error")
            return
        if self.metodo not in ITERATIVOS:
            self.metodo = "Gauss-Seidel"
            self._aplicar_metodo()
        self.resultado = self.resultados[self.metodo]
        self.comparacion = ps.comparacion_iterativa(self.resultados["Jacobi"], self.resultados["Gauss-Seidel"])
        self.modo_grafica = "Error log₁₀"
        self.selector_grafica.marcar(self.modo_grafica)
        self._mostrar_resultado()
        self.panel.mostrar(self.comparacion)

    def _descartar(self):
        if getattr(self, "resultado", None) is None and not getattr(self, "resultados", None):
            return
        self.resultado, self.resultados, self.comparacion = None, {}, None
        self._reiniciar_resultado()

    def _reiniciar_resultado(self):
        self.estado.configure(text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.valor.configure(text="")
        self.datos.configure(text="")
        self.tabla.limpiar()
        self.panel.mostrar(self._lineas_ayuda())
        self._dibujar_grafica()

    def _mostrar_resultado(self):
        r = self.resultado
        directo = self.metodo == "Gauss-Jordan"
        if directo:
            textos = {"unica": "✓ Solución única", "infinitas": "⚠ Infinitas soluciones", "incompatible": "✗ Incompatible"}
            self.estado.configure(text=textos[r.tipo], style="Panel.Exito.TLabel" if r.tipo == "unica" else "Panel.Error.TLabel")
            solucion = r.solucion
            datos = [f"{len(r.pasos)} pasos de eliminación"]
            if r.solucion:
                datos.append(f"residuo ‖b − AX‖∞ = {ps.g(r.residuo, 3)}")
            self.tabla.definir_filas([(i + 1, ps.titulo_paso(p)) for i, p in enumerate(r.pasos)])
            self.panel.mostrar(self.comparacion or ps.resumen_directo(r))
        else:
            self.estado.configure(text="✓ Convergencia alcanzada" if r.convergio else "✗ Sin convergencia",
                                  style="Panel.Exito.TLabel" if r.convergio else "Panel.Error.TLabel")
            solucion = r.solucion
            datos = [f"{len(r.iteraciones)} iteraciones",
                     f"residuo ‖b − AX‖∞ = {ps.g(r.iteraciones[-1].residuo, 3) if r.iteraciones else '—'}",
                     f"ρ(T) ≈ {r.radio_espectral:.4f}" if r.radio_espectral is not None else "", r.motivo]
            total = len(r.iteraciones)
            self.tabla.definir_filas(ps.filas_iterativas(r), lambda i: (
                ["final_ok" if r.convergio else "final_no"] if i == total else []))
            self.panel.mostrar(self.comparacion or ps.resumen_iterativo(r))
        exacta = getattr(r, "exacta", ()) if directo else ()
        self.valor.configure(text="\n".join(
            f"{nombre_bonito(v)} = {str(q).replace('-', '−') if exacta else ps.g(x, 10)}"
            for v, x, q in zip(self.variables, solucion, exacta or solucion)) or "—")
        if exacta:
            datos.insert(0, "Exacta: ≈ decimales en el procedimiento")
        self.datos.configure(text="\n".join(d for d in datos if d))
        self._dibujar_grafica()

    def _al_elegir_fila(self, indice):
        r = self.resultado
        if r is None:
            return
        if self.metodo == "Gauss-Jordan":
            self.panel.mostrar(ps.lineas_paso(r.pasos[indice]))
        else:
            self.panel.mostrar(ps.detalle_iterativo(r, indice))

    def _lineas_completas(self):
        r = self.resultado
        if r is None:
            return self._lineas_ayuda()
        lineas = list(self.comparacion or [])
        if lineas:
            lineas.append(("", "normal"))
        if self.metodo == "Gauss-Jordan":
            lineas += ps.resumen_directo(r)[:-2]
            for paso in r.pasos:
                lineas += [("", "normal")] + ps.lineas_paso(paso)
        else:
            lineas += ps.resumen_iterativo(r)[:-2]
            for indice in range(1, len(r.iteraciones) + 1):
                lineas += [("", "normal")] + ps.detalle_iterativo(r, indice)
        return lineas

    def _lineas_ayuda(self):
        return [("Cómo usar esta vista", "titulo"),
                ("1. Escribe el sistema (una ecuación por línea) o carga un ejercicio.", "normal"),
                ("2. Revisa el análisis: det(A), dominancia diagonal y ρ(T).", "normal"),
                ("3. Elige el método y pulsa «Resolver». «Comparar J / GS» ejecuta ambos iterativos.", "normal"),
                ("4. Cada fila de la tabla muestra aquí sus sustituciones u operaciones de fila.", "normal"),
                ("", "normal"), ("Fórmula", "titulo"), (FORMULAS[self.metodo], "formula")]

    # ================================================================ gráfica
    def _cambiar_grafica(self, modo):
        self.modo_grafica = modo
        self.selector_grafica.marcar(modo)
        self._dibujar_grafica()

    def _dibujar_plano_2x2(self):
        """Las dos rectas y su intersección (y, si hay, el camino de Jacobi / Gauss-Seidel)."""
        self.plano.definir_funcion(None)
        if self.A is None or not admite_plano_sistema(self.A):
            self.plano.definir_capas([])
            self.plano.definir_puntos([])
            self.nota_grafica.configure(text="")
            self.aviso_grafica.configure(text="El plano está disponible con 2 ecuaciones y 2 incógnitas.")
            self.aviso_grafica.lift()
            return
        self.aviso_grafica.lower(self.plano)
        trayectoria = None
        if self.resultado is not None and self.metodo in ITERATIVOS and self.resultado.iteraciones:
            trayectoria = [(0, self.resultado.x0)] + [(paso.k, paso.x) for paso in self.resultado.iteraciones]
        self._dibujo_plano = dibujo_sistema(self.A, self.b, trayectoria)
        self.plano.definir_funcion(None, self._dibujo_plano.curvas)
        self.plano.definir_capas(self._dibujo_plano.capas)
        self.plano.definir_puntos(self._dibujo_plano.puntos)
        self.nota_grafica.configure(text=self._dibujo_plano.nota)
        self.nota_grafica.lift()
        self._reencuadrar_plano(forzar=True)

    def _reencuadrar_plano(self, forzar=False):
        """Misma escala en x e y para que las pendientes de las rectas se vean reales."""
        dibujo = getattr(self, "_dibujo_plano", None)
        if self.modo_grafica != "Plano" or dibujo is None or self.plano.winfo_width() < 60:
            return
        if forzar or self.plano.ajuste_automatico:
            self.plano.encuadrar(*encuadre_proporcional(dibujo.encuadre, self.plano.winfo_width(),
                                                        self.plano.winfo_height()))

    def _dibujar_grafica(self):
        if self.modo_grafica == "Plano":
            self._dibujar_plano_2x2()
            return
        self.plano.definir_funcion(None)
        self.nota_grafica.configure(text="")
        iterativos = {m: r for m, r in self.resultados.items() if m in ITERATIVOS}
        if not iterativos:
            self.plano.definir_capas([])
            self.plano.definir_puntos([])
            self.aviso_grafica.configure(
                text="Gauss-Jordan es un método directo: no hay iteraciones que graficar."
                if self.metodo == "Gauss-Jordan" else "Resuelve con Jacobi o Gauss-Seidel para ver la convergencia.")
            self.aviso_grafica.lift()
            return
        self.aviso_grafica.lower(self.plano)
        if self.modo_grafica == "Componentes":
            capas, puntos, limites = convergencia.capas_componentes(self.resultado or next(iter(iterativos.values())))
        else:
            capas, puntos, limites = convergencia.capas_error(iterativos)
        self.plano.definir_capas(capas)
        self.plano.definir_puntos(puntos)
        self.plano.encuadrar(*convergencia.encuadre(limites))

    # ================================================================ acciones
    def cargar_ejercicio(self, ejercicio):
        datos = ejercicio.datos
        if ejercicio.metodo != self.metodo:
            self.cambiar_metodo(ejercicio.metodo)
        self.variable_x0.set(datos.get("x0", ""))
        # Los ejercicios que piden aritmética exacta se cargan en fracciones; los demás, en decimales.
        self.modo_numeros = "Fracciones" if datos.get("exacto") else "Decimales"
        self.selector_numeros.marcar(ETIQUETA_NUMEROS[self.modo_numeros])
        self.campo_tolerancia.establecer("1e-6")
        self.campo_iteraciones.establecer("200" if ejercicio.metodo in ITERATIVOS else "100")
        self.establecer_texto(datos["sistema"])
        if datos.get("reordenar"):
            self.reordenar()
        self.resolver()
        self._validar(f"{ejercicio.dificultad} · {ejercicio.fuente}. {ejercicio.justificacion}", "ok")

    def cargar_ejemplo(self):
        self.variable_x0.set("0, 0, 0, 0")
        self.establecer_texto(GUIA)
        self.resolver()

    def limpiar(self):
        self.variable_x0.set("")
        self.campo_tolerancia.establecer("1e-6")
        self.campo_iteraciones.establecer("100")
        self.establecer_texto("")
