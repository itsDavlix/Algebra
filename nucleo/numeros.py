"""Utilidades numéricas: validación, conversión y formato seguro de valores."""

import math
import re

EPSILON = 1e-10

# Acepta enteros, decimales con punto y notación científica. No acepta NaN/Inf,
# guiones bajos ni expresiones para evitar entradas ambiguas.
_PATRON_NUMERO = re.compile(
    r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$", re.ASCII
)


# Evita que valores infinitos o entradas no numéricas lleguen a las operaciones.
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


def escala_de(valores):
    """Devuelve la mayor magnitud absoluta de una colección, incluso anidada."""
    try:
        magnitudes = []
        pendientes = [iter(valores)]
        while pendientes:
            for valor in pendientes.pop():
                if isinstance(valor, (list, tuple)):
                    pendientes.append(iter(valor))
                else:
                    magnitudes.append(abs(asegurar_finito(valor)))
        return max(magnitudes, default=0.0)
    except TypeError as exc:
        raise ValueError("Los valores para calcular la escala no son una colección válida.") from exc


def umbral_cero(escala):
    """Calcula el umbral de cero relativo a una escala finita no negativa."""
    escala = asegurar_finito(escala, "La escala")
    if escala < 0:
        raise ValueError("La escala debe ser mayor o igual que cero.")
    return EPSILON * escala


def limpiar_numero(numero, escala=None):
    """Da formato legible a un número finito, evitando -0 y decimales innecesarios."""
    numero = asegurar_finito(numero)
    umbral = EPSILON if escala is None else umbral_cero(escala)
    if abs(numero) <= umbral:
        return "0"

    # Evita convertir números gigantes a int solo para mostrarlos.
    entero = round(numero)
    if (
        entero != 0
        and abs(numero) < 1e15
        and abs(numero - entero) <= EPSILON * abs(entero)
    ):
        return str(int(entero))

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
