"""Ejercicios guardados por método y dificultad.

Fuentes:
- «Banco de ejercicios: sistemas de ecuaciones lineales, matrices y ecuaciones
  no lineales» (Partes I, II y III).
- «Métodos iterativos: Jacobi y Gauss-Seidel» (presentación y ejemplos paso a paso).

Cada ejercicio indica el método recomendado y por qué, porque en el banco la
elección del método forma parte de la evaluación. Todos están verificados en
tests/test_ejercicios.py con tolerancia 10⁻⁶.
"""

from dataclasses import dataclass, field

NIVELES = ("Básico", "Intermedio", "Avanzado")


@dataclass(frozen=True)
class Ejercicio:
    clave: str
    titulo: str
    dificultad: str
    metodo: str
    datos: dict
    enunciado: str
    justificacion: str
    fuente: str
    esperado: dict = field(default_factory=dict)


BANCO = "Banco de ejercicios"
CLASE = "Clase Jacobi y Gauss-Seidel"

# ------------------------------------------------------------------ raíces (Parte III)
RAICES = (
    Ejercicio("nl1", "x³ − 4x − 9 = 0", "Básico", "Bisección",
              {"funcion": "x^3 - 4x - 9", "a": "2", "b": "3"},
              "Localice una raíz real y justifique el intervalo inicial.",
              "f(2) = −9 < 0 y f(3) = 6 > 0: Bolzano asegura una raíz en [2, 3]. Bisección garantiza "
              "convergencia y su cota (b − a)/2ⁿ indica de antemano cuántas iteraciones hacen falta.",
              f"{BANCO}, Parte III, ejercicio 1", {"raiz": 2.7065279545}),
    Ejercicio("nl8", "x³ + x − 1 = 0", "Básico", "Newton-Raphson",
              {"funcion": "x^3 + x - 1", "x0": "1"},
              "Determine la raíz real y compare la gráfica con las iteraciones.",
              "f′(x) = 3x² + 1 > 0: f es creciente y tiene una sola raíz. Con x₀ = 1, f(1)·f″(1) = 1·6 > 0 "
              "(condición de Fourier): Newton converge cuadráticamente.",
              f"{BANCO}, Parte III, ejercicio 8", {"raiz": 0.6823278038}),
    Ejercicio("nl4", "x·ln(x) − 1 = 0", "Intermedio", "Regula Falsi",
              {"funcion": "x ln(x) - 1", "a": "1", "b": "2"},
              "Determine la raíz positiva teniendo en cuenta el dominio (x > 0).",
              "El dominio exige x > 0; en [1, 2] f está definida y f(1) = −1, f(2) ≈ 0.386. Regula Falsi "
              "aprovecha que f es casi lineal en el intervalo y no sale del dominio.",
              f"{BANCO}, Parte III, ejercicio 4", {"raiz": 1.7632228344}),
    Ejercicio("nl6", "ln(x + 2) + x² − 2 = 0", "Intermedio", "Regula Falsi",
              {"funcion": "ln(x+2) + x^2 - 2", "a": "0", "b": "1"},
              "Determine una raíz real dentro del dominio (x > −2).",
              "f(0) ≈ −1.307 y f(1) ≈ 0.099 cambian de signo en [0, 1], dentro del dominio. Regula Falsi "
              "mantiene la raíz encerrada y converge más rápido que Bisección en este intervalo.",
              f"{BANCO}, Parte III, ejercicio 6", {"raiz": 0.9569892367}),
    Ejercicio("nl7", "e^(−x) − x² + 0.5 = 0", "Intermedio", "Secante",
              {"funcion": "e^(-x) - x^2 + 0.5", "x0": "0", "x1": "1"},
              "Encuentre una raíz positiva y analice la estabilidad del método.",
              "f(0) = 1.5 y f(1) ≈ −0.132. Secante no necesita la derivada y, con dos valores que rodean "
              "la raíz, converge de forma superlineal (p ≈ 1.618) sin oscilar.",
              f"{BANCO}, Parte III, ejercicio 7", {"raiz": 0.9430917183}),
    Ejercicio("nl5", "x⁴ − 3x² − 3 = 0", "Intermedio", "Newton-Raphson",
              {"funcion": "x^4 - 3x^2 - 3", "x0": "2"},
              "Encuentre una raíz positiva analizando la forma de la función.",
              "f es par y f′(0) = 0: un x₀ cercano a 0 daría una tangente casi horizontal. Con x₀ = 2, "
              "f(2) = 1 y f″(2) = 42 tienen el mismo signo (Fourier): Newton converge sin saltar la raíz.",
              f"{BANCO}, Parte III, ejercicio 5", {"raiz": 1.9471229667}),
    Ejercicio("nl3", "cos(x) − x·eˣ = 0", "Intermedio", "Newton-Raphson",
              {"funcion": "cos(x) - x e^x", "x0": "1"},
              "Determine una raíz real en el intervalo positivo.",
              "f(0) = 1 > 0 y f(1) ≈ −2.18 < 0. En x₀ = 1, f(1)·f″(1) > 0 (ambos negativos): se cumple "
              "Fourier. Con x₀ = 0 no se cumpliría (f(0)·f″(0) < 0).",
              f"{BANCO}, Parte III, ejercicio 3", {"raiz": 0.5177573637}),
    Ejercicio("nl2", "eˣ − 3x² = 0", "Avanzado", "Bisección",
              {"funcion": "e^x - 3x^2", "a": "0", "b": "1"},
              "Encuentre una raíz positiva evitando valores iniciales inestables.",
              "f′ se anula cerca de x ≈ 0.204 y x ≈ 2.833: allí Newton daría tangentes casi horizontales. "
              "En [0, 1], f(0) = 1 y f(1) ≈ −0.28: Bisección es robusta frente a esos puntos críticos. "
              "Hay otra raíz positiva cerca de 3.733.",
              f"{BANCO}, Parte III, ejercicio 2", {"raiz": 0.9100075725}),
    Ejercicio("nl9", "x·e^(−x) − 0.2 = 0", "Avanzado", "Secante",
              {"funcion": "x e^(-x) - 0.2", "x0": "2", "x1": "3"},
              "Determine una raíz positiva; si hay más de una, indique cuál aproxima.",
              "Hay dos raíces positivas (≈ 0.2592 y ≈ 2.5426) separadas por el máximo en x = 1, donde "
              "f′(1) = 0. Se aproxima la mayor con x₀ = 2, x₁ = 3, lejos del máximo, para que la secante "
              "no se vuelva horizontal.",
              f"{BANCO}, Parte III, ejercicio 9", {"raiz": 2.5426413577}),
    Ejercicio("nl10", "x² − 5·sin(x) = 0", "Avanzado", "Newton-Raphson",
              {"funcion": "x^2 - 5 sin(x)", "x0": "2.5"},
              "Encuentre una raíz positiva no trivial (x ≠ 0).",
              "x = 0 es raíz trivial. Con x₀ = 2.5, lejos de 0: f(2.5) ≈ 3.26 y f″(2.5) ≈ 4.99 tienen el "
              "mismo signo (Fourier), así que Newton converge a la raíz no trivial ≈ 2.0859.",
              f"{BANCO}, Parte III, ejercicio 10", {"raiz": 2.0859345838}),
)

# ------------------------------------------------------------------ sistemas lineales
def _sistema(ecuaciones):
    return "\n".join(ecuaciones)


GUIA = _sistema(["10x₁ − x₂ + 2x₃ = 6", "−x₁ + 11x₂ − x₃ + 3x₄ = 25",
                 "2x₁ − x₂ + 10x₃ − x₄ = −11", "3x₂ − x₃ + 8x₄ = 15"])
PRACTICA = _sistema(["8x₁ − x₂ + x₃ = 8", "−x₁ + 10x₂ − 2x₃ + x₄ = 7",
                     "x₁ − 2x₂ + 9x₃ − x₄ = −4", "x₂ − x₃ + 7x₄ = 5"])
SISTEMAS_BANCO = {
    1: (["-3x - y + 4z + 5w = -6", "3x + 4y - 2z + 3w = 16", "-4x + 3y - z + 2w = -12",
         "-2x - 4y + 2z + 5w = -12"], (4, 2, 2, 0)),
    2: (["-x - y + 3z - 2w = -18", "6x + 4y + 5z - w = 21", "x - y + 2z + 3w = 9", "-3y + 6z - 2w = -21"],
        (5, 1, -2, 3)),
    3: (["6x + 2y + 6z + 6w = -18", "-2x + 5y - 3z - w = 21", "-2x - 3y + z + 4w = -13",
         "-2x + 6y + z + 6w = 10"], (-2, 3, 0, -2)),
    4: (["-2x + 2y - 2w = -2", "-x - 2y - 4z - 2w = -25", "2x + 3y + 4z + 2w = 31", "x + 2y + 5z - 2w = 6"],
        (1, 5, 1, 5)),
    5: (["x + 4y - z + 3w = 6", "3x - 2y + z + 3w = 22", "-3x + 4y + 6z + 3w = 41", "-x + 3y + 4z + w = 22"],
        (0, -1, 5, 5)),
    6: (["3x + 3y + 5z + 6w = 8", "-x + 6y - 4z + 2w = -6", "x - y + 2z + 6w = -7", "2x - 2y + 4z = 10"],
        (4, 1, 1, -2)),
    7: (["-4x - 3y + 2z - 2w = -26", "6x + 3y + 2z - 3w = 21", "-3x - y + 3z - 2w = -21",
         "4x - y - 2z + 4w = 32"], (5, 0, 0, 3)),
    8: (["-2z - 2w = 8", "-2x + 2y - 2z + 5w = -22", "-y - 3z + 2w = -7", "-4x + 6y - 4z + 5w = -26"],
        (0, -1, 0, -4)),
    9: (["2z + 4w = 8", "6x - 4y - 2z + 5w = 11", "-4x + y + z + 2w = -11", "2w = 2"], (5, 5, 2, 1)),
    10: (["-2x + 3z + 4w = 7", "4x + 6y + 3z + 2w = 21", "5x - 2y + 3z + 2w = 42", "2x - 3y - 2z - w = 8"],
         (5, -2, 3, 2)),
}


def _gauss_jordan(numero, dificultad, motivo):
    ecuaciones, solucion = SISTEMAS_BANCO[numero]
    return Ejercicio(f"gj{numero}", f"Banco · sistema {numero}", dificultad, "Gauss-Jordan",
                     {"sistema": _sistema(ecuaciones)},
                     "Resuelva el sistema, expréselo como A·X = B y verifique la solución.", motivo,
                     f"{BANCO}, Parte I, ejercicio {numero}", {"solucion": solucion})


SISTEMAS = (
    _gauss_jordan(9, "Básico", "Cinco coeficientes nulos y la ecuación 2w = 2 da w directamente: "
                               "pocas operaciones de fila."),
    _gauss_jordan(8, "Básico", "Tres coeficientes nulos; la diagonal tiene ceros, así que hace falta "
                               "intercambiar filas (pivoteo)."),
    _gauss_jordan(4, "Intermedio", "Un cero en la matriz; requiere eliminar en las cuatro columnas."),
    _gauss_jordan(2, "Intermedio", "Un cero y coeficientes pequeños; buena práctica de eliminación completa."),
    _gauss_jordan(6, "Intermedio", "a₄₄ = 0: el pivoteo parcial es necesario para no dividir entre cero."),
    _gauss_jordan(1, "Avanzado", "Matriz densa sin ceros; det(A) = 649 y fracciones intermedias."),
    _gauss_jordan(3, "Avanzado", "Matriz densa; los pivotes cambian de fila varias veces."),
    _gauss_jordan(5, "Avanzado", "Matriz densa con solución que incluye x = 0."),
    _gauss_jordan(7, "Avanzado", "Matriz densa; dos componentes de la solución valen 0."),
    _gauss_jordan(10, "Avanzado", "Matriz densa con det(A) = −284."),
    Ejercicio("it_guia_j", "Ejemplo guía (dominante)", "Básico", "Jacobi", {"sistema": GUIA, "x0": "0, 0, 0, 0"},
              "Aplique Jacobi desde X⁽⁰⁾ = (0, 0, 0, 0).",
              "Estrictamente diagonalmente dominante por filas: convergencia garantizada. Es el ejemplo "
              "desarrollado en la clase.", f"{CLASE}, sistema guía", {"solucion": (1, 2, -1, 1)}),
    Ejercicio("it_guia_gs", "Ejemplo guía (dominante)", "Básico", "Gauss-Seidel",
              {"sistema": GUIA, "x0": "0, 0, 0, 0"}, "Aplique Gauss-Seidel desde X⁽⁰⁾ = (0, 0, 0, 0).",
              "Mismo sistema que Jacobi: compare el número de iteraciones (Gauss-Seidel usa los valores "
              "nuevos de inmediato).", f"{CLASE}, sistema guía", {"solucion": (1, 2, -1, 1)}),
    Ejercicio("it_practica_j", "Actividad en parejas", "Intermedio", "Jacobi",
              {"sistema": PRACTICA, "x0": "0, 0, 0, 0"},
              "Aplique Jacobi y compare 3 iteraciones con Gauss-Seidel.",
              "Dominante por filas (8 > 2, 10 > 4, 9 > 4, 7 > 2): ambos convergen.",
              f"{CLASE}, actividad de aplicación", {}),
    Ejercicio("it_practica_gs", "Actividad en parejas", "Intermedio", "Gauss-Seidel",
              {"sistema": PRACTICA, "x0": "0, 0, 0, 0"},
              "Aplique Gauss-Seidel y compare 3 iteraciones con Jacobi.",
              "Dominante por filas: ambos convergen; Gauss-Seidel en menos iteraciones.",
              f"{CLASE}, actividad de aplicación", {}),
    Ejercicio("it_banco9", "Banco · sistema 9 (reordenar)", "Intermedio", "Gauss-Seidel",
              {"sistema": _sistema(SISTEMAS_BANCO[9][0]), "x0": "0, 0, 0, 0", "reordenar": True},
              "Resuelva con Gauss-Seidel.",
              "La diagonal tiene ceros: hay que reordenar las ecuaciones. Con el orden 3, 2, 1, 4 se obtiene "
              "ρ(T_GS) ≈ 0.39 < 1 y converge aunque no sea dominante.",
              f"{BANCO}, Parte I, ejercicio 9", {"solucion": SISTEMAS_BANCO[9][1]}),
    Ejercicio("it_banco10", "Banco · sistema 10 (Jacobi falla)", "Avanzado", "Gauss-Seidel",
              {"sistema": _sistema(SISTEMAS_BANCO[10][0]), "x0": "0, 0, 0, 0", "reordenar": True},
              "Compare Jacobi y Gauss-Seidel tras reordenar.",
              "Ningún orden es dominante. Reordenado, ρ(T_GS) ≈ 0.39 (converge) pero ρ(T_J) ≈ 1.11 "
              "(Jacobi no converge): muestra que la convergencia depende del método y de la matriz.",
              f"{BANCO}, Parte I, ejercicio 10", {"solucion": SISTEMAS_BANCO[10][1]}),
    Ejercicio("it_banco1", "Banco · sistema 1 (no converge)", "Avanzado", "Jacobi",
              {"sistema": _sistema(SISTEMAS_BANCO[1][0]), "x0": "0, 0, 0, 0"},
              "Intente resolver con Jacobi y analice el resultado.",
              "ρ(T_J) ≈ 2 > 1: Jacobi diverge. Ni reordenando se logra ρ < 1 con Jacobi; conviene un "
              "método directo (Gauss-Jordan).", f"{BANCO}, Parte I, ejercicio 1", {}),
)

# ------------------------------------------------------------------ matrices (Parte II)
MATRICES_BANCO = {
    1: ([[-4, 5, -4, 5], [-3, 3, -1, 3], [-3, 5, 1, -1], [1, -4, -1, -3]], -146),
    2: ([[3, -3, -1, 4], [0, -3, 0, 6], [0, 0, -2, 2], [-3, -3, 3, 3]], -54),
    3: ([[-3, -4, 2, 0], [1, 6, -3, 3], [1, 2, 0, 5], [3, 4, 3, -2]], 348),
    4: ([[-2, 0, -4, -1], [-3, -3, -3, 0], [6, -3, 4, 2], [-2, -3, -1, 2]], -99),
    5: ([[1, -3, 4, 5], [2, 4, 4, 2], [0, -3, -4, -1], [0, -3, 3, -3]], 342),
    6: ([[3, -3, 2, -3], [3, 3, 1, 5], [1, 6, 6, -1], [3, -2, 5, 1]], 844),
    7: ([[5, 6, -2, 4], [-1, 4, 1, 3], [1, 6, 3, 0], [6, 0, -1, 6]], 728),
    8: ([[5, 6, 1, 2], [6, 6, 2, -1], [-3, -3, 4, -2], [-3, 1, 3, 6]], 75),
    9: ([[2, -1, -3, 5], [-3, -4, 0, 1], [0, -3, -1, 6], [5, 4, 1, 2]], 55),
    10: ([[-4, -2, -4, 5], [-2, 2, 1, 4], [2, 0, 2, 4], [5, 3, -2, -4]], -654),
}


def _matriz(numero, dificultad, motivo):
    filas, det = MATRICES_BANCO[numero]
    return Ejercicio(f"m{numero}", f"Banco · matriz {numero}", dificultad, "Inversa",
                     {"matriz": "\n".join(" ".join(str(v) for v in fila) for fila in filas)},
                     "Calcule det(A) y A⁻¹; justifique la existencia de la inversa y verifique A·A⁻¹ = I₄.",
                     motivo, f"{BANCO}, Parte II, ejercicio {numero}", {"det": det})


MATRICES = (
    _matriz(2, "Básico", "Cuatro ceros (fila 3 casi triangular): det(A) = −54 y A⁻¹ con fracciones simples."),
    _matriz(9, "Básico", "Dos ceros; det(A) = 55 y A⁻¹ con denominadores 5 y 11."),
    _matriz(3, "Intermedio", "Dos ceros; det(A) = 348, inversa con denominador 29 tras simplificar."),
    _matriz(4, "Intermedio", "Dos ceros; det(A) = −99, inversa con denominadores 33 y 11."),
    _matriz(5, "Intermedio", "Dos ceros en la primera columna; det(A) = 342."),
    _matriz(7, "Intermedio", "Dos ceros; det(A) = 728 y denominadores grandes (364)."),
    _matriz(8, "Avanzado", "Densa; det(A) = 75 pero la inversa tiene entradas grandes (p. ej. −34/15)."),
    _matriz(1, "Avanzado", "Densa; det(A) = −146 con denominadores 73 y 146."),
    _matriz(10, "Avanzado", "Densa salvo un cero; det(A) = −654."),
    _matriz(6, "Avanzado", "Densa sin ceros; det(A) = 844, denominador 844 en toda la inversa."),
)

TODOS = RAICES + SISTEMAS + MATRICES


def ejercicios_de(metodos):
    """Ejercicios cuyo método está en la lista, ordenados por dificultad."""
    metodos = (metodos,) if isinstance(metodos, str) else tuple(metodos)
    elegidos = [e for e in TODOS if e.metodo in metodos]
    return sorted(elegidos, key=lambda e: NIVELES.index(e.dificultad))
