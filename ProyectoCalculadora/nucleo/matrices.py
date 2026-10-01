"""Módulo de matrices: lectura, formato y operaciones algebraicas básicas."""

import re

from nucleo.numeros import convertir_numero, limpiar_numero, asegurar_finito, EPSILON

MAX_FILAS = 40
MAX_COLUMNAS = 40


def _validar_matriz(matriz, nombre="La matriz", validar_limites=True):
    if not isinstance(matriz, (list, tuple)) or not matriz:
        raise ValueError(f"{nombre} no puede estar vacía.")
    if not isinstance(matriz[0], (list, tuple)) or not matriz[0]:
        raise ValueError(f"{nombre} debe contener al menos una columna.")
    columnas = len(matriz[0])
    if validar_limites and (len(matriz) > MAX_FILAS or columnas > MAX_COLUMNAS):
        raise ValueError(
            f"{nombre} excede el tamaño máximo permitido de {MAX_FILAS}×{MAX_COLUMNAS}."
        )
    for i, fila in enumerate(matriz, 1):
        if not isinstance(fila, (list, tuple)) or len(fila) != columnas:
            raise ValueError(f"{nombre} no es rectangular: revisa la fila {i}.")
        for j, valor in enumerate(fila, 1):
            asegurar_finito(valor, f"Elemento [{i},{j}] de {nombre.lower()}")
    return len(matriz), columnas


def leer_matriz(texto, nombre="matriz"):
    """Interpreta una matriz por filas y reporta la ubicación exacta de entradas inválidas."""
    texto = str(texto).strip()
    if not texto:
        raise ValueError(f"Escribe datos para la {nombre} antes de continuar.")

    lineas_originales = texto.splitlines()
    if any(not linea.strip() for linea in lineas_originales):
        raise ValueError(
            f"La {nombre} contiene una fila vacía. Elimina líneas en blanco entre las filas."
        )
    if len(lineas_originales) > MAX_FILAS:
        raise ValueError(f"La {nombre} supera el máximo de {MAX_FILAS} filas.")

    matriz = []
    columnas = None
    for numero_linea, linea in enumerate(lineas_originales, start=1):
        limpio = linea.strip()
        if limpio.startswith(",") or limpio.endswith(",") or re.search(r",\s*,", limpio):
            raise ValueError(
                f"Fila {numero_linea} de la {nombre}: hay una coma sin número."
            )
        partes = limpio.replace(",", " ").split()
        if len(partes) > MAX_COLUMNAS:
            raise ValueError(
                f"Fila {numero_linea} de la {nombre}: supera el máximo de {MAX_COLUMNAS} columnas."
            )
        fila = [
            convertir_numero(parte, f"Elemento [{numero_linea},{columna}] de la {nombre}")
            for columna, parte in enumerate(partes, start=1)
        ]
        if columnas is None:
            columnas = len(fila)
        elif len(fila) != columnas:
            raise ValueError(
                f"La {nombre} no es rectangular: la fila 1 tiene {columnas} elementos "
                f"y la fila {numero_linea} tiene {len(fila)}."
            )
        matriz.append(fila)

    _validar_matriz(matriz, f"La {nombre}")
    return matriz


def matriz_a_texto(matriz):
    if not matriz:
        return "[]"
    _validar_matriz(matriz)
    return "\n".join("[ " + "   ".join(limpiar_numero(x) for x in fila) + " ]" for fila in matriz)


def matriz_ampliada_a_texto(matriz, separacion):
    _validar_matriz(matriz, "La matriz ampliada", validar_limites=False)
    if not isinstance(separacion, int) or not 0 < separacion < len(matriz[0]):
        raise ValueError("La separación de la matriz ampliada no es válida.")
    lineas = []
    for fila in matriz:
        izquierda = "   ".join(limpiar_numero(x) for x in fila[:separacion])
        derecha = "   ".join(limpiar_numero(x) for x in fila[separacion:])
        lineas.append(f"[ {izquierda}   |   {derecha} ]")
    return "\n".join(lineas)


def dimensiones(matriz):
    return _validar_matriz(matriz)


def _validar_mismas_dimensiones(a, b):
    da, db = dimensiones(a), dimensiones(b)
    if da != db:
        raise ValueError(f"Las matrices deben tener el mismo tamaño: A es {da[0]}×{da[1]} y B es {db[0]}×{db[1]}.")


def sumar_matrices(a, b):
    _validar_mismas_dimensiones(a, b)
    return [[asegurar_finito(a[i][j] + b[i][j], f"Resultado [{i+1},{j+1}]") for j in range(len(a[0]))] for i in range(len(a))]


def restar_matrices(a, b):
    _validar_mismas_dimensiones(a, b)
    return [[asegurar_finito(a[i][j] - b[i][j], f"Resultado [{i+1},{j+1}]") for j in range(len(a[0]))] for i in range(len(a))]


def multiplicar_matriz_escalar(matriz, escalar):
    dimensiones(matriz)
    escalar = asegurar_finito(escalar, "El escalar")
    return [[asegurar_finito(escalar * valor, f"Resultado [{i+1},{j+1}]") for j, valor in enumerate(fila)] for i, fila in enumerate(matriz)]


def multiplicar_matrices(a, b):
    filas_a, columnas_a = dimensiones(a)
    filas_b, columnas_b = dimensiones(b)
    if columnas_a != filas_b:
        raise ValueError(
            f"No se pueden multiplicar: A es {filas_a}×{columnas_a} y B es {filas_b}×{columnas_b}. "
            f"Se necesita columnas(A) = filas(B), pero {columnas_a} ≠ {filas_b}."
        )
    resultado = []
    for i in range(filas_a):
        fila = []
        for j in range(columnas_b):
            total = 0.0
            for k in range(columnas_a):
                producto = asegurar_finito(a[i][k] * b[k][j], f"Producto intermedio para [{i+1},{j+1}]")
                total = asegurar_finito(total + producto, f"Resultado [{i+1},{j+1}]")
            fila.append(total)
        resultado.append(fila)
    return resultado


def matrices_aproximadamente_iguales(a, b):
    if dimensiones(a) != dimensiones(b):
        return False
    filas, columnas = dimensiones(a)
    return all(abs(a[i][j] - b[i][j]) <= 1e-8 for i in range(filas) for j in range(columnas))


def matriz_inversa_con_pasos(matriz):
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError(f"La matriz debe ser cuadrada para calcular su inversa; recibiste {filas}×{columnas}.")

    n = filas
    aumentada = []
    for i in range(n):
        identidad = [1.0 if i == j else 0.0 for j in range(n)]
        aumentada.append([float(valor) for valor in matriz[i]] + identidad)

    pasos = [
        "PASO 1. Verificar que A sea cuadrada.\n" f"A tiene {filas} filas y {columnas} columnas, por lo tanto sí es cuadrada.",
        "PASO 2. Formar la matriz aumentada [A | I].\n\n" + matriz_ampliada_a_texto(aumentada, n),
    ]
    numero_paso = 3

    for columna in range(n):
        fila_pivote = max(range(columna, n), key=lambda i: abs(aumentada[i][columna]))
        if abs(aumentada[fila_pivote][columna]) <= EPSILON:
            raise ValueError("La matriz no tiene inversa porque es singular (determinante igual a 0).")

        if fila_pivote != columna:
            aumentada[columna], aumentada[fila_pivote] = aumentada[fila_pivote], aumentada[columna]
            pasos.append(f"PASO {numero_paso}. Intercambiar F{columna + 1} ↔ F{fila_pivote + 1}.\n\n" + matriz_ampliada_a_texto(aumentada, n))
            numero_paso += 1

        pivote = aumentada[columna][columna]
        if abs(pivote - 1.0) > EPSILON:
            aumentada[columna] = [asegurar_finito(valor / pivote, "Valor durante Gauss-Jordan") for valor in aumentada[columna]]
            pasos.append(f"PASO {numero_paso}. Convertir el pivote de la columna {columna + 1} en 1:\nF{columna + 1} ← F{columna + 1} ÷ ({limpiar_numero(pivote)}).\n\n" + matriz_ampliada_a_texto(aumentada, n))
            numero_paso += 1

        for i in range(n):
            if i == columna:
                continue
            factor = aumentada[i][columna]
            if abs(factor) > EPSILON:
                nueva_fila = []
                for j in range(2 * n):
                    valor = aumentada[i][j] - factor * aumentada[columna][j]
                    nueva_fila.append(asegurar_finito(valor, "Valor durante Gauss-Jordan"))
                aumentada[i] = nueva_fila
                signo = "−" if factor >= 0 else "+"
                magnitud = limpiar_numero(abs(factor))
                pasos.append(f"PASO {numero_paso}. Hacer 0 la entrada de F{i + 1}, columna {columna + 1}:\nF{i + 1} ← F{i + 1} {signo} ({magnitud})F{columna + 1}.\n\n" + matriz_ampliada_a_texto(aumentada, n))
                numero_paso += 1

    inversa = [[0.0 if abs(valor) <= EPSILON else asegurar_finito(valor) for valor in fila[n:]] for fila in aumentada]
    pasos.append(f"PASO {numero_paso}. La parte izquierda ya es I; por eso la parte derecha es A⁻¹.\n\nA⁻¹ =\n" + matriz_a_texto(inversa))
    return inversa, pasos


def matriz_inversa(matriz):
    inversa, _ = matriz_inversa_con_pasos(matriz)
    return inversa
