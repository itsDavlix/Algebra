"""Módulo de vectores: lectura, formato y operaciones algebraicas en R^n."""

from nucleo.numeros import convertir_numero, limpiar_numero


def leer_vector(texto):
    """Interpreta un vector escrito en una línea, separado por comas o espacios."""
    partes = texto.strip().replace(",", " ").split()
    if not partes:
        raise ValueError("Escribe un vector antes de continuar.")
    return [convertir_numero(parte) for parte in partes]


def vector_a_texto(vector):
    """Da formato (a, b, c, ...) a un vector para mostrarlo en pantalla."""
    return "(" + ", ".join(limpiar_numero(x) for x in vector) + ")"


def _validar_misma_dimension(v1, v2):
    """Dos vectores solo se suman o restan si tienen igual cantidad de componentes."""
    if len(v1) != len(v2):
        raise ValueError("Los dos vectores deben tener la misma cantidad de componentes.")


def sumar_vectores(v1, v2):
    """Suma componente a componente: (a1,...,an) + (b1,...,bn) = (a1+b1,...,an+bn)."""
    _validar_misma_dimension(v1, v2)
    return [a + b for a, b in zip(v1, v2)]


def restar_vectores(v1, v2):
    """Resta componente a componente: (a1,...,an) - (b1,...,bn) = (a1-b1,...,an-bn)."""
    _validar_misma_dimension(v1, v2)
    return [a - b for a, b in zip(v1, v2)]


def multiplicar_vector_escalar(vector, escalar):
    """Multiplicación por escalar: k(a1,...,an) = (k*a1,...,k*an)."""
    return [escalar * componente for componente in vector]