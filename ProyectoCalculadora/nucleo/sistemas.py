"""Módulo de sistemas lineales: eliminación Gauss-Jordan y combinación lineal."""

from nucleo.numeros import EPSILON
from nucleo.matrices import dimensiones


def resolver_sistema_gauss_jordan(a, b):
    """
    Resuelve la ecuación matricial A·X = B mediante Gauss-Jordan.

    Procedimiento algebraico:
    1. Se arma la matriz aumentada [A | B].
    2. Se busca, columna por columna, una fila con pivote no nulo.
    3. Se normaliza esa fila (pivote = 1) y se anula el resto de la columna.
    4. Una fila del tipo 0 0 ... 0 | valor_no_cero indica un sistema incompatible.
    5. Las columnas sin pivote corresponden a variables libres, fijadas en 0
       para entregar una solución particular.

    Retorna: (solución X, tipo de solución "unica"/"infinitas", columnas pivote).
    """
    filas_a, columnas_a = dimensiones(a)
    filas_b, columnas_b = dimensiones(b)
    if filas_a != filas_b:
        raise ValueError("Para resolver A · X = B, A y B deben tener la misma cantidad de filas.")

    aumentada = [list(map(float, a[i])) + list(map(float, b[i])) for i in range(filas_a)]
    ancho = columnas_a + columnas_b
    fila_pivote = 0
    columnas_pivote = []

    for columna in range(columnas_a):
        mejor_fila, mejor_valor = None, 0.0
        for i in range(fila_pivote, filas_a):
            valor = abs(aumentada[i][columna])
            if valor > mejor_valor and valor > EPSILON:
                mejor_valor, mejor_fila = valor, i

        if mejor_fila is None:
            continue  # Columna sin pivote: variable libre.

        aumentada[fila_pivote], aumentada[mejor_fila] = aumentada[mejor_fila], aumentada[fila_pivote]

        pivote = aumentada[fila_pivote][columna]
        aumentada[fila_pivote] = [valor / pivote for valor in aumentada[fila_pivote]]

        for i in range(filas_a):
            if i == fila_pivote:
                continue
            factor = aumentada[i][columna]
            if abs(factor) > EPSILON:
                aumentada[i] = [
                    aumentada[i][j] - factor * aumentada[fila_pivote][j] for j in range(ancho)
                ]

        columnas_pivote.append(columna)
        fila_pivote += 1
        if fila_pivote == filas_a:
            break

    for fila in aumentada:
        if all(abs(valor) <= EPSILON for valor in fila[:columnas_a]):
            if any(abs(valor) > EPSILON for valor in fila[columnas_a:]):
                raise ValueError(
                    "No existe una solución: los datos de A y B hacen que el sistema sea incompatible."
                )

    solucion = [[0.0] * columnas_b for _ in range(columnas_a)]
    for indice_fila, columna_variable in enumerate(columnas_pivote):
        for j in range(columnas_b):
            solucion[columna_variable][j] = aumentada[indice_fila][columnas_a + j]

    tipo = "unica" if len(columnas_pivote) == columnas_a else "infinitas"
    return solucion, tipo, columnas_pivote


def verificar_combinacion_lineal(generadores, objetivo):
    """
    Determina si 'objetivo' es combinación lineal de 'generadores'.

    Se arma A colocando cada generador como columna y se resuelve A·c = objetivo;
    c son los coeficientes de la combinación buscada.
    """
    if not generadores:
        raise ValueError("Agrega al menos un vector en la lista de vectores generadores.")

    dimension = len(objetivo)
    for vector in generadores:
        if len(vector) != dimension:
            raise ValueError(
                "Todos los vectores generadores y el vector objetivo deben tener "
                "la misma cantidad de componentes."
            )

    a = [[vector[i] for vector in generadores] for i in range(dimension)]
    b = [[valor] for valor in objetivo]

    try:
        solucion, tipo, _ = resolver_sistema_gauss_jordan(a, b)
    except ValueError:
        return False, None, None

    return True, [fila[0] for fila in solucion], tipon