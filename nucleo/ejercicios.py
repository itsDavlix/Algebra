"""Ejercicios guardados por método y dificultad.

Fuentes:
- «Banco de ejercicios: sistemas de ecuaciones lineales, matrices y ecuaciones
  no lineales» (Partes I a IV: 49 ejercicios).
- «Métodos iterativos: Jacobi y Gauss-Seidel» (presentación y ejemplos paso a paso).

Cada ejercicio indica el método recomendado y por qué, porque en el banco la
elección del método forma parte de la evaluación. Todos están verificados en
tests/test_ejercicios.py con tolerancia 10⁻⁶.
"""

import re
from dataclasses import dataclass, field
from fractions import Fraction as F

NIVELES = ("Básico", "Intermedio", "Avanzado")
PARTES = {"I": "Parte I · Sistemas lineales", "II": "Parte II · Determinante e inversa",
          "III": "Parte III · Ecuaciones no lineales", "IV": "Parte IV · Fraccionarias y compuestas"}
_ROMANOS = {"I": 1, "II": 2, "III": 3, "IV": 4}


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

    @property
    def _referencia(self):
        return re.search(r"Parte (IV|I{1,3}), ejercicio (\d+)", self.fuente)

    @property
    def documento(self):
        """Identificador en el banco: «P1-E9»; vacío si el ejercicio viene de la clase."""
        ref = self._referencia
        return f"P{_ROMANOS[ref.group(1)]}-E{ref.group(2)}" if ref else ""

    @property
    def parte(self):
        """«Parte I · Sistemas lineales», o la fuente (p. ej. la clase) si no es del banco."""
        ref = self._referencia
        return PARTES[ref.group(1)] if ref else self.fuente.split(",")[0]

    @property
    def orden(self):
        """Para ordenar: parte del banco, dificultad y número de ejercicio; la clase va al final."""
        ref = self._referencia
        parte = _ROMANOS[ref.group(1)] if ref else 9
        return parte, NIVELES.index(self.dificultad), int(ref.group(2)) if ref else 0


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
    # Parte III, ejercicios 11-15: el banco sugiere el método; se escriben tal como vienen.
    Ejercicio("nl11", "ln(x) + sen(x) = 1.2", "Intermedio", "Bisección",
              {"funcion": "ln(x) + sen(x) = 1.2", "a": "1", "b": "2"},
              "Método sugerido: bisección o falsa posición. Dominio: x > 0.",
              "f(1) ≈ −0.359 y f(2) ≈ 0.402: cambio de signo en [1, 2], dentro del dominio. Hay otras raíces "
              "(≈ 3.06 y ≈ 5.71); este intervalo aísla la primera. Con falsa posición converge en 9 iteraciones.",
              f"{BANCO}, Parte III, ejercicio 11", {"raiz": 1.2754488}),
    Ejercicio("nl12", "e^(−x) + cos(x) = 0.5", "Intermedio", "Secante",
              {"funcion": "e^(−x) + cos(x) = 0.5", "x0": "1", "x1": "2"},
              "Método sugerido: secante.",
              "f(1) ≈ 0.408 y f(2) ≈ −0.781 rodean la raíz; la secante no necesita derivar e^(−x) + cos(x). "
              "Por el coseno hay infinitas raíces positivas: se aproxima la primera (≈ 1.3324).",
              f"{BANCO}, Parte III, ejercicio 12", {"raiz": 1.3323902}),
    Ejercicio("nl13", "x² − 3 sen(x) − ln(x + 2) = 0", "Avanzado", "Newton-Raphson",
              {"funcion": "x² − 3 sen(x) − ln(x + 2) = 0", "x0": "2.5"},
              "Método sugerido: Newton-Raphson. Dominio: x > −2.",
              "Tiene dos raíces (≈ −0.1876 y ≈ 2.0226); se busca la positiva. En x₀ = 2.5, f(x₀) ≈ 2.95 y "
              "f″(x₀) ≈ 3.85 tienen el mismo signo (Fourier) y f′(x₀) ≈ 7.18 ≠ 0: converge en 5 iteraciones.",
              f"{BANCO}, Parte III, ejercicio 13", {"raiz": 2.0226002}),
    Ejercicio("nl14", "e^(x/2) + sen(2x) = 3", "Intermedio", "Regula Falsi",
              {"funcion": "e^(x/2) + sen(2x) = 3", "a": "2", "b": "3"},
              "Método sugerido: bisección o falsa posición.",
              "Única raíz real: f(2) ≈ −1.04 y f(3) ≈ 1.20. Falsa posición cumple la tolerancia en x y en |f| "
              "en 9 iteraciones; bisección necesita 20 y deja |f| ≈ 2·10⁻⁶ porque f es empinada (f′ ≈ 4.5).",
              f"{BANCO}, Parte III, ejercicio 14", {"raiz": 2.6730623}),
    Ejercicio("nl15", "ln(x + 3) + cos(x) = x/2", "Avanzado", "Secante",
              {"funcion": "ln(x + 3) + cos(x) = x/2", "x0": "2", "x1": "3"},
              "Método sugerido: secante. Dominio: x > −3.",
              "Cuatro raíces reales (≈ −2.373, 2.165, 5.256, 6.463): x₀ = 2 y x₁ = 3, con f(2) ≈ 0.193 y "
              "f(3) ≈ −0.698, encierran la primera positiva y la secante converge en 6 iteraciones.",
              f"{BANCO}, Parte III, ejercicio 15", {"raiz": 2.1646088}),
    # Parte IV: identificar el dominio antes de iterar.
    Ejercicio("fr1", "sen(x) / ln(x) = 1", "Intermedio", "Bisección",
              {"funcion": "sen(x) / ln(x) = 1", "a": "2", "b": "3"},
              "Dominio: x > 0 y x ≠ 1 (ln(1) = 0 anula el denominador).",
              "Un intervalo que contenga x = 1 (como [0.5, 1.5]) cambia de signo por el polo, no por una raíz. "
              "En [2, 3], f(2) ≈ 0.312 y f(3) ≈ −0.872 y f es continua: Bolzano aplica. Raíz única ≈ 2.2191.",
              f"{BANCO}, Parte IV, ejercicio 1", {"raiz": 2.2191076}),
    Ejercicio("fr2", "2x³ / (x − 3) = 0", "Avanzado", "Bisección",
              {"funcion": "2x³/(x − 3) = 0", "a": "-1", "b": "0.5"},
              "El documento no indica el lado derecho: se toma «= 0» (igualdad supuesta). Dominio: x ≠ 3.",
              "Despeje exacto: 2x³ = 0 → x = 0, que respeta x ≠ 3. Es raíz triple (f ≈ −2x³/3 cerca de 0): "
              "falsa posición, la sugerida, se estanca; bisección en [−1, 0.5] converge (21 iteraciones).",
              f"{BANCO}, Parte IV, ejercicio 2", {"raiz": 0.0}),
    Ejercicio("fr2_rf", "2x³ / (x − 3) = 0 (falsa posición)", "Avanzado", "Regula Falsi",
              {"funcion": "2x³/(x − 3) = 0", "a": "-1", "b": "0.5"},
              "Contraejemplo: aplique la falsa posición sugerida y analice por qué no converge.",
              "En una raíz triple f es casi plana: la recta secante corta lejos de 0 y siempre se mueve el "
              "mismo extremo. Con 100 iteraciones no cumple la tolerancia; compárelo con bisección.",
              f"{BANCO}, Parte IV, ejercicio 2", {"converge": False}),
    Ejercicio("fr3", "e^(1/x) + 2x / tan(x) = 2", "Avanzado", "Newton-Raphson",
              {"funcion": "e^(1/x) + 2x / tan(x) = 2", "x0": "1"},
              "Dominio: x ≠ 0 (1/x) y tan(x) definida y no nula: x ≠ kπ/2.",
              "Hay infinitas raíces (≈ −4.58, 1.54, 4.63, 7.80, …). En x₀ = 1 la función está definida, "
              "f(1) ≈ 2.00 y f″(1) ≈ 6.13 cumplen Fourier y f′(1) ≈ −4.26 ≠ 0: converge a ≈ 1.5424.",
              f"{BANCO}, Parte IV, ejercicio 3", {"raiz": 1.5423960}),
    Ejercicio("fr4", "ln(x + 1) / (x² − 4) = −0.1", "Intermedio", "Bisección",
              {"funcion": "ln(x + 1) / (x² − 4) = −0.1", "a": "0", "b": "1"},
              "Dominio: x > −1 y x ≠ ±2 (en el dominio, solo x = 2 anula el denominador).",
              "[1, 3] cambia de signo pero contiene el polo x = 2. En [0, 1], f(0) = 0.1 y f(1) ≈ −0.131 y f "
              "es continua: raíz única ≈ 0.4605.",
              f"{BANCO}, Parte IV, ejercicio 4", {"raiz": 0.4605188}),
    Ejercicio("fr5", "(x + 4) / (x − 1) = 0", "Básico", "Bisección",
              {"funcion": "(x + 4)/(x − 1) = 0", "a": "-6", "b": "-3"},
              "El documento no indica el lado derecho: se toma «= 0» (igualdad supuesta). Dominio: x ≠ 1.",
              "Despeje exacto: x + 4 = 0 → x = −4 (≠ 1). [−6, −3] no contiene el polo x = 1 y "
              "f(−6) ≈ 0.286, f(−3) = −0.25: bisección lo confirma numéricamente.",
              f"{BANCO}, Parte IV, ejercicio 5", {"raiz": -4.0}),
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
    # 11-19 tal como vienen en el documento (subíndices, fracciones entre paréntesis, guion «–»).
    11: (["2x₂ − 3x₃ + x₄ + 4x₅ = −18", "3x₁ + 2x₃ − 4x₄ + x₅ = 6", "−2x₁ + 5x₂ + 3x₄ − 2x₅ = −2",
          "4x₁ − x₂ + 3x₃ − 3x₅ = 24", "x₁ − 3x₂ − 2x₃ + 5x₄ = 4"], (2, -1, 3, 1, -2)),
    12: (["0.5x − 0.75y + 2z – (1/3)w = 181/60", "1.5x + y − 2.5z + (2/3)w = −0.75",
          "−x + 0.5y + (3/4)z − 2w = 7/30", "(2/3)x − 2y + 0.5z + 1.25w = 253/120"],
         (F(162683, 104610), F(-16458, 17435), F(96608, 156915), F(-94081, 104610))),
    13: (["12x + 6y + 4z + 3w = 9", "30x + 20y + 15z + 12w = 23", "20x + 15y + 12z + 10w = 16",
          "105x + 84y + 70z + 60w = 87"], (1, -2, 3, -1)),
    14: (["2x − 3y + z + 4w = 7", "4x − y − 3z + 2w = 5", "−2x + 8y − 6z − 10w = −16", "3x + 2y − 4z + w = 4"],
         None),
    15: (["(1/2)x₂ + x₃ − x₄ = 3", "2x₁ + x₂ − x₃ + (1/2)x₄ = 5", "x₁ − x₂ + 2x₃ + x₄ = 1",
          "(1/2)x₁ + 2x₂ + x₃ − x₄ = 4"], (F(115, 32), F(-17, 32), F(3, 64), F(-103, 32))),
    16: (["0.5x₁ + 1.5x₂ − 0.5x₃ + 2.0x₄ = 4.5", "1.2x₁ − 0.8x₂ + 2.4x₃ + 0.6x₄ = 3.2",
          "2.1x₁ + 1.0x₂ − 1.3x₃ + 0.5x₄ = −1.7", "−0.7x₁ + 2.2x₂ + 1.1x₄ = 2.6"],
         (F(-3034, 3841), F(-11882, 19205), F(2871, 3841), F(59504, 19205))),
    17: (["2x₁ + (2/3)x₂ − (1/2)x₃ + x₄ = 2", "(3/4)x₁ + x₂ + (2/5)x₃ − x₄ = 1",
          "x₁ − (1/3)x₂ + 2x₃ + (1/2)x₄ = 5", "2x₁ + x₂ + (1/4)x₃ + (3/2)x₄ = 6"],
         (F(-143, 331), F(3531, 1324), F(850, 331), F(1569, 662))),
    18: (["1.25x₂ + 2.50x₃ − 0.75x₄ = 2.25", "0.50x₁ − 1.50x₂ + 0.25x₃ + 2.00x₄ = −1.50",
          "1.75x₁ + 0.50x₂ − 1.00x₃ + 0.25x₄ = 3.00", "−1.00x₁ + 2.25x₂ + 0.75x₃ + 1.50x₄ = 4.25"],
         (F(10138, 9355), F(3795, 1871), F(324, 9355), F(928, 1871))),
    19: (["x₁ + (3/5)x₂ + x₃ + (1/2)x₄ = 7/5", "(1/4)x₁ − 2x₂ + (3/2)x₃ + x₄ = −2",
          "2x₁ + (1/3)x₂ − x₃ + (2/3)x₄ = 3", "x₁ − (1/2)x₂ + (1/4)x₃ + 2x₄ = 5"],
         (F(-1868, 4789), F(8931, 4789), F(-4646, 4789), F(15720, 4789))),
}
TITULOS_SISTEMAS = {
    1: "Densa, sin ceros", 2: "Un cero, coeficientes pequeños", 3: "Densa, pivotes cambian de fila",
    4: "Un cero en la matriz", 5: "Densa", 6: "a₄₄ = 0 (pivoteo)", 7: "Densa", 8: "Diagonal con ceros",
    9: "2w = 2 da w directo", 10: "Densa", 11: "5×5, diagonal nula", 12: "Fracciones y decimales (exacto)",
    13: "Mal condicionado (exacto)", 14: "Analizar: ¿solución única?", 15: "Coeficientes fraccionarios",
    16: "Coeficientes decimales", 17: "Fracciones propias e impropias", 18: "Decimales mixtos",
    19: "Coeficientes racionales",
}


def _gauss_jordan(numero, dificultad, motivo, exacto=False):
    """exacto: el ejercicio se carga con Gauss-Jordan en fracciones (lo pide el banco o lo aconseja)."""
    ecuaciones, solucion = SISTEMAS_BANCO[numero]
    datos = {"sistema": _sistema(ecuaciones)}
    if exacto:
        datos["exacto"] = True
    esperado = {"solucion": solucion} if solucion is not None else {"tipo": "infinitas"}
    return Ejercicio(f"gj{numero}", TITULOS_SISTEMAS[numero], dificultad, "Gauss-Jordan", datos,
                     "Resuelva el sistema, expréselo como A·X = B y verifique la solución.", motivo,
                     f"{BANCO}, Parte I, ejercicio {numero}", esperado)


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
    _gauss_jordan(11, "Avanzado", "5×5 con los cinco aᵢᵢ = 0: Gauss-Jordan necesita 4 intercambios de fila. "
                                  "Jacobi diverge (ρ ≈ 1.15 aun reordenando); Gauss-Seidel solo reordenando."),
    _gauss_jordan(12, "Avanzado", "El banco pide operar con fracciones o ≥ 8 cifras: con fracciones exactas el "
                                  "residuo es 0 y la solución es exacta (denominadores grandes, p. ej. 104610).",
                  exacto=True),
    _gauss_jordan(13, "Avanzado", "Matriz tipo Hilbert, mal condicionada (cond ≈ 5.8·10⁴): en decimales se "
                                  "pierden cifras; con fracciones sale exacta (1, −2, 3, −1).", exacto=True),
    _gauss_jordan(14, "Intermedio", "det(A) = 0 y rango(A) = rango([A|B]) = 3 < 4: no hay solución única, "
                                    "hay infinitas (una incógnita libre). Gauss-Jordan lo clasifica.",
                  exacto=True),
    _gauss_jordan(15, "Intermedio", "Coeficientes 1/2: con fracciones exactas la solución tiene denominador 64.",
                  exacto=True),
    _gauss_jordan(16, "Intermedio", "Decimales: se conservan ≥ 8 cifras; a₃₄ = 0 en la última fila."),
    _gauss_jordan(17, "Intermedio", "Fracciones propias e impropias: Gauss-Jordan exacto sin intercambios. "
                                    "También convergen Jacobi y Gauss-Seidel (ρ < 1) aunque no sea dominante.",
                  exacto=True),
    _gauss_jordan(18, "Intermedio", "a₁₁ = 0: hace falta intercambiar filas; decimales con dos cifras."),
    _gauss_jordan(19, "Avanzado", "Coeficientes racionales variados (1/3, 3/5, 2/3): solución exacta con "
                                  "denominador 4789.", exacto=True),
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
    Ejercicio("it_banco9", "Diagonal con ceros (reordenar)", "Intermedio", "Gauss-Seidel",
              {"sistema": _sistema(SISTEMAS_BANCO[9][0]), "x0": "0, 0, 0, 0", "reordenar": True},
              "Resuelva con Gauss-Seidel.",
              "La diagonal tiene ceros: hay que reordenar las ecuaciones. Con el orden 3, 2, 1, 4 se obtiene "
              "ρ(T_GS) ≈ 0.39 < 1 y converge aunque no sea dominante.",
              f"{BANCO}, Parte I, ejercicio 9", {"solucion": SISTEMAS_BANCO[9][1]}),
    Ejercicio("it_banco10", "Gauss-Seidel sí, Jacobi no", "Avanzado", "Gauss-Seidel",
              {"sistema": _sistema(SISTEMAS_BANCO[10][0]), "x0": "0, 0, 0, 0", "reordenar": True},
              "Compare Jacobi y Gauss-Seidel tras reordenar.",
              "Ningún orden es dominante. Reordenado, ρ(T_GS) ≈ 0.39 (converge) pero ρ(T_J) ≈ 1.11 "
              "(Jacobi no converge): muestra que la convergencia depende del método y de la matriz.",
              f"{BANCO}, Parte I, ejercicio 10", {"solucion": SISTEMAS_BANCO[10][1]}),
    Ejercicio("it_banco17", "Jacobi más rápido que Gauss-Seidel", "Intermedio", "Jacobi",
              {"sistema": _sistema(SISTEMAS_BANCO[17][0]), "x0": "0, 0, 0, 0"},
              "Resuelva con Jacobi y compare con Gauss-Seidel («Comparar J / GS»).",
              "No es dominante (solo la fila 3 cumple), pero ρ(T_J) ≈ 0.54 y ρ(T_GS) ≈ 0.63 son < 1: ambos "
              "convergen. Aquí Jacobi gana (25 frente a 32 iteraciones): Gauss-Seidel no siempre es más rápido.",
              f"{BANCO}, Parte I, ejercicio 17", {"solucion": SISTEMAS_BANCO[17][1]}),
    Ejercicio("it_banco11", "5×5, diagonal nula (reordenar)", "Avanzado", "Gauss-Seidel",
              {"sistema": _sistema(SISTEMAS_BANCO[11][0]), "x0": "0, 0, 0, 0, 0", "reordenar": True},
              "Resuelva con Gauss-Seidel tras reordenar las ecuaciones.",
              "Ningún orden es dominante; con el orden 2, 3, 1, 5, 4 ρ(T_GS) ≈ 0.81 < 1: converge, aunque lento "
              "(≈ 70 iteraciones). Jacobi no converge en ningún orden.",
              f"{BANCO}, Parte I, ejercicio 11", {"solucion": SISTEMAS_BANCO[11][1]}),
    Ejercicio("it_banco1", "Jacobi diverge (ρ ≈ 2)", "Avanzado", "Jacobi",
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


TITULOS_MATRICES = {1: "Densa", 2: "Cuatro ceros", 3: "Dos ceros", 4: "Dos ceros", 5: "Ceros en la columna 1",
                    6: "Densa, sin ceros", 7: "Dos ceros", 8: "Densa, inversa grande", 9: "Dos ceros",
                    10: "Densa salvo un cero"}


def _matriz(numero, dificultad, motivo):
    filas, det = MATRICES_BANCO[numero]
    return Ejercicio(f"m{numero}", TITULOS_MATRICES[numero], dificultad, "Inversa",
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
