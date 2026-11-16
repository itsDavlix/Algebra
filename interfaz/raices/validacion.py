"""Condiciones de cada método, comprobadas antes de resolver.

validar() es una función pura: recibe los datos y devuelve (mensaje, nivel),
con nivel en «pendiente», «ok», «aviso» o «error». La vista solo la muestra.
"""

from interfaz.raices.configuracion import evaluar
from nucleo.biseccion import MAX_ITERACIONES, iteraciones_necesarias


def validar(metodo, funcion, textos, leer, derivada=None, segunda=None):
    """textos: textos escritos en los campos del método; leer(): (valores, tol, iteraciones)."""
    if funcion is None:
        return "Paso ①: escribe f(x) arriba. La gráfica aparecerá y podrás elegir los valores aquí.", "pendiente"
    if not all(texto.strip() for texto in textos):
        return ("Haz clic en la gráfica donde quieras colocar el valor, escríbelo o pulsa "
                "«Sugerir valores».", "pendiente")
    try:
        valores, tolerancia, iteraciones = leer()
    except ValueError as exc:
        return str(exc), "error"
    if tolerancia <= 0:
        return "La tolerancia debe ser mayor que cero.", "error"
    if not 1 <= iteraciones <= MAX_ITERACIONES:
        return f"El máximo de iteraciones debe estar entre 1 y {MAX_ITERACIONES}.", "error"
    if metodo in ("Bisección", "Regula Falsi"):
        return _validar_cerrado(metodo, funcion, valores, tolerancia, iteraciones)
    if metodo == "Newton-Raphson":
        return _validar_newton(funcion, valores["x0"], derivada, segunda)
    return _validar_secante(funcion, valores["x0"], valores["x1"])


def _validar_cerrado(metodo, f, valores, tolerancia, iteraciones):
    a, b = valores["a"], valores["b"]
    if a >= b:
        return "Debe cumplirse a < b.", "error"
    fa, fb = evaluar(f, a), evaluar(f, b)
    if fa is None or fb is None:
        return "f no está definida en " + ("a." if fa is None else "b."), "error"
    if fa == 0 or fb == 0:
        return "✓ Uno de los extremos ya es una raíz.", "ok"
    if (fa < 0) == (fb < 0):
        return (f"f(a) = {fa:.6g} y f(b) = {fb:.6g} tienen el mismo signo: no se cumple Bolzano. "
                "Elige otro intervalo o pulsa «Sugerir valores».", "error")
    texto = (f"✓ f(a)·f(b) < 0: f(a) = {fa:.6g}, f(b) = {fb:.6g}. Por Bolzano hay al menos "
             "una raíz en [a, b].")
    if metodo == "Bisección":
        necesarias = iteraciones_necesarias(a, b, tolerancia)
        texto += f"\nIteraciones necesarias: n ≥ log₂((b − a)/tol) = {necesarias}."
        if necesarias > iteraciones:
            return texto + f" Sube el máximo a {necesarias} o más.", "aviso"
    return texto, "ok"


def _validar_newton(f, x0, derivada, segunda):
    f0 = evaluar(f, x0)
    if f0 is None:
        return "f no está definida en x₀.", "error"
    if derivada is None:
        return "Revisa la derivada escrita.", "error"
    d0 = evaluar(derivada, x0)
    if d0 is None:
        return "f′ no está definida en x₀.", "error"
    if d0 == 0:
        return "f′(x₀) = 0: la tangente es horizontal y no corta el eje x. Elige otro x₀.", "error"
    texto = f"✓ f(x₀) = {f0:.6g},  f′(x₀) = {d0:.6g}."
    s0 = evaluar(segunda, x0) if segunda else None
    if s0 is not None and f0 * s0 > 0:
        return texto + "\nf(x₀)·f″(x₀) > 0: se cumple la condición de Fourier.", "ok"
    return texto + "\nNo se cumple f(x₀)·f″(x₀) > 0; puede converger, pero revisa las iteraciones.", "aviso"


def _validar_secante(f, x0, x1):
    if x0 == x1:
        return "x₀ y x₁ deben ser distintos.", "error"
    f0, f1 = evaluar(f, x0), evaluar(f, x1)
    if f0 is None or f1 is None:
        return "f no está definida en " + ("x₀." if f0 is None else "x₁."), "error"
    if f0 == f1:
        return "f(x₀) = f(x₁): la secante es horizontal. Elige otros valores.", "error"
    return f"✓ f(x₀) = {f0:.6g},  f(x₁) = {f1:.6g}. La secante corta el eje x.", "ok"
