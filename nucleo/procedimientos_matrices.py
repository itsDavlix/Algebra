"""Operaciones con matrices con su paso a paso y su verificación.

Reutiliza el núcleo existente (determinantes exactos, Gauss-Jordan para la
inversa, transpuesta y rango) y añade lo que pide el banco de ejercicios:
justificar la inversa con det(A) ≠ 0 y comprobar A·A⁻¹ = I.
"""

from dataclasses import dataclass, field
from fractions import Fraction

from nucleo.determinantes import determinante, determinante_con_pasos, resumen_eficiencia
from nucleo.matrices import (
    matriz_inversa_con_pasos, matriz_transpuesta_con_pasos, multiplicar_matrices, rango_matriz_con_pasos,
)

OPERACIONES = ("det(A)", "A⁻¹", "Aᵀ", "rango(A)", "A + B", "A − B", "A · B", "k · A")
BINARIAS = ("A + B", "A − B", "A · B")


@dataclass(frozen=True)
class ResultadoMatriz:
    operacion: str
    valor: object                 # número o matriz (lista de listas)
    pasos: tuple                  # textos «PASO n. …»
    verificacion: tuple = ()      # líneas (texto, estilo)
    determinante: object = None
    datos: dict = field(default_factory=dict)

    @property
    def es_matriz(self):
        return isinstance(self.valor, list)


# ---------------------------------------------------------------- formato
def numero(valor, fracciones=False, cifras=8):
    """Entero exacto, fracción (si se pide y es exacta) o decimal con 8 cifras."""
    if isinstance(valor, Fraction):
        if valor.denominator == 1:
            return str(valor.numerator).replace("-", "−")
        if fracciones:
            return f"{valor.numerator}/{valor.denominator}".replace("-", "−")
        valor = float(valor)
    valor = float(valor)
    if abs(valor) < 1e-12:
        return "0"
    if valor.is_integer() and abs(valor) < 1e15:
        return str(int(valor)).replace("-", "−")
    if fracciones:
        fraccion = Fraction(valor).limit_denominator(100000)
        if abs(float(fraccion) - valor) <= 1e-9 * max(1.0, abs(valor)):
            return f"{fraccion.numerator}/{fraccion.denominator}".replace("-", "−")
    return f"{valor:.{cifras}g}".replace("-", "−")


def matriz_texto(matriz, fracciones=False, sangria=""):
    celdas = [[numero(v, fracciones) for v in fila] for fila in matriz]
    ancho = max(len(c) for fila in celdas for c in fila)
    return "\n".join(sangria + "[ " + "  ".join(c.rjust(ancho) for c in fila) + " ]" for fila in celdas)


def _identidad(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _validar_cuadrada(A, operacion):
    if len(A) != len(A[0]):
        raise ValueError(f"{operacion} requiere una matriz cuadrada; A es {len(A)}×{len(A[0])}.")


# ---------------------------------------------------------------- operaciones
def calcular(operacion, A, B=None, k=None, metodo_det="lu"):
    if operacion not in OPERACIONES:
        raise ValueError("Elige una operación.")
    if operacion == "det(A)":
        _validar_cuadrada(A, "El determinante")
        valor, pasos, comprobacion = determinante_con_pasos(A, metodo_det)
        _, eficiencia = resumen_eficiencia(A)
        verificacion = ((comprobacion, "ok" if "✓" in comprobacion else "normal"),
                        ("", "normal"), (eficiencia, "tenue"))
        return ResultadoMatriz(operacion, valor, tuple(pasos), verificacion, valor, {"metodo": metodo_det})
    if operacion == "A⁻¹":
        return _inversa(A)
    if operacion == "Aᵀ":
        valor, pasos = matriz_transpuesta_con_pasos(A)
        return ResultadoMatriz(operacion, valor, tuple(pasos))
    if operacion == "rango(A)":
        valor, pasos = rango_matriz_con_pasos(A)
        n_min = min(len(A), len(A[0]))
        nota = ("Rango completo." if valor == n_min else f"Rango deficiente: {n_min - valor} fila(s) dependiente(s).")
        return ResultadoMatriz(operacion, valor, tuple(pasos), ((nota, "ok" if valor == n_min else "aviso"),))
    if operacion == "k · A":
        if k is None:
            raise ValueError("Escribe el escalar k.")
        valor = [[k * v for v in fila] for fila in A]
        pasos = [f"PASO 1. Multiplicar cada entrada de A por k = {numero(k)}:\n"
                 + "\n".join(f"Fila {i + 1}: " + ", ".join(f"{numero(k)}·({numero(v)}) = {numero(k * v)}" for v in fila)
                             for i, fila in enumerate(A))]
        return ResultadoMatriz(operacion, valor, tuple(pasos))
    if B is None:
        raise ValueError("Escribe la matriz B.")
    if operacion in ("A + B", "A − B"):
        if (len(A), len(A[0])) != (len(B), len(B[0])):
            raise ValueError(f"Para sumar o restar, A ({len(A)}×{len(A[0])}) y B ({len(B)}×{len(B[0])}) "
                             "deben tener el mismo tamaño.")
        signo = 1 if operacion == "A + B" else -1
        simbolo = "+" if signo == 1 else "−"
        valor = [[a + signo * b for a, b in zip(fa, fb)] for fa, fb in zip(A, B)]
        pasos = [f"PASO {i + 1}. Fila {i + 1}: cᵢⱼ = aᵢⱼ {simbolo} bᵢⱼ\n"
                 + ", ".join(f"{numero(a)} {simbolo} ({numero(b)}) = {numero(c)}" for a, b, c in zip(fa, fb, fc))
                 for i, (fa, fb, fc) in enumerate(zip(A, B, valor))]
        return ResultadoMatriz(operacion, valor, tuple(pasos))
    if len(A[0]) != len(B):
        raise ValueError(f"A·B requiere columnas de A = filas de B; A es {len(A)}×{len(A[0])} y B es "
                         f"{len(B)}×{len(B[0])}.")
    valor = multiplicar_matrices(A, B)
    pasos = []
    for i, fila in enumerate(A):
        detalle = []
        for j in range(len(B[0])):
            productos = " + ".join(f"({numero(fila[m])})({numero(B[m][j])})" for m in range(len(B)))
            detalle.append(f"c{i + 1}{j + 1} = {productos} = {numero(valor[i][j])}")
        pasos.append(f"PASO {i + 1}. Fila {i + 1} de A por cada columna de B:\n" + "\n".join(detalle))
    return ResultadoMatriz(operacion, valor, tuple(pasos), ((f"A·B es {len(A)}×{len(B[0])}.", "normal"),))


def _inversa(A):
    """det(A) primero (justifica la existencia), luego Gauss-Jordan sobre [A | I] y A·A⁻¹ = I."""
    _validar_cuadrada(A, "La inversa")
    n = len(A)
    det = determinante(A, "lu")
    justificacion = (f"PASO 0. Justificar la existencia de la inversa:\ndet(A) = {numero(det)}"
                     + (" ≠ 0, por lo tanto A es invertible." if det != 0 else
                        " = 0: A es singular y NO tiene inversa."))
    if det == 0:
        return ResultadoMatriz("A⁻¹", None, (justificacion,),
                               (("A es singular: sus filas son linealmente dependientes y [A | I] no puede "
                                 "reducirse a [I | A⁻¹].", "error"),), det)
    inversa, pasos = matriz_inversa_con_pasos(A)
    producto = multiplicar_matrices(A, inversa)
    error = max(abs(producto[i][j] - (1.0 if i == j else 0.0)) for i in range(n) for j in range(n))
    verificacion = (("Verificación A·A⁻¹ = I" + "ₙ" if n > 9 else "Verificación A·A⁻¹ = I" + "₀₁₂₃₄₅₆₇₈₉"[n], "titulo"),
                    (matriz_texto([[round(v, 10) + 0.0 for v in fila] for fila in producto]), "formula"),
                    (f"Error máximo respecto de I: {error:.1e}", "formula"),
                    ("✓ Se cumple A·A⁻¹ = I (salvo redondeo)." if error < 1e-9 else
                     "⚠ El producto se aleja de I: la matriz está mal condicionada.", "ok" if error < 1e-9 else "aviso"))
    return ResultadoMatriz("A⁻¹", inversa, (justificacion, *pasos), verificacion, det, {"producto": producto,
                                                                                       "error": error})
