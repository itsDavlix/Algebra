"""Métodos iterativos de Jacobi y Gauss-Seidel para A·x = b, sin bibliotecas externas.

Siguen la teoría de la clase (Burden-Faires, Chapra):
- Se despeja cada incógnita: aᵢᵢ xᵢ = bᵢ − Σⱼ≠ᵢ aᵢⱼ xⱼ.
- Jacobi: xᵢ⁽ᵏ⁺¹⁾ = [bᵢ − Σⱼ≠ᵢ aᵢⱼ xⱼ⁽ᵏ⁾] / aᵢᵢ  (solo valores de la iteración anterior).
- Gauss-Seidel: xᵢ⁽ᵏ⁺¹⁾ = [bᵢ − Σⱼ<ᵢ aᵢⱼ xⱼ⁽ᵏ⁺¹⁾ − Σⱼ>ᵢ aᵢⱼ xⱼ⁽ᵏ⁾] / aᵢᵢ  (usa al instante los nuevos).
- Parada: ‖x⁽ᵏ⁺¹⁾ − x⁽ᵏ⁾‖∞ ≤ ε y ‖b − A x⁽ᵏ⁺¹⁾‖∞ ≤ ε (cambio y residuo, como se recomienda).
- Convergencia: la dominancia diagonal estricta por filas es suficiente, no necesaria; el
  criterio exacto es ρ(T) < 1, con T la matriz de iteración. Aquí ρ(T) se estima con la
  fórmula de Gelfand ρ(T) = lim ‖Tᵏ‖^(1/k).
"""

import itertools
import math
from dataclasses import dataclass, field

METODOS_ITERATIVOS = ("Jacobi", "Gauss-Seidel")
MAX_ITERACIONES = 1000
LIMITE_DIVERGENCIA = 1e12


@dataclass(frozen=True)
class Sustitucion:
    """Cálculo de una componente: qué valores se usaron y de qué iteración venían."""

    indice: int
    terminos: tuple          # ((j, aᵢⱼ, xⱼ usado, es_nuevo), ...)
    numerador: float
    valor: float


@dataclass(frozen=True)
class IteracionSistema:
    k: int
    x: tuple
    cambio: float             # ‖x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾‖∞
    residuo: float            # ‖b − A x⁽ᵏ⁾‖∞
    sustituciones: tuple


@dataclass(frozen=True)
class FilaDominancia:
    fila: int
    diagonal: float
    suma: float

    @property
    def cumple(self):
        return abs(self.diagonal) > self.suma


@dataclass(frozen=True)
class ResultadoIterativo:
    metodo: str
    variables: tuple
    A: tuple
    b: tuple
    x0: tuple
    tolerancia: float
    iteraciones: tuple
    convergio: bool
    motivo: str
    dominancia: tuple
    radio_espectral: float = None
    reordenado: tuple = field(default=())   # permutación aplicada a las filas, si la hubo

    @property
    def solucion(self):
        return self.iteraciones[-1].x if self.iteraciones else self.x0

    @property
    def estrictamente_dominante(self):
        return all(fila.cumple for fila in self.dominancia)


# ---------------------------------------------------------------- utilidades
def norma_infinito(vector):
    return max((abs(v) for v in vector), default=0.0)


def residuo(A, b, x):
    """r = b − A x."""
    return [bi - sum(aij * xj for aij, xj in zip(fila, x)) for fila, bi in zip(A, b)]


def _validar(A, b, x0, tolerancia, max_iteraciones):
    n = len(A)
    if n == 0 or any(len(fila) != n for fila in A):
        raise ValueError("Los métodos iterativos necesitan un sistema cuadrado (n ecuaciones, n incógnitas).")
    if len(b) != n:
        raise ValueError("b debe tener una componente por ecuación.")
    if x0 is None:
        x0 = [0.0] * n
    if len(x0) != n:
        raise ValueError(f"El vector inicial x⁽⁰⁾ debe tener {n} componentes.")
    if not tolerancia > 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if type(max_iteraciones) is not int or not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}.")
    ceros = [i + 1 for i in range(n) if A[i][i] == 0]
    if ceros:
        raise ValueError(
            f"La diagonal tiene ceros en la(s) fila(s) {', '.join(map(str, ceros))}: no se puede despejar "
            "esa incógnita. Reordena las ecuaciones (botón «Reordenar filas») cuando sea válido.")
    return [list(map(float, fila)) for fila in A], [float(v) for v in b], [float(v) for v in x0]


def dominancia_diagonal(A):
    """|aᵢᵢ| > Σⱼ≠ᵢ |aᵢⱼ| fila por fila."""
    return tuple(FilaDominancia(i + 1, A[i][i], sum(abs(a) for j, a in enumerate(A[i]) if j != i))
                 for i in range(len(A)))


def matriz_iteracion(A, metodo):
    """T_J = −D⁻¹(L + U)   ·   T_GS = −(D + L)⁻¹ U."""
    n = len(A)
    if metodo == "Jacobi":
        return [[0.0 if i == j else -A[i][j] / A[i][i] for j in range(n)] for i in range(n)]
    # Gauss-Seidel: columna j de T resolviendo (D + L) t = −U eⱼ por sustitución hacia adelante.
    T = [[0.0] * n for _ in range(n)]
    for j in range(n):
        derecho = [-A[i][j] if j > i else 0.0 for i in range(n)]
        t = [0.0] * n
        for i in range(n):
            t[i] = (derecho[i] - sum(A[i][m] * t[m] for m in range(i))) / A[i][i]
        for i in range(n):
            T[i][j] = t[i]
    return T


def radio_espectral(T, potencias=64):
    """ρ(T) ≈ ‖Tᵏ‖∞^(1/k) (Gelfand). Se toma k = 64 con normalización para no desbordar."""
    n = len(T)
    potencia = [fila[:] for fila in T]
    escala_log = 0.0
    k = 1
    while k < potencias:
        potencia = [[sum(potencia[i][m] * potencia[m][j] for m in range(n)) for j in range(n)] for i in range(n)]
        escala_log *= 2
        k *= 2
        norma = max(sum(abs(v) for v in fila) for fila in potencia)
        if norma == 0:
            return 0.0
        potencia = [[v / norma for v in fila] for fila in potencia]
        escala_log += math.log(norma)
    return math.exp(escala_log / k)


def reordenar_para_dominancia(A, b, metodo="Gauss-Seidel"):
    """Busca el orden de ecuaciones más favorable para el método.

    Reordenar ecuaciones no cambia la solución. Se descartan los órdenes con
    ceros en la diagonal y se elige el de menor ρ(T) (criterio exacto de
    convergencia); a igualdad, el que tenga más filas diagonalmente dominantes.
    Para n ≤ 7 se prueban todas las permutaciones.
    Devuelve (A_reordenada, b_reordenada, permutación, ρ) o None si no mejora.
    """
    n = len(A)
    if n > 7:
        return None
    A = [list(map(float, fila)) for fila in A]

    def puntaje(filas):
        try:
            rho = radio_espectral(matriz_iteracion(filas, metodo))
        except (OverflowError, ZeroDivisionError, ValueError):
            return None
        dominantes = sum(1 for fila in dominancia_diagonal(filas) if fila.cumple)
        return rho, -dominantes

    actual = None if any(A[i][i] == 0 for i in range(n)) else puntaje(A)
    mejor, mejor_puntaje = None, None
    for permutacion in itertools.permutations(range(n)):
        filas = [A[p] for p in permutacion]
        if any(filas[i][i] == 0 for i in range(n)):
            continue
        valor = puntaje(filas)
        if valor is not None and (mejor_puntaje is None or valor < mejor_puntaje):
            mejor, mejor_puntaje = permutacion, valor
    if mejor is None or list(mejor) == list(range(n)) or (actual is not None and mejor_puntaje >= actual):
        return None
    return [A[p][:] for p in mejor], [b[p] for p in mejor], tuple(mejor), mejor_puntaje[0]


# ---------------------------------------------------------------- métodos
def resolver_iterativo(A, b, metodo, x0=None, tolerancia=1e-6, max_iteraciones=100, variables=None,
                       reordenado=()):
    """Jacobi o Gauss-Seidel con registro de cada sustitución."""
    if metodo not in METODOS_ITERATIVOS:
        raise ValueError("Elige Jacobi o Gauss-Seidel.")
    A, b, x = _validar(A, b, x0, tolerancia, max_iteraciones)
    n = len(A)
    variables = tuple(variables or [f"x{i + 1}" for i in range(n)])
    dominancia = dominancia_diagonal(A)
    try:
        rho = radio_espectral(matriz_iteracion(A, metodo))
    except (OverflowError, ZeroDivisionError, ValueError):
        rho = None
    inicial = tuple(x)
    pasos = []

    def resultado(convergio, motivo):
        return ResultadoIterativo(metodo, variables, tuple(map(tuple, A)), tuple(b), inicial, tolerancia,
                                  tuple(pasos), convergio, motivo, dominancia, rho, tuple(reordenado))

    for k in range(1, max_iteraciones + 1):
        anterior = list(x)
        nuevo = list(x) if metodo == "Gauss-Seidel" else [0.0] * n
        sustituciones = []
        for i in range(n):
            terminos = []
            suma = 0.0
            for j in range(n):
                if j == i:
                    continue
                # Jacobi usa solo x⁽ᵏ⁾; Gauss-Seidel usa x⁽ᵏ⁺¹⁾ para j < i.
                usa_nuevo = metodo == "Gauss-Seidel" and j < i
                valor_j = nuevo[j] if usa_nuevo else anterior[j]
                terminos.append((j, A[i][j], valor_j, usa_nuevo))
                suma += A[i][j] * valor_j
            numerador = b[i] - suma
            valor = numerador / A[i][i]
            nuevo[i] = valor
            sustituciones.append(Sustitucion(i, tuple(terminos), numerador, valor))
        x = nuevo
        if not all(math.isfinite(v) for v in x) or norma_infinito(x) > LIMITE_DIVERGENCIA:
            pasos.append(IteracionSistema(k, tuple(x), math.inf, math.inf, tuple(sustituciones)))
            return resultado(False, "Las aproximaciones crecen sin control: el método diverge para este "
                                    "sistema. Revisa la dominancia diagonal o reordena las ecuaciones.")
        cambio = norma_infinito([a - c for a, c in zip(x, anterior)])
        r = norma_infinito(residuo(A, b, x))
        pasos.append(IteracionSistema(k, tuple(x), cambio, r, tuple(sustituciones)))
        if cambio <= tolerancia and r <= tolerancia:
            return resultado(True, "‖x⁽ᵏ⁺¹⁾ − x⁽ᵏ⁾‖∞ y el residuo ‖b − Ax‖∞ son menores o iguales que la tolerancia.")
        # Si ρ(T) ≥ 1 y el cambio no baja en 5 iteraciones, no hay convergencia que esperar.
        if rho is not None and rho >= 1 and k >= 10 and cambio >= pasos[-6].cambio:
            return resultado(False, f"El cambio entre iteraciones no disminuye y ρ(T) ≈ {rho:.4g} ≥ 1: "
                                    "el método no converge para este sistema.")
    return resultado(False, "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia.")
