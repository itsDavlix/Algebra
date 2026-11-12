"""Módulo de matrices: lectura, formato y operaciones algebraicas básicas."""

import re

from nucleo.numeros import (
    convertir_numero, limpiar_numero, asegurar_finito, escala_de, umbral_cero,
)

MAX_FILAS = 40
MAX_COLUMNAS = 40


# Comprueba que la matriz sea rectangular, finita y esté dentro de los límites.
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


def _normalizar_lineas_matriz(texto):
    """Acepta filas separadas por salto de línea, punto y coma o barras verticales."""
    filas = []
    for bloque in re.split(r"[;\n]+", str(texto).strip()):
        bloque = bloque.strip()
        if not bloque:
            continue
        if "|" in bloque:
            filas.extend(part.strip() for part in bloque.split("|") if part.strip())
        else:
            filas.append(bloque)
    if not filas:
        raise ValueError("La matriz no contiene datos válidos.")
    return filas


def leer_matriz(texto, nombre="matriz"):
    """Interpreta una matriz por filas y reporta la ubicación exacta de entradas inválidas."""
    texto = str(texto).strip()
    if not texto:
        raise ValueError(f"Escribe datos para la {nombre} antes de continuar.")

    if any(not linea.strip() for linea in texto.splitlines()):
        raise ValueError(
            f"La {nombre} contiene una fila vacía. Elimina líneas en blanco entre las filas."
        )
    lineas_originales = _normalizar_lineas_matriz(texto)
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
        partes = re.split(r"[\s,]+", limpio)
        partes = [parte for parte in partes if parte]
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
    return "\n".join(
        "[ " + "   ".join(limpiar_numero(x, abs(x)) for x in fila) + " ]"
        for fila in matriz
    )


def matriz_ampliada_a_texto(matriz, separacion):
    _validar_matriz(matriz, "La matriz ampliada", validar_limites=False)
    if not isinstance(separacion, int) or not 0 < separacion < len(matriz[0]):
        raise ValueError("La separación de la matriz ampliada no es válida.")
    lineas = []
    for fila in matriz:
        izquierda = "   ".join(
            limpiar_numero(x, abs(x)) for x in fila[:separacion]
        )
        derecha = "   ".join(
            limpiar_numero(x, abs(x)) for x in fila[separacion:]
        )
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


def _buscar_pivote(matriz, fila_inicial, columna, umbral):
    """Busca la fila con mayor pivote absoluto que supere el umbral."""
    if fila_inicial >= len(matriz):
        return None
    fila = max(range(fila_inicial, len(matriz)), key=lambda i: abs(matriz[i][columna]))
    return fila if abs(matriz[fila][columna]) > umbral else None


def _normalizar_fila(matriz, indice_fila, pivote):
    """Divide una fila aumentada por su pivote y valida los resultados."""
    matriz[indice_fila] = [
        asegurar_finito(valor / pivote, "Valor durante Gauss-Jordan")
        for valor in matriz[indice_fila]
    ]


def _eliminar_columna(matriz, fila_pivote, columna, umbral, ancho):
    """Elimina una columna respecto del pivote y retorna las filas modificadas."""
    cambios = []
    for indice_fila in range(len(matriz)):
        if indice_fila == fila_pivote:
            continue
        factor = matriz[indice_fila][columna]
        # Las filas con pivote ya están normalizadas: el umbral de la matriz
        # original no sirve para descartar sus factores (por ejemplo 0.5).
        if factor == 0:
            continue
        nueva_fila = []
        for indice in range(ancho):
            producto = asegurar_finito(
                factor * matriz[fila_pivote][indice],
                "Producto durante Gauss-Jordan",
            )
            nueva_fila.append(
                asegurar_finito(
                    matriz[indice_fila][indice] - producto,
                    "Valor durante Gauss-Jordan",
                )
            )
        nueva_fila[columna] = 0.0
        matriz[indice_fila] = nueva_fila
        cambios.append((indice_fila, factor))
    return cambios


def _texto_paso_gauss_jordan(numero, titulo, aumentada, separacion, instruccion=None):
    """Formatea un paso de intercambio u operación de fila de Gauss-Jordan."""
    descripcion = titulo if instruccion is None else f"{titulo}\n{instruccion}"
    representacion = (
        matriz_a_texto(aumentada)
        if separacion is None
        else matriz_ampliada_a_texto(aumentada, separacion)
    )
    return (
        f"PASO {numero}. {descripcion}\n\n"
        + representacion
    )


def norma_1(matriz):
    """Calcula la mayor suma absoluta de columna de una matriz válida."""
    filas, columnas = dimensiones(matriz)
    return max(
        asegurar_finito(
            sum(abs(matriz[i][j]) for i in range(filas)),
            "La norma 1 de la matriz",
        )
        for j in range(columnas)
    )


def numero_condicion_1(matriz, inversa):
    """Calcula cond₁(A) como el producto de las normas 1 de A y A⁻¹."""
    dimensiones_a = dimensiones(matriz)
    if dimensiones_a != dimensiones(inversa):
        raise ValueError("La matriz y su inversa deben tener las mismas dimensiones.")
    if dimensiones_a[0] != dimensiones_a[1]:
        raise ValueError("El número de condición requiere una matriz cuadrada.")
    return asegurar_finito(
        norma_1(matriz) * norma_1(inversa),
        "El número de condición de la matriz",
    )


def matriz_transpuesta(matriz):
    """Intercambia filas y columnas de una matriz rectangular válida."""
    dimensiones(matriz)
    return [list(columna) for columna in zip(*matriz)]


def matriz_transpuesta_con_pasos(matriz):
    """Calcula la transpuesta, documenta el intercambio y comprueba la doble transpuesta."""
    transpuesta = matriz_transpuesta(matriz)
    recuperada = matriz_transpuesta(transpuesta)
    comprobada = recuperada == [list(fila) for fila in matriz]
    pasos = [
        "PASO 1. Intercambiar cada fila de A por una columna de Aᵀ.",
        "PASO 2. Formar la matriz transpuesta:\nAᵀ =\n" + matriz_a_texto(transpuesta),
        "COMPROBACIÓN. Transponer Aᵀ debe recuperar A:\n"
        + ("✓ (Aᵀ)ᵀ = A." if comprobada else "✗ La doble transpuesta no coincide."),
    ]
    return transpuesta, pasos


def _rango_por_eliminacion(matriz, nombre="A", registrar_pasos=False):
    """Reduce una copia de la matriz y retorna el rango y sus pasos opcionales."""
    filas, columnas = dimensiones(matriz)
    reducida = [[float(valor) for valor in fila] for fila in matriz]
    umbral = umbral_cero(escala_de(matriz))
    pasos = [f"PASO 1. Copiar {nombre} para aplicar eliminación por filas."]
    fila_pivote = 0
    numero_paso = 2
    for columna in range(columnas):
        mejor_fila = _buscar_pivote(reducida, fila_pivote, columna, umbral)
        if mejor_fila is None:
            if registrar_pasos:
                pasos.append(
                    f"PASO {numero_paso}. La columna {columna + 1} no tiene pivote "
                    "distinto de cero a la escala de la matriz."
                )
                numero_paso += 1
            continue
        if mejor_fila != fila_pivote:
            reducida[fila_pivote], reducida[mejor_fila] = (
                reducida[mejor_fila], reducida[fila_pivote]
            )
            if registrar_pasos:
                pasos.append(_texto_paso_gauss_jordan(
                    numero_paso,
                    f"Intercambiar F{fila_pivote + 1} ↔ F{mejor_fila + 1}.",
                    reducida, None,
                ))
                numero_paso += 1

        pivote = reducida[fila_pivote][columna]
        if pivote != 1.0:
            _normalizar_fila(reducida, fila_pivote, pivote)
            if registrar_pasos:
                pasos.append(_texto_paso_gauss_jordan(
                    numero_paso, f"Normalizar F{fila_pivote + 1}:",
                    reducida, None,
                    f"F{fila_pivote + 1} ← F{fila_pivote + 1} ÷ "
                    f"({limpiar_numero(pivote, escala_de(matriz))}).",
                ))
                numero_paso += 1

        cambios = _eliminar_columna(
            reducida, fila_pivote, columna, umbral, columnas,
        )
        if registrar_pasos:
            for indice_fila, factor in cambios:
                signo = "−" if factor >= 0 else "+"
                pasos.append(_texto_paso_gauss_jordan(
                    numero_paso,
                    f"Eliminar la entrada de F{indice_fila + 1}, columna {columna + 1}:",
                    reducida, None,
                    f"F{indice_fila + 1} ← F{indice_fila + 1} {signo} "
                    f"({limpiar_numero(abs(factor), abs(factor))})F{fila_pivote + 1}.",
                ))
                numero_paso += 1
        fila_pivote += 1
        if fila_pivote == filas:
            break
    return fila_pivote, pasos


def rango_matriz_con_pasos(matriz):
    """Calcula el rango y verifica que coincida con el de la matriz transpuesta."""
    rango, pasos = _rango_por_eliminacion(matriz, registrar_pasos=True)
    transpuesta = matriz_transpuesta(matriz)
    rango_transpuesta, _ = _rango_por_eliminacion(transpuesta)
    pasos.append(
        "COMPROBACIÓN. Comparar rango(A) y rango(Aᵀ): "
        f"{rango} = {rango_transpuesta}."
        + (" ✓ La igualdad se cumple." if rango == rango_transpuesta else " ✗ La igualdad no se cumple.")
    )
    return rango, pasos


def rango_matriz(matriz):
    """Devuelve el rango de una matriz usando eliminación con tolerancia relativa."""
    rango, _ = rango_matriz_con_pasos(matriz)
    return rango


def matriz_inversa_con_pasos(matriz):
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError(f"La matriz debe ser cuadrada para calcular su inversa; recibiste {filas}×{columnas}.")

    # Se combina A con la identidad para transformar [A | I] en [I | A⁻¹].
    n = filas
    umbral = umbral_cero(escala_de(matriz))
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
        fila_pivote = _buscar_pivote(aumentada, columna, columna, umbral)
        if fila_pivote is None:
            raise ValueError("La matriz no tiene inversa porque es singular (determinante igual a 0).")

        if fila_pivote != columna:
            aumentada[columna], aumentada[fila_pivote] = aumentada[fila_pivote], aumentada[columna]
            pasos.append(_texto_paso_gauss_jordan(
                numero_paso, f"Intercambiar F{columna + 1} ↔ F{fila_pivote + 1}.",
                aumentada, n,
            ))
            numero_paso += 1

        pivote = aumentada[columna][columna]
        if pivote != 1.0:
            _normalizar_fila(aumentada, columna, pivote)
            pasos.append(_texto_paso_gauss_jordan(
                numero_paso, f"Convertir el pivote de la columna {columna + 1} en 1:",
                aumentada, n,
                f"F{columna + 1} ← F{columna + 1} ÷ ({limpiar_numero(pivote, escala_de(matriz))}).",
            ))
            numero_paso += 1

        cambios = _eliminar_columna(aumentada, columna, columna, umbral, 2 * n)
        for indice_fila, factor in cambios:
            signo = "−" if factor >= 0 else "+"
            magnitud = limpiar_numero(abs(factor), abs(factor))
            pasos.append(_texto_paso_gauss_jordan(
                numero_paso,
                f"Hacer 0 la entrada de F{indice_fila + 1}, columna {columna + 1}:",
                aumentada, n,
                f"F{indice_fila + 1} ← F{indice_fila + 1} {signo} ({magnitud})F{columna + 1}.",
            ))
            numero_paso += 1

    inversa_sin_limpiar = [
        [asegurar_finito(valor, "Elemento de la matriz inversa") for valor in fila[n:]]
        for fila in aumentada
    ]
    escala_inversa = escala_de(inversa_sin_limpiar)
    inversa = [
        [
            0.0 if abs(valor) <= umbral_cero(escala_inversa) else valor
            for valor in fila
        ]
        for fila in inversa_sin_limpiar
    ]
    pasos.append(f"PASO {numero_paso}. La parte izquierda ya es I; por eso la parte derecha es A⁻¹.\n\nA⁻¹ =\n" + matriz_a_texto(inversa))
    condicion = numero_condicion_1(matriz, inversa)
    if condicion > 1e8:
        cifras = len(str(int(condicion))) - 1
        pasos.append(
            "ADVERTENCIA. A está mal condicionada: "
            f"cond₁(A) ≈ {limpiar_numero(condicion)}; "
            f"pierde aproximadamente {cifras} cifras significativas."
        )
    return inversa, pasos


def matriz_inversa(matriz):
    inversa, _ = matriz_inversa_con_pasos(matriz)
    return inversa
