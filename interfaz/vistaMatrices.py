"""Vista de matrices: determinante, inversa (con justificación y verificación), transpuesta,
rango y operaciones entre matrices, con el mismo diseño que las demás vistas.

Las entradas aceptan enteros, decimales, fracciones (1/3) y operaciones (sqrt(2), pi).
"""

import tkinter as tk
from tkinter import ttk

from interfaz.campoMatematico import CampoValor
from interfaz.componentes import ajustar_letra_de_texto, MenuEjercicios, PanelProcedimiento, SelectorSegmentado, TablaPaginada, tarjeta
from interfaz.estilos import PALETA, fuente
from nucleo.determinantes import recomendar_metodo
from nucleo.ejercicios import MATRICES_BANCO, ejercicios_de
from nucleo.procedimientos_matrices import BINARIAS, OPERACIONES, calcular, matriz_texto, numero
from nucleo.procedimientos_sistemas import lineas_paso, titulo_paso
from nucleo.sistemas_texto import leer_matriz_texto

DESCRIPCIONES = {
    "det(A)": "Cofactores (desarrollo por la fila con más ceros) o LU con pivoteo parcial; se comprueba con el otro método.",
    "A⁻¹": "Se justifica con det(A) ≠ 0, se reduce [A | I] → [I | A⁻¹] y se verifica A·A⁻¹ = I.",
    "Aᵀ": "Las filas de A pasan a ser las columnas de Aᵀ; se comprueba que (Aᵀ)ᵀ = A.",
    "rango(A)": "Número de pivotes tras la eliminación; se comprueba rango(A) = rango(Aᵀ).",
    "A + B": "Suma entrada por entrada; A y B deben tener el mismo tamaño.",
    "A − B": "Resta entrada por entrada; A y B deben tener el mismo tamaño.",
    "A · B": "cᵢⱼ = Σₖ aᵢₖ bₖⱼ; las columnas de A deben ser tantas como las filas de B.",
    "k · A": "Cada entrada de A se multiplica por el escalar k.",
}


def _area_texto(padre, alto=5):
    texto = tk.Text(padre, height=alto, width=22, wrap="none", font=fuente(12, mono=True),
                    background=PALETA["campo"], foreground=PALETA["texto"], insertbackground=PALETA["acento_hover"],
                    highlightthickness=1, highlightbackground=PALETA["borde"], highlightcolor=PALETA["acento"],
                    relief="flat", padx=10, pady=8, undo=True)
    texto.colores_propios = True
    return texto


class VistaMatrices(ttk.Frame):
    ALTO_MINIMO = 680

    def __init__(self, padre):
        super().__init__(padre, padding=(22, 18, 22, 14))
        self.operacion = "A⁻¹"
        self.metodo_det = "lu"
        self.resultado = None
        self.fracciones = tk.BooleanVar(value=True)
        self.ventanas = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=48, uniform="zonas")
        self.rowconfigure(2, weight=52, uniform="zonas")
        self._construir_encabezado()
        self._construir_entrada()
        self._construir_resultados()
        self._aplicar_operacion()

    # ================================================================ diseño
    def _construir_encabezado(self):
        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        encabezado.columnconfigure(1, weight=1)
        ttk.Label(encabezado, text="Matrices", style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
        self.etiqueta_descripcion = ttk.Label(encabezado, style="Tenue.TLabel", justify="left")
        self.etiqueta_descripcion.grid(row=0, column=1, sticky="ew", padx=(16, 12))
        encabezado.bind("<Configure>", lambda e: self.etiqueta_descripcion.configure(wraplength=max(200, e.width - 640)))
        acciones = ttk.Frame(encabezado)
        acciones.grid(row=0, column=2, sticky="e")
        MenuEjercicios(acciones, ejercicios_de(("Inversa", "Determinante")), self.cargar_ejercicio).pack(
            side="left", padx=(0, 6))
        ttk.Button(acciones, text="Ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Ver inversa", command=self.mostrar_inversa).pack(side="left", padx=(0, 6))
        ttk.Button(acciones, text="Limpiar", command=self.limpiar).pack(side="left")
        self.selector = SelectorSegmentado(encabezado, OPERACIONES, self.cambiar_operacion)
        self.selector.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def _construir_entrada(self):
        cuerpo = ttk.Frame(self)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.rowconfigure(0, weight=1)
        cuerpo.columnconfigure((0, 1), weight=1, uniform="matrices")
        cuerpo.columnconfigure(2, minsize=330)
        self.textos = {}
        self.estados = {}
        for columna, nombre in enumerate(("A", "B")):
            marco = tarjeta(cuerpo, padding=(14, 10), row=0, column=columna, sticky="nsew", padx=(0, 12))
            marco.columnconfigure(0, weight=1)
            marco.rowconfigure(1, weight=1)
            ttk.Label(marco, text=f"MATRIZ {nombre} · una fila por línea", style="Panel.Seccion.TLabel").grid(
                row=0, column=0, sticky="w", pady=(0, 6))
            texto = _area_texto(marco)
            texto.grid(row=1, column=0, sticky="nsew")
            texto.bind("<KeyRelease>", lambda _e, n=nombre: self._validar_entrada(n))
            estado = ttk.Label(marco, style="Panel.Ayuda.TLabel", justify="left", wraplength=300)
            estado.grid(row=2, column=0, sticky="ew", pady=(6, 0))
            self.textos[nombre], self.estados[nombre] = texto, estado
            if nombre == "B":
                self.marco_b = marco

        lateral = tarjeta(cuerpo, padding=(14, 10), row=0, column=2, sticky="nsew")
        lateral.columnconfigure(0, weight=1)
        ttk.Label(lateral, text="OPCIONES", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.marco_det = ttk.Frame(lateral, style="Panel.TFrame")
        self.marco_det.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Label(self.marco_det, text="Método del determinante", style="Panel.Formula.TLabel").pack(anchor="w")
        self.selector_det = SelectorSegmentado(self.marco_det, ("Cofactores", "LU"), self._cambiar_metodo_det)
        self.selector_det.pack(anchor="w", pady=(4, 0))
        self.recomendacion = ttk.Label(self.marco_det, style="Panel.Tenue.TLabel", justify="left", wraplength=300)
        self.recomendacion.pack(anchor="w", pady=(4, 0))
        self.campo_k = CampoValor(lateral, "Escalar k", "El escalar k", al_enter=self.calcular)
        self.campo_k.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Checkbutton(lateral, text="Mostrar fracciones exactas", variable=self.fracciones,
                        command=self._refrescar, style="Panel.TCheckbutton").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.validacion = ttk.Label(lateral, style="Panel.Pendiente.TLabel", justify="left", wraplength=300)
        self.validacion.grid(row=4, column=0, sticky="new", pady=(10, 8))
        lateral.rowconfigure(4, weight=1)
        ttk.Button(lateral, text="Calcular", style="Panel.Accion.TButton", command=self.calcular).grid(
            row=5, column=0, sticky="ew")

    def _construir_resultados(self):
        zona = ttk.Frame(self, padding=(0, 10, 0, 0))
        zona.grid(row=2, column=0, sticky="nsew")
        zona.rowconfigure(0, weight=1)
        zona.columnconfigure(0, weight=3, minsize=330)
        zona.columnconfigure(1, weight=2)
        zona.columnconfigure(2, weight=3, minsize=320)
        marco = tarjeta(zona, row=0, column=0, sticky="nsew", padx=(0, 12))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(2, weight=1)
        ttk.Label(marco, text="RESULTADO", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.estado = ttk.Label(marco, text="Sin calcular", style="Panel.Pendiente.TLabel", justify="left",
                                wraplength=320)
        self.estado.grid(row=1, column=0, sticky="w", pady=(6, 4))
        self.valor = tk.Text(marco, height=6, width=30, wrap="none", state="disabled", font=fuente(12, mono=True),
                             background=PALETA["superficie"], foreground=PALETA["texto"], borderwidth=0,
                             highlightthickness=0, cursor="arrow")
        self.valor.colores_propios = True
        self.valor.grid(row=2, column=0, sticky="nsew")
        self.valor.bind("<Configure>", lambda _e: ajustar_letra_de_texto(self.valor, 12, 7, permitir_partir=False), add="+")
        self.tabla = TablaPaginada(zona, "PASOS", al_elegir=self._al_elegir_paso,
                                   titulo_ventana=lambda: f"Pasos · {self.operacion}")
        self.tabla.configurar_columnas((("n", "n", 44), ("paso", "Operación", 300, "w")))
        self.tabla.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        self.panel = PanelProcedimiento(zona, self._lineas_completas,
                                        titulo_ventana=lambda: f"Procedimiento · {self.operacion}")
        self.panel.grid(row=0, column=2, sticky="nsew")

    # ================================================================ operación
    def _aplicar_operacion(self):
        self.selector.marcar(self.operacion)
        self.etiqueta_descripcion.configure(text=DESCRIPCIONES[self.operacion])
        binaria = self.operacion in BINARIAS
        self.textos["B"].configure(state="normal" if binaria else "disabled",
                                   background=PALETA["campo"] if binaria else PALETA["superficie"])
        self.estados["B"].configure(text="" if binaria else "No se usa en esta operación.",
                                    foreground=PALETA["texto_tenue"])
        if self.operacion == "det(A)":
            self.marco_det.grid()
        else:
            self.marco_det.grid_remove()
        if self.operacion == "k · A":
            self.campo_k.grid()
        else:
            self.campo_k.grid_remove()
        self.selector_det.marcar("Cofactores" if self.metodo_det == "cofactores" else "LU")
        self._validar_entrada("A")

    def cambiar_operacion(self, operacion):
        self.operacion = operacion
        self._aplicar_operacion()
        self._descartar()

    def _cambiar_metodo_det(self, nombre):
        self.metodo_det = "cofactores" if nombre == "Cofactores" else "lu"
        self.selector_det.marcar(nombre)
        self._descartar()

    # ================================================================ entrada
    def _leer(self, nombre):
        return leer_matriz_texto(self.textos[nombre].get("1.0", "end"), nombre)

    def _validar_entrada(self, nombre):
        self._descartar()
        texto = self.textos[nombre].get("1.0", "end").strip()
        if nombre == "B" and self.operacion not in BINARIAS:
            return
        if not texto:
            self.estados[nombre].configure(text="Escribe la matriz: valores separados por espacios.",
                                           foreground=PALETA["texto_suave"])
            return
        try:
            matriz = self._leer(nombre)
        except ValueError as exc:
            self.estados[nombre].configure(text=f"✗ {exc}", foreground=PALETA["error"])
            return
        filas, columnas = len(matriz), len(matriz[0])
        self.estados[nombre].configure(text=f"✓ {nombre} es {filas}×{columnas}" + (" (cuadrada)" if filas == columnas else ""),
                                       foreground=PALETA["exito"])
        if nombre == "A" and filas == columnas:
            _, motivo = recomendar_metodo(matriz)
            self.recomendacion.configure(text=motivo)

    # ================================================================ calcular
    def calcular(self):
        try:
            A = self._leer("A")
            B = self._leer("B") if self.operacion in BINARIAS else None
            k = self.campo_k.obtener() if self.operacion == "k · A" else None
            resultado = calcular(self.operacion, A, B, k, self.metodo_det)
        except ValueError as exc:
            self.validacion.configure(text=str(exc), foreground=PALETA["error"])
            return
        self.resultado = resultado
        self.validacion.configure(text="Calculado. Selecciona un paso para ver su detalle.",
                                  foreground=PALETA["texto_suave"])
        self._refrescar()

    def _refrescar(self):
        r = self.resultado
        if r is None:
            return
        fr = self.fracciones.get()
        if r.operacion == "A⁻¹" and r.valor is None:
            self.estado.configure(text=f"✗ det(A) = {numero(r.determinante)}: A es singular, no tiene inversa.",
                                  style="Panel.Error.TLabel")
            texto = ""
        elif r.operacion == "A⁻¹":
            self.estado.configure(text=f"✓ det(A) = {numero(r.determinante)} ≠ 0 → A es invertible",
                                  style="Panel.Exito.TLabel")
            error = r.datos.get("error", 0)
            texto = "A⁻¹ =\n" + matriz_texto(r.valor, fr) + f"\n\nA·A⁻¹ = I  (error máx. {error:.1e})"
        elif r.es_matriz:
            self.estado.configure(text=f"✓ {r.operacion}", style="Panel.Exito.TLabel")
            texto = f"{r.operacion} =\n" + matriz_texto(r.valor, fr)
        else:
            self.estado.configure(text=f"✓ {r.operacion} calculado", style="Panel.Exito.TLabel")
            texto = f"{r.operacion} = {numero(r.valor, fr)}"
        self.valor.configure(state="normal")
        self.valor.delete("1.0", "end")
        self.valor.insert("1.0", texto)
        self.valor.configure(state="disabled")
        ajustar_letra_de_texto(self.valor, 12, 7, permitir_partir=False)    # A⁻¹ con fracciones: que se vea completa
        self.tabla.definir_filas([(i + 1, titulo_paso(p)) for i, p in enumerate(r.pasos)])
        self.panel.mostrar(self._resumen())

    def _resumen(self):
        r = self.resultado
        lineas = [(f"{r.operacion}", "titulo"), (DESCRIPCIONES[r.operacion], "normal"), ("", "normal")]
        lineas += list(r.verificacion)
        lineas += [("", "normal"), ("Selecciona un paso de la tabla para ver su desarrollo.", "tenue")]
        return lineas

    def _al_elegir_paso(self, indice):
        if self.resultado is not None:
            self.panel.mostrar(lineas_paso(self.resultado.pasos[indice]))

    def _lineas_completas(self):
        if self.resultado is None:
            return [("Calcula una operación para ver su procedimiento.", "normal")]
        lineas = self._resumen()[:-2]
        for paso in self.resultado.pasos:
            lineas += [("", "normal")] + lineas_paso(paso)
        return lineas

    def _descartar(self):
        if self.resultado is None:
            return
        self.resultado = None
        self.estado.configure(text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.valor.configure(state="normal")
        self.valor.delete("1.0", "end")
        self.valor.configure(state="disabled")
        self.tabla.limpiar()
        self.panel.mostrar([])

    # ================================================================ acciones
    def mostrar_inversa(self):
        """Selecciona la inversa y la calcula usando la matriz A actual."""
        self.cambiar_operacion("A⁻¹")
        self.calcular()

    def _escribir(self, nombre, texto):
        caja = self.textos[nombre]
        estado = str(caja.cget("state"))
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state=estado)
        self._validar_entrada(nombre)

    def cargar_ejercicio(self, ejercicio):
        self.cambiar_operacion("A⁻¹")
        self._escribir("A", ejercicio.datos["matriz"])
        self.calcular()
        self.validacion.configure(text=f"{ejercicio.dificultad} · {ejercicio.fuente}. {ejercicio.justificacion}",
                                  foreground=PALETA["exito"])

    def cargar_ejemplo(self):
        filas, _ = MATRICES_BANCO[2]
        self._escribir("A", "\n".join(" ".join(str(v) for v in fila) for fila in filas))
        self.calcular()

    def limpiar(self):
        for nombre in ("A", "B"):
            self._escribir(nombre, "")
        self._descartar()
