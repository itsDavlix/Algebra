"""Análisis de una función en un intervalo: puntos notables y valores sugeridos.

Todo se obtiene de la propia función con métodos programados aquí:
- Raíces: cambio de signo entre muestras (teorema de Bolzano) refinado por
  bisección. Se descartan polos: si |f| crece al refinar, no es una raíz.
- Máximos y mínimos: raíces de f′ con cambio de signo (+→− máximo, −→+ mínimo).
- Inflexiones: raíces de f″ con cambio de signo (cambia la concavidad).
- Corte con el eje y: f(0), si 0 está en el intervalo y en el dominio.

El muestreo no demuestra que no existan otras raíces entre dos muestras del
mismo signo; por eso se informa como «puntos encontrados en la vista».
"""

import math
from dataclasses import dataclass
from typing import Optional

from nucleo.expresiones import derivada_numerica, formatear_numero


TIPOS = {
    "raiz": "Raíz",
    "maximo": "Máximo local",
    "minimo": "Mínimo local",
    "inflexion": "Inflexión",
    "corte_y": "Corte con eje y",
}
MAXIMO_POR_TIPO = 25
_RAIZ_DOBLE = ("Raíz doble: f(x) = 0 y f′(x) = 0. La curva toca el eje sin cruzarlo, por eso no "
               "hay cambio de signo y los métodos cerrados (Bisección, Regula Falsi) no la encierran.")


@dataclass(frozen=True)
class PuntoNotable:
    tipo: str
    x: float
    y: float
    explicacion: str
    intervalo: Optional[tuple] = None

    @property
    def nombre(self):
        return TIPOS[self.tipo]


def _n(valor):
    return formatear_numero(float(f"{valor:.6g}"), bonito=True)


def _evaluar(funcion, x):
    try:
        valor = funcion(x)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
    return valor if valor is not None and math.isfinite(valor) else None


def muestrear(funcion, a, b, cantidad):
    """cantidad+1 puntos equiespaciados; None donde f no está definida."""
    paso = (b - a) / cantidad
    return [(a + i * paso, _evaluar(funcion, a + i * paso)) for i in range(cantidad + 1)]


def refinar_cambio_de_signo(funcion, a, b, fa, fb, iteraciones=80):
    """Bisección interna: estrecha [a, b] conservando el cambio de signo."""
    for _ in range(iteraciones):
        c = a + (b - a) / 2
        if c in (a, b):
            break
        fc = _evaluar(funcion, c)
        if fc is None:
            return None
        if fc == 0:
            return c
        if (fa < 0) != (fc < 0):
            b, fb = c, fc
        else:
            a, fa = c, fc
    return a if abs(fa) <= abs(fb) else b


def _cambios_de_signo(muestras):
    for (a, fa), (b, fb) in zip(muestras, muestras[1:]):
        if fa is None or fb is None:
            continue
        if fa == 0:
            yield a, a, fa, fa
        elif (fa < 0) != (fb < 0) and fb != 0:
            yield a, b, fa, fb


def _sin_duplicados(puntos, separacion):
    resultado = []
    for punto in sorted(puntos, key=lambda p: p.x):
        if not resultado or abs(punto.x - resultado[-1].x) > separacion or punto.tipo != resultado[-1].tipo:
            resultado.append(punto)
    return resultado


def puntos_notables(funcion, a, b, derivada=None, segunda=None, cantidad=600):
    """Busca raíces, extremos, inflexiones y el corte con y en [a, b]."""
    if not (math.isfinite(a) and math.isfinite(b)) or a >= b:
        return []
    if derivada is None:
        def derivada(x):
            return derivada_numerica(funcion, x)
    if segunda is None:
        def segunda(x):
            return derivada_numerica(derivada, x)
    paso = (b - a) / cantidad
    separacion = paso * 0.5
    muestras = muestrear(funcion, a, b, cantidad)
    puntos = []

    # Raíces de f.
    for xa, xb, fa, fb in _cambios_de_signo(muestras):
        x = xa if xa == xb else refinar_cambio_de_signo(funcion, xa, xb, fa, fb)
        if x is None:
            continue
        fx = _evaluar(funcion, x)
        if fx is None or abs(fx) > max(abs(fa), abs(fb)):
            continue  # el signo cambió por un polo, no por una raíz
        if xa != xb:
            explicacion = (f"Raíz: f(x) = 0. Entre {_n(xa)} y {_n(xb)} los valores f = {_n(fa)} y "
                           f"{_n(fb)} tienen signos opuestos (Bolzano); se refinó por bisección.")
        else:
            izquierda, derecha = _evaluar(funcion, x - paso), _evaluar(funcion, x + paso)
            if izquierda is not None and derecha is not None and (izquierda > 0) == (derecha > 0):
                explicacion = _RAIZ_DOBLE
            else:
                explicacion = "Raíz: la función vale exactamente 0 en este punto y cambia de signo."
        puntos.append(PuntoNotable("raiz", x, 0.0 if fx == 0 else fx, explicacion,
                                   (xa, xb) if xa != xb else None))

    # Extremos: cambios de signo de f′.
    pendientes = [(x, _evaluar(derivada, x) if y is not None else None) for x, y in muestras]
    for xa, xb, da, db in _cambios_de_signo(pendientes):
        x = xa if xa == xb else refinar_cambio_de_signo(derivada, xa, xb, da, db)
        if x is None:
            continue
        y = _evaluar(funcion, x)
        dx = _evaluar(derivada, x)
        if y is None or dx is None or abs(dx) > max(abs(da), abs(db)):
            continue
        izquierda = _evaluar(derivada, x - paso)
        derecha = _evaluar(derivada, x + paso)
        if izquierda is None or derecha is None or (izquierda > 0) == (derecha > 0):
            continue
        es_maximo = izquierda > 0
        tipo = "maximo" if es_maximo else "minimo"
        explicacion = (
            f"{TIPOS[tipo]}: f′(x) = 0 y la pendiente pasa de "
            + ("positiva a negativa: la curva sube y luego baja." if es_maximo
               else "negativa a positiva: la curva baja y luego sube.")
        )
        puntos.append(PuntoNotable(tipo, x, y, explicacion))
        if abs(y) <= 1e-9 * max(1.0, abs(x)) and not any(
                p.tipo == "raiz" and abs(p.x - x) <= paso for p in puntos):
            puntos.append(PuntoNotable("raiz", x, y, _RAIZ_DOBLE))

    # Inflexiones: cambios de signo de f″.
    curvaturas = [(x, _evaluar(segunda, x) if y is not None else None) for x, y in muestras]
    for xa, xb, ca, cb in _cambios_de_signo(curvaturas):
        x = xa if xa == xb else refinar_cambio_de_signo(segunda, xa, xb, ca, cb)
        if x is None:
            continue
        y = _evaluar(funcion, x)
        cx = _evaluar(segunda, x)
        if y is None or cx is None or abs(cx) > max(abs(ca), abs(cb)):
            continue
        puntos.append(PuntoNotable(
            "inflexion", x, y,
            "Punto de inflexión: f″(x) = 0 y cambia de signo; la curva pasa de "
            + ("cóncava hacia arriba a cóncava hacia abajo." if ca > 0
               else "cóncava hacia abajo a cóncava hacia arriba."),
        ))

    # Corte con el eje y.
    if a <= 0 <= b:
        y0 = _evaluar(funcion, 0.0)
        if y0 is not None:
            puntos.append(PuntoNotable("corte_y", 0.0, y0, f"Corte con el eje y: x = 0 y f(0) = {_n(y0)}."))

    por_tipo = {}
    for punto in _sin_duplicados(puntos, separacion):
        por_tipo.setdefault(punto.tipo, []).append(punto)
    resultado = []
    for tipo in TIPOS:
        resultado.extend(por_tipo.get(tipo, [])[:MAXIMO_POR_TIPO])
    return resultado


def rango_vertical(funcion, a, b, cantidad=400):
    """Rango de y robusto (percentiles 5–95 %) para encuadrar sin que un polo lo arruine."""
    valores = sorted(y for _, y in muestrear(funcion, a, b, cantidad) if y is not None)
    if not valores:
        return -1.0, 1.0
    inferior = valores[int(0.05 * (len(valores) - 1))]
    superior = valores[int(0.95 * (len(valores) - 1))]
    inferior, superior = min(inferior, 0.0), max(superior, 0.0)
    if superior - inferior < 1e-9:
        inferior, superior = inferior - 1, superior + 1
    margen = (superior - inferior) * 0.12
    return inferior - margen, superior + margen


# ---------------------------------------------------------------------------
# Valores sugeridos para cada método
# ---------------------------------------------------------------------------

def _redondeo_que_conserva_signo(funcion, xa, xb):
    """Intervalo de extremos «limpios» (pocos decimales) con el mismo cambio de signo.

    Prueba 0, 1, 2… decimales: floor(a) y ceil(b). Acepta el primero que sea
    angosto, esté en el dominio y tenga exactamente un cambio de signo.
    """
    ancho = xb - xa
    for decimales in range(0, 10):
        factor = 10 ** decimales
        a = math.floor(xa * factor) / factor
        b = math.ceil(xb * factor) / factor
        if a >= b or b - a > max(1.0, 10 * ancho):
            continue
        fa, fb = _evaluar(funcion, a), _evaluar(funcion, b)
        if fa is None or fb is None or fa == 0 or fb == 0 or (fa < 0) == (fb < 0):
            continue
        internas = [y for _, y in muestrear(funcion, a, b, 40)]
        if all(y is not None for y in internas):
            cambios = sum(1 for y1, y2 in zip(internas, internas[1:]) if (y1 < 0) != (y2 < 0))
            if cambios == 1:
                return a, b
    return xa, xb


@dataclass(frozen=True)
class Sugerencia:
    valores: dict
    explicacion: str


def sugerir_valores(metodo, funcion, raiz, derivada=None, segunda=None):
    """Propone valores iniciales alrededor de una raíz detectada en la gráfica."""
    if raiz.intervalo is None:
        delta = max(0.5, abs(raiz.x) * 0.1)
        xa, xb = raiz.x - delta, raiz.x + delta
    else:
        xa, xb = raiz.intervalo
    a, b = _redondeo_que_conserva_signo(funcion, xa, xb)
    fa, fb = _evaluar(funcion, a), _evaluar(funcion, b)
    if metodo in ("Bisección", "Regula Falsi"):
        if fa is None or fb is None or (fa < 0) == (fb < 0):
            return Sugerencia({}, "Esta raíz no tiene cambio de signo (raíz doble): "
                                  "los métodos cerrados no pueden encerrarla. Usa Newton-Raphson.")
        return Sugerencia(
            {"a": _n(a), "b": _n(b)},
            f"a = {_n(a)}, b = {_n(b)}: f(a) = {_n(fa)} y f(b) = {_n(fb)} tienen signos opuestos, "
            "así que por el teorema de Bolzano hay al menos una raíz en [a, b].",
        )
    if metodo == "Secante":
        return Sugerencia(
            {"x0": _n(a), "x1": _n(b)},
            f"x0 = {_n(a)} y x1 = {_n(b)} rodean la raíz detectada (≈ {_n(raiz.x)}); "
            "la primera secante cortará el eje cerca de ella.",
        )
    # Newton-Raphson: condición de Fourier f(x0)·f″(x0) > 0 garantiza que la
    # sucesión no salte al otro lado de la raíz cuando f′ y f″ no cambian de signo.
    if segunda is None:
        def segunda(x):
            return derivada_numerica(lambda t: derivada_numerica(funcion, t), x)
    candidatos = [a, b] if raiz.intervalo is not None else [xb, xa]
    for x0 in candidatos:
        f0, s0 = _evaluar(funcion, x0), _evaluar(segunda, x0)
        d0 = _evaluar(derivada, x0) if derivada else derivada_numerica(funcion, x0)
        if f0 is not None and s0 is not None and d0 and f0 * s0 > 0:
            return Sugerencia(
                {"x0": _n(x0)},
                f"x0 = {_n(x0)}: f(x0) = {_n(f0)} y f″(x0) = {_n(s0)} tienen el mismo signo "
                "(condición de Fourier), por lo que las tangentes se acercan a la raíz sin saltarla.",
            )
    x0 = min(candidatos, key=lambda t: abs(t - raiz.x))
    return Sugerencia(
        {"x0": _n(x0)},
        f"x0 = {_n(x0)} es el valor limpio más cercano a la raíz detectada (≈ {_n(raiz.x)}). "
        "No se cumple la condición de Fourier, así que revisa que las iteraciones converjan.",
    )
