"""Vista de sistemas lineales A·X = B: Gauss-Jordan, Jacobi y Gauss-Seidel.

Flujo, como en la clase: ① escribir el sistema (se muestra su forma matricial)
→ análisis previo (det(A), dominancia diagonal, ρ(T)) → ② parámetros →
resolver → resultado verificado, tabla paginada y paso a paso.
"""

import tkinter as tk
from tkinter import ttk

from interfaz.campoMatematico import CampoValor
from interfaz.componentes import (
    MenuEjercicios, PanelProcedimiento, SelectorSegmentado, TablaPaginada, tarjeta,
)
from interfaz.estilos import PALETA, fuente
from interfaz.motorGrafica import PlanoCartesiano
from interfaz.sistemas import convergencia
from nucleo import procedimientos_sistemas as ps
from nucleo.determinantes import determinante
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
        self.vista_previa = ttk.Label(entrada, style="Panel.Formula.TLabel", justify="left")
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
        ttk.Label(cabecera, text="CONVERGENCIA", style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        self.selector_grafica = SelectorSegmentado(cabecera, ("Componentes", "Error log₁₀"), self._cambiar_grafica)
        self.selector_grafica.grid(row=0, column=1)
        self.selector_grafica.marcar(self.modo_grafica)
        self.plano = PlanoCartesiano(grafica, height=160)
        self.plano.grid(row=1, column=0, sticky="nsew")
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
        self.validacion = ttk.Label(lateral, style="Panel.Pendiente.TLabel", justify="left", wraplength=300)
        self.validacion.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        lateral.rowconfigure(3, weight=1)
        botones = ttk.Frame(lateral, style="Panel.TFrame")
        botones.grid(row=4, column=0, columnspan=3, sticky="ew")
        botones.columnconfigure((0, 1), weight=1)
        self.boton_reordenar = ttk.Button(botones, text="Reordenar filas", style="Panel.TButton",
                                          command=self.reordenar)
        self.boton_reordenar.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(botones, text="Resolver", style="Panel.Accion.TButton", command=self.resolver).grid(
            row=0, column=1, sticky="ew")

    def _construir_resultados(self):
        zona = ttk.Frame(self, padding=(0, 10, 0, 0))
        zona.grid(row=2, column=0, sticky="nsew")
        zona.rowconfigure(0, weight=1)
        zona.columnconfigure(0, minsize=250)
        zona.columnconfigure(1, weight=3)
        zona.columnconfigure(2, weight=2, minsize=320)
        tarjeta_resultado = tarjeta(zona, row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(tarjeta_resultado, text="RESULTADO", style="Panel.Seccion.TLabel").pack(anchor="w")
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
        """Lee el sistema y muestra su forma matricial, det(A), dominancia y ρ(T)."""
        self._programado = None
        self._descartar()
        texto = self.obtener_texto()
        if not texto:
            self.variables, self.A, self.b = (), None, None
            self.vista_previa.configure(text="")
            self.estado_entrada.configure(text="Escribe el sistema o carga un ejercicio.", foreground=PALETA["texto_suave"])
            self.analisis.configure(text="")
            self._validar("Paso ①: escribe el sistema a la izquierda.", "pendiente")
            return
        try:
            variables, A, b = leer_sistema(texto)
        except ValueError as exc:
            self.variables, self.A, self.b = (), None, None
            self.vista_previa.configure(text="")
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
        self.vista_previa.configure(text=self._matriz_aumentada())
        if self.metodo in ITERATIVOS:
            self.tabla.configurar_columnas(ps.columnas_iterativas(self.variables))
        self._mostrar_analisis()

    def _matriz_aumentada(self):
        ancho = max(len(ps.coef(v)) for fila in self.A for v in fila + [0])
        ancho_b = max(len(ps.coef(v)) for v in self.b)
        return "\n".join("[ " + " ".join(ps.coef(v).replace("-", "−").rjust(ancho) for v in fila)
                         + " | " + ps.coef(bi).replace("-", "−").rjust(ancho_b) + " ]"
                         for fila, bi in zip(self.A, self.b))

    def _mostrar_analisis(self):
        A, n, m = self.A, len(self.A), len(self.variables)
        lineas = []
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
        filas = dominancia_diagonal(A)
        marcas = " ".join(f"F{f.fila}{'✓' if f.cumple else '✗'}" for f in filas)
        dominante = all(f.cumple for f in filas)
        lineas.append(f"Dominancia diagonal: {marcas}")
        if any(A[i][i] == 0 for i in range(n)):
            self.analisis.configure(text="\n".join(lineas))
            return self._validar("Hay ceros en la diagonal: no se puede despejar. Pulsa «Reordenar filas».", "error")
        rho = radio_espectral(matriz_iteracion(A, self.metodo))
        lineas.append(f"ρ(T_{'J' if self.metodo == 'Jacobi' else 'GS'}) ≈ {rho:.4f}  {'< 1 ✓' if rho < 1 else '≥ 1 ✗'}")
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
            return ps.resolver_directo(self.A, self.b, self.variables)
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
        self.valor.configure(text="\n".join(f"{nombre_bonito(v)} = {ps.g(x, 10)}"
                                            for v, x in zip(self.variables, solucion)) or "—")
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

    def _dibujar_grafica(self):
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
