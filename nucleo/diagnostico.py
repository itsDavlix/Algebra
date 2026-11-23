"""Diagnóstico previo de un sistema A·X = B para Gauss-Jordan, Jacobi y Gauss-Seidel.

Antes de resolver dice qué método funciona y por qué, con los datos que lo
justifican: det(A) e intercambios de fila para Gauss-Jordan; ceros en la
diagonal, ρ(T) y el mejor orden de ecuaciones para los iterativos, junto con
una estimación de las iteraciones necesarias k ≈ log(ε) / log(ρ).
"""

import math
from dataclasses import dataclass

from nucleo.determinantes import determinante
from nucleo.iterativos import (
    dominancia_diagonal, matriz_iteracion, radio_espectral, reordenar_para_dominancia,
)
from nucleo.procedimientos_sistemas import resolver_directo

# Probar todas las permutaciones cuesta n!: con n = 7 tarda más de un segundo,
# demasiado para recalcular mientras se escribe. El botón «Reordenar filas» sí
# busca hasta n = 7.
MAX_ORDEN_AUTOMATICO = 6
MAX_GAUSS_JORDAN = 12

FUNCIONA, REORDENAR, NO_FUNCIONA, SIN_DATOS = "funciona", "reordenar", "no", "sin_datos"


@dataclass(frozen=True)
class Veredicto:
    metodo: str
    estado: str                    # FUNCIONA, REORDENAR, NO_FUNCIONA o SIN_DATOS
    detalle: str                   # explicación completa
    breve: str = ""                # una línea para el panel
    rho: float = None
    permutacion: tuple = None      # orden de ecuaciones recomendado (base 0)
    iteraciones: int = None        # estimación con k ≈ log(ε) / log(ρ)

    @property
    def marca(self):
        return {FUNCIONA: "✓", REORDENAR: "↻", NO_FUNCIONA: "✗"}.get(self.estado, "·")


def iteraciones_estimadas(rho, tolerancia):
    """Iteraciones para que el error inicial (≈ 1) se reduzca por debajo de ε, si el error decrece como ρᵏ."""
    if rho is None or not 0 <= rho < 1 or tolerancia <= 0:
        return None
    if rho == 0:
        return 1
    return max(1, math.ceil(math.log(tolerancia) / math.log(rho)))


def _texto(valor):
    return f"{valor:.4g}".replace("-", "−")


def _orden(permutacion):
    return ", ".join(str(p + 1) for p in permutacion)


def _gauss_jordan(A, b, det):
    n, m = len(A), len(A[0])
    if n != m:
        return Veredicto("Gauss-Jordan", FUNCIONA, f"Sistema {n}×{m}: clasificará si hay una, infinitas o ninguna solución.",
                         f"{n}×{m}: clasifica el sistema")
    if det == 0:
        return Veredicto("Gauss-Jordan", FUNCIONA, "det(A) = 0: indicará si hay infinitas soluciones o ninguna.",
                         "det = 0: clasifica el sistema")
    if n > MAX_GAUSS_JORDAN:
        return Veredicto("Gauss-Jordan", FUNCIONA, "det(A) ≠ 0: solución única.", "det ≠ 0 · solución única")
    pasos = resolver_directo(A, b, [f"x{i}" for i in range(n)]).pasos
    intercambios = sum(1 for paso in pasos if paso.startswith("PASO") and "Intercambiar" in paso.splitlines()[0])
    if intercambios:
        motivo = (f"{intercambios} intercambio{'s' if intercambios > 1 else ''} de fila"
                  + (" (hay ceros en la diagonal)" if any(A[i][i] == 0 for i in range(n)) else " (pivoteo parcial)"))
    else:
        motivo = "sin intercambios de fila"
    breve = f"det ≠ 0 · {intercambios} intercambio{'s' if intercambios != 1 else ''}" if intercambios else "det ≠ 0 · sin intercambios"
    return Veredicto("Gauss-Jordan", FUNCIONA, f"Solución única · {motivo}.", breve)


def _iterativo(A, b, metodo, tolerancia):
    n = len(A)
    ceros = [i + 1 for i in range(n) if A[i][i] == 0]
    rho_actual = None
    if not ceros:
        rho_actual = radio_espectral(matriz_iteracion(A, metodo))
        if rho_actual < 1:
            dominante = all(f.cumple for f in dominancia_diagonal(A))
            motivo = "dominante: convergencia garantizada" if dominante else "no es dominante, pero ρ < 1"
            return Veredicto(metodo, FUNCIONA, f"ρ(T) ≈ {_texto(rho_actual)} < 1 · {motivo}.",
                             f"ρ ≈ {_texto(rho_actual)} · {'dominante' if dominante else 'no dominante'}", rho_actual,
                             iteraciones=iteraciones_estimadas(rho_actual, tolerancia))
    problema = (f"Ceros en la diagonal (fila{'s' if len(ceros) > 1 else ''} {', '.join(map(str, ceros))})" if ceros
                else f"ρ(T) ≈ {_texto(rho_actual)} ≥ 1")
    if n > MAX_ORDEN_AUTOMATICO:
        return Veredicto(metodo, NO_FUNCIONA if not ceros else SIN_DATOS,
                         f"{problema}. Pulsa «Reordenar filas» para buscar otro orden.",
                         "ceros en la diagonal · prueba reordenar" if ceros else f"ρ ≈ {_texto(rho_actual)} ≥ 1 · prueba reordenar",
                         rho_actual)
    mejora = reordenar_para_dominancia(A, b, metodo)
    if mejora is None:
        if ceros:
            return Veredicto(metodo, NO_FUNCIONA, f"{problema} en todos los órdenes posibles.",
                             "ceros en la diagonal en todo orden")
        return Veredicto(metodo, NO_FUNCIONA, f"{problema} y ningún orden lo mejora: diverge.",
                         f"ρ ≈ {_texto(rho_actual)} ≥ 1 · diverge", rho_actual)
    _A, _b, permutacion, rho = mejora
    if rho < 1:
        return Veredicto(metodo, REORDENAR, f"{problema}. Con el orden {_orden(permutacion)}: ρ ≈ {_texto(rho)} < 1.",
                         f"orden {_orden(permutacion)} → ρ ≈ {_texto(rho)}", rho, permutacion,
                         iteraciones_estimadas(rho, tolerancia))
    return Veredicto(metodo, NO_FUNCIONA, f"{problema}. Ni con el mejor orden ({_orden(permutacion)}): "
                                          f"ρ ≈ {_texto(rho)} ≥ 1, diverge.",
                     f"ρ ≈ {_texto(rho)} ≥ 1 aun reordenando", rho, permutacion)


def diagnosticar(A, b, tolerancia=1e-6):
    """Veredicto de Gauss-Jordan, Jacobi y Gauss-Seidel para el sistema tal como está escrito."""
    n, m = len(A), len(A[0])
    det = determinante(A, "lu") if n == m else None
    veredictos = [_gauss_jordan(A, b, det)]
    for metodo in ("Jacobi", "Gauss-Seidel"):
        if n != m:
            veredictos.append(Veredicto(metodo, NO_FUNCIONA, "Necesita tantas ecuaciones como incógnitas.",
                                        "el sistema no es cuadrado"))
        elif det == 0:
            veredictos.append(Veredicto(metodo, NO_FUNCIONA, "det(A) = 0: no hay solución única que aproximar.",
                                        "det = 0: sin solución única"))
        else:
            veredictos.append(_iterativo(A, b, metodo, tolerancia))
    return veredictos


def anotar_dominancia(A):
    """Por fila: (|aᵢᵢ|, Σ|aᵢⱼ| j≠i, cumple) para mostrarlo junto a la matriz."""
    return [(abs(f.diagonal), f.suma, f.cumple) for f in dominancia_diagonal(A)]
