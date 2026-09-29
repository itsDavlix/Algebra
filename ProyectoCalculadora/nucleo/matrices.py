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