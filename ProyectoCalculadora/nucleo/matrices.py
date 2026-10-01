"""Módulo de matrices: lectura, formato y operaciones algebraicas básicas."""

from nucleo.numeros import convertir_numero, limpiar_numero


def leer_matriz(texto):
    """Interpreta una matriz escrita por filas (una fila por línea)."""
    lineas = [linea for linea in texto.strip().splitlines() if linea.strip()]
    if not lineas:
        raise ValueError("No encontré datos para formar la matriz.")

    matriz = []
    columnas = None
    for numero_linea, linea in enumerate(lineas, start=1):
        fila = [convertir_numero(parte) for parte in linea.replace(",", " ").split()]
        if not fila:
            raise ValueError(f"La fila {numero_linea} está vacía.")
        if columnas is None:
            columnas = len(fila)
        elif len(fila) != columnas:
            raise ValueError(
                f"La matriz no está bien formada: todas sus filas deben tener {columnas} elementos."
            )
        matriz.append(fila)
    return matriz


def matriz_a_texto(matriz):
    """Da formato de filas [ ... ] a una matriz para mostrarla en pantalla."""
    if not matriz:
        return "[]"
    return "\n".join("[ " + "   ".join(limpiar_numero(x) for x in fila) + " ]" for fila in matriz)


def matriz_ampliada_a_texto(matriz, separacion):
    """Formatea una matriz aumentada marcando la separación con una barra vertical."""
    lineas = []
    for fila in matriz:
        izquierda = "   ".join(limpiar_numero(x) for x in fila[:separacion])
        derecha = "   ".join(limpiar_numero(x) for x in fila[separacion:])
        lineas.append(f"[ {izquierda}   |   {derecha} ]")
    return "\n".join(lineas)


def dimensiones(matriz):
    """Retorna (cantidad de filas, cantidad de columnas) de una matriz."""
    return len(matriz), len(matriz[0])


def _validar_mismas_dimensiones(a, b):
    """La suma o resta de matrices exige que ambas tengan el mismo tamaño."""
    if dimensiones(a) != dimensiones(b):
        raise ValueError("Para sumar o restar, las dos matrices deben tener el mismo tamaño.")


def sumar_matrices(a, b):
    """Suma elemento a elemento: C[i][j] = A[i][j] + B[i][j]."""
    _validar_mismas_dimensiones(a, b)
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def restar_matrices(a, b):
    """Resta elemento a elemento: C[i][j] = A[i][j] - B[i][j]."""
    _validar_mismas_dimensiones(a, b)
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def multiplicar_matriz_escalar(matriz, escalar):
    """Multiplica cada entrada por el escalar k: C[i][j] = k * A[i][j]."""
    return [[escalar * valor for valor in fila] for fila in matriz]


def multiplicar_matrices(a, b):
    """
    Producto matricial C = A·B, válido solo si columnas de A = filas de B.
    Cada entrada se calcula como C[i][j] = suma(A[i][k] * B[k][j]).
    """
    filas_a, columnas_a = dimensiones(a)
    filas_b, columnas_b = dimensiones(b)
    if columnas_a != filas_b:
        raise ValueError(
            "No se pueden multiplicar estas matrices. La cantidad de columnas de A "
            "debe coincidir con la cantidad de filas de B."
        )
    return [
        [sum(a[i][k] * b[k][j] for k in range(columnas_a)) for j in range(columnas_b)]
        for i in range(filas_a)
    ]


def matrices_aproximadamente_iguales(a, b):
    """Compara dos matrices con una pequeña tolerancia numérica (errores de redondeo)."""
    if dimensiones(a) != dimensiones(b):
        return False
    filas, columnas = dimensiones(a)
    return all(
        abs(a[i][j] - b[i][j]) <= 1e-8 for i in range(filas) for j in range(columnas)
    )


def matriz_inversa_con_pasos(matriz):
    """Calcula A⁻¹ por Gauss-Jordan y devuelve también el procedimiento explicado."""
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError("La matriz debe ser cuadrada para poder calcular su inversa.")

    n = filas
    aumentada = []
    for i in range(n):
        identidad = [1.0 if i == j else 0.0 for j in range(n)]
        aumentada.append([float(valor) for valor in matriz[i]] + identidad)

    pasos = [
        "PASO 1. Verificar que A sea cuadrada.\n"
        f"A tiene {filas} filas y {columnas} columnas, por lo tanto sí es cuadrada.",
        "PASO 2. Formar la matriz aumentada [A | I].\n\n"
        + matriz_ampliada_a_texto(aumentada, n),
    ]
    numero_paso = 3

    for columna in range(n):
        fila_pivote = max(range(columna, n), key=lambda i: abs(aumentada[i][columna]))
        if abs(aumentada[fila_pivote][columna]) <= 1e-10:
            raise ValueError(
                "La matriz no tiene inversa porque es singular (determinante igual a 0)."
            )

        if fila_pivote != columna:
            aumentada[columna], aumentada[fila_pivote] = aumentada[fila_pivote], aumentada[columna]
            pasos.append(
                f"PASO {numero_paso}. Intercambiar F{columna + 1} ↔ F{fila_pivote + 1} "
                "para colocar un pivote no nulo.\n\n"
                + matriz_ampliada_a_texto(aumentada, n)
            )
            numero_paso += 1

        pivote = aumentada[columna][columna]
        if abs(pivote - 1.0) > 1e-10:
            aumentada[columna] = [valor / pivote for valor in aumentada[columna]]
            pasos.append(
                f"PASO {numero_paso}. Convertir el pivote de la columna {columna + 1} en 1:\n"
                f"F{columna + 1} ← F{columna + 1} ÷ ({limpiar_numero(pivote)}).\n\n"
                + matriz_ampliada_a_texto(aumentada, n)
            )
            numero_paso += 1

        for i in range(n):
            if i == columna:
                continue
            factor = aumentada[i][columna]
            if abs(factor) > 1e-10:
                aumentada[i] = [
                    aumentada[i][j] - factor * aumentada[columna][j]
                    for j in range(2 * n)
                ]
                signo = "−" if factor >= 0 else "+"
                magnitud = limpiar_numero(abs(factor))
                pasos.append(
                    f"PASO {numero_paso}. Hacer 0 la entrada de F{i + 1}, columna {columna + 1}:\n"
                    f"F{i + 1} ← F{i + 1} {signo} ({magnitud})F{columna + 1}.\n\n"
                    + matriz_ampliada_a_texto(aumentada, n)
                )
                numero_paso += 1

    inversa = [fila[n:] for fila in aumentada]
    inversa = [
        [0.0 if abs(valor) <= 1e-10 else valor for valor in fila]
        for fila in inversa
    ]

    pasos.append(
        f"PASO {numero_paso}. La parte izquierda ya es I; por eso la parte derecha es A⁻¹.\n\n"
        "A⁻¹ =\n" + matriz_a_texto(inversa)
    )
    return inversa, pasos


def matriz_inversa(matriz):
    """Calcula la matriz inversa mediante eliminación Gauss-Jordan."""
    inversa, _ = matriz_inversa_con_pasos(matriz)
    return inversa
