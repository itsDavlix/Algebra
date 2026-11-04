"""Pestaña Matrices: operaciones matriciales con procedimiento paso a paso."""

import tkinter as tk
from tkinter import ttk

from nucleo.numeros import convertir_numero, limpiar_numero, EPSILON
from nucleo.matrices import (
    matriz_a_texto, dimensiones, sumar_matrices, restar_matrices,
    multiplicar_matriz_escalar, multiplicar_matrices, matriz_inversa_con_pasos,
)
from nucleo.determinantes import (
    recomendar_metodo, determinante_con_pasos, formatear_determinante,
)
from nucleo.comprobaciones import matrices_aproximadamente_iguales, matriz_identidad
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado


def _separar_pasos(pasos):
    return "\n\n" + ("\n\n" + "─" * 56 + "\n\n").join(pasos)


class EntradaMatriz(ttk.Frame):
    """Editor de matriz en celdas para no depender de espacios entre números."""

    def __init__(self, padre, nombre, valores):
        super().__init__(padre)
        self.nombre = nombre
        self.celdas = []
        filas = len(valores)
        columnas = len(valores[0])

        # Los selectores ajustan el tamaño sin perder valores que ya se escribieron.
        controles = ttk.Frame(self)
        controles.pack(fill="x", pady=(0, 4))
        ttk.Label(controles, text=f"Matriz {nombre}:").pack(side="left")
        ttk.Label(controles, text="Filas").pack(side="left", padx=(12, 3))
        self.filas_var = tk.StringVar(value=str(filas))
        ttk.Spinbox(
            controles, from_=1, to=40, width=3, textvariable=self.filas_var,
            state="readonly", command=self._cambiar_tamano,
        ).pack(side="left")
        ttk.Label(controles, text="Columnas").pack(side="left", padx=(8, 3))
        self.columnas_var = tk.StringVar(value=str(columnas))
        ttk.Spinbox(
            controles, from_=1, to=40, width=3, textvariable=self.columnas_var,
            state="readonly", command=self._cambiar_tamano,
        ).pack(side="left")

        # El lienzo permite desplazar la cuadrícula cuando no cabe completa.
        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(
            marco, height=120, background="white", highlightthickness=0
        )
        barra_y = ttk.Scrollbar(marco, orient="vertical", command=self.canvas.yview)
        barra_x = ttk.Scrollbar(marco, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        self.contenido = ttk.Frame(self.canvas)
        self.ventana_canvas = self.canvas.create_window(
            (0, 0), window=self.contenido, anchor="nw"
        )
        self.contenido.bind("<Configure>", self._actualizar_scrollregion)
        self.canvas.bind("<Configure>", self._ajustar_ancho_contenido)
        self._dibujar_celdas(valores)

    def _actualizar_scrollregion(self, _evento=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho_contenido(self, _evento=None):
        ancho = max(self.canvas.winfo_width(), self.contenido.winfo_reqwidth())
        self.canvas.itemconfigure(self.ventana_canvas, width=ancho)
        self._actualizar_scrollregion()

    def _leer_valores_actuales(self):
        return [[celda.get() for celda in fila] for fila in self.celdas]

    def _cambiar_tamano(self):
        # Conserva celdas existentes y deja vacías las nuevas posiciones.
        valores = self._leer_valores_actuales()
        filas, columnas = int(self.filas_var.get()), int(self.columnas_var.get())
        nuevos = [
            [
                valores[i][j] if i < len(valores) and j < len(valores[i]) else ""
                for j in range(columnas)
            ]
            for i in range(filas)
        ]
        self._dibujar_celdas(nuevos)

    def _dibujar_celdas(self, valores):
        # Redibuja encabezados y casillas usando el tamaño actual de la matriz.
        for widget in self.contenido.winfo_children():
            widget.destroy()
        self.celdas = []
        columnas = len(valores[0])
        self.contenido.grid_columnconfigure(0, weight=0)
        for j in range(columnas):
            self.contenido.grid_columnconfigure(j + 1, weight=1, uniform="columna")
        ttk.Label(self.contenido, text="").grid(row=0, column=0, padx=2, pady=2)
        for j in range(columnas):
            ttk.Label(self.contenido, text=str(j + 1)).grid(
                row=0, column=j + 1, padx=2, pady=2
            )
        for i, fila in enumerate(valores):
            ttk.Label(self.contenido, text=str(i + 1)).grid(
                row=i + 1, column=0, padx=2, pady=2
            )
            celdas_fila = []
            for j, valor in enumerate(fila):
                celda = ttk.Entry(self.contenido, width=8, justify="center")
                celda.grid(row=i + 1, column=j + 1, padx=2, pady=2, sticky="ew")
                celda.insert(0, valor)
                celdas_fila.append(celda)
            self.celdas.append(celdas_fila)
        self.canvas.configure(height=min(280, max(170, 35 * len(valores) + 35)))
        self.contenido.update_idletasks()
        self._ajustar_ancho_contenido()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def obtener(self):
        # Valida cada casilla e informa la coordenada del valor incorrecto.
        matriz = []
        for i, fila in enumerate(self.celdas, start=1):
            matriz.append([
                convertir_numero(celda.get(), f"Elemento [{i},{j}] de la matriz {self.nombre}")
                for j, celda in enumerate(fila, start=1)
            ])
        return matriz

    def limpiar(self):
        for fila in self.celdas:
            for celda in fila:
                celda.delete(0, "end")


class PestanaMatrices(ttk.Frame):
    """Agrupa la entrada de matrices A y B y explica cada operación realizada."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)
        self._construir_entrada()
        self._construir_operaciones()

    def _construir_entrada(self):
        # Coloca las matrices una junto a la otra para ampliar su espacio visible.
        marco = ttk.LabelFrame(
            self, text="Matrices A y B — ingresa cada valor en su casilla",
            style="Seccion.TLabelframe", padding=10,
        )
        marco.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 7))
        marco.columnconfigure(0, weight=1, uniform="matrices")
        marco.columnconfigure(1, weight=1, uniform="matrices")
        marco.rowconfigure(0, weight=1)

        self.entrada_a = EntradaMatriz(marco, "A", [["1", "2"], ["3", "4"]])
        self.entrada_a.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.entrada_b = EntradaMatriz(marco, "B", [["5", "6"], ["7", "8"]])
        self.entrada_b.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def _construir_operaciones(self):
        # Separa los botones de cálculo del panel donde se muestran los resultados.
        marco = ttk.LabelFrame(self, text="Elige una operación", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=1, column=0, sticky="nsew", padx=(0, 7))

        botones = ttk.Frame(marco)
        botones.pack(fill="x")
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        ttk.Button(botones, text="Sumar (A + B)", command=self._accion_suma).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Restar (A − B)", command=self._accion_resta).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Multiplicar por escalar (k·A)", command=self._accion_escalar).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Multiplicar matrices (A × B)", command=self._accion_producto).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Matriz inversa (A⁻¹)", style="Accion.TButton", command=self._accion_inversa).grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        # Abre la recomendación antes de habilitar la elección del método.
        ttk.Button(botones, text="Determinante de A", command=self._accion_determinante).grid(
            row=3, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        fila_escalar = ttk.Frame(marco)
        fila_escalar.pack(fill="x", pady=(8, 0))
        ttk.Label(fila_escalar, text="Escalar (k):").pack(side="left")
        self.ent_escalar = ttk.Entry(fila_escalar, width=12)
        self.ent_escalar.pack(side="left", padx=8)
        self.ent_escalar.insert(0, "2")
        ttk.Button(fila_escalar, text="Limpiar", command=self._limpiar).pack(side="right")

        marco_resultado = ttk.LabelFrame(
            self, text="Resultado y procedimiento paso a paso",
            style="Seccion.TLabelframe", padding=10,
        )
        marco_resultado.grid(row=1, column=1, sticky="nsew", padx=(7, 0))
        area, self.txt_resultado = crear_area_resultado(marco_resultado, alto=10)
        area.pack(fill="both", expand=True)

    def _obtener_ab(self):
        return self.entrada_a.obtener(), self.entrada_b.obtener()

    def _accion_suma(self):
        try:
            # Calcula A+B y comprueba que al restar B se recupere A.
            a, b = self._obtener_ab()
            resultado = sumar_matrices(a, b)
            filas, columnas = dimensiones(a)
            calculos = []
            for i in range(filas):
                for j in range(columnas):
                    calculos.append(
                        f"C[{i + 1},{j + 1}] = {limpiar_numero(a[i][j])} + "
                        f"{limpiar_numero(b[i][j])} = {limpiar_numero(resultado[i][j])}"
                    )
            reconstruida = restar_matrices(resultado, b)
            comprobado = matrices_aproximadamente_iguales(reconstruida, a)
            pasos = [
                f"PASO 1. Verificar dimensiones.\nA y B son de tamaño {filas}×{columnas}, así que se pueden sumar.",
                "PASO 2. Sumar los elementos que están en la misma posición:\n" + "\n".join(calculos),
                "PASO 3. Colocar los resultados en la matriz C = A + B.\n\n" + matriz_a_texto(resultado),
                "COMPROBACIÓN. C − B debe recuperar A:\n\n"
                + matriz_a_texto(reconstruida)
                + ("\n\n✓ La comprobación es correcta." if comprobado else "\n\n✗ La comprobación no coincide."),
            ]
            mostrar_texto(self.txt_resultado, "A + B =\n" + matriz_a_texto(resultado) + _separar_pasos(pasos))
        except ValueError as error:
            mostrar_error(error)

    def _accion_resta(self):
        try:
            # Calcula A-B y comprueba que al sumar B se recupere A.
            a, b = self._obtener_ab()
            resultado = restar_matrices(a, b)
            filas, columnas = dimensiones(a)
            calculos = []
            for i in range(filas):
                for j in range(columnas):
                    calculos.append(
                        f"C[{i + 1},{j + 1}] = {limpiar_numero(a[i][j])} − "
                        f"{limpiar_numero(b[i][j])} = {limpiar_numero(resultado[i][j])}"
                    )
            reconstruida = sumar_matrices(resultado, b)
            comprobado = matrices_aproximadamente_iguales(reconstruida, a)
            pasos = [
                f"PASO 1. Verificar dimensiones.\nA y B son de tamaño {filas}×{columnas}, así que se pueden restar.",
                "PASO 2. Restar los elementos que están en la misma posición:\n" + "\n".join(calculos),
                "PASO 3. Colocar los resultados en C = A − B.\n\n" + matriz_a_texto(resultado),
                "COMPROBACIÓN. C + B debe recuperar A:\n\n"
                + matriz_a_texto(reconstruida)
                + ("\n\n✓ La comprobación es correcta." if comprobado else "\n\n✗ La comprobación no coincide."),
            ]
            mostrar_texto(self.txt_resultado, "A − B =\n" + matriz_a_texto(resultado) + _separar_pasos(pasos))
        except ValueError as error:
            mostrar_error(error)

    def _accion_escalar(self):
        try:
            # Multiplica cada elemento de A por k y comprueba el caso correspondiente.
            a = self.entrada_a.obtener()
            escalar = convertir_numero(self.ent_escalar.get())
            resultado = multiplicar_matriz_escalar(a, escalar)
            filas, columnas = dimensiones(a)
            calculos = []
            for i in range(filas):
                for j in range(columnas):
                    calculos.append(
                        f"C[{i + 1},{j + 1}] = {limpiar_numero(escalar)} × "
                        f"{limpiar_numero(a[i][j])} = {limpiar_numero(resultado[i][j])}"
                    )
            if abs(escalar) > EPSILON:
                reconstruida = multiplicar_matriz_escalar(resultado, 1.0 / escalar)
                comprobado = matrices_aproximadamente_iguales(reconstruida, a)
                texto_comprobacion = (
                    "COMPROBACIÓN. Dividir k·A entre k debe recuperar A:\n\n"
                    + matriz_a_texto(reconstruida)
                )
            else:
                esperada = [[0.0 for _ in range(columnas)] for _ in range(filas)]
                comprobado = matrices_aproximadamente_iguales(resultado, esperada)
                texto_comprobacion = (
                    "COMPROBACIÓN. Como k = 0, el resultado debe ser la matriz cero:\n\n"
                    + matriz_a_texto(resultado)
                )
            texto_comprobacion += "\n\n✓ La comprobación es correcta." if comprobado else "\n\n✗ La comprobación no coincide."
            pasos = [
                f"PASO 1. Tomar el escalar k = {limpiar_numero(escalar)}.",
                "PASO 2. Multiplicar k por cada entrada de A:\n" + "\n".join(calculos),
                "PASO 3. Formar la matriz resultante k·A.\n\n" + matriz_a_texto(resultado),
                texto_comprobacion,
            ]
            mostrar_texto(
                self.txt_resultado,
                f"{limpiar_numero(escalar)} · A =\n{matriz_a_texto(resultado)}" + _separar_pasos(pasos),
            )
        except ValueError as error:
            mostrar_error(error)

    def _accion_producto(self):
        try:
            # Calcula A·B si las dimensiones interiores son compatibles.
            a, b = self._obtener_ab()
            resultado = multiplicar_matrices(a, b)
            filas_a, columnas_a = dimensiones(a)
            filas_b, columnas_b = dimensiones(b)
            calculos = []
            for i in range(filas_a):
                for j in range(columnas_b):
                    productos = [a[i][k] * b[k][j] for k in range(columnas_a)]
                    expresion = " + ".join(
                        f"({limpiar_numero(a[i][k])}×{limpiar_numero(b[k][j])})"
                        for k in range(columnas_a)
                    )
                    suma = " + ".join(limpiar_numero(x) for x in productos)
                    calculos.append(
                        f"C[{i + 1},{j + 1}] = {expresion} = {suma} = {limpiar_numero(resultado[i][j])}"
                    )
            recalculada = [
                [sum(a[i][k] * b[k][j] for k in range(columnas_a)) for j in range(columnas_b)]
                for i in range(filas_a)
            ]
            comprobado = matrices_aproximadamente_iguales(recalculada, resultado)
            pasos = [
                f"PASO 1. Verificar compatibilidad.\nA es {filas_a}×{columnas_a} y B es {filas_b}×{columnas_b}. "
                f"Como columnas(A) = filas(B) = {columnas_a}, el producto existe y será {filas_a}×{columnas_b}.",
                "PASO 2. Multiplicar cada fila de A por cada columna de B y sumar los productos:\n" + "\n".join(calculos),
                "PASO 3. Formar C = A×B con los valores calculados.\n\n" + matriz_a_texto(resultado),
                "COMPROBACIÓN. Se recalcula cada producto fila×columna y se compara con C.\n"
                + ("✓ Todas las entradas coinciden." if comprobado else "✗ Hay entradas que no coinciden."),
            ]
            mostrar_texto(self.txt_resultado, "A × B =\n" + matriz_a_texto(resultado) + _separar_pasos(pasos))
        except ValueError as error:
            mostrar_error(error)

    def _accion_inversa(self):
        try:
            # Calcula A⁻¹ y comprueba ambos productos A·A⁻¹ y A⁻¹·A.
            a = self.entrada_a.obtener()
            resultado, pasos = matriz_inversa_con_pasos(a)
            orden, _ = dimensiones(a)
            identidad = matriz_identidad(orden)
            izquierda = multiplicar_matrices(a, resultado)
            derecha = multiplicar_matrices(resultado, a)
            comprobado = (
                matrices_aproximadamente_iguales(izquierda, identidad)
                and matrices_aproximadamente_iguales(derecha, identidad)
            )
            pasos.append(
                "COMPROBACIÓN. Una inversa correcta debe cumplir A·A⁻¹ = I y A⁻¹·A = I.\n\n"
                "A·A⁻¹ =\n" + matriz_a_texto(izquierda)
                + "\n\nA⁻¹·A =\n" + matriz_a_texto(derecha)
                + ("\n\n✓ Ambas multiplicaciones producen la identidad." if comprobado else "\n\n✗ La comprobación no produce la identidad.")
            )
            mostrar_texto(self.txt_resultado, "A⁻¹ =\n" + matriz_a_texto(resultado) + _separar_pasos(pasos))
        except ValueError as error:
            mostrar_error(error)

    def _accion_determinante(self):
        """Valida A y presenta la eficiencia antes de que el usuario elija."""
        try:
            # Revisa A antes de abrir el selector de método.
            a = self.entrada_a.obtener()
            _, recomendacion = recomendar_metodo(a)
        except ValueError as error:
            mostrar_error(error)
            return

        # La ventana modal conserva la matriz evaluada durante toda la selección.
        ventana = tk.Toplevel(self)
        ventana.title("Elegir método del determinante")
        ventana.transient(self.winfo_toplevel())
        contenido = ttk.Frame(ventana, padding=18)
        contenido.pack(fill="both", expand=True)
        ttk.Label(contenido, text=f"Matriz A: {len(a)} × {len(a)}", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(
            contenido,
            text="✓ Validación: todas las entradas son números finitos y A es cuadrada.",
        ).pack(anchor="w", pady=(4, 0))
        ttk.Label(contenido, text=recomendacion, wraplength=490).pack(anchor="w", pady=12)
        ttk.Label(contenido, text="Cofactores se detiene tras 100000 expansiones para evitar "
                  "una espera excesiva. En ese caso, podés elegir LU.", wraplength=490).pack(anchor="w")

        # Ningún método queda seleccionado automáticamente: la decisión es del usuario.
        metodo = tk.StringVar(value="")
        for nombre, valor in (("Cofactores", "cofactores"), ("LU con pivoteo parcial", "lu")):
            ttk.Radiobutton(contenido, text=nombre, variable=metodo, value=valor).pack(anchor="w", pady=5)

        def calcular():
            """Calcula con el método elegido y muestra sus pasos y la comprobación."""
            try:
                # Presenta el desarrollo del método seleccionado y su contraste.
                elegido = metodo.get()
                resultado, pasos, comprobacion = determinante_con_pasos(a, elegido)
                pasos.append(comprobacion)
                mostrar_texto(self.txt_resultado,
                              f"det(A) = {formatear_determinante(resultado)} "
                              f"(método: {elegido.upper()})"
                              + _separar_pasos(pasos))
                ventana.destroy()
            except ValueError as error:
                mostrar_error(error)

        # Cancelar cierra el diálogo sin ejecutar una operación.
        ttk.Button(contenido, text="Calcular", command=calcular).pack(side="left", pady=12)
        ttk.Button(contenido, text="Cancelar", command=ventana.destroy).pack(side="right", pady=12)
        ventana.grab_set()

    def _limpiar(self):
        self.entrada_a.limpiar()
        self.entrada_b.limpiar()
        self.ent_escalar.delete(0, "end")
        mostrar_texto(self.txt_resultado, "")
