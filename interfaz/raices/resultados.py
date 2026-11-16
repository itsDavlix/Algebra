"""Parte de la vista de raíces que valida, resuelve y muestra resultados.

Lee los parámetros, valida las condiciones del método, resuelve, compara,
llena la tabla paginada y el procedimiento.
"""

from interfaz.estilos import PALETA
from interfaz.raices import capas
from interfaz.raices.validacion import validar
from nucleo import procedimientos
from nucleo.analisis import sugerir_valores
from nucleo.biseccion import iteraciones_necesarias, resolver_biseccion
from nucleo.metodosabiertos import resolver_metodo_abierto
from nucleo.reglafalsa import resolver_reglafalsa

COLORES_NIVEL = {"pendiente": "texto_suave", "ok": "exito", "aviso": "aviso", "error": "error"}


class ResultadosMixin:
    """Requiere: metodo, funcion, campos, validacion, plano, tabla_iteraciones, panel_procedimiento."""

    # ========================================================== parámetros
    def _leer_parametros(self):
        valores = {clave: campo.obtener() for clave, campo in self.campos.items()}
        tolerancia = self.campo_tolerancia.obtener()
        iteraciones = self.campo_iteraciones.obtener()
        if not float(iteraciones).is_integer():
            raise ValueError("El máximo de iteraciones debe ser un número entero.")
        return valores, tolerancia, int(iteraciones)

    def _al_cambiar_parametros(self):
        if self.resultado is not None:
            self._descartar_resultado()
        mensaje, color = self._validar_parametros()
        self.validacion.configure(text=mensaje, foreground=color)
        if self.resultado is None:
            self.plano.definir_capas(self._capas_previas())

    def _validar_parametros(self):
        """Condiciones del método activo (ver validacion.py); devuelve (mensaje, color)."""
        mensaje, nivel = validar(
            self.metodo, self.funcion, [campo.variable.get() for campo in self.campos.values()],
            self._leer_parametros, self._derivada_en_uso(), self.segunda)
        return mensaje, PALETA[COLORES_NIVEL[nivel]]

    def _derivada_en_uso(self):
        if self.metodo != "Newton-Raphson":
            return None
        if self._texto_derivada().strip():
            return self.campo_derivada.expresion
        return self.derivada

    def _valores_actuales(self):
        valores = {}
        for clave, campo in self.campos.items():
            try:
                valores[clave] = campo.obtener()
            except ValueError:
                pass
        return valores

    def _capas_previas(self):
        return capas.capas_previas(self.metodo, self.funcion, self._valores_actuales())

    def _capas_resultado(self):
        return capas.capas_resultado(self.metodo, self.resultado, self.funcion, self.iteracion_elegida)

    def _puntos_del_metodo(self):
        return capas.puntos_del_metodo(self.metodo, self.resultado)

    def _puntos_relevantes(self):
        return capas.puntos_relevantes(self.metodo, self.resultado, self.funcion)

    def sugerir(self):
        """Toma la raíz elegida (o la más cercana al centro) y propone valores justificados."""
        if self.funcion is None:
            self.validacion.configure(text="Primero escribe una función válida.", foreground=PALETA["error"])
            return
        raices = [p for p in self.notables if p.tipo == "raiz"]
        if not raices:
            self.validacion.configure(
                text="No hay raíces visibles en la gráfica. Aleja la vista (rueda o −) para buscar más.",
                foreground=PALETA["aviso"])
            return
        elegido = self.tabla_notables.selection()
        punto = self.notables_por_clave.get(elegido[0]) if elegido else None
        x0, x1, _, _ = self.plano.vista
        referencia = punto.x if punto else (x0 + x1) / 2
        raiz = punto if punto and punto.tipo == "raiz" else min(raices, key=lambda r: abs(r.x - referencia))
        sugerencia = sugerir_valores(self.metodo, self.funcion, raiz, self._derivada_en_uso(), self.segunda)
        if not sugerencia.valores:
            self.validacion.configure(text=sugerencia.explicacion, foreground=PALETA["aviso"])
            return
        for clave, valor in sugerencia.valores.items():
            self.campos[clave].establecer(valor)
        if self.metodo == "Bisección":
            a, b = (self.campos[c].obtener() for c in ("a", "b"))
            tolerancia = self.campo_tolerancia.obtener()
            # Al menos las iteraciones teóricas; 100 deja margen a Regula Falsi al comparar.
            self.campo_iteraciones.establecer(str(max(100, iteraciones_necesarias(a, b, tolerancia) + 1)))
        clave_raiz = next((c for c, p in self.notables_por_clave.items() if p is raiz), None)
        self.explicacion.configure(text=sugerencia.explicacion)
        if clave_raiz and self.tabla_notables.selection() != (clave_raiz,):
            self._explicacion_pendiente = sugerencia.explicacion
            self.tabla_notables.selection_set(clave_raiz)

    # ============================================================ resolver
    def resolver(self):
        mensaje, color = self._validar_parametros()
        if color == PALETA["error"] or self.funcion is None:
            self.validacion.configure(text=mensaje, foreground=PALETA["error"])
            return
        if not all(campo.variable.get().strip() for campo in self.campos.values()):
            self.validacion.configure(text=mensaje, foreground=PALETA["error"])
            return
        try:
            valores, tolerancia, iteraciones = self._leer_parametros()
            resultado = self._resolver_con(self.metodo, valores, tolerancia, iteraciones)
        except ValueError as exc:
            self._descartar_resultado()
            self.validacion.configure(text=str(exc), foreground=PALETA["error"])
            return
        self.resultado = resultado
        self.resultados_por_metodo[self.metodo] = resultado
        self.comparacion = None
        self.iteracion_elegida = None
        self._mostrar_resultado()

    def _resolver_con(self, metodo, valores, tolerancia, iteraciones):
        texto = self.campo_funcion.obtener()
        if metodo == "Bisección":
            return resolver_biseccion(texto, valores["a"], valores["b"], tolerancia, iteraciones)
        if metodo == "Regula Falsi":
            return resolver_reglafalsa(texto, valores["a"], valores["b"], tolerancia, iteraciones)
        if metodo == "Newton-Raphson":
            return resolver_metodo_abierto(texto, metodo, valores["x0"], derivada=self._texto_derivada(),
                                           tolerancia=tolerancia, max_iteraciones=iteraciones)
        return resolver_metodo_abierto(texto, metodo, valores["x0"], valores["x1"],
                                       tolerancia=tolerancia, max_iteraciones=iteraciones)

    def _descartar_resultado(self):
        """Los resultados dejan de valer si cambian la función o los valores."""
        if (getattr(self, "resultado", None) is None and not self.resultados_por_metodo
                and self.comparacion is None and hasattr(self, "tabla")):
            return
        self.resultados_por_metodo = {}
        self.comparacion = None
        self.resultado = None
        self._reiniciar_resultado_ui()

    def _reiniciar_resultado_ui(self):
        self.iteracion_elegida = None
        self.estado.configure(text="Sin calcular", style="Panel.Pendiente.TLabel")
        self.valor.configure(text="x ≈ —")
        self.datos.configure(text="")
        self.motivo.configure(text="")
        self.tabla_iteraciones.limpiar()
        self._mostrar_resumen_vacio()
        self._actualizar_puntos_grafica()
        self.plano.definir_capas(self._capas_previas())

    def _mostrar_resultado(self, encuadrar=True):
        r = self.resultado
        if r.convergio:
            self.estado.configure(text="✓ Convergencia alcanzada", style="Panel.Exito.TLabel")
        else:
            self.estado.configure(text="✗ Sin convergencia", style="Panel.Error.TLabel")
        self.valor.configure(text=f"x ≈ {r.raiz:.10g}".replace("-", "−"))
        error = "—" if r.error is None else f"{r.error:.3g}"
        lineas = [f"residuo |f(x)| = {abs(r.valor_funcion):.3g}", f"error = {error}", f"iteraciones = {len(r.iteraciones)}"]
        if self.metodo == "Bisección":
            lineas.append(f"teóricas = {r.iteraciones_teoricas}")
        self.datos.configure(text="\n".join(lineas).replace("-", "−"))
        motivo = r.motivo
        if getattr(r, "advertencia", ""):
            motivo += "\n\n⚠ " + r.advertencia
        self.motivo.configure(text="Motivo de parada: " + motivo)
        self.validacion.configure(text="Resuelto. Selecciona una iteración para verla en la gráfica.",
                                  foreground=PALETA["texto_suave"])
        if encuadrar and not self._vista_manual:
            self._encuadrar(self._puntos_relevantes())
        self._llenar_tabla()
        self._mostrar_lineas(procedimientos.resumen(self.metodo, r))
        self._actualizar_puntos_grafica()
        self.plano.definir_capas(self._capas_resultado())

    # ============================================================ tabla y procedimiento
    def _llenar_tabla(self):
        r = self.resultado
        total = len(r.iteraciones)
        self.tabla_iteraciones.definir_filas(
            [procedimientos.fila(self.metodo, paso) for paso in r.iteraciones],
            lambda i: (["final_ok" if r.convergio else "final_no"] if i == total - 1 else []))

    def _al_elegir_iteracion(self, indice):
        if self.resultado is None:
            return
        self.iteracion_elegida = indice
        self._mostrar_lineas(procedimientos.detalle(self.metodo, self.resultado, indice))
        self.plano.definir_capas(self._capas_resultado())
        self.plano.seleccionar(f"i{indice}", centrar=True)

    def _mostrar_lineas(self, lineas):
        self.panel_procedimiento.mostrar(lineas)

    def _lineas_completas(self):
        """Comparación (si la hay), resumen y desarrollo de todas las iteraciones."""
        lineas = list(self.comparacion or [])
        if self.resultado is None:
            return lineas or self._lineas_resumen_vacio()
        if lineas:
            lineas.append(("", "normal"))
        lineas += procedimientos.resumen(self.metodo, self.resultado)[:-2]
        for indice in range(len(self.resultado.iteraciones)):
            lineas.append(("", "normal"))
            lineas += procedimientos.detalle(self.metodo, self.resultado, indice)
        return lineas

    def abrir_tabla_completa(self):
        if self.resultado is None:
            self.validacion.configure(text="Resuelve primero para ver las iteraciones.", foreground=PALETA["aviso"])
            return
        self.tabla_iteraciones.abrir_completa()
        self.ventanas["tabla"] = self.tabla_iteraciones.ventanas["tabla"]

    def abrir_procedimiento_completo(self):
        self.panel_procedimiento.abrir_completo()
        self.ventanas["procedimiento"] = self.panel_procedimiento.ventanas["procedimiento"]

    def _mostrar_resumen_vacio(self):
        self._mostrar_lineas(self._lineas_resumen_vacio())

    def _lineas_resumen_vacio(self):
        return ([
            ("Cómo usar esta vista", "titulo"),
            ("1. Escribe f(x): la gráfica y sus puntos notables aparecen al instante.", "normal"),
            ("2. Elige los valores iniciales: haz clic en la gráfica para colocarlos, pulsa «Sugerir "
             "valores» (usa la raíz elegida en la lista) o escríbelos.", "normal"),
            ("3. Revisa la validación del método y pulsa «Resolver» o Enter.", "normal"),
            ("4. Recorre la tabla por páginas; cada fila muestra aquí su desarrollo y se "
             "resalta en la gráfica.", "normal"),
            ("", "normal"),
            ("Fórmula", "titulo"),
            (procedimientos.FORMULAS[self.metodo], "formula"),
        ])
