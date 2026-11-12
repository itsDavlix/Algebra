"""Selección y resolución de ecuaciones por Newton-Raphson o Secante."""

import tkinter as tk
from tkinter import ttk

from interfaz.ayudas import crear_area_resultado, mostrar_error, mostrar_texto
from interfaz.graficaMetodosAbiertos import GraficaMetodosAbiertos
from nucleo.biseccion import preparar_funcion
from nucleo.metodosabiertos import (
    METODOS_ABIERTOS, formatear_resultado_abierto, resolver_metodo_abierto,
)
from nucleo.numeros import convertir_numero


class PestanaMetodosAbiertos(ttk.Frame):
    """Recibe semillas manuales y muestra el procedimiento del método elegido."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1, minsize=310)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.resultado = None
        self._datos_grafica = None
        self._ventana_grafica = None
        self.var_metodo = tk.StringVar(self, value=METODOS_ABIERTOS[0])
        for nombre in ("ecuacion", "derivada", "x0", "x1", "tolerancia", "iteraciones"):
            setattr(self, "var_" + nombre, tk.StringVar(self))

        marco = ttk.LabelFrame(self, text="Resolver f(x) = 0", padding=12,
                               style="Seccion.TLabelframe")
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(marco, text="Método abierto:").pack(anchor="w")
        self.selector_metodo = ttk.Combobox(
            marco, textvariable=self.var_metodo, values=METODOS_ABIERTOS, state="readonly",
        )
        self.selector_metodo.pack(fill="x", pady=(3, 10))
        self.selector_metodo.bind("<<ComboboxSelected>>", self._seleccionar_metodo)

        for nombre, etiqueta in (
            ("ecuacion", "Ecuación o expresión f(x):"),
            ("derivada", "Derivada f'(x) — Newton-Raphson:"),
            ("x0", "Valor inicial x0:"), ("x1", "Segundo valor x1 — Secante:"),
            ("tolerancia", "Tolerancia absoluta (paso y residuo):"),
            ("iteraciones", "Máximo de iteraciones (1–1000):"),
        ):
            ttk.Label(marco, text=etiqueta).pack(anchor="w")
            entrada = ttk.Entry(marco, textvariable=getattr(self, "var_" + nombre))
            entrada.entrada_matematica = nombre in ("ecuacion", "derivada")
            entrada.pack(fill="x", pady=(2, 7))
            entrada.bind("<Return>", self._accion_resolver)
            setattr(self, "entrada_" + nombre, entrada)

        ttk.Label(
            marco, text="Usa * para multiplicar y ^ para potencias.\n"
            "Para g(x) = h(x), escribe la derivada de g(x) − h(x).\n"
            "Estos métodos no requieren cambio de signo y pueden no converger. "
            "Newton requiere una derivada correcta cerca de la raíz.",
            style="Ayuda.TLabel", wraplength=300, justify="left",
        ).pack(anchor="w", pady=(3, 10))
        ttk.Button(marco, text="Resolver", command=self._accion_resolver).pack(fill="x")
        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=(6, 0))
        ttk.Button(botones, text="Cargar ejemplo", command=self._cargar_ejemplo).pack(side="left")
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=6)
        salida = ttk.LabelFrame(self, text="Respuesta y explicación", padding=12,
                                style="Seccion.TLabelframe")
        salida.grid(row=0, column=1, sticky="nsew")
        self.boton_grafica = ttk.Button(salida, text="Graficar y ver puntos", state="disabled",
                                       command=self._abrir_grafica)
        self.boton_grafica.pack(anchor="e", pady=(0, 6))
        area, self.txt_resultado = crear_area_resultado(salida, alto=20, destacado=True)
        area.pack(fill="both", expand=True)
        self._cargar_ejemplo()

    def _seleccionar_metodo(self, _evento=None):
        newton = self.var_metodo.get() == "Newton-Raphson"
        self.entrada_derivada.configure(state="normal" if newton else "disabled")
        self.entrada_x1.configure(state="disabled" if newton else "normal")
        self.resultado = None
        self._descartar_grafica()
        mostrar_texto(self.txt_resultado, f"Método seleccionado: {self.var_metodo.get()}. Pulsa «Resolver».")

    def _accion_resolver(self, _evento=None):
        try:
            metodo = self.var_metodo.get()
            x0 = convertir_numero(self.var_x0.get(), "x0")
            x1 = convertir_numero(self.var_x1.get(), "x1") if metodo == "Secante" else None
            tolerancia = convertir_numero(self.var_tolerancia.get(), "La tolerancia")
            try:
                max_iteraciones = int(self.var_iteraciones.get())
            except ValueError as exc:
                raise ValueError("El máximo de iteraciones debe ser un entero entre 1 y 1000.") from exc
            self.resultado = resolver_metodo_abierto(
                self.var_ecuacion.get(), metodo, x0, x1=x1,
                derivada=self.var_derivada.get(), tolerancia=tolerancia,
                max_iteraciones=max_iteraciones,
            )
            mostrar_texto(self.txt_resultado, formatear_resultado_abierto(self.resultado))
            self._descartar_grafica()
            funcion, _ = preparar_funcion(self.var_ecuacion.get())
            self._datos_grafica = (funcion, self.resultado, (x0, x1) if metodo == "Secante" else (x0,))
            self.boton_grafica.configure(state="normal")
        except ValueError as error:
            self.resultado = None
            self._descartar_grafica()
            mostrar_texto(self.txt_resultado, "NO SE PUDO RESOLVER\nNo se pudo resolver la ecuación.\n\n" + str(error))
            mostrar_error(error)

    def _abrir_grafica(self):
        """Grafica una copia del último cálculo, aunque se editen después los campos."""
        if self._datos_grafica is None:
            return
        if self._ventana_grafica is not None and self._ventana_grafica.winfo_exists():
            self._ventana_grafica.deiconify()
            self._ventana_grafica.lift()
            return
        self._ventana_grafica = GraficaMetodosAbiertos(self, *self._datos_grafica)

    def _descartar_grafica(self):
        """Retira la gráfica anterior al limpiar, cambiar de método o recalcular."""
        ventana = getattr(self, "_ventana_grafica", None)
        if ventana is not None and ventana.winfo_exists():
            ventana.destroy()
        self._ventana_grafica = None
        self._datos_grafica = None
        self.boton_grafica.configure(state="disabled")

    def _cargar_ejemplo(self):
        for nombre, valor in (
            ("ecuacion", "x^3 - x - 2 = 0"), ("derivada", "3*x^2 - 1"),
            ("x0", "1.5"), ("x1", "2"), ("tolerancia", "1e-6"), ("iteraciones", "100"),
        ):
            getattr(self, "var_" + nombre).set(valor)
        self._seleccionar_metodo()

    def _limpiar(self):
        for nombre in ("ecuacion", "derivada", "x0", "x1"):
            getattr(self, "var_" + nombre).set("")
        self.var_tolerancia.set("1e-6")
        self.var_iteraciones.set("100")
        self.resultado = None
        self._descartar_grafica()
        mostrar_texto(self.txt_resultado, "")
        self.entrada_ecuacion.focus_set()
