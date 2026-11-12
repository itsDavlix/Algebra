"""Newton-Raphson y Secante para ecuaciones reales, sin bibliotecas externas."""

from dataclasses import dataclass
from typing import Optional

from nucleo.biseccion import MAX_ITERACIONES, preparar_funcion
from nucleo.numeros import asegurar_finito


METODOS_ABIERTOS = ("Newton-Raphson", "Secante")


@dataclass(frozen=True)
class IteracionAbierta:
    numero: int
    anterior: Optional[float]
    actual: float
    valor_actual: float
    pendiente: float
    siguiente: float
    valor_siguiente: float
    error: float


@dataclass(frozen=True)
class ResultadoAbierto:
    metodo: str
    expresion: str
    tolerancia: float
    raiz: float
    valor_funcion: float
    error: Optional[float]
    iteraciones: tuple
    convergio: bool
    motivo: str


def resolver_metodo_abierto(ecuacion, metodo, x0, x1=None, derivada="",
                           tolerancia=1e-6, max_iteraciones=100):
    """Selecciona un método sin exigir un intervalo con cambio de signo.

    Newton requiere la expresión de f'(x); Secante, dos semillas distintas.
    La tolerancia absoluta se aplica al paso y al residuo: ambos deben ser
    pequeños. No representa una cota del error real ni garantiza convergencia.
    """
    if metodo not in METODOS_ABIERTOS:
        raise ValueError("Selecciona Newton-Raphson o Secante.")
    x0 = asegurar_finito(x0, "El valor inicial x0")
    tolerancia = asegurar_finito(tolerancia, "La tolerancia")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if type(max_iteraciones) is not int or not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}.")
    funcion, expresion = preparar_funcion(ecuacion)
    funcion_derivada = None
    if metodo == "Newton-Raphson":
        if not isinstance(derivada, str) or not derivada.strip():
            raise ValueError("Escribe la derivada f'(x) para Newton-Raphson.")
        funcion_derivada, _ = preparar_funcion(derivada)
    else:
        x1 = asegurar_finito(x1, "El valor inicial x1")
        if x0 == x1:
            raise ValueError("Secante requiere valores iniciales x0 y x1 distintos.")

    pasos = []
    error = None

    def resultado(x, fx, convergio, motivo):
        return ResultadoAbierto(
            metodo, expresion, tolerancia, x, fx, error, tuple(pasos), convergio, motivo,
        )

    actual, valor_actual = x0, funcion(x0)
    if valor_actual == 0:
        error = 0.0
        return resultado(actual, valor_actual, True, "x0 es una raíz en la precisión de cálculo.")
    anterior, valor_anterior = None, None
    if metodo == "Secante":
        anterior, valor_anterior = actual, valor_actual
        actual, valor_actual = x1, funcion(x1)
        if valor_actual == 0:
            error = 0.0
            return resultado(actual, valor_actual, True, "x1 es una raíz en la precisión de cálculo.")

    for numero in range(1, max_iteraciones + 1):
        if funcion_derivada is not None:
            pendiente = funcion_derivada(actual)
            if pendiente == 0:
                return resultado(actual, valor_actual, False,
                                 "La derivada es cero. Elige otro valor inicial.")
            desplazamiento = valor_actual / pendiente
        else:
            if valor_actual == valor_anterior:
                return resultado(actual, valor_actual, False,
                                 "f(x_n) y f(x_n−1) son iguales; el denominador de Secante es cero.")
            # Escala las evaluaciones para evitar desbordar al restarlas.
            escala = max(abs(valor_actual), abs(valor_anterior))
            diferencia = valor_actual / escala - valor_anterior / escala
            distancia = asegurar_finito(actual - anterior, "La distancia entre aproximaciones")
            if distancia == 0 or diferencia == 0:
                return resultado(actual, valor_actual, False,
                                 "Se agotó la precisión numérica para calcular la secante.")
            desplazamiento = (valor_actual / escala) / diferencia * distancia
            pendiente = asegurar_finito((diferencia / distancia) * escala, "La pendiente secante")
        siguiente = asegurar_finito(actual - desplazamiento, "La siguiente aproximación")
        valor_siguiente = funcion(siguiente)
        error = asegurar_finito(abs(siguiente - actual), "El error aproximado")
        pasos.append(IteracionAbierta(
            numero, anterior, actual, valor_actual, pendiente, siguiente, valor_siguiente, error,
        ))
        if valor_siguiente == 0:
            return resultado(siguiente, valor_siguiente, True, "f(x) = 0 en la precisión de cálculo.")
        if error <= tolerancia and abs(valor_siguiente) <= tolerancia:
            return resultado(siguiente, valor_siguiente, True,
                             "El paso y el residuo absoluto cumplen la tolerancia.")
        if siguiente == actual:
            return resultado(siguiente, valor_siguiente, False,
                             "La aproximación se estancó sin cumplir la tolerancia del residuo.")
        anterior, valor_anterior = actual, valor_actual
        actual, valor_actual = siguiente, valor_siguiente

    return resultado(actual, valor_actual, False,
                     "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia.")


def formatear_resultado_abierto(resultado):
    """Muestra la fórmula, la comprobación y el procedimiento de cada paso."""
    n = lambda valor: f"{valor:.10g}"
    estado = "Convergencia alcanzada" if resultado.convergio else "Aproximación sin convergencia"
    error = "no disponible" if resultado.error is None else n(resultado.error)
    lineas = [
        resultado.metodo.upper(), "", f"{estado}: x ≈ {n(resultado.raiz)}",
        f"Comprobación: f(x) = {n(resultado.valor_funcion)}",
        f"Error aproximado |x_nuevo − x_actual|: {error}",
        f"Tolerancia absoluta (paso y residuo): {n(resultado.tolerancia)}",
        f"Iteraciones: {len(resultado.iteraciones)}", f"Motivo: {resultado.motivo}",
        "", f"f(x) = {resultado.expresion}",
        "El error aproximado no es una cota del error real en la raíz.", "",
        ("Newton: x_nuevo = x_actual − f(x_actual)/f'(x_actual)"
         if resultado.metodo == "Newton-Raphson" else
         "Secante: x_nuevo = x_actual − f(x_actual)(x_actual−x_anterior)"
         "/(f(x_actual)−f(x_anterior))"),
    ]
    for paso in resultado.iteraciones:
        lineas.extend(["", f"ITERACIÓN {paso.numero}"])
        if paso.anterior is not None and resultado.metodo == "Secante":
            lineas.append(f"x_anterior = {n(paso.anterior)}")
        lineas.extend([
            f"x_actual = {n(paso.actual)}; f(x_actual) = {n(paso.valor_actual)}",
            f"Pendiente = {n(paso.pendiente)}",
            f"x_nuevo = {n(paso.siguiente)}; f(x_nuevo) = {n(paso.valor_siguiente)}",
            f"Error aproximado = {n(paso.error)}",
        ])
    return "\n".join(lineas)
