"""Resolución de ecuaciones reales por bisección, sin dependencias externas."""

import ast
import math
import operator
from dataclasses import dataclass

from nucleo.numeros import asegurar_finito


MAX_ITERACIONES = 1000
_FUNCIONES = {
    "sin": math.sin, "sen": math.sin, "cos": math.cos, "tan": math.tan,
    "sqrt": math.sqrt, "raiz": math.sqrt, "exp": math.exp,
    "log": math.log, "ln": math.log, "log10": math.log10, "abs": abs,
}
_CONSTANTES = {"pi": math.pi, "e": math.e}
_OPERACIONES = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: math.pow,
}


def preparar_funcion(ecuacion):
    """Devuelve (f, expresión) para una expresión en x o una igualdad.

    Recorre únicamente nodos matemáticos permitidos; no ejecuta código Python.
    Cada operación trabaja con reales finitos, también en las potencias.
    """
    if not isinstance(ecuacion, str) or not ecuacion.strip():
        raise ValueError("Escribe una ecuación, por ejemplo x^3 - x - 2 = 0.")
    texto = ecuacion.strip()
    if len(texto) > 500:
        raise ValueError("La ecuación es demasiado larga (máximo 500 caracteres).")
    texto = (texto.replace("^", "**").replace("×", "*").replace("÷", "/")
             .replace("−", "-").replace("π", "pi"))
    partes = texto.split("=")
    if len(partes) > 2 or any(not parte.strip() for parte in partes):
        raise ValueError("Usa una sola igualdad, por ejemplo x^2 = 2.")
    try:
        if len(partes) == 2:
            # Cada lado debe ser válido por separado. Así, una igualdad dentro
            # de una llamada o unos paréntesis sin cerrar no se reinterpretan.
            izquierda = ast.parse(partes[0].strip(), mode="eval")
            derecha = ast.parse(partes[1].strip(), mode="eval")
            arbol = ast.Expression(ast.BinOp(left=izquierda.body, op=ast.Sub(), right=derecha.body))
            texto = f"({partes[0].strip()}) - ({partes[1].strip()})"
        else:
            arbol = ast.parse(texto, mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError(
            "La ecuación no es válida. Usa x, paréntesis y operadores; "
            "escribe 2*x para multiplicar y punto para los decimales."
        ) from exc
    if sum(1 for _ in ast.walk(arbol)) > 200:
        raise ValueError("La ecuación es demasiado compleja. Simplifícala.")

    def validar(nodo, profundidad=0):
        if profundidad > 40:
            raise ValueError("La ecuación contiene demasiadas operaciones anidadas.")
        if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
            asegurar_finito(nodo.value, "Una constante de la ecuación")
        elif isinstance(nodo, ast.Name) and nodo.id in {"x", *_CONSTANTES}:
            pass
        elif isinstance(nodo, ast.BinOp) and type(nodo.op) in _OPERACIONES:
            validar(nodo.left, profundidad + 1)
            validar(nodo.right, profundidad + 1)
        elif isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.UAdd, ast.USub)):
            validar(nodo.operand, profundidad + 1)
        elif (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
              and nodo.func.id in _FUNCIONES and len(nodo.args) == 1 and not nodo.keywords):
            validar(nodo.args[0], profundidad + 1)
        else:
            raise ValueError(
                "Usa solo números, x, pi, e, +, -, *, /, ^ y funciones permitidas: "
                + ", ".join(_FUNCIONES) + "."
            )

    validar(arbol.body)

    def evaluar(nodo, x):
        if isinstance(nodo, ast.Constant):
            valor = float(nodo.value)
        elif isinstance(nodo, ast.Name):
            valor = x if nodo.id == "x" else _CONSTANTES[nodo.id]
        elif isinstance(nodo, ast.BinOp):
            valor = _OPERACIONES[type(nodo.op)](evaluar(nodo.left, x), evaluar(nodo.right, x))
        elif isinstance(nodo, ast.UnaryOp):
            valor = evaluar(nodo.operand, x)
            if isinstance(nodo.op, ast.USub):
                valor = -valor
        else:  # Las llamadas ya fueron validadas; todas tienen un solo argumento.
            valor = _FUNCIONES[nodo.func.id](evaluar(nodo.args[0], x))
        return asegurar_finito(valor, "El valor de la función")

    def funcion(x):
        x = asegurar_finito(x, "x")
        try:
            return evaluar(arbol.body, x)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            raise ValueError(
                f"No se puede evaluar f(x) en x = {_numero(x)}: "
                "hay una operación fuera del dominio real, división entre cero "
                "o un valor demasiado grande. Revisa la función y el intervalo."
            ) from exc

    return funcion, texto


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
        "Puede no haber una raíz detectable por este muestreo. Escribe a y b manualmente "
        "y comprueba que f sea continua en todo el intervalo."
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

    def resultado(raiz, valor, error, convergio, motivo):
        return ResultadoBiseccion(
            expresion, intervalo_inicial, tolerancia, raiz, valor, error,
            tuple(iteraciones), convergio, motivo,
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

    for numero in range(1, max_iteraciones + 1):
        # Evita desbordamientos tanto en a+b como en b-a.
        c = a / 2 + b / 2 if a < 0 < b else a + (b - a) / 2
        fc = funcion(c)
        # En aritmética exacta equivale a (b-a)/2. Conserva una cota también
        # cuando el punto medio se redondea hacia uno de los extremos.
        error = max(c - a, b - c)
        iteraciones.append(IteracionBiseccion(numero, a, b, c, fa, fb, fc, error))
        if fc == 0:
            return resultado(c, fc, 0.0, True, "f(c) = 0 en la precisión de cálculo.")
        if error <= tolerancia:
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
        ])
        if paso.numero == len(resultado.iteraciones):
            lineas.append("Parada: " + resultado.motivo)
        elif (paso.fa < 0) != (paso.fc < 0):
            lineas.append(f"f(a) y f(c) tienen signos opuestos: conservar [{n(paso.a)}, {n(paso.c)}].")
        else:
            lineas.append(f"f(c) y f(b) tienen signos opuestos: conservar [{n(paso.c)}, {n(paso.b)}].")
    return "\n".join(lineas)
