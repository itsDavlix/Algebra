"""Pestaña de Regula Falsi con la gráfica y la tabla de Bisección."""

from tkinter import ttk

from interfaz.ayudas import mostrar_error, mostrar_texto
from interfaz.pestanaBiseccion import PestanaBiseccion, _numero_tabla
from nucleo.biseccion import autoajustar_biseccion, preparar_funcion
from nucleo.reglafalsa import (
    nota_estancamiento, resolver_reglafalsa,
)


def _numero_regla_falsa(valor):
    """Representa valores opcionales de la tabla sin perder cifras útiles."""
    return "—" if valor is None else _numero_tabla(valor)


class PestanaReglaFalsa(PestanaBiseccion):
    """Calcula una raíz por falsa posición y comparte la gráfica de Bisección."""

    def __init__(self, padre):
        super().__init__(padre)
        self.txt_resultado.configure(height=8)
        self.marco_entrada.configure(text="Resolver f(x) = 0 por Regula Falsi")
        self.tabla_iteraciones.heading("c", text="Falsa posición")
        self.tabla_iteraciones.heading("error", text="Error aprox.")
        for widget in self.marco_entrada.winfo_children():
            if (isinstance(widget, ttk.Button)
                    and widget.cget("text") == "Resolver por bisección"):
                widget.configure(text="Resolver por Regula Falsi")
                break
        self._cargar_ejemplo()

    def _accion_resolver(self, _evento=None):
        """Autoajusta los parámetros, resuelve y actualiza sus vistas."""
        try:
            ajuste = autoajustar_biseccion(self.var_ecuacion.get())
            self._aplicar_autoajuste(ajuste)
            resultado = resolver_reglafalsa(
                self.var_ecuacion.get(), ajuste.a, ajuste.b, ajuste.tolerancia, 100,
            )
            mostrar_texto(self.txt_resultado, self._resumen_regla_falsa(resultado))
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

    @staticmethod
    def _resumen_regla_falsa(resultado):
        estado = "convergencia alcanzada" if resultado.convergio else "aproximación sin convergencia"
        error = _numero_regla_falsa(resultado.error)
        lineas = [
            "RESPUESTA · RAÍZ APROXIMADA" if resultado.convergio else "SIN CONVERGENCIA · ÚLTIMA APROXIMACIÓN",
            f"x ≈ {_numero_tabla(resultado.raiz)}",
            f"Estado: {estado}", "", "COMPROBACIÓN",
            f"Al sustituir la aproximación: f(x) = {_numero_tabla(resultado.valor_funcion)}",
            f"Error estimado |c − c anterior|: {error}",
            f"Tolerancia: {_numero_tabla(resultado.tolerancia)}",
            "", "EXPLICACIÓN · REGULA FALSI",
            f"Iteraciones: {len(resultado.iteraciones)}",
            f"Motivo: {resultado.motivo}",
            "Unimos los extremos con una recta y usamos su corte con el eje x como aproximación. "
            "Después conservamos el intervalo con cambio de signo.",
            "Expande las iteraciones de la tabla inferior para ver las operaciones y decisiones.",
        ]
        aviso = nota_estancamiento(resultado)
        if aviso:
            lineas.append("AVISO: " + aviso)
        else:
            lineas.append("La tolerancia no es una cota del error real en x.")
        return "\n".join(lineas)

    def _actualizar_tabla_iteraciones(self, resultado):
        """Muestra cada falsa posición y las evaluaciones que justifican el paso."""
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
                    _numero_tabla(paso.a), _numero_tabla(paso.b),
                    _numero_tabla(paso.c), _numero_tabla(paso.fc),
                    _numero_regla_falsa(paso.error),
                ),
                open=False, tags=(estilo_fila,),
            )
            detalles = (
                (
                    "c = b − f(b)(a−b) / (f(a)−f(b))",
                    ("", "", _numero_tabla(paso.c), "", ""),
                ),
                (f"Evaluación: f(a) = {_numero_tabla(paso.fa)}", ("",) * 5),
                (f"Evaluación: f(b) = {_numero_tabla(paso.fb)}", ("",) * 5),
                (f"Evaluación: f(c) = {_numero_tabla(paso.fc)}", ("",) * 5),
                (
                    "Error aproximado |c − c anterior|",
                    ("", "", "", "", _numero_regla_falsa(paso.error)
                     if paso.error is not None else ""),
                ),
                (
                    "Error relativo aproximado εa",
                    (
                        "", "", "", "",
                        "—" if paso.error_relativo is None
                        else f"{_numero_tabla(paso.error_relativo)} %",
                    ),
                ),
            )
            for texto, valores in detalles:
                tabla.insert(
                    iid, "end", text=texto, values=valores, tags=("detalle",),
                )

            if paso.numero == len(resultado.iteraciones):
                decision = "Parada: " + resultado.motivo
                valores_decision = ("",) * 5
                estilo_decision = "parada_ok" if resultado.convergio else "parada_no"
            elif paso.extremo_movido == "b":
                decision = "Decisión: f(a)·f(c) < 0 → b = c"
                valores_decision = (
                    _numero_tabla(paso.a), _numero_tabla(paso.c), "", "", "",
                )
                estilo_decision = "decision"
            elif paso.extremo_movido == "a":
                decision = "Decisión: f(c)·f(b) < 0 → a = c"
                valores_decision = (
                    _numero_tabla(paso.c), _numero_tabla(paso.b), "", "", "",
                )
                estilo_decision = "decision"
            else:
                decision = "Parada: " + resultado.motivo
                valores_decision = ("",) * 5
                estilo_decision = "parada_ok" if resultado.convergio else "parada_no"
            tabla.insert(
                iid, "end", text=decision, values=valores_decision,
                tags=(estilo_decision,),
            )

    def _aplicar_autoajuste(self, ajuste):
        """Muestra el intervalo y los parámetros usados por Regula Falsi."""
        super()._aplicar_autoajuste(ajuste)
        self.var_iteraciones.set("100")

    def _cargar_ejemplo(self):
        """Carga el ejemplo conocido de la raíz de x^3 - x - 2."""
        self.var_ecuacion.set("x^3 - x - 2 = 0")
        self.var_a.set("1")
        self.var_b.set("2")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        self.resultado_biseccion = None
        self.funcion_grafica = None
        self._actualizar_tabla_iteraciones_vacia()
        self.mensaje_grafica = "Resuelve la ecuación para ver su gráfica y la raíz aproximada."
        self._redibujar_grafica()
        mostrar_texto(
            self.txt_resultado,
            "Pulsa «Resolver por Regula Falsi» para calcular la raíz del ejemplo.",
        )
