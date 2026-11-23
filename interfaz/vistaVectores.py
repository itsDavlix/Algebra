"""Vista de vectores con el mismo diseño que Matrices: operación, datos, resultado y pasos.

Las componentes aceptan enteros, decimales, fracciones (1/3) y operaciones (sqrt(2), pi).
"""

import re
import tkinter as tk
from tkinter import ttk

from interfaz.campoMatematico import CampoValor
from interfaz.dibujos import admite_plano_vectores, dibujo_vectores
from interfaz.ventanaPlano import abrir_plano
from interfaz.componentes import PanelProcedimiento, SelectorSegmentado, TablaPaginada, tarjeta
from interfaz.estilos import PALETA, fuente
from nucleo.expresiones import evaluar_valor
from nucleo.procedimientos_matrices import numero
from nucleo.procedimientos_sistemas import lineas_paso, titulo_paso
from nucleo.sistemas import verificar_combinacion_lineal_con_pasos
from nucleo.vectores import (
    multiplicar_vector_escalar, norma_vector_con_pasos, producto_cruz_con_pasos, producto_punto_con_pasos,
    restar_vectores, sumar_vectores, vectores_linealmente_independientes_con_pasos,
)

OPERACIONES = ("V₁ + V₂", "V₁ − V₂", "k · V₁", "V₁ · V₂", "V₁ × V₂", "‖V₁‖", "Combinación lineal", "Independencia")
USA = {  # qué datos necesita cada operación
    "V₁ + V₂": ("v1", "v2"), "V₁ − V₂": ("v1", "v2"), "k · V₁": ("v1", "k"), "V₁ · V₂": ("v1", "v2"),
    "V₁ × V₂": ("v1", "v2"), "‖V₁‖": ("v1",), "Combinación lineal": ("v1", "conjunto"),
    "Independencia": ("conjunto",),
}
DESCRIPCIONES = {
    "V₁ + V₂": "Suma componente a componente; los vectores deben tener la misma dimensión.",
    "V₁ − V₂": "Resta componente a componente; los vectores deben tener la misma dimensión.",
    "k · V₁": "Cada componente se multiplica por el escalar k.",
    "V₁ · V₂": "Producto punto: Σ aᵢbᵢ. Se comprueba que V₁·V₂ = V₂·V₁.",
    "V₁ × V₂": "Producto cruz en R³ por cofactores; se comprueba que es ortogonal a V₁ y a V₂.",
    "‖V₁‖": "Norma euclidiana √(Σ vᵢ²), calculada con escalado para evitar desbordes.",
    "Combinación lineal": "¿b = c₁v₁ + … + cₖvₖ? Se resuelve A·c = b por Gauss-Jordan (generadores como columnas).",
    "Independencia": "El conjunto es independiente si el rango de la matriz de columnas iguala el número de vectores.",
}


def _leer(texto, nombre):
    partes = [p for p in re.split(r"[\s;]+|,\s*", str(texto).strip("()[] \n")) if p]
    if not partes:
        raise ValueError(f"Escribe {nombre}: componentes separadas por comas o espacios.")
    return [evaluar_valor(p, f"La componente {i} de {nombre}") for i, p in enumerate(partes, 1)]


def _vector_texto(vector):
    return "(" + ", ".join(numero(v) for v in vector) + ")"


class VistaVectores(ttk.Frame):
    ALTO_MINIMO = 640

    def __init__(self, padre):
        super().__init__(padre, padding=(22, 18, 22, 14))
        self.operacion = "V₁ · V₂"
        self.resultado = None   # (texto_resultado, pasos)
        self.ventanas = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=45, uniform="zonas")
        self.rowconfigure(2, weight=55, uniform="zonas")
        self._construir_encabezado()
        self._construir_entrada()
        self._construir_resultados()
        self._aplicar_operacion()

    def _construir_encabezado(self):
        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        encabezado.columnconfigure(1, weight=1)
        ttk.Label(encabezado, text="Vectores", style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
        self.etiqueta_descripcion = ttk.Label(encabezado, style="Tenue.TLabel", justify="left")
        self.etiqueta_descripcion.grid(row=0, column=1, sticky="ew", padx=(16, 12))
        acciones = ttk.Frame(encabezado)
        acciones.grid(row=0, column=2, sticky="e")
        ttk.Button(acciones, text="Ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Limpiar", command=self.limpiar).pack(side="left")
        self.selector = SelectorSegmentado(encabezado, OPERACIONES, self.cambiar_operacion)
        self.selector.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def _construir_entrada(self):
        cuerpo = ttk.Frame(self)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.rowconfigure(0, weight=1)
        cuerpo.columnconfigure((0, 1), weight=1, uniform="v")
        cuerpo.columnconfigure(2, minsize=300)
        datos = tarjeta(cuerpo, padding=(14, 10), row=0, column=0, sticky="nsew", padx=(0, 12))
        datos.columnconfigure(0, weight=1)
        ttk.Label(datos, text="VECTORES", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.etiqueta_v1 = ttk.Label(datos, text="V₁", style="Panel.Formula.TLabel")
        self.etiqueta_v1.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.v1 = tk.StringVar()
        self.entrada_v1 = ttk.Entry(datos, textvariable=self.v1, font=fuente(12, mono=True))
        self.entrada_v1.grid(row=2, column=0, sticky="ew", pady=(3, 0))
        ttk.Label(datos, text="V₂", style="Panel.Formula.TLabel").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.v2 = tk.StringVar()
        self.entrada_v2 = ttk.Entry(datos, textvariable=self.v2, font=fuente(12, mono=True))
        self.entrada_v2.grid(row=4, column=0, sticky="ew", pady=(3, 0))
        self.campo_k = CampoValor(datos, "Escalar k", "El escalar k", al_enter=self.calcular)
        self.campo_k.grid(row=5, column=0, sticky="w", pady=(8, 0))
        ttk.Label(datos, text="Componentes separadas por comas o espacios: 1, −2, 1/3",
                  style="Panel.Tenue.TLabel").grid(row=6, column=0, sticky="w", pady=(8, 0))
        for variable in (self.v1, self.v2):
            variable.trace_add("write", lambda *_: self._descartar())

        conjunto = tarjeta(cuerpo, padding=(14, 10), row=0, column=1, sticky="nsew", padx=(0, 12))
        conjunto.columnconfigure(0, weight=1)
        conjunto.rowconfigure(1, weight=1)
        ttk.Label(conjunto, text="CONJUNTO · un vector por línea", style="Panel.Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6))
        self.texto_conjunto = tk.Text(conjunto, height=4, width=20, wrap="none", font=fuente(12, mono=True),
                                      background=PALETA["campo"], foreground=PALETA["texto"],
                                      insertbackground=PALETA["acento_hover"], highlightthickness=1,
                                      highlightbackground=PALETA["borde"], highlightcolor=PALETA["acento"],
                                      relief="flat", padx=10, pady=8)
        self.texto_conjunto.colores_propios = True
        self.texto_conjunto.grid(row=1, column=0, sticky="nsew")
        self.nota_conjunto = ttk.Label(conjunto, style="Panel.Tenue.TLabel", wraplength=300, justify="left")
        self.nota_conjunto.grid(row=2, column=0, sticky="w", pady=(6, 0))

        lateral = tarjeta(cuerpo, padding=(14, 10), row=0, column=2, sticky="nsew")
        lateral.columnconfigure(0, weight=1)
        lateral.rowconfigure(1, weight=1)
        ttk.Label(lateral, text="CÁLCULO", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.validacion = ttk.Label(lateral, style="Panel.Pendiente.TLabel", justify="left", wraplength=270)
        self.validacion.grid(row=1, column=0, sticky="new", pady=(8, 8))
        ttk.Button(lateral, text="Calcular", style="Panel.Accion.TButton", command=self.calcular).grid(
            row=2, column=0, sticky="ew")
        self.boton_plano = ttk.Button(lateral, text="◇ Ver en el plano", style="Panel.TButton",
                                      command=self.ver_plano, state="disabled")
        self.boton_plano.grid(row=3, column=0, sticky="ew", pady=(6, 0))

    def _construir_resultados(self):
        zona = ttk.Frame(self, padding=(0, 10, 0, 0))
        zona.grid(row=2, column=0, sticky="nsew")
        zona.rowconfigure(0, weight=1)
        zona.columnconfigure(0, weight=2, minsize=280)
        zona.columnconfigure(1, weight=2)
        zona.columnconfigure(2, weight=3, minsize=320)
        marco = tarjeta(zona, row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(marco, text="RESULTADO", style="Panel.Seccion.TLabel").pack(anchor="w")
        self.estado = ttk.Label(marco, text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.estado.pack(anchor="w", pady=(6, 4))
        self.valor = ttk.Label(marco, style="Panel.Formula.TLabel", justify="left", wraplength=320,
                               foreground=PALETA["texto"],
                               font=fuente(14, "bold", mono=True))
        self.valor.pack(anchor="w")
        self.tabla = TablaPaginada(zona, "PASOS", al_elegir=self._al_elegir_paso,
                                   titulo_ventana=lambda: f"Pasos · {self.operacion}")
        self.tabla.configurar_columnas((("n", "n", 44), ("paso", "Operación", 280, "w")))
        self.tabla.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        self.panel = PanelProcedimiento(zona, self._lineas_completas,
                                        titulo_ventana=lambda: f"Procedimiento · {self.operacion}")
        self.panel.grid(row=0, column=2, sticky="nsew")

    # ---------------------------------------------------------------- operación
    def cambiar_operacion(self, operacion):
        self.operacion = operacion
        self._aplicar_operacion()
        self._descartar()

    def _aplicar_operacion(self):
        usa = USA[self.operacion]
        self.selector.marcar(self.operacion)
        self.etiqueta_descripcion.configure(text=DESCRIPCIONES[self.operacion])
        self.etiqueta_v1.configure(text="b (vector objetivo)" if self.operacion == "Combinación lineal" else "V₁")
        self.entrada_v1.state(["!disabled"] if "v1" in usa else ["disabled"])
        self.entrada_v2.state(["!disabled"] if "v2" in usa else ["disabled"])
        self.campo_k.habilitar("k" in usa)
        activo = "conjunto" in usa
        self.texto_conjunto.configure(state="normal" if activo else "disabled",
                                      background=PALETA["campo"] if activo else PALETA["superficie"])
        self.nota_conjunto.configure(text={"Combinación lineal": "Generadores v₁, v₂, …",
                                           "Independencia": "Vectores del conjunto a analizar"}.get(self.operacion,
                                                                                                 "No se usa en esta operación."))
        self.validacion.configure(text="Escribe los datos activos y pulsa «Calcular».", foreground=PALETA["texto_suave"])

    # ---------------------------------------------------------------- cálculo
    def _conjunto(self):
        lineas = [l for l in self.texto_conjunto.get("1.0", "end").splitlines() if l.strip()]
        if not lineas:
            raise ValueError("Escribe al menos un vector en el conjunto (uno por línea).")
        return [_leer(l, f"el vector {i}") for i, l in enumerate(lineas, 1)]

    def calcular(self):
        op = self.operacion
        k = None
        try:
            v1 = _leer(self.v1.get(), "V₁") if "v1" in USA[op] else None
            v2 = _leer(self.v2.get(), "V₂") if "v2" in USA[op] else None
            if op == "V₁ + V₂":
                valor = sumar_vectores(v1, v2)
                pasos = ["PASO 1. Sumar componente a componente:\n" + ", ".join(
                    f"{numero(a)} + ({numero(b)}) = {numero(c)}" for a, b, c in zip(v1, v2, valor))]
                texto = _vector_texto(valor)
            elif op == "V₁ − V₂":
                valor = restar_vectores(v1, v2)
                pasos = ["PASO 1. Restar componente a componente:\n" + ", ".join(
                    f"{numero(a)} − ({numero(b)}) = {numero(c)}" for a, b, c in zip(v1, v2, valor))]
                texto = _vector_texto(valor)
            elif op == "k · V₁":
                k = self.campo_k.obtener()
                valor = multiplicar_vector_escalar(v1, k)
                pasos = [f"PASO 1. Multiplicar cada componente por k = {numero(k)}:\n" + ", ".join(
                    f"{numero(k)}·({numero(a)}) = {numero(c)}" for a, c in zip(v1, valor))]
                texto = _vector_texto(valor)
            elif op == "V₁ · V₂":
                valor, pasos = producto_punto_con_pasos(v1, v2)
                texto = f"V₁ · V₂ = {numero(valor)}"
            elif op == "V₁ × V₂":
                valor, pasos = producto_cruz_con_pasos(v1, v2)
                texto = f"V₁ × V₂ = {_vector_texto(valor)}"
            elif op == "‖V₁‖":
                valor, pasos = norma_vector_con_pasos(v1)
                texto = f"‖V₁‖ = {numero(valor)}"
            elif op == "Combinación lineal":
                es, coeficientes, tipo, pasos = verificar_combinacion_lineal_con_pasos(self._conjunto(), v1)
                if es:
                    texto = "Sí es combinación lineal\n" + "\n".join(
                        f"c{i + 1} = {numero(c[0] if isinstance(c, list) else c)}" for i, c in enumerate(coeficientes))
                else:
                    texto = "No es combinación lineal"
            else:
                independientes, pasos = vectores_linealmente_independientes_con_pasos(self._conjunto())
                texto = "Linealmente independientes" if independientes else "Linealmente dependientes"
        except ValueError as exc:
            self.validacion.configure(text=str(exc), foreground=PALETA["error"])
            return
        self.resultado = (texto, tuple(pasos))
        self._dibujo = dibujo_vectores(op, v1, v2, k) if admite_plano_vectores(op, v1, v2) else None
        self.boton_plano.state(["!disabled"] if self._dibujo else ["disabled"])
        self.estado.configure(text=f"✓ {op}", style="Panel.Exito.TLabel")
        self.valor.configure(text=texto)
        self.tabla.definir_filas([(i + 1, titulo_paso(p)) for i, p in enumerate(pasos)])
        self.panel.mostrar(self._lineas_completas())
        self.validacion.configure(text="Calculado. Selecciona un paso para ver su detalle.",
                                  foreground=PALETA["texto_suave"])

    def ver_plano(self):
        """Los vectores de R² como flechas desde el origen, en ventana aparte."""
        if getattr(self, "_dibujo", None):
            abrir_plano(self, "plano", f"Plano · {self.operacion}", self._dibujo)

    def _al_elegir_paso(self, indice):
        if self.resultado:
            self.panel.mostrar(lineas_paso(self.resultado[1][indice]))

    def _lineas_completas(self):
        if not self.resultado:
            return [("Elige una operación, escribe los datos y pulsa «Calcular».", "normal")]
        lineas = [(self.operacion, "titulo"), (DESCRIPCIONES[self.operacion], "normal")]
        for paso in self.resultado[1]:
            lineas += [("", "normal")] + lineas_paso(paso)
        return lineas

    def _descartar(self):
        if not getattr(self, "resultado", None):
            return
        self.resultado = None
        self._dibujo = None
        self.boton_plano.state(["disabled"])
        self.estado.configure(text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.valor.configure(text="")
        self.tabla.limpiar()
        self.panel.mostrar([])

    def cargar_ejemplo(self):
        self.v1.set("1, 2, 3")
        self.v2.set("4, −5, 6")
        self.calcular()

    def limpiar(self):
        self.v1.set("")
        self.v2.set("")
        self.campo_k.establecer("")
        estado = str(self.texto_conjunto.cget("state"))
        self.texto_conjunto.configure(state="normal")
        self.texto_conjunto.delete("1.0", "end")
        self.texto_conjunto.configure(state=estado)
        self._descartar()
