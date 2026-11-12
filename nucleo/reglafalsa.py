"""Resolución de ecuaciones reales por Regula Falsi, sin dependencias externas."""

import math
from dataclasses import dataclass
from typing import Optional

from nucleo.biseccion import MAX_ITERACIONES, _numero, preparar_funcion
from nucleo.numeros import asegurar_finito


@dataclass(frozen=True)
class IteracionReglaFalsa:
    """Valores de una aproximación y su estimación de error."""

    numero: int
    a: float
    b: float
    c: float
    fa: float
    fb: float
    fc: float
    error: Optional[float]
    error_relativo: Optional[float]
    extremo_movido: str


@dataclass(frozen=True)
class ResultadoReglaFalsa:
    """Resultado inmutable de una ejecución del método de falsa posición."""

    expresion: str
    intervalo_inicial: tuple
    tolerancia: float
    raiz: float
    valor_funcion: float
    error: Optional[float]
    iteraciones: tuple
    convergio: bool
    motivo: str
    extremo_estancado: str


def punto_falsa_posicion(a, b, fa, fb):
    """Calcula el corte de la secante con x, escalando para evitar desbordes."""
    a = asegurar_finito(a, "El extremo a")
    b = asegurar_finito(b, "El extremo b")
    fa = asegurar_finito(fa, "f(a)")
    fb = asegurar_finito(fb, "f(b)")
    if a >= b:
        raise ValueError("El extremo a debe ser menor que b.")
    if fa == 0 or fb == 0 or (fa < 0) == (fb < 0):
        raise ValueError("f(a) y f(b) deben tener signos opuestos para calcular la falsa posición.")

    escala = max(abs(fa), abs(fb))
    wa, wb = fa / escala, fb / escala
    t = wa / (wa - wb)
    diferencia = b - a
    if math.isinf(diferencia):
        c = a * (1 - t) + b * t
    else:
        c = a + t * diferencia
    return min(max(c, a), b)


def resolver_reglafalsa(ecuacion, a, b, tolerancia=1e-6, max_iteraciones=100):
    """Busca una raíz aproximada en un intervalo con valores de signos opuestos.

    La parada requiere tanto un paso pequeño como un residuo absoluto pequeño.
    El paso es una estimación, no una cota. Se requiere f continua en [a,b].
    """
    a = asegurar_finito(a, "El extremo a")
    b = asegurar_finito(b, "El extremo b")
    tolerancia = asegurar_finito(tolerancia, "La tolerancia")
    if a >= b:
        raise ValueError("El extremo a debe ser menor que b.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if type(max_iteraciones) is not int or not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(
            f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}."
        )

    funcion, expresion = preparar_funcion(ecuacion)
    intervalo_inicial = (a, b)
    iteraciones = []

    def crear_resultado(raiz, valor, error, convergio, motivo):
        extremo_estancado = ""
        if (len(iteraciones) >= 5 and iteraciones[-1].extremo_movido
                and len({paso.extremo_movido for paso in iteraciones[-5:]}) == 1):
            extremo_estancado = "b" if iteraciones[-1].extremo_movido == "a" else "a"
        return ResultadoReglaFalsa(
            expresion, intervalo_inicial, tolerancia, raiz, valor, error,
            tuple(iteraciones), convergio, motivo, extremo_estancado,
        )

    fa = funcion(a)
    if fa == 0:
        return crear_resultado(a, fa, 0.0, True, "f(a) = 0 en la precisión de cálculo.")
    fb = funcion(b)
    if fb == 0:
        return crear_resultado(b, fb, 0.0, True, "f(b) = 0 en la precisión de cálculo.")
    if (fa < 0) == (fb < 0):
        raise ValueError(
            f"f(a) = {_numero(fa)} y f(b) = {_numero(fb)} tienen el mismo signo. "
            "Elige otro intervalo con signos opuestos. Esto no significa que "
            "la ecuación no tenga raíces."
        )
    magnitud_extremos = max(abs(fa), abs(fb))
    c = None
    fc = None
    error = None

    for numero in range(1, max_iteraciones + 1):
        c = punto_falsa_posicion(a, b, fa, fb)
        fc = funcion(c)
        if iteraciones:
            error = abs(c - iteraciones[-1].c)
            error_relativo = None if c == 0 else abs((c - iteraciones[-1].c) / c) * 100
        else:
            error = None
            error_relativo = None

        if fc == 0:
            extremo_movido = ""
        elif (fa < 0) != (fc < 0):
            extremo_movido = "b"
        else:
            extremo_movido = "a"
        iteraciones.append(
            IteracionReglaFalsa(
                numero, a, b, c, fa, fb, fc, error, error_relativo, extremo_movido,
            )
        )

        if fc == 0:
            return crear_resultado(
                c, fc, error, True, "f(c) = 0 en la precisión de cálculo.",
            )
        if error is not None and error <= tolerancia:
            if abs(fc) > magnitud_extremos:
                return crear_resultado(
                    c, fc, error, False,
                    "Posible discontinuidad (polo): |f(c)| supera las magnitudes "
                    "de los extremos; x no es una raíz.",
                )
            if abs(fc) <= tolerancia:
                return crear_resultado(
                    c, fc, error, True,
                    "El cambio entre aproximaciones y el residuo absoluto "
                    "son menores o iguales que la tolerancia.",
                )
        if c == a or c == b:
            return crear_resultado(
                c, fc, error, False,
                "Se alcanzó el límite de precisión numérica antes de cumplir la tolerancia.",
            )
        if extremo_movido == "b":
            b, fb = c, fc
        else:
            a, fa = c, fc

    return crear_resultado(
        c, fc, error, False,
        "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia.",
    )


def nota_estancamiento(resultado):
    """Explica qué extremo permaneció fijo si los últimos cinco pasos lo indican."""
    if not resultado.extremo_estancado:
        return ""
    return (
        f"El extremo {resultado.extremo_estancado} no cambió en las últimas 5 "
        "iteraciones; el error real puede ser mayor que el estimado; compara con Bisección."
    )


def formatear_resultado_reglafalsa(resultado):
    """Presenta la estimación, las condiciones y el procedimiento de cada iteración."""
    n = _numero
    a, b = resultado.intervalo_inicial
    error = "no disponible" if resultado.error is None else n(resultado.error)
    lineas = [
        "MÉTODO DE REGULA FALSI",
        "",
        "RESULTADO: " + (
            "convergencia alcanzada." if resultado.convergio
            else "aproximación sin convergencia."
        ),
        f"x ≈ {n(resultado.raiz)}",
        f"Comprobación: f(x) = {n(resultado.valor_funcion)}",
        f"Error estimado |c_nuevo - c_anterior|: {error}",
        f"Iteraciones realizadas: {len(resultado.iteraciones)}",
        f"Motivo de parada: {resultado.motivo}",
        "",
        f"f(x) = {resultado.expresion}",
        f"Intervalo inicial: [{n(a)}, {n(b)}]",
        f"Tolerancia absoluta (paso y residuo): {n(resultado.tolerancia)}",
        "",
        "CONDICIÓN: el método cerrado requiere f continua en todo [a,b] y "
        "valores de signos opuestos en los extremos. El cambio de signo no "
        "descarta discontinuidades. Se exige que el paso y el residuo absoluto "
        "cumplan la tolerancia; el paso no es una cota del error en x. "
        "Los cálculos usan la precisión de coma flotante de Python.",
        "",
        "PROCEDIMIENTO PASO A PASO",
        "1. Evaluar f(a) y f(b), comprobar el cambio de signo y la continuidad.",
        "2. Unir (a,f(a)) y (b,f(b)); calcular el corte c de esa secante con x.",
        "3. Evaluar f(c); reemplazar el extremo que conserva el cambio de signo.",
        "4. Repetir hasta que f(c)=0, el paso y el residuo cumplan la tolerancia "
        "o se alcance un límite.",
    ]
    aviso = nota_estancamiento(resultado)
    if aviso:
        lineas.extend(["", "AVISO: " + aviso])
    else:
        lineas.extend([
            "",
            "La tolerancia no es una cota del error real en x; compárala con "
            "otros métodos si necesitas una garantía.",
        ])
    if not resultado.iteraciones:
        lineas.extend(["", "La raíz está en un extremo; no fue necesario iterar."])

    for paso in resultado.iteraciones:
        lineas.extend([
            "", "─" * 42,
            f"ITERACIÓN {paso.numero}",
            f"a = {n(paso.a)}; b = {n(paso.b)}",
            f"f(a) = {n(paso.fa)}; f(b) = {n(paso.fb)}",
            f"escala = max(|f(a)|, |f(b)|); t = (f(a)/escala) / "
            "((f(a)/escala) - (f(b)/escala))",
            f"c = a + t(b-a) = {n(paso.c)}",
            f"f(c) = {n(paso.fc)}",
            "Error estimado |c_nuevo - c_anterior| = "
            + ("no disponible" if paso.error is None else n(paso.error)),
            "Error relativo aproximado εa = "
            + ("no disponible" if paso.error_relativo is None
               else f"{n(paso.error_relativo)} %"),
        ])
        if paso.numero == len(resultado.iteraciones):
            lineas.append("Parada: " + resultado.motivo)
        elif paso.extremo_movido == "b":
            lineas.append("Decisión: f(a)·f(c) < 0 → b = c")
        else:
            lineas.append("Decisión: f(c)·f(b) < 0 → a = c")
    return "\n".join(lineas)
