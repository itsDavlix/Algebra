"""Vista de números romanos con el mismo diseño que Vectores y Matrices.

Se calcula mientras se escribe: no hay ventanas emergentes de error, solo un
aviso en línea. Cada número muestra su equivalente decimal al instante.
"""

import tkinter as tk
from tkinter import ttk

from interfaz.componentes import PanelProcedimiento, SelectorSegmentado, TablaPaginada, tarjeta
from interfaz.estilos import PALETA, fuente
from nucleo.procedimientos_sistemas import lineas_paso, titulo_paso
from nucleo.romanos import operar_romanos_con_pasos, romano_a_entero

OPERACIONES = {"A + B": "+", "A − B": "-", "A × B": "*", "A ÷ B": "/"}
DESCRIPCIONES = {
    "A + B": "Se convierten A y B a decimal, se suman y el resultado vuelve a romano.",
    "A − B": "La resta debe dar un número positivo: los romanos no tienen cero ni negativos.",
    "A × B": "El producto no puede superar 3999 (MMMCMXCIX).",
    "A ÷ B": "La división debe ser exacta y B distinto de cero.",
}


class VistaRomanos(ttk.Frame):
    ALTO_MINIMO = 560

    def __init__(self, padre):
        super().__init__(padre, padding=(22, 18, 22, 14))
        self.operacion = "A + B"
        self.resultado = None   # (romano, decimal, pasos)
        self.ventanas = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=40, uniform="zonas")
        self.rowconfigure(2, weight=60, uniform="zonas")
        self._construir_encabezado()
        self._construir_entrada()
        self._construir_resultados()
        self.cargar_ejemplo()

    # ---------------------------------------------------------------- construcción
    def _construir_encabezado(self):
        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        encabezado.columnconfigure(1, weight=1)
        ttk.Label(encabezado, text="Números romanos", style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
        self.etiqueta_descripcion = ttk.Label(encabezado, style="Tenue.TLabel", justify="left")
        self.etiqueta_descripcion.grid(row=0, column=1, sticky="ew", padx=(16, 12))
        acciones = ttk.Frame(encabezado)
        acciones.grid(row=0, column=2, sticky="e")
        ttk.Button(acciones, text="Ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Limpiar", command=self.limpiar).pack(side="left")
        self.selector = SelectorSegmentado(encabezado, tuple(OPERACIONES), self.cambiar_operacion)
        self.selector.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def _campo(self, padre, fila, etiqueta):
        ttk.Label(padre, text=etiqueta, style="Panel.Formula.TLabel").grid(row=fila, column=0, sticky="w",
                                                                         pady=(8 if fila else 0, 0))
        variable = tk.StringVar()
        entrada = ttk.Entry(padre, textvariable=variable, font=fuente(13, mono=True))
        entrada.grid(row=fila + 1, column=0, sticky="ew", pady=(3, 0))
        entrada.bind("<Return>", lambda _e: self.calcular())
        nota = ttk.Label(padre, style="Panel.Tenue.TLabel")
        nota.grid(row=fila + 2, column=0, sticky="w", pady=(2, 0))
        variable.trace_add("write", lambda *_: self._al_escribir())
        return variable, entrada, nota

    def _construir_entrada(self):
        cuerpo = ttk.Frame(self)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.rowconfigure(0, weight=1)
        cuerpo.columnconfigure((0, 1), weight=1, uniform="r")
        datos = tarjeta(cuerpo, padding=(14, 10), row=0, column=0, sticky="nsew", padx=(0, 12))
        datos.columnconfigure(0, weight=1)
        ttk.Label(datos, text="NÚMEROS", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.a, self.entrada_a, self.nota_a = self._campo(datos, 1, "A")
        self.b, self.entrada_b, self.nota_b = self._campo(datos, 4, "B")
        lateral = tarjeta(cuerpo, padding=(14, 10), row=0, column=1, sticky="nsew")
        lateral.columnconfigure(0, weight=1)
        lateral.rowconfigure(1, weight=1)
        ttk.Label(lateral, text="CÁLCULO", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.validacion = ttk.Label(lateral, style="Panel.Pendiente.TLabel", justify="left", wraplength=360)
        self.validacion.grid(row=1, column=0, sticky="new", pady=(8, 8))
        ttk.Label(lateral, text="Notación estándar de I a MMMCMXCIX (1 a 3999). Se calcula al escribir.",
                  style="Panel.Tenue.TLabel", wraplength=360, justify="left").grid(row=2, column=0, sticky="w",
                                                                                   pady=(0, 8))
        ttk.Button(lateral, text="Calcular", style="Panel.Accion.TButton", command=self.calcular).grid(
            row=3, column=0, sticky="ew")

    def _construir_resultados(self):
        zona = ttk.Frame(self, padding=(0, 10, 0, 0))
        zona.grid(row=2, column=0, sticky="nsew")
        zona.rowconfigure(0, weight=1)
        zona.columnconfigure(0, weight=2, minsize=240)
        zona.columnconfigure(1, weight=2)
        zona.columnconfigure(2, weight=3, minsize=320)
        marco = tarjeta(zona, row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(marco, text="RESULTADO", style="Panel.Seccion.TLabel").pack(anchor="w")
        self.estado = ttk.Label(marco, text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.estado.pack(anchor="w", pady=(6, 4))
        self.valor = ttk.Label(marco, style="Panel.Formula.TLabel", justify="left", wraplength=300,
                               font=fuente(20, "bold", mono=True))
        self.valor.pack(anchor="w")
        self.decimal = ttk.Label(marco, style="Panel.Tenue.TLabel")
        self.decimal.pack(anchor="w", pady=(2, 0))
        self.tabla = TablaPaginada(zona, "PASOS", al_elegir=self._al_elegir_paso,
                                   titulo_ventana=lambda: f"Pasos · {self.operacion}")
        self.tabla.configurar_columnas((("n", "n", 44), ("paso", "Operación", 260, "w")))
        self.tabla.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        self.panel = PanelProcedimiento(zona, self._lineas_completas,
                                        titulo_ventana=lambda: f"Procedimiento · {self.operacion}")
        self.panel.grid(row=0, column=2, sticky="nsew")

    # ---------------------------------------------------------------- estado
    def cambiar_operacion(self, operacion):
        self.operacion = operacion
        self.selector.marcar(operacion)
        self.etiqueta_descripcion.configure(text=DESCRIPCIONES[operacion])
        self.calcular(en_silencio=True)

    def _vista_previa(self, texto, nota):
        """Equivalente decimal de lo escrito; devuelve el valor o None."""
        if not texto.strip():
            nota.configure(text="", style="Panel.Tenue.TLabel")
            return None
        try:
            valor = romano_a_entero(texto)
        except ValueError as exc:
            nota.configure(text=f"✗ {exc}", style="Panel.Error.TLabel")
            return None
        nota.configure(text=f"= {valor}", style="Panel.Exito.TLabel")
        return valor

    def _al_escribir(self):
        self._vista_previa(self.a.get(), self.nota_a)
        self._vista_previa(self.b.get(), self.nota_b)
        self.calcular(en_silencio=True)

    # ---------------------------------------------------------------- cálculo
    def calcular(self, en_silencio=False):
        """En silencio (al escribir) un dato incompleto no se marca como error."""
        a, b = self.a.get().strip(), self.b.get().strip()
        if not a or not b:
            self._descartar()
            if not en_silencio:
                self.validacion.configure(text="Escribe los dos números romanos.", style="Panel.Aviso.TLabel")
            else:
                self.validacion.configure(text="Escribe A y B.", style="Panel.Pendiente.TLabel")
            return
        try:
            romano, decimal, pasos = operar_romanos_con_pasos(a, b, OPERACIONES[self.operacion])
            comprobado = romano_a_entero(romano)
        except ValueError as exc:
            self._descartar()
            self.validacion.configure(text=str(exc), style="Panel.Error.TLabel")
            return
        pasos = list(pasos) + [
            "COMPROBACIÓN. Convertir el resultado romano de nuevo a decimal debe conservar el valor:\n"
            f"{romano} = {comprobado}\n" + ("✓ La comprobación es correcta." if comprobado == decimal
                                            else "✗ La comprobación no coincide.")]
        self.resultado = (romano, decimal, tuple(pasos))
        self.estado.configure(text=f"✓ {self.operacion}", style="Panel.Exito.TLabel")
        self.valor.configure(text=romano)
        self.decimal.configure(text=f"= {decimal} en decimal")
        self.tabla.definir_filas([(i + 1, titulo_paso(p)) for i, p in enumerate(pasos)])
        self.panel.mostrar(self._lineas_completas())
        self.validacion.configure(text="Calculado. Selecciona un paso para ver su detalle.",
                                  style="Panel.Pendiente.TLabel")

    def _al_elegir_paso(self, indice):
        if self.resultado:
            self.panel.mostrar(lineas_paso(self.resultado[2][indice]))

    def _lineas_completas(self):
        if not self.resultado:
            return [("Escribe dos números romanos y elige la operación.", "normal")]
        a, b = self.a.get().strip().upper(), self.b.get().strip().upper()
        lineas = [(f"{a} {self.operacion[2]} {b} = {self.resultado[0]}  ({self.resultado[1]})", "titulo"),
                  (DESCRIPCIONES[self.operacion], "normal")]
        for paso in self.resultado[2]:
            lineas += [("", "normal")] + lineas_paso(paso)
        return lineas

    def _descartar(self):
        if not self.resultado:
            return
        self.resultado = None
        self.estado.configure(text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.valor.configure(text="")
        self.decimal.configure(text="")
        self.tabla.limpiar()
        self.panel.mostrar([])

    def cargar_ejemplo(self):
        self.a.set("XIV")
        self.b.set("VI")
        self.cambiar_operacion(self.operacion)

    def limpiar(self):
        self.a.set("")
        self.b.set("")
        self._descartar()
