"""Determinantes por expansión de cofactores y factorización LU con pivoteo."""

from fractions import Fraction
from nucleo.matrices import dimensiones
from nucleo.numeros import asegurar_finito


# La cota limita el trabajo factorial sin impedir matrices grandes con muchos ceros.
MAX_EXPANSIONES = 100000


def _preparar(matriz):
    """Valida una matriz cuadrada y copia sus valores como racionales exactos."""
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError("El determinante requiere una matriz cuadrada.")
    # Los racionales evitan descartar pivotes pequeños y errores de cancelación.
    # Se conserva exactamente el valor numérico recibido por el núcleo.
    return [[Fraction(asegurar_finito(valor)) for valor in fila] for fila in matriz]


def recomendar_metodo(matriz):
    """Devuelve una recomendación previa basada en el orden, sin calcular el determinante."""
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError("El determinante requiere una matriz cuadrada.")
    if filas <= 3:
        return ("cofactores", "Se recomiendan cofactores: para órdenes de 1 a 3, "
                "las fórmulas cortas suelen requerir menos trabajo que factorizar LU.")
    return ("lu", "Se recomienda LU: requiere O(n³) operaciones aritméticas, frente "
            "a O(n!) de cofactores en el peor caso. Es una estimación general; "
            "los ceros pueden reducir mucho el trabajo de cofactores.")


def determinante_cofactores(matriz):
    """Expande por la fila con más ceros y omite los términos nulos."""
    a = _preparar(matriz)
    expansiones = 0

    def expandir(actual):
        """Resuelve los casos base y construye los menores con su signo alternado."""
        nonlocal expansiones
        expansiones += 1
        if expansiones > MAX_EXPANSIONES:
            raise ValueError("Cofactores superó el límite de 100000 expansiones. "
                             "Seleccioná LU para calcular esta matriz.")
        n = len(actual)
        if n == 1:
            return actual[0][0]
        if n == 2:
            return actual[0][0] * actual[1][1] - actual[0][1] * actual[1][0]

        # Una fila nula da determinante cero; los demás ceros no generan menores.
        fila = max(range(n), key=lambda i: actual[i].count(0))
        total = Fraction(0)
        for columna, valor in enumerate(actual[fila]):
            if valor == 0:
                continue
            menor = [r[:columna] + r[columna + 1:]
                     for i, r in enumerate(actual) if i != fila]
            total += (-1) ** (fila + columna) * valor * expandir(menor)
        return total

    return expandir(a)


def determinante_lu(matriz):
    """Calcula det(A) = (-1)^intercambios · producto(diagonal(U)), con PA = LU."""
    u = _preparar(matriz)
    n = len(u)
    signo = 1

    # El pivoteo parcial elige el mayor valor absoluto disponible en cada columna.
    for columna in range(n):
        pivote = max(range(columna, n), key=lambda i: abs(u[i][columna]))
        if u[pivote][columna] == 0:
            return Fraction(0)
        if pivote != columna:
            u[columna], u[pivote] = u[pivote], u[columna]
            signo *= -1

        # Los multiplicadores son las entradas de L, cuya diagonal vale uno.
        # Basta conservar U porque det(L) = 1; la matriz original no se modifica.
        for fila in range(columna + 1, n):
            factor = u[fila][columna] / u[columna][columna]
            u[fila][columna] = Fraction(0)
            for j in range(columna + 1, n):
                u[fila][j] -= factor * u[columna][j]

    # Cada intercambio cambia el signo del determinante una sola vez.
    resultado = Fraction(signo)
    for i in range(n):
        resultado *= u[i][i]
    return resultado


def determinante(matriz, metodo):
    """Ejecuta únicamente el método elegido y rechaza opciones desconocidas."""
    if metodo == "cofactores":
        return determinante_cofactores(matriz)
    if metodo == "lu":
        return determinante_lu(matriz)
    raise ValueError("Seleccioná cofactores o LU.")


def formatear_determinante(valor):
    """Muestra enteros exactos o una aproximación sin redondear valores pequeños a cero."""
    if valor.denominator == 1:
        return str(valor.numerator)
    try:
        aproximado = asegurar_finito(valor)
    except ValueError:
        return str(valor)
    # La fracción preserva valores que no se pueden representar como decimales finitos.
    if aproximado == 0 and valor != 0:
        return str(valor)
    return f"≈ {aproximado:.12g}"
