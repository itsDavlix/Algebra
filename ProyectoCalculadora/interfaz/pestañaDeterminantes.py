"""Pestaña Determinantes: cálculo por cofactores o LU con validación en vivo."""

import tkinter as tk
from tkinter import ttk, simpledialog

from nucleo.determinantes import (
    resumen_eficiencia, determinante_con_pasos, formatear_determinante,
    validar_entrada_determinante,
)
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado, AyudaEmergente

EJEMPLO = "2 1 1\n4 3 3\n8 7 9"
SEPARADOR = "\n\n" + "─" * 40 + "\n\n"

class PestanaDeterminantes(ttk.Frame):
    """Valida la matriz mientras se escribe, recomienda un método y muestra el procedimiento."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.matriz = None          # Matriz válida actual (None si hay errores).
        self.recomendado = None     # Método más eficiente para el orden actual.
        self.metodo = tk.StringVar(value="")  # Ningún método queda preseleccionado.
        self._construir_entrada()
        self._construir_calculo()
        self._al_cambiar_matriz()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _construir_entrada(self):
        """Columna izquierda: matriz A y lista de validaciones en vivo."""
        # El editor de texto permite pegar una matriz completa fila por fila.
        marco = ttk.LabelFrame(self, text="1. Matriz A", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Una fila por línea; usa espacios, comas, punto y coma o barras verticales.",
                  style="Ayuda.TLabel").pack(anchor="w")
        self.txt_matriz = tk.Text(marco, height=9, width=30)
        self.txt_matriz.pack(fill="x", pady=(4, 8))
        self.txt_matriz.insert("1.0", EJEMPLO)
        self.txt_matriz.bind("<KeyRelease>", lambda _e: self._al_cambiar_matriz())
        AyudaEmergente(self.txt_matriz, "El determinante solo existe para matrices cuadradas (n × n).")

        botones = ttk.Frame(marco)
        botones.pack(fill="x")
        ttk.Button(botones, text="Ejemplo 3×3", command=self._cargar_ejemplo).pack(side="left")
        ttk.Button(botones, text="Crear matriz", command=self._crear_matriz).pack(side="left", padx=(6, 0))
        ttk.Button(botones, text="Matriz identidad", command=self._crear_identidad).pack(side="left", padx=(6, 0))
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(side="right")

        # Lista de validaciones: cada línea cambia de color según su estado.
        ttk.Label(marco, text="Validaciones", style="Negrita.TLabel").pack(anchor="w", pady=(14, 4))
        self.lbl_validaciones = [ttk.Label(marco, wraplength=300, justify="left") for _ in range(4)]
        for etiqueta in self.lbl_validaciones:
            etiqueta.pack(anchor="w", pady=1)
        self.lbl_detalle = ttk.Label(marco, wraplength=300, justify="left", style="Error.TLabel")
        self.lbl_detalle.pack(anchor="w", pady=(8, 0))

    def _construir_calculo(self):
        """Columna derecha: eficiencia, elección del método y resultado."""
        # La recomendación aparece antes de seleccionar el método de cálculo.
        marco = ttk.LabelFrame(self, text="2. Método y resultado", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        # Tarjeta azul con la comparación de eficiencia, visible ANTES de elegir.
        tarjeta = ttk.Frame(marco, style="Tarjeta.TFrame", padding=10)
        tarjeta.pack(fill="x")
        ttk.Label(tarjeta, text="¿Cuál conviene?", style="TarjetaTitulo.TLabel").pack(anchor="w")
        self.lbl_eficiencia = ttk.Label(tarjeta, style="Tarjeta.TLabel", wraplength=520, justify="left")
        self.lbl_eficiencia.pack(anchor="w", pady=(4, 0))

        ttk.Label(marco, text="Elige el método:", style="Negrita.TLabel").pack(anchor="w", pady=(12, 2))
        self.radios = {}
        for clave, nombre in (("cofactores", "Cofactores"), ("lu", "LU con pivoteo parcial")):
            radio = ttk.Radiobutton(marco, text=nombre, variable=self.metodo, value=clave,
                                    command=self._actualizar_boton)
            radio.pack(anchor="w", pady=2)
            self.radios[clave] = (radio, nombre)

        self.btn_calcular = ttk.Button(marco, text="Calcular determinante", style="Accion.TButton",
                                       command=self._calcular)
        self.btn_calcular.pack(fill="x", pady=12)

        ttk.Label(marco, text="Resultado y procedimiento paso a paso:").pack(anchor="w", pady=(0, 4))
        area, self.txt_resultado = crear_area_resultado(marco, alto=14)
        area.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Validación y estado de los controles
    # ------------------------------------------------------------------
    def _al_cambiar_matriz(self):
        """Revalida el texto, actualiza el semáforo y la recomendación de eficiencia."""
        # Actualiza la matriz usable y el estado de cada validación.
        self.matriz, comprobaciones = validar_entrada_determinante(self.txt_matriz.get("1.0", "end"))

        # Cada comprobación muestra ✓ (cumple), ✗ (falla) o • (pendiente).
        detalle = ""
        for etiqueta, (estado, descripcion, texto) in zip(self.lbl_validaciones, comprobaciones):
            simbolo, estilo = {True: ("✓", "Valido.TLabel"), False: ("✗", "Error.TLabel"),
                               None: ("•", "Pendiente.TLabel")}[estado]
            etiqueta.configure(text=f"{simbolo}  {descripcion}", style=estilo)
            if estado is False:
                detalle = texto
        self.lbl_detalle.configure(text=detalle)

        # Con la matriz válida se calcula la recomendación; si no, se bloquea la elección.
        if self.matriz is None:
            self.recomendado = None
            self.lbl_eficiencia.configure(text="Escribe una matriz cuadrada válida para ver cuál método conviene.")
        else:
            self.recomendado, texto = resumen_eficiencia(self.matriz)
            self.lbl_eficiencia.configure(text=texto)

        # La etiqueta ★ indica el método más eficiente sin elegirlo por el usuario.
        for clave, (radio, nombre) in self.radios.items():
            marca = "   ★ Más eficiente" if clave == self.recomendado else ""
            radio.configure(text=nombre + marca, state="normal" if self.matriz else "disabled")
        self._actualizar_boton()

    def _actualizar_boton(self):
        """Habilita Calcular solo si la matriz es válida y ya se eligió un método."""
        activo = self.matriz is not None and self.metodo.get() in ("cofactores", "lu")
        self.btn_calcular.state(["!disabled"] if activo else ["disabled"])

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _calcular(self):
        """Ejecuta el método elegido y muestra valor, pasos y comprobación cruzada."""
        try:
            # El núcleo devuelve el resultado, los pasos y la comprobación independiente.
            elegido = self.metodo.get()
            valor, pasos, comprobacion = determinante_con_pasos(self.matriz, elegido)
        except ValueError as error:
            mostrar_error(error)
            return
        pasos.append(comprobacion)
        encabezado = f"det(A) = {formatear_determinante(valor)}   (método: {elegido.upper()})"
        mostrar_texto(self.txt_resultado, encabezado + SEPARADOR + SEPARADOR.join(pasos))

    def _crear_matriz(self):
        """Genera una matriz con ceros para evitar errores de escritura manual."""
        filas = simpledialog.askinteger("Tamaño", "Número de filas:", initialvalue=3, minvalue=1, maxvalue=12)
        if filas is None:
            return
        columnas = simpledialog.askinteger("Tamaño", "Número de columnas:", initialvalue=filas, minvalue=1, maxvalue=12)
        if columnas is None:
            return
        contenido = [" ".join("0" for _ in range(columnas)) for _ in range(filas)]
        self.txt_matriz.delete("1.0", "end")
        self.txt_matriz.insert("1.0", "\n".join(contenido))
        self._al_cambiar_matriz()

    def _crear_identidad(self):
        """Crea una matriz identidad útil para pruebas rápidas."""
        orden = simpledialog.askinteger("Tamaño", "Orden de la identidad:", initialvalue=3, minvalue=1, maxvalue=10)
        if orden is None:
            return
        filas = []
        for i in range(orden):
            fila = ["1" if i == j else "0" for j in range(orden)]
            filas.append(" ".join(fila))
        self.txt_matriz.delete("1.0", "end")
        self.txt_matriz.insert("1.0", "\n".join(filas))
        self._al_cambiar_matriz()

    def _cargar_ejemplo(self):
        """Reemplaza el contenido por una matriz 3×3 de ejemplo."""
        self.txt_matriz.delete("1.0", "end")
        self.txt_matriz.insert("1.0", EJEMPLO)
        self._al_cambiar_matriz()

    def _limpiar(self):
        """Vacía la entrada, la elección de método y el resultado."""
        self.txt_matriz.delete("1.0", "end")
        self.metodo.set("")
        mostrar_texto(self.txt_resultado, "")
        self._al_cambiar_matriz()