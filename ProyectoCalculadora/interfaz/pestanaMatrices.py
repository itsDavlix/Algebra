"""Pestaña Matrices: operaciones matriciales con procedimiento paso a paso."""

import tkinter as tk
from tkinter import ttk

from nucleo.numeros import convertir_numero, limpiar_numero, EPSILON
from nucleo.matrices import (
    leer_matriz, matriz_a_texto, dimensiones, sumar_matrices, restar_matrices,
    multiplicar_matriz_escalar, multiplicar_matrices, matriz_inversa_con_pasos,
)
from nucleo.comprobaciones import matrices_aproximadamente_iguales, matriz_identidad
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado, AyudaEmergente


def _separar_pasos(pasos):
    return "\n\n" + ("\n\n" + "─" * 56 + "\n\n").join(pasos)


class PestanaMatrices(ttk.Frame):
    """Agrupa la entrada de matrices A y B y explica cada operación realizada."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_entrada()
        self._construir_operaciones()

    def _construir_entrada(self):
        marco = ttk.LabelFrame(self, text="Matrices A y B", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Matriz A (una fila por línea):").pack(anchor="w")
        self.txt_a = tk.Text(marco, height=9)
        self.txt_a.pack(fill="x", pady=(2, 10))
        self.txt_a.insert("1.0", "1 2\n3 4")
        AyudaEmergente(self.txt_a, "Separa los valores de cada fila con espacios o comas.")

        ttk.Label(marco, text="Matriz B (una fila por línea):").pack(anchor="w")
        self.txt_b = tk.Text(marco, height=9)
        self.txt_b.pack(fill="x", pady=(2, 10))
        self.txt_b.insert("1.0", "5 6\n7 8")

        fila_escalar = ttk.Frame(marco)
        fila_escalar.pack(fill="x", pady=5)
        ttk.Label(fila_escalar, text="Escalar (k):").pack(side="left")
        self.ent_escalar = ttk.Entry(fila_escalar, width=12)
        self.ent_escalar.pack(side="left", padx=8)
        self.ent_escalar.insert(0, "2")
        ttk.Button(fila_escalar, text="Limpiar", command=self._limpiar).pack(side="right")

    def _construir_operaciones(self):
        marco = ttk.LabelFrame(self, text="Elige una operación", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        botones = ttk.Frame(marco)
        botones.pack(fill="x")
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        ttk.Button(botones, text="Sumar (A + B)", command=self._accion_suma).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Restar (A − B)", command=self._accion_resta).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Multiplicar por escalar (k·A)", command=self._accion_escalar).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Multiplicar matrices (A × B)", command=self._accion_producto).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Matriz inversa (A⁻¹)", style="Accion.TButton", command=self._accion_inversa).grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        ttk.Label(marco, text="Resultado y procedimiento paso a paso:").pack(anchor="w", pady=(16, 4))
        marco_resultado, self.txt_resultado = crear_area_resultado(marco, alto=20)
        marco_resultado.pack(fill="both", expand=True)

    def _obtener_ab(self):
        return leer_matriz(self.txt_a.get("1.0", "end"), "matriz A"), leer_matriz(self.txt_b.get("1.0", "end"), "matriz B")

    def _accion_suma(self):
        try:
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
            a = leer_matriz(self.txt_a.get("1.0", "end"), "matriz A")
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
            a = leer_matriz(self.txt_a.get("1.0", "end"), "matriz A")
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

    def _limpiar(self):
        self.txt_a.delete("1.0", "end")
        self.txt_b.delete("1.0", "end")
        self.ent_escalar.delete(0, "end")
        mostrar_texto(self.txt_resultado, "")
