"""Resolución de ecuaciones reales por bisección, sin dependencias externas."""

import math
from dataclasses import dataclass
from typing import Optional

from nucleo.expresiones import analizar
from nucleo.analisis import comprobar_continuidad
from nucleo.numeros import asegurar_finito


MAX_ITERACIONES = 1000


def preparar_funcion(ecuacion):
    """Devuelve (f, expresión) para una expresión en x o una igualdad.

    Usa el evaluador propio de nucleo.expresiones: valida una lista blanca de
    operaciones y nunca ejecuta código Python escrito por la persona.
    """
    expresion = analizar(ecuacion)
    return expresion, expresion.texto


@dataclass(frozen=True)
class IteracionBiseccion:
    numero: int
    a: float
    b: float
    c: float
    fa: float
    fb: float
    fc: float
    error: float
    error_relativo: Optional[float] = None


@dataclass(frozen=True)
class ResultadoBiseccion:
    expresion: str
    intervalo_inicial: tuple
    tolerancia: float
    raiz: float
    valor_funcion: float
    error: float
    iteraciones: tuple
    convergio: bool
    motivo: str
    iteraciones_teoricas: int = 0


def iteraciones_necesarias(a, b, tolerancia):
    """Menor n con (b − a)/2ⁿ ≤ tolerancia: n = ⌈log₂((b − a)/tolerancia)⌉."""
    # log₂(b − a) se calcula como log₂(b/2 − a/2) + 1 para no desbordar.
    log_ancho = math.log2(b / 2 - a / 2) + 1
    exceso = log_ancho - math.log2(tolerancia)
    return max(1, math.ceil(exceso - 1e-12))


@dataclass(frozen=True)
class AjusteBiseccion:
    a: float
    b: float
    fa: float
    fb: float
    tolerancia: float
    max_iteraciones: int


def autoajustar_biseccion(ecuacion):
    """Propone un intervalo muestreado y una cota de error acorde con su ancho.

    El muestreo no demuestra continuidad; esa condición debe revisarse aparte.
    """
    funcion, _ = preparar_funcion(ecuacion)
    for potencia in range(21):
        radio = 2 ** potencia
        puntos = []
        for indice in range(-8, 9):
            x = radio * indice / 8
            try:
                valor = funcion(x)
            except ValueError:
                puntos.append((x, None))
            else:
                puntos.append((x, valor))

        candidatos = []
        for (a, fa), (b, fb) in zip(puntos, puntos[1:]):
            if fa is None or fb is None:
                continue
            if fa != 0 and fb != 0 and (fa < 0) == (fb < 0):
                continue
            # Descarta los saltos de dominio visibles también en el interior.
            try:
                funcion((a + b) / 2)
            except ValueError:
                continue
            candidatos.append((a, b, fa, fb))

        if candidatos:
            # Si hay varias raíces posibles, prefiere la cercana a cero y,
            # en caso de empate, la situada a la derecha.
            a, b, fa, fb = min(
                candidatos, key=lambda par: (abs((par[0] + par[1]) / 2),
                                             -((par[0] + par[1]) / 2)),
            )
            ancho = b - a
            tolerancia = max(1e-12, ancho * 1e-6)
            iteraciones = min(MAX_ITERACIONES,
                              max(1, math.ceil(math.log2(ancho / tolerancia)) + 1))
            return AjusteBiseccion(a, b, fa, fb, tolerancia, iteraciones)

    raise ValueError(
        "No se encontró un intervalo con cambio de signo entre -1 048 576 y 1 048 576. "
        "Puede no haber una raíz detectable por este muestreo. "
        "Comprueba la ecuación y que f sea continua en el intervalo."
    )


def resolver_biseccion(ecuacion, a, b, tolerancia=1e-6, max_iteraciones=100):
    """Busca una raíz de una función continua en [a, b] con cambio de signo.

    Se detiene si f(c) es cero en coma flotante o si la cota del error en x
    es <= tolerancia. No usa |f(c)| como sustituto del error en la raíz.
    Alcanzar el límite de iteraciones o de precisión no se presenta como éxito.
    La continuidad es una condición que debe comprobar quien usa el método.
    """
    a = asegurar_finito(a, "El extremo a")
    b = asegurar_finito(b, "El extremo b")
    tolerancia = asegurar_finito(tolerancia, "La tolerancia")
    if a >= b:
        raise ValueError("El extremo a debe ser menor que b.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if type(max_iteraciones) is not int or not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}.")

    funcion, expresion = preparar_funcion(ecuacion)
    intervalo_inicial = (a, b)
    iteraciones = []
    discontinuidad = comprobar_continuidad(funcion, a, b)
    if discontinuidad:
        raise ValueError(discontinuidad)

    teoricas = iteraciones_necesarias(a, b, tolerancia)

    def resultado(raiz, valor, error, convergio, motivo):
        return ResultadoBiseccion(
            expresion, intervalo_inicial, tolerancia, raiz, valor, error,
            tuple(iteraciones), convergio, motivo, teoricas,
        )

    fa = funcion(a)
    if fa == 0:
        return resultado(a, fa, 0.0, True, "f(a) = 0 en la precisión de cálculo.")
    fb = funcion(b)
    if fb == 0:
        return resultado(b, fb, 0.0, True, "f(b) = 0 en la precisión de cálculo.")
    # Comparar signos evita desbordar o convertir productos diminutos en cero.
    if (fa < 0) == (fb < 0):
        raise ValueError(
            f"f(a) = {_numero(fa)} y f(b) = {_numero(fb)} tienen el mismo signo. "
            "Elige otro intervalo con signos opuestos. Esto no significa que "
            "la ecuación no tenga raíces."
        )
    magnitud_extremos = max(abs(fa), abs(fb))

    for numero in range(1, max_iteraciones + 1):
        # Evita desbordamientos tanto en a+b como en b-a.
        c = a / 2 + b / 2 if a < 0 < b else a + (b - a) / 2
        fc = funcion(c)
        # En aritmética exacta equivale a (b-a)/2. Conserva una cota también
        # cuando el punto medio se redondea hacia uno de los extremos.
        error = max(c - a, b - c)
        previo = iteraciones[-1].c if iteraciones else None
        relativo = None if previo is None or c == 0 else abs(c - previo) / abs(c) * 100
        iteraciones.append(IteracionBiseccion(numero, a, b, c, fa, fb, fc, error, relativo))
        if fc == 0:
            return resultado(c, fc, 0.0, True, "f(c) = 0 en la precisión de cálculo.")
        if error <= tolerancia:
            if abs(fc) > magnitud_extremos:
                return resultado(
                    c, fc, error, False,
                    "Posible discontinuidad (polo): |f(c)| supera las magnitudes "
                    "de los extremos; x no es una raíz.",
                )
            return resultado(c, fc, error, True, "La cota del error en x es menor o igual que la tolerancia.")
        if c == a or c == b:
            return resultado(c, fc, error, False,
                             "Se alcanzó el límite de precisión numérica antes de cumplir la tolerancia.")
        if (fa < 0) != (fc < 0):
            b, fb = c, fc
        else:
            a, fa = c, fc

    return resultado(c, fc, error, False,
                     "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia.")


def _numero(valor):
    """Conserva cifras pequeñas y suficiente precisión para reproducir el valor."""
    texto = repr(float(valor))
    return texto[:-2] if texto.endswith(".0") else texto


def formatear_resultado_biseccion(resultado):
    """Muestra resultado, comprobación y cada reducción del intervalo."""
    n = _numero
    a, b = resultado.intervalo_inicial
    lineas = [
        "MÉTODO DE BISECCIÓN",
        "",
        "RESULTADO: " + ("convergencia alcanzada." if resultado.convergio else "aproximación sin convergencia."),
        f"x ≈ {n(resultado.raiz)}",
        f"Comprobación: f(x) = {n(resultado.valor_funcion)}",
        f"Cota del error en x: {n(resultado.error)}",
        f"Iteraciones realizadas: {len(resultado.iteraciones)}",
        f"Motivo de parada: {resultado.motivo}",
        "",
        f"f(x) = {resultado.expresion}",
        f"Intervalo inicial: [{n(a)}, {n(b)}]",
        f"Tolerancia absoluta en x: {n(resultado.tolerancia)}",
        f"Iteraciones necesarias: n ≥ log₂((b − a)/tol) → n = {resultado.iteraciones_teoricas}",
        "",
        "CONDICIÓN: f debe ser continua en todo el intervalo. El cambio de "
        "signo por sí solo no descarta una discontinuidad. Los cálculos "
        "utilizan la precisión de coma flotante de Python.",
        "",
        "PROCEDIMIENTO PASO A PASO",
        "1. Evaluar los extremos y comprobar una raíz en ellos o signos opuestos.",
        "2. Calcular c = (a + b) / 2 y evaluar f(c).",
        "3. Si no se cumple la parada, conservar la mitad con signos opuestos.",
        "4. Repetir hasta cumplir la tolerancia o alcanzar un límite.",
    ]
    if not resultado.iteraciones:
        lineas.extend(["", "La raíz se encontró en un extremo; no fue necesario dividir el intervalo."])
    for paso in resultado.iteraciones:
        lineas.extend([
            "", "─" * 42,
            f"ITERACIÓN {paso.numero}",
            f"a = {n(paso.a)}; b = {n(paso.b)}",
            f"f(a) = {n(paso.fa)}; f(b) = {n(paso.fb)}",
            f"c = (a + b) / 2 = {n(paso.c)}",
            f"f(c) = {n(paso.fc)}",
            f"Cota del error = max(c-a, b-c) = {n(paso.error)}",
            "Error relativo aproximado εa = " + (
                "no disponible" if paso.error_relativo is None else f"{paso.error_relativo:.6g} %"),
        ])
        if paso.numero == len(resultado.iteraciones):
            lineas.append("Parada: " + resultado.motivo)
        elif (paso.fa < 0) != (paso.fc < 0):
            lineas.append(f"f(a) y f(c) tienen signos opuestos: conservar [{n(paso.a)}, {n(paso.c)}].")
        else:
            lineas.append(f"f(c) y f(b) tienen signos opuestos: conservar [{n(paso.c)}, {n(paso.b)}].")
    return "\n".join(lineas)
