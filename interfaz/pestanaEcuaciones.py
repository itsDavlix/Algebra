"""Pestaña Ecuaciones A·X = B con resolución y comprobación paso a paso."""

import tkinter as tk
from tkinter import ttk

from nucleo.matrices import leer_matriz, matriz_a_texto, multiplicar_matrices, dimensiones
from nucleo.comprobaciones import matrices_aproximadamente_iguales, numeros_aproximadamente_iguales
from nucleo.numeros import limpiar_numero, escala_de
from nucleo.sistemas import (
    resolver_sistema_gauss_jordan_con_pasos, ErrorSistemaIncompatible,
    solucion_general_texto,
)
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado, AyudaEmergente


def _bloque(pasos):
    return "\n\n" + ("\n\n" + "─" * 56 + "\n\n").join(pasos)


class PestanaEcuaciones(ttk.Frame):
    """Permite resolver A·X = B y comprobar X mostrando el procedimiento."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_entrada()
        self._construir_resultado()

    def _construir_entrada(self):
        # Recibe A, B y una posible solución X para resolver o comprobar.
        marco = ttk.LabelFrame(self, text="Resolver A · X = B", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Matriz A:").pack(anchor="w")
        self.txt_a = tk.Text(marco, width=38, height=5)
        self.txt_a.entrada_lista = True
        self.txt_a.pack(fill="x", pady=(2, 8))
        self.txt_a.insert("1.0", "2 1\n1 -1")
        AyudaEmergente(self.txt_a, "Matriz de coeficientes del sistema.")

        ttk.Label(marco, text="Matriz B:").pack(anchor="w")
        self.txt_b = tk.Text(marco, width=38, height=5)
        self.txt_b.entrada_lista = True
        self.txt_b.pack(fill="x", pady=(2, 8))
        self.txt_b.insert("1.0", "5\n1")

        ttk.Button(marco, text="Resolver ecuación matricial", style="Accion.TButton", command=self._accion_resolver).pack(fill="x", pady=5)

        ttk.Label(marco, text="Para comprobar una X concreta, escríbela aquí:").pack(anchor="w", pady=(12, 0))
        self.txt_x = tk.Text(marco, width=38, height=5)
        self.txt_x.entrada_lista = True
        self.txt_x.pack(fill="x", pady=(2, 8))
        self.txt_x.insert("1.0", "2\n1")

        fila_botones = ttk.Frame(marco)
        fila_botones.pack(fill="x", pady=5)
        ttk.Button(fila_botones, text="Comprobar A · X = B", command=self._accion_evaluar).pack(side="left", fill="x", expand=True)
        ttk.Button(fila_botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=(6, 0))

    def _construir_resultado(self):
        # El procedimiento puede ser largo, por eso se muestra en un área desplazable.
        marco = ttk.LabelFrame(self, text="Resultado y procedimiento paso a paso", style="Seccion.TLabelframe", padding=12)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        marco_resultado, self.txt_resultado = crear_area_resultado(marco, alto=24, destacado=True)
        marco_resultado.pack(fill="both", expand=True)

    def _accion_resolver(self):
        try:
            # Resuelve A·X=B y verifica que la solución reproduzca B.
            a = leer_matriz(self.txt_a.get("1.0", "end"), "matriz A")
            b = leer_matriz(self.txt_b.get("1.0", "end"), "matriz B")
            solucion, tipo, pivotes, pasos = resolver_sistema_gauss_jordan_con_pasos(a, b)

            salida = (
                "RESPUESTA · SOLUCIÓN ÚNICA\nX =\n" + matriz_a_texto(solucion)
                if tipo == "unica" else
                "RESPUESTA · INFINITAS SOLUCIONES\n" + solucion_general_texto(a, b)
            )
            salida += (
                "\n\nTipo de solución: única."
                if tipo == "unica"
                else (
                    "\n\nUna solución particular (variables libres = 0):\nX =\n"
                    + matriz_a_texto(solucion)
                )
            )
            producto = multiplicar_matrices(a, solucion)
            comprobado = matrices_aproximadamente_iguales(producto, b)
            salida += (
                "\n\nCOMPROBACIÓN\nSustituimos la X mostrada en A·X y comparamos con B.\n\n"
                "A·X =\n" + matriz_a_texto(producto)
                + "\n\nB =\n" + matriz_a_texto(b)
                + ("\n\n✓ La solución comprobada satisface A·X = B." if comprobado else "\n\n✗ La solución no coincide con B.")
            )
            salida += (
                "\n\nEXPLICACIÓN PASO A PASO\n"
                "Usamos Gauss-Jordan: transformamos [A | B] mediante operaciones de fila "
                "hasta poder leer los valores de X.\n"
                "Columnas con pivote: " + (", ".join(str(i + 1) for i in pivotes) or "ninguna")
                + _bloque(pasos)
            )
            mostrar_texto(self.txt_resultado, salida)

            texto_x = "\n".join(
                " ".join(repr(float(x)) for x in fila)
                for fila in solucion
            )
            self.txt_x.delete("1.0", "end")
            self.txt_x.insert("1.0", texto_x)
        except ErrorSistemaIncompatible as error:
            mostrar_texto(self.txt_resultado,
                          "SIN SOLUCIÓN\nEl sistema es incompatible: ninguna X satisface A·X = B."
                          "\n\nEXPLICACIÓN PASO A PASO" + _bloque(error.pasos))
        except ValueError as error:
            mostrar_texto(self.txt_resultado, "NO SE PUDO RESOLVER\nRevisa los datos ingresados.\n\n" + str(error))
            mostrar_error(error)

    def _accion_evaluar(self):
        try:
            # Multiplica la X ingresada por A y compara cada entrada con B.
            a = leer_matriz(self.txt_a.get("1.0", "end"), "matriz A")
            b = leer_matriz(self.txt_b.get("1.0", "end"), "matriz B")
            x = leer_matriz(self.txt_x.get("1.0", "end"), "matriz X")

            producto = multiplicar_matrices(a, x)
            cumple = matrices_aproximadamente_iguales(producto, b)
            filas_a, columnas_a = dimensiones(a)
            _, columnas_x = dimensiones(x)
            escala_a, escala_x = escala_de(a), escala_de(x)
            escala_producto, escala_b = escala_de(producto), escala_de(b)
            calculos = []
            for i in range(filas_a):
                for j in range(columnas_x):
                    expresion = " + ".join(
                        f"({limpiar_numero(a[i][k], escala_a)}×"
                        f"{limpiar_numero(x[k][j], escala_x)})"
                        for k in range(columnas_a)
                    )
                    calculos.append(
                        f"(A·X)[{i + 1},{j + 1}] = {expresion} = "
                        f"{limpiar_numero(producto[i][j], escala_producto)}"
                    )

            comparaciones = []
            for i in range(len(producto)):
                for j in range(len(producto[0])):
                    simbolo = (
                        "≈"
                        if numeros_aproximadamente_iguales(producto[i][j], b[i][j])
                        else "≠"
                    )
                    comparaciones.append(
                        f"Posición [{i + 1},{j + 1}]: "
                        f"{limpiar_numero(producto[i][j], escala_producto)} {simbolo} "
                        f"{limpiar_numero(b[i][j], escala_b)}"
                    )

            pasos = [
                "PASO 1. Calcular A·X fila por columna:\n" + "\n".join(calculos),
                "PASO 2. Matriz obtenida A·X:\n\n" + matriz_a_texto(producto),
                "PASO 3. Comparar A·X con B posición por posición:\n" + "\n".join(comparaciones),
                "PASO 4. Conclusión: " + (
                    "todas las entradas coinciden, por lo tanto X sí cumple A·X=B."
                    if cumple
                    else "hay al menos una entrada diferente, por lo tanto X no cumple A·X=B."
                ),
            ]
            salida = (
                ("RESPUESTA · X SÍ CUMPLE A · X = B." if cumple else "RESPUESTA · X NO CUMPLE A · X = B.")
                + "\n\nEXPLICACIÓN PASO A PASO" + _bloque(pasos)
            )
            mostrar_texto(self.txt_resultado, salida)
        except ValueError as error:
            mostrar_texto(self.txt_resultado, "NO SE PUDO COMPROBAR\nRevisa los datos ingresados.\n\n" + str(error))
            mostrar_error(error)

    def _limpiar(self):
        for caja in (self.txt_a, self.txt_b, self.txt_x):
            caja.delete("1.0", "end")
        mostrar_texto(self.txt_resultado, "")
