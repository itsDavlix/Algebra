"""Módulo de utilidades numéricas: conversión y formato de valores."""

EPSILON = 1e-10


def limpiar_numero(numero):
    """Redondea un valor casi entero y da formato legible a los decimales."""
    if abs(numero - round(numero)) < EPSILON:
        return str(int(round(numero)))
    return f"{numero:.6f}".rstrip("0").rstrip(".")


def convertir_numero(texto):
    """Convierte texto a float, rechazando valores no finitos (NaN, infinito)."""
    texto = texto.strip()
    if texto == "":
        raise ValueError("Falta un número. Revisa los datos que escribiste.")
    try:
        numero = float(texto)
    except ValueError:
        raise ValueError(f"{texto!r} no parece ser un número válido.")
    if numero != numero or numero in (float("inf"), float("-inf")):
        raise ValueError("Solo se permiten números reales finitos.")
    return numero