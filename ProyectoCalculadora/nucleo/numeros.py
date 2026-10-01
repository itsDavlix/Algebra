"""Utilidades numéricas: validación, conversión y formato seguro de valores."""

import math
import re

EPSILON = 1e-10

# Acepta enteros, decimales con punto y notación científica. No acepta NaN/Inf,
# guiones bajos ni expresiones para evitar entradas ambiguas.
_PATRON_NUMERO = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


def asegurar_finito(numero, contexto="El resultado"):
    """Valida que un valor sea un número real finito y devuelve float(numero)."""
    try:
        valor = float(numero)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{contexto} no es un número real válido.") from exc
    if not math.isfinite(valor):
        raise ValueError(
            f"{contexto} es demasiado grande o no es finito. Usa valores de menor magnitud."
        )
    return valor


def limpiar_numero(numero):
    """Da formato legible a un número finito, evitando -0 y decimales innecesarios."""
    numero = asegurar_finito(numero)
    if abs(numero) <= EPSILON:
        return "0"

    # Evita convertir números gigantes a int solo para mostrarlos.
    if abs(numero) < 1e15 and abs(numero - round(numero)) < EPSILON:
        return str(int(round(numero)))

    # Notación científica para magnitudes que serían poco legibles en decimal fijo.
    if abs(numero) >= 1e9 or abs(numero) < 1e-6:
        return f"{numero:.6g}"
    return f"{numero:.6f}".rstrip("0").rstrip(".")


def convertir_numero(texto, contexto="El valor"):
    """Convierte texto a float con sintaxis controlada y rechazo explícito de NaN/Inf."""
    if texto is None:
        raise ValueError(f"{contexto} está vacío.")

    texto = str(texto).strip()
    if not texto:
        raise ValueError(f"{contexto} está vacío. Escribe un número.")
    if not _PATRON_NUMERO.fullmatch(texto):
        raise ValueError(
            f"{contexto} ({texto!r}) no es un número válido. "
            "Usa, por ejemplo: -3, 2.5 o 1e-4."
        )

    try:
        numero = float(texto)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{contexto} ({texto!r}) no se puede convertir a número.") from exc
    return asegurar_finito(numero, contexto)
