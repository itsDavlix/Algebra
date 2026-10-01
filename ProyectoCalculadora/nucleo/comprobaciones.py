"""Funciones reutilizables para comprobar resultados de la calculadora."""

from nucleo.numeros import asegurar_finito
from nucleo.matrices import dimensiones

TOLERANCIA = 1e-8


def numeros_aproximadamente_iguales(a, b, tolerancia=TOLERANCIA):
    """Compara dos números finitos admitiendo pequeños errores de redondeo."""
    a = asegurar_finito(a, "Primer valor de la comprobación")
    b = asegurar_finito(b, "Segundo valor de la comprobación")
    tolerancia = asegurar_finito(tolerancia, "La tolerancia")
    if tolerancia < 0:
        raise ValueError("La tolerancia de comprobación no puede ser negativa.")
    return abs(a - b) <= tolerancia


def vectores_aproximadamente_iguales(a, b, tolerancia=TOLERANCIA):
    """Devuelve True si dos vectores tienen igual dimensión y valores equivalentes."""
    if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)):
        raise ValueError("Los valores a comprobar deben ser vectores.")
    if len(a) != len(b):
        return False
    return all(
        numeros_aproximadamente_iguales(x, y, tolerancia)
        for x, y in zip(a, b)
    )


def matrices_aproximadamente_iguales(a, b, tolerancia=TOLERANCIA):
    """Devuelve True si dos matrices tienen igual tamaño y entradas equivalentes."""
    if dimensiones(a) != dimensiones(b):
        return False
    filas, columnas = dimensiones(a)
    return all(
        numeros_aproximadamente_iguales(a[i][j], b[i][j], tolerancia)
        for i in range(filas)
        for j in range(columnas)
    )


def matriz_identidad(orden):
    """Construye una matriz identidad de tamaño ``orden`` para comprobaciones."""
    if isinstance(orden, bool) or not isinstance(orden, int) or orden <= 0:
        raise ValueError("El orden de la matriz identidad debe ser un entero positivo.")
    return [
        [1.0 if i == j else 0.0 for j in range(orden)]
        for i in range(orden)
    ]
