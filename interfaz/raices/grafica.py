"""Parte de la vista de raíces que maneja la función y el plano cartesiano.

Encuadre automático, puntos notables, clic para colocar valores, derivada
automática o manual y modo expandido.
"""

import math

from interfaz.componentes import numero_corto
from interfaz.estilos import PALETA
from interfaz.motorGrafica import PuntoGrafico
from interfaz.raices.configuracion import ESTILO_PUNTO, ETIQUETA_CORTA, NOMBRE_PARAMETRO, evaluar
from nucleo.analisis import puntos_notables


class GraficaMixin:
    """Requiere: plano, campo_funcion, campo_derivada, campos, tabla_notables, explicacion."""

    # ========================================================= función y vista
    def _al_cambiar_funcion(self, expresion):
        anterior = self.funcion
        self.funcion = expresion
        self.derivada = self.segunda = None
        if expresion is not None:
            try:
                self.derivada = expresion.derivada()
                self.segunda = self.derivada.derivada()
            except ValueError:
                self.derivada = self.segunda = None
        self._descartar_resultado()
        self._habilitar_parametros(expresion is not None)
        self.explicacion.configure(
            text="Haz clic en un punto de la lista o de la gráfica para centrarlo y ver cómo se obtuvo."
            if expresion is not None else "Escribe una función para ver sus raíces, extremos e inflexiones.")
        self.plano.definir_funcion(expresion)
        if expresion is None:
            self.notables = []
            self._actualizar_notables()
        elif anterior is None or not self._vista_manual:
            self._encuadrar_funcion()
        else:
            self._recalcular_notables()
        self._actualizar_derivada_mostrada()
        self._al_cambiar_parametros()

    def _habilitar_parametros(self, activo):
        """Paso ②: los valores iniciales se eligen después de ver la gráfica."""
        for campo in (*self._todos_los_campos.values(), self.campo_tolerancia, self.campo_iteraciones):
            campo.habilitar(activo)
        for boton in (self.boton_sugerir, self.boton_resolver):
            boton.state(["!disabled"] if activo else ["disabled"])

    def _al_clic_plano(self, x, _y):
        """Coloca el valor inicial donde se hizo clic (a y b, o x₀ y x₁, alternando)."""
        if self.funcion is None or self.expandido:
            return
        claves = list(self.campos)
        clave = claves[self._clics % len(claves)]
        self._clics += 1
        valor = self.plano.redondear_a_pixel(x)
        self.campos[clave].establecer(valor)
        if {"a", "b"} <= set(claves) and clave == "b":
            try:
                a, b = self.campos["a"].obtener(), self.campos["b"].obtener()
            except ValueError:
                a = b = None
            if a is not None and a > b:
                texto_a, texto_b = self.campos["a"].variable.get(), self.campos["b"].variable.get()
                self.campos["a"].establecer(texto_b)
                self.campos["b"].establecer(texto_a)
        nombre = NOMBRE_PARAMETRO[clave]
        siguiente = claves[self._clics % len(claves)] if len(claves) > 1 else None
        texto = f"{nombre} = {valor} colocado desde la gráfica."
        if siguiente:
            texto += f" El próximo clic colocará {NOMBRE_PARAMETRO[siguiente]}."
        self.explicacion.configure(text=texto)

    def _al_cambiar_derivada(self, _expresion):
        if self._sincronizando_derivada:
            return
        self._descartar_resultado()
        self._actualizar_derivada_mostrada()
        self._al_cambiar_parametros()

    def _alternar_derivada(self, automatica=None):
        """Cambia entre derivada automática (solo lectura) y escrita a mano."""
        self.derivada_automatica = (not self.derivada_automatica) if automatica is None else automatica
        if self.derivada_automatica:
            self.boton_derivada.configure(text="✎ Editar")
        else:
            self.boton_derivada.configure(text="↺ Automática")
            self.campo_derivada.entrada.state(["!readonly"])
            self.campo_derivada.focus_set()
            self.campo_derivada.entrada.icursor("end")
        self._descartar_resultado()
        self._actualizar_derivada_mostrada()
        self._al_cambiar_parametros()

    def _actualizar_derivada_mostrada(self):
        if self.campo_derivada is None:
            return
        if not self.derivada_automatica:
            self.campo_derivada.entrada.state(["!readonly"])
            if not self.campo_derivada.obtener().strip():
                self.campo_derivada.mostrar_nota("Escribe f′(x); se comparará con la pendiente real de f.")
            return
        texto = self.derivada.bonito if self.derivada is not None else ""
        self._sincronizando_derivada = True
        try:
            self.campo_derivada.entrada.state(["!readonly"])
            self.campo_derivada.establecer(texto)
            self.campo_derivada.entrada.state(["readonly"])
        finally:
            self._sincronizando_derivada = False
        if self.derivada is not None:
            self.campo_derivada.mostrar_nota("✓ Automática: calculada con las reglas de derivación.",
                                             PALETA["exito"])
        else:
            self.campo_derivada.mostrar_nota("Se calculará al escribir f(x).", PALETA["texto_suave"])

    def _texto_derivada(self):
        """Lo que recibe Newton: vacío en modo automático (lo deriva el núcleo)."""
        if self.campo_derivada is None or self.derivada_automatica:
            return ""
        return self.campo_derivada.obtener()

    def _encuadrar_funcion(self):
        """Vista inicial: abarca los puntos notables cercanos al origen."""
        notables = puntos_notables(self.funcion, -10, 10, self.derivada, self.segunda)
        puntos = [(p.x, p.y) for p in notables]
        self._encuadrar(puntos or [(-5.0, 0.0), (5.0, 0.0)])
        self._vista_manual = False
        self._recalcular_notables()

    def _encuadrar(self, puntos):
        """Encuadra los puntos dados (x, y) más el origen, con margen.

        El alto se toma de esos puntos y de la curva en la zona central
        (percentiles 10–90 %), para que las colas no aplasten la gráfica.
        """
        xs = [x for x, _ in puntos] + [0.0]
        x0, x1 = min(xs), max(xs)
        margen = max(1.0, (x1 - x0) * 0.25)
        x0, x1 = x0 - margen, x1 + margen
        ys = [y for _, y in puntos] + [0.0]
        centro0, centro1 = min(xs), max(xs)
        if centro1 > centro0:
            valores = sorted(v for v in (evaluar(self.funcion, centro0 + (centro1 - centro0) * i / 80)
                                         for i in range(81)) if v is not None)
            if valores:
                # Percentiles 20–80 %: una asíntota (p. ej. e^(1/x) cerca de 0) no aplasta la curva.
                ys += [valores[len(valores) // 5], valores[(4 * len(valores)) // 5]]
        y0, y1 = min(ys), max(ys)
        alto_minimo = (x1 - x0) * 0.25
        if y1 - y0 < alto_minimo:
            centro = (y0 + y1) / 2
            y0, y1 = centro - alto_minimo / 2, centro + alto_minimo / 2
        margen_y = (y1 - y0) * 0.18
        y0, y1 = y0 - margen_y, y1 + margen_y
        self._ajustando_vista = True
        self.plano.encuadrar(x0, x1, y0, y1)
        self._ajustando_vista = False

    def _al_cambiar_vista(self, vista):
        # El plano avisa 250 ms después de cualquier cambio, también de un encuadre automático:
        # solo cuenta como vista manual si la persona hizo zoom o arrastró.
        if not self._ajustando_vista and not self.plano.ajuste_automatico:
            self._vista_manual = True
        self._recalcular_notables()

    def _recalcular_notables(self):
        if self.funcion is None:
            self.notables = []
        else:
            x0, x1, _, _ = self.plano.vista
            self.notables = puntos_notables(self.funcion, x0, x1, self.derivada, self.segunda)
        self._actualizar_notables()

    def _actualizar_notables(self):
        elegido = self.tabla_notables.selection()
        anterior = self.notables_por_clave.get(elegido[0]) if elegido else None
        self.tabla_notables.delete(*self.tabla_notables.get_children())
        self.notables_por_clave = {}
        for indice, punto in enumerate(self.notables):
            clave = f"n{indice}"
            self.notables_por_clave[clave] = punto
            self.tabla_notables.insert("", "end", iid=clave, tags=(punto.tipo,),
                                       values=(punto.nombre, numero_corto(punto.x), numero_corto(punto.y)))
        if anterior:
            for clave, punto in self.notables_por_clave.items():
                if punto.tipo == anterior.tipo and math.isclose(punto.x, anterior.x, rel_tol=1e-6, abs_tol=1e-9):
                    self.tabla_notables.selection_set(clave)
                    break
        self._actualizar_puntos_grafica()

    def _actualizar_puntos_grafica(self):
        puntos = []
        x0, x1, _, _ = self.plano.vista
        cerca = (x1 - x0) / 200
        for clave, punto in self.notables_por_clave.items():
            forma, color = ESTILO_PUNTO[punto.tipo]
            etiqueta = ETIQUETA_CORTA[punto.tipo]
            # La raíz calculada ya tiene su propia etiqueta: evita repetirla.
            if self.resultado is not None and punto.tipo == "raiz" and abs(punto.x - self.resultado.raiz) < cerca:
                etiqueta = ""
            puntos.append(PuntoGrafico(clave, punto.x, punto.y, forma, PALETA[color], etiqueta, punto.nombre))
        if self.resultado is not None:
            puntos.extend(self._puntos_del_metodo())
        self.plano.definir_puntos(puntos)

    def _al_elegir_notable(self, _evento=None):
        elegido = self.tabla_notables.selection()
        if not elegido:
            return
        punto = self.notables_por_clave.get(elegido[0])
        if punto is None:
            return
        texto = self._explicacion_pendiente or punto.explicacion
        self._explicacion_pendiente = None
        self.explicacion.configure(text=texto)
        self.plano.seleccionar(elegido[0], centrar=True)

    def _al_seleccionar_punto(self, clave):
        if clave in getattr(self, "notables_por_clave", {}):
            self.tabla_notables.selection_set(clave)
            self.tabla_notables.see(clave)
        elif clave.startswith("i"):
            indice = int(clave[1:])
            if self.resultado and indice < len(self.resultado.iteraciones):
                self.tabla_iteraciones.seleccionar(indice)

    def _expandir(self, expandido):
        """La gráfica ocupa toda la vista (como en GeoGebra) y se restaura al salir."""
        self.expandido = expandido
        widgets = (self.tarjeta_funcion, self.lateral, self.resultados)
        if expandido:
            for widget in widgets:
                widget.grid_remove()
            self.rowconfigure(3, weight=0, uniform="")
        else:
            for widget in widgets:
                widget.grid()
            self.rowconfigure(3, weight=38, uniform="zonas")
