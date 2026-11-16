"""Vista común para Bisección, Regula Falsi, Newton-Raphson y Secante.

Flujo: ① escribir f(x) → la gráfica y sus puntos notables aparecen al instante
→ ② elegir valores iniciales (clic, «Sugerir valores» o a mano), validados en
vivo y dibujados → resolver → resultado, tabla paginada y paso a paso.

Este archivo solo arma la pantalla y coordina eventos. Las condiciones de cada
método están en validacion.py y lo que se dibuja en el plano, en capas.py.
"""

from tkinter import ttk

from interfaz.campoMatematico import CampoMatematico, CampoValor, texto_atajos
from interfaz.componentes import (
    MenuEjercicios, PanelProcedimiento, SelectorSegmentado, TablaPaginada, tarjeta as crear_tarjeta,
)
from interfaz.estilos import PALETA, fuente
from interfaz.motorGrafica import PlanoCartesiano
from interfaz.raices.configuracion import CONFIGURACION, ESTILO_PUNTO
from interfaz.raices.grafica import GraficaMixin
from interfaz.raices.resultados import ResultadosMixin
from nucleo import procedimientos
from nucleo.ejercicios import ejercicios_de

ANCHO_RESULTADO = 250


class VistaRaiz(GraficaMixin, ResultadosMixin, ttk.Frame):
    """Pantalla de uno o varios métodos de raíces que comparten función y gráfica."""

    # Bajo este alto la vista deja de comprimirse y aparece la barra de la página.
    ALTO_MINIMO = 680

    def __init__(self, padre, metodos):
        super().__init__(padre, padding=(22, 18, 22, 14))
        self.metodos = (metodos,) if isinstance(metodos, str) else tuple(metodos)
        self.metodo = self.metodos[0]
        self.resultados_por_metodo = {}
        self.comparacion = None
        self.funcion = None
        self.derivada = None
        self.segunda = None
        self.notables = []
        self.notables_por_clave = {}
        self.resultado = None
        self.iteracion_elegida = None
        self.expandido = False
        self._ajustando_vista = False
        self._vista_manual = False
        self._explicacion_pendiente = None
        self._clics = 0
        self.ventanas = {}
        self.columnconfigure(0, weight=1)
        # La gráfica y los resultados se reparten el alto en proporción 62 : 38,
        # sin importar el tamaño natural de su contenido: todo cabe en la ventana.
        self.rowconfigure(2, weight=62, uniform="zonas")
        self.rowconfigure(3, weight=38, uniform="zonas")
        self._construir_encabezado()
        self._construir_funcion()
        self._construir_cuerpo()
        self._aplicar_metodo()
        self._habilitar_parametros(False)
        self._al_cambiar_parametros()
        self._mostrar_resumen_vacio()

    @property
    def config(self):
        return CONFIGURACION[self.metodo]

    # Accesos directos usados por las pruebas y por otras vistas.
    @property
    def tabla(self):
        return self.tabla_iteraciones.tabla

    @property
    def por_pagina(self):
        return self.tabla_iteraciones.por_pagina

    @property
    def etiqueta_pagina(self):
        return self.tabla_iteraciones.etiqueta_pagina

    @property
    def detalle(self):
        return self.panel_procedimiento.texto

    def _ir_a_pagina(self, pagina, seleccionar=None):
        self.tabla_iteraciones.ir_a_pagina(pagina, seleccionar)

    # ================================================================ diseño
    def _construir_encabezado(self):
        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        encabezado.columnconfigure(1, weight=1)
        self.titulo = ttk.Label(encabezado, text=self.metodo, style="Titulo.TLabel")
        self.titulo.grid(row=0, column=0, sticky="w")
        informacion = ttk.Frame(encabezado)
        informacion.grid(row=0, column=1, sticky="ew", padx=(16, 12))
        self.etiqueta_formula = ttk.Label(informacion, text="", style="Formula.TLabel")
        self.etiqueta_formula.pack(anchor="w")
        self.etiqueta_descripcion = ttk.Label(informacion, text="", style="Tenue.TLabel", justify="left")
        self.etiqueta_descripcion.pack(anchor="w", fill="x")
        informacion.bind("<Configure>", lambda e: self.etiqueta_descripcion.configure(
            wraplength=max(160, e.width - 4)))
        acciones = ttk.Frame(encabezado)
        acciones.grid(row=0, column=2, sticky="e")
        self.selector = None
        if len(self.metodos) > 1:
            # Control segmentado para alternar métodos sin perder la función ni la gráfica.
            self.selector = SelectorSegmentado(acciones, self.metodos, self.cambiar_metodo)
            self.selector.pack(side="left", padx=(0, 12))
            ttk.Button(acciones, text="Comparar ambos", command=self.comparar).pack(side="left", padx=(0, 6))
        self.menu_ejercicios = MenuEjercicios(acciones, ejercicios_de(self.metodos), self.cargar_ejercicio)
        self.menu_ejercicios.pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Limpiar", command=self.limpiar).pack(side="left")

    def _construir_funcion(self):
        self.tarjeta_funcion = crear_tarjeta(self, row=1, column=0, sticky="ew", pady=(0, 10))
        self.tarjeta_funcion.configure(padding=(14, 10))
        self.tarjeta_funcion.columnconfigure(0, weight=3)
        self.campo_funcion = CampoMatematico(
            self.tarjeta_funcion, "f(x) =", al_cambiar=self._al_cambiar_funcion, panel=True,
            texto_vacio="Escribe la función o una igualdad: x^3 - x - 2,  2x = cos x,  e^(-x) - x",
            al_enter=self.resolver,
        )
        self.campo_funcion.grid(row=0, column=0, sticky="ew")
        self.campo_derivada = None
        if "Newton-Raphson" in self.metodos:
            # f′(x) va al lado de f(x) para no robar alto a la gráfica.
            self.tarjeta_funcion.columnconfigure(1, weight=2)
            self.campo_derivada = CampoMatematico(
                self.tarjeta_funcion, "f′(x) =", al_cambiar=self._al_cambiar_derivada, panel=True,
                permitir_vacio=True, texto_vacio="Vacío: se calcula con las reglas de derivación.",
                al_enter=self.resolver, ancho=24,
            )
            self.campo_derivada.grid(row=0, column=1, sticky="ew", padx=(16, 0))
            # Modo automático: el campo muestra la derivada calculada y no se edita.
            # «Editar» pasa a modo manual (partiendo de la calculada) y se verifica al resolver.
            self.derivada_automatica = True
            self._sincronizando_derivada = False
            self.boton_derivada = ttk.Button(self.campo_derivada, text="✎ Editar", style="Panel.TButton",
                                             command=self._alternar_derivada)
            self.boton_derivada.grid(row=0, column=2, padx=(8, 0))
        pie = ttk.Frame(self.tarjeta_funcion, style="Panel.TFrame")
        pie.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        pie.columnconfigure(1, weight=1)
        ttk.Label(pie, text="① Escribe f(x): la gráfica se genera sin valores iniciales.",
                  style="Panel.Ayuda.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(pie, text=texto_atajos(self) + "   ·   también: 2x, sin x, √, ², π",
                  style="Panel.Tenue.TLabel").grid(row=0, column=1, sticky="e")

    def _construir_cuerpo(self):
        self.cuerpo = ttk.Frame(self)
        self.cuerpo.grid(row=2, column=0, sticky="nsew")
        self.cuerpo.columnconfigure(0, weight=1)
        self.cuerpo.rowconfigure(0, weight=1)
        self.plano = PlanoCartesiano(self.cuerpo, height=200, al_seleccionar=self._al_seleccionar_punto,
                                     al_cambiar_vista=self._al_cambiar_vista, al_expandir=self._expandir,
                                     al_clic=self._al_clic_plano)
        self.plano.grid(row=0, column=0, sticky="nsew")
        self.lateral = ttk.Frame(self.cuerpo)
        self.lateral.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self.lateral.rowconfigure(1, weight=1)
        self.lateral.columnconfigure(0, weight=1, minsize=310)
        self._construir_parametros()
        self._construir_notables()

        # Franja inferior: resultado | iteraciones | procedimiento.
        self.resultados = ttk.Frame(self, padding=(0, 10, 0, 0))
        self.resultados.grid(row=3, column=0, sticky="nsew")
        self.resultados.rowconfigure(0, weight=1)
        self.resultados.columnconfigure(0, minsize=ANCHO_RESULTADO)
        self.resultados.columnconfigure(1, weight=3)
        self.resultados.columnconfigure(2, weight=2, minsize=300)
        self._construir_tarjeta_resultado()
        self.tabla_iteraciones = TablaPaginada(
            self.resultados, "ITERACIONES", al_elegir=self._al_elegir_iteracion,
            titulo_ventana=lambda: f"Iteraciones · {self.metodo}",
            nota=lambda: (f"{self.metodo} · {len(self.resultado.iteraciones)} iteraciones · {self.resultado.motivo}"
                          if self.resultado else ""))
        self.tabla_iteraciones.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        self.panel_procedimiento = PanelProcedimiento(
            self.resultados, self._lineas_completas, titulo_ventana=lambda: f"Procedimiento · {self.metodo}")
        self.panel_procedimiento.grid(row=0, column=2, sticky="nsew")

    def _construir_parametros(self):
        tarjeta = crear_tarjeta(self.lateral, row=0, column=0, sticky="ew")
        tarjeta.configure(padding=(14, 10))
        self.titulo_parametros = ttk.Label(tarjeta, text="② VALORES INICIALES", style="Panel.Seccion.TLabel")
        self.titulo_parametros.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))
        # Se crean los campos de todos los métodos de la vista; _aplicar_metodo
        # muestra solo los del método activo (x₀ es compartido por Newton y Secante).
        self.campos = {}
        self._todos_los_campos = {}
        for metodo in self.metodos:
            for clave, etiqueta, contexto in CONFIGURACION[metodo]["parametros"]:
                if clave not in self._todos_los_campos:
                    self._todos_los_campos[clave] = CampoValor(
                        tarjeta, etiqueta, contexto, al_cambiar=self._al_cambiar_parametros,
                        al_enter=self.resolver)
        self.campo_tolerancia = CampoValor(tarjeta, "Tolerancia", "La tolerancia",
                                           al_cambiar=self._al_cambiar_parametros, al_enter=self.resolver)

        self.campo_iteraciones = CampoValor(tarjeta, "Máx. iter.", "El máximo de iteraciones",
                                            al_cambiar=self._al_cambiar_parametros, al_enter=self.resolver)
        # Todos los valores en una sola fila para dejar alto a los puntos notables.
        for columna in range(4):
            tarjeta.columnconfigure(columna, weight=1, uniform="p")
        self.validacion = ttk.Label(tarjeta, text="", style="Panel.Pendiente.TLabel", wraplength=350,
                                    justify="left")
        self.validacion.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(8, 8))
        self.campo_tolerancia.establecer("1e-6")
        self.campo_iteraciones.establecer("100")
        botones = ttk.Frame(tarjeta, style="Panel.TFrame")
        botones.grid(row=4, column=0, columnspan=4, sticky="ew")
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)
        self.boton_sugerir = ttk.Button(botones, text="Sugerir valores", style="Panel.TButton",
                                        command=self.sugerir)
        self.boton_sugerir.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.boton_resolver = ttk.Button(botones, text="Resolver", style="Panel.Accion.TButton",
                                         command=self.resolver)
        self.boton_resolver.grid(row=0, column=1, sticky="ew")

    def _construir_notables(self):
        tarjeta = crear_tarjeta(self.lateral, row=1, column=0, sticky="nsew", pady=(10, 0))
        tarjeta.configure(padding=(14, 10))
        tarjeta.columnconfigure(0, weight=1)
        tarjeta.rowconfigure(1, weight=1)
        ttk.Label(tarjeta, text="PUNTOS NOTABLES EN LA VISTA", style="Panel.Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6))
        self.tabla_notables = ttk.Treeview(tarjeta, columns=("tipo", "x", "y"), show="headings",
                                           height=2, style="Tabla.Treeview", selectmode="browse")
        for columna, titulo, ancho in (("tipo", "Tipo", 128), ("x", "x", 78), ("y", "y", 78)):
            self.tabla_notables.heading(columna, text=titulo, anchor="w")
            self.tabla_notables.column(columna, width=ancho, minwidth=ancho - 10, anchor="w", stretch=True)
        for tipo, (_, color) in ESTILO_PUNTO.items():
            self.tabla_notables.tag_configure(tipo, foreground=PALETA[color])
        self.tabla_notables.grid(row=1, column=0, sticky="nsew")
        self.tabla_notables.bind("<<TreeviewSelect>>", self._al_elegir_notable)
        self.explicacion = ttk.Label(tarjeta, text="Escribe una función para ver sus raíces, extremos e "
                                     "inflexiones. Haz clic en uno para centrarlo.",
                                     style="Panel.Ayuda.TLabel", wraplength=340, justify="left")
        self.explicacion.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def _construir_tarjeta_resultado(self):
        tarjeta = crear_tarjeta(self.resultados, row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(tarjeta, text="RESULTADO", style="Panel.Seccion.TLabel").pack(anchor="w")
        self.estado = ttk.Label(tarjeta, text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.estado.pack(anchor="w", pady=(6, 0))
        self.valor = ttk.Label(tarjeta, text="x ≈ —", style="Panel.Resultado.TLabel", font=fuente(17, "bold", mono=True))
        self.valor.pack(anchor="w", pady=(2, 6))
        self.datos = ttk.Label(tarjeta, text="", style="Panel.Formula.TLabel", justify="left")
        self.datos.pack(anchor="w")
        # Ancho de ajuste fijo: un motivo largo no debe ensanchar la tarjeta y robar espacio a la tabla.
        self.motivo = ttk.Label(tarjeta, text="", style="Panel.Ayuda.TLabel", justify="left",
                                wraplength=ANCHO_RESULTADO - 34)
        self.motivo.pack(anchor="w", fill="x", pady=(8, 0))

    # ============================================================ métodos
    def _aplicar_metodo(self):
        """Ajusta título, fórmula, campos y columnas al método activo."""
        self.titulo.configure(text=" / ".join(self.metodos) if len(self.metodos) > 1 else self.metodo)
        self.etiqueta_formula.configure(text=procedimientos.FORMULAS[self.metodo])
        self.etiqueta_descripcion.configure(text=self.config["descripcion"])
        if self.selector is not None:
            self.selector.marcar(self.metodo)
        if self.campo_derivada is not None:
            if self.metodo == "Newton-Raphson":
                self.campo_derivada.grid()
            else:
                self.campo_derivada.grid_remove()
        for campo in self._todos_los_campos.values():
            campo.grid_remove()
        self.titulo_parametros.configure(text=self.config["titulo_parametros"])
        self._clics = 0
        self.campos = {clave: self._todos_los_campos[clave] for clave, _, _ in self.config["parametros"]}
        visibles = list(self.campos.values()) + [self.campo_tolerancia, self.campo_iteraciones]
        for indice, campo in enumerate(visibles):
            campo.grid(row=1, column=indice, sticky="new", padx=(0, 6) if indice < len(visibles) - 1 else 0)
        self.tabla_iteraciones.configurar_columnas(procedimientos.COLUMNAS[self.metodo])

    def cambiar_metodo(self, metodo):
        """Alterna el método conservando función, gráfica, valores y resultados."""
        if metodo == self.metodo or metodo not in self.metodos:
            return
        if self.resultado is not None:
            self.resultados_por_metodo[self.metodo] = self.resultado
        self.metodo = metodo
        self._aplicar_metodo()
        self.resultado = self.resultados_por_metodo.get(metodo)
        self.iteracion_elegida = None
        if self.resultado is not None:
            self._mostrar_resultado(encuadrar=False)
            if self.comparacion is not None:
                self._mostrar_lineas(self.comparacion)
        else:
            self._reiniciar_resultado_ui()
            mensaje, color = self._validar_parametros()
            self.validacion.configure(text=mensaje, foreground=color)
        self._actualizar_derivada_mostrada()

    def comparar(self):
        """Resuelve con los dos métodos de la vista y verifica que coincidan."""
        if self.funcion is None:
            self.validacion.configure(text="Primero escribe una función válida.", foreground=PALETA["error"])
            return
        faltan = [campo.etiqueta.cget("text") for campo in self._todos_los_campos.values()
                  if not campo.variable.get().strip()]
        if faltan:
            self.validacion.configure(
                text=f"Para comparar se necesitan {', '.join(faltan)}. Escríbelos o pulsa «Sugerir valores».",
                foreground=PALETA["error"])
            return
        try:
            valores = {clave: campo.obtener() for clave, campo in self._todos_los_campos.items()}
            _, tolerancia, iteraciones = self._leer_parametros()
            resultados = {metodo: self._resolver_con(metodo, valores, tolerancia, iteraciones)
                          for metodo in self.metodos}
        except ValueError as exc:
            self.validacion.configure(text=str(exc), foreground=PALETA["error"])
            return
        self.resultados_por_metodo = resultados
        self.resultado = resultados[self.metodo]
        self.iteracion_elegida = None
        self.comparacion = procedimientos.comparacion(resultados)
        self._mostrar_resultado()
        self._mostrar_lineas(self.comparacion)
        coinciden = any(estilo == "ok" for _, estilo in self.comparacion)
        self.validacion.configure(
            text=("✓ Ambos métodos llegan a la misma raíz. " if coinciden else
                  "⚠ Los métodos no coinciden; revisa la comparación. ")
            + "Alterna el selector para ver las iteraciones de cada uno.",
            foreground=PALETA["exito"] if coinciden else PALETA["aviso"])

    # ============================================================ acciones
    def cargar_ejemplo(self):
        funcion, valores = self.config["ejemplo"]
        for metodo in self.metodos:
            valores = {**CONFIGURACION[metodo]["ejemplo"][1], **valores}
        self._vista_manual = False
        self.campo_funcion.establecer(funcion)
        if self.campo_derivada is not None:
            self._alternar_derivada(automatica=True)
        for clave, valor in valores.items():
            self._todos_los_campos[clave].establecer(valor)
        self.campo_tolerancia.establecer("1e-6")
        self.campo_iteraciones.establecer("100")
        self.resolver()

    def cargar_ejercicio(self, ejercicio):
        """Carga un ejercicio guardado: cambia al método recomendado y resuelve."""
        if ejercicio.metodo != self.metodo:
            self.cambiar_metodo(ejercicio.metodo)
        self._vista_manual = False
        self.campo_funcion.establecer(ejercicio.datos["funcion"])
        if self.campo_derivada is not None:
            self._alternar_derivada(automatica=True)
        for clave, campo in self._todos_los_campos.items():
            campo.establecer(ejercicio.datos.get(clave, campo.variable.get()))
        self.campo_tolerancia.establecer("1e-6")
        self.campo_iteraciones.establecer("100")
        self.resolver()
        self.explicacion.configure(text=f"{ejercicio.dificultad} · {ejercicio.fuente}. {ejercicio.justificacion}")

    def limpiar(self):
        self.campo_funcion.establecer("")
        if self.campo_derivada is not None:
            self._alternar_derivada(automatica=True)
        for campo in self._todos_los_campos.values():
            campo.establecer("")
        self.campo_tolerancia.establecer("1e-6")
        self.campo_iteraciones.establecer("100")
        self._vista_manual = False
        self.explicacion.configure(text="Escribe una función para ver sus raíces, extremos e inflexiones.")
        self._descartar_resultado()
