"""Evaluador propio de expresiones matemáticas en x, sin bibliotecas externas.

Responsabilidades:
1. Normalizar lo que escribe la persona (símbolos Unicode, ^, multiplicación
   implícita como 2x o 3(x+1), funciones sin paréntesis como sin x).
2. Validar el árbol sintáctico con una lista blanca de operaciones. Nunca se
   ejecuta código Python escrito por la persona: el árbol se traduce a
   funciones de Python construidas aquí mismo.
3. Derivar simbólicamente aplicando las reglas del cálculo (suma, producto,
   cociente, potencia y regla de la cadena) y simplificar el resultado.
4. Escribir la expresión de nuevo como texto editable o en notación legible.
"""

import ast
import difflib
import math
import re
from fractions import Fraction

from nucleo.numeros import asegurar_finito


LONGITUD_MAXIMA = 500
NODOS_MAXIMOS = 200
PROFUNDIDAD_MAXIMA = 40


# ---------------------------------------------------------------------------
# Funciones y constantes admitidas
# ---------------------------------------------------------------------------

def _potencia(base, exponente):
    """Potencia real. Admite raíces impares de negativos: (-8)^(1/3) = -2.

    Si el exponente es una fracción p/q con q impar, la potencia de una base
    negativa es real; con q par no existe en los reales y se informa.
    """
    if base < 0 and exponente != int(exponente):
        fraccion = Fraction(exponente).limit_denominator(1000)
        if fraccion.denominator % 2 == 1 and abs(float(fraccion) - exponente) <= 1e-12:
            magnitud = math.pow(-base, exponente)
            return -magnitud if fraccion.numerator % 2 else magnitud
        raise ValueError("potencia fuera del dominio real")
    return math.pow(base, exponente)


def _raiz_cubica(valor):
    return math.copysign(abs(valor) ** (1 / 3), valor) if valor else 0.0


def _raiz_n(valor, indice):
    if indice == 0:
        raise ValueError("índice cero")
    return _potencia(valor, 1 / indice)


def _log_base(valor, base):
    if base <= 0 or base == 1:
        raise ValueError("base de logaritmo inválida")
    return math.log(valor) / math.log(base)


def _sec(u):
    return 1 / math.cos(u)


def _csc(u):
    return 1 / math.sin(u)


def _cot(u):
    return math.cos(u) / math.sin(u)


# nombre canónico: (función, número de argumentos)
FUNCIONES = {
    "sin": (math.sin, 1), "cos": (math.cos, 1), "tan": (math.tan, 1),
    "sec": (_sec, 1), "csc": (_csc, 1), "cot": (_cot, 1),
    "asin": (math.asin, 1), "acos": (math.acos, 1), "atan": (math.atan, 1),
    "sinh": (math.sinh, 1), "cosh": (math.cosh, 1), "tanh": (math.tanh, 1),
    "sqrt": (math.sqrt, 1), "cbrt": (_raiz_cubica, 1), "raiz": (_raiz_n, 2),
    "exp": (math.exp, 1), "ln": (math.log, 1), "log": (_log_base, 2),
    "log10": (math.log10, 1), "log2": (math.log2, 1), "abs": (abs, 1),
}

# Alias que acepta la entrada -> nombre canónico.
ALIAS = {
    "sen": "sin", "arcsin": "asin", "arcsen": "asin", "asen": "asin",
    "arccos": "acos", "arctan": "atan", "atg": "atan", "tg": "tan",
    "senh": "sinh", "cosec": "csc", "cotg": "cot", "ctg": "cot",
    "raiz2": "sqrt", "raizc": "cbrt", "abs": "abs",
}

CONSTANTES = {"pi": math.pi, "e": math.e}
VARIABLE = "x"

# Descripciones breves para el autocompletado de la interfaz.
DESCRIPCIONES = {
    "sin": "seno", "cos": "coseno", "tan": "tangente", "sec": "secante",
    "csc": "cosecante", "cot": "cotangente", "asin": "arcoseno",
    "acos": "arcocoseno", "atan": "arcotangente", "sinh": "seno hiperbólico",
    "cosh": "coseno hiperbólico", "tanh": "tangente hiperbólica",
    "sqrt": "raíz cuadrada", "cbrt": "raíz cúbica real", "raiz": "raíz n-ésima: raiz(x, n)",
    "exp": "exponencial eˣ", "ln": "logaritmo natural",
    "log": "log(x) natural · log(x, b) en base b", "log10": "logaritmo base 10",
    "log2": "logaritmo base 2", "abs": "valor absoluto",
    "si": "por tramos: si(condición, valor, otro)", "pi": "constante π", "e": "constante e",
}

_COMPARACIONES = {
    ast.Lt: ("<", "<", lambda a, b: a < b), ast.Gt: (">", ">", lambda a, b: a > b),
    ast.LtE: ("<=", "≤", lambda a, b: a <= b), ast.GtE: (">=", "≥", lambda a, b: a >= b),
    ast.Eq: ("==", "=", lambda a, b: a == b), ast.NotEq: ("!=", "≠", lambda a, b: a != b),
}

_NOMBRES_CONOCIDOS = set(FUNCIONES) | set(ALIAS) | set(CONSTANTES) | {VARIABLE, "si"}


def nombres_disponibles():
    """Funciones y constantes que la interfaz puede sugerir, sin alias."""
    return sorted(set(FUNCIONES) | {"si", "pi", "e"})


# ---------------------------------------------------------------------------
# 1. Normalización del texto
# ---------------------------------------------------------------------------

_SUSTITUCIONES = (
    ("−", "-"), ("–", "-"), ("×", "*"), ("·", "*"), ("⋅", "*"), ("÷", "/"),
    ("π", "pi"), ("≤", "<="), ("≥", ">="), ("≠", "!="), ("²", "^2"), ("³", "^3"),
    ("√", " sqrt "), ("∛", " cbrt "),
)
_TOKEN = re.compile(
    r"\s*(?:(?P<num>(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<id>[A-Za-z_][A-Za-z_0-9]*)"
    r"|(?P<op>\*\*|<=|>=|==|!=|[-+*/^(),<>=]))"
)


def _tokenizar(texto):
    tokens = []
    posicion = 0
    texto = texto.rstrip()
    while posicion < len(texto):
        coincidencia = _TOKEN.match(texto, posicion)
        if not coincidencia or coincidencia.end() == posicion:
            caracter = texto[posicion:].lstrip()[:1]
            raise ValueError(f"El carácter «{caracter}» no se reconoce. Usa números, x, operadores y funciones.")
        tipo = coincidencia.lastgroup
        valor = coincidencia.group(tipo)
        if tipo == "op" and valor == "**":
            valor = "^"
        tokens.append((tipo, valor))
        posicion = coincidencia.end()
    return tokens


def _dividir_identificador(nombre):
    """Separa nombres pegados: 'xsin' -> ['x', 'sin'], 'pix' -> ['pi', 'x']."""
    if nombre in _NOMBRES_CONOCIDOS:
        return [nombre]
    # Programación dinámica: la partición con menos piezas, prefiriendo nombres largos.
    mejor = {0: []}
    for inicio in range(len(nombre)):
        if inicio not in mejor:
            continue
        for fin in range(len(nombre), inicio, -1):
            pieza = nombre[inicio:fin]
            if pieza in _NOMBRES_CONOCIDOS:
                candidato = mejor[inicio] + [pieza]
                if fin not in mejor or len(candidato) < len(mejor[fin]):
                    mejor[fin] = candidato
    if len(nombre) in mejor:
        return mejor[len(nombre)]
    sugerencia = difflib.get_close_matches(nombre, sorted(_NOMBRES_CONOCIDOS), n=1, cutoff=0.6)
    pista = f" ¿Quisiste decir «{sugerencia[0]}»?" if sugerencia else ""
    raise ValueError(f"«{nombre}» no es una función ni una constante conocida.{pista}")


def _clasificar(tokens):
    """Convierte identificadores en variable, constante o función."""
    salida = []
    for tipo, valor in tokens:
        if tipo != "id":
            salida.append((tipo, valor))
            continue
        for pieza in _dividir_identificador(valor):
            pieza = ALIAS.get(pieza, pieza)
            if pieza == VARIABLE or pieza in CONSTANTES:
                salida.append(("var", pieza))
            else:
                salida.append(("fn", pieza))
    return salida


_TERMINA_FACTOR = {"num", "var", ")"}
_EMPIEZA_FACTOR = {"num", "var", "fn", "("}


def _clave(token):
    tipo, valor = token
    return valor if tipo == "op" and valor in "()" else tipo


def _envolver_funciones_sin_parentesis(tokens):
    """sin x -> sin(x), sin 2x -> sin(2x), √x -> sqrt(x).

    Toma el término inmediato: factores numéricos o variables seguidos, con
    sus exponentes. Se detiene en + - * / , ) o en otra función.
    """
    salida = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        salida.append(token)
        i += 1
        if token[0] != "fn" or (i < len(tokens) and tokens[i] == ("op", "(")):
            continue
        inicio = i
        while i < len(tokens):
            if tokens[i][0] in ("num", "var"):
                i += 1
            elif tokens[i] == ("op", "^") and i + 1 < len(tokens) and tokens[i + 1][0] in ("num", "var"):
                i += 2
            elif (tokens[i] == ("op", "^") and i + 2 < len(tokens)
                  and tokens[i + 1] == ("op", "-") and tokens[i + 2][0] == "num"):
                i += 3
            else:
                break
        if i == inicio:
            raise ValueError(f"Escribe el argumento de {token[1]} entre paréntesis, por ejemplo {token[1]}(x).")
        salida.append(("op", "("))
        salida.extend(_envolver_funciones_sin_parentesis(tokens[inicio:i]))
        salida.append(("op", ")"))
    return salida


def _insertar_productos(tokens):
    salida = []
    for token in tokens:
        if salida and _clave(salida[-1]) in _TERMINA_FACTOR and _clave(token) in _EMPIEZA_FACTOR:
            if not (salida[-1][0] == "num" and token[0] == "num"):
                salida.append(("op", "*"))
        salida.append(token)
    return salida


def _a_python(tokens):
    partes = []
    for tipo, valor in tokens:
        partes.append("**" if (tipo, valor) == ("op", "^") else valor)
    return " ".join(partes)


def normalizar(texto):
    """Devuelve (izquierda, derecha|None) como texto en sintaxis de Python."""
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Escribe una función, por ejemplo x^3 - x - 2.")
    texto = texto.strip()
    if len(texto) > LONGITUD_MAXIMA:
        raise ValueError(f"La expresión es demasiado larga (máximo {LONGITUD_MAXIMA} caracteres).")
    for original, reemplazo in _SUSTITUCIONES:
        texto = texto.replace(original, reemplazo)
    tokens = _clasificar(_tokenizar(texto))
    if tokens.count(("op", "(")) != tokens.count(("op", ")")):
        faltan = tokens.count(("op", "(")) - tokens.count(("op", ")"))
        raise ValueError(
            f"Falta cerrar {faltan} paréntesis." if faltan > 0
            else f"Hay {-faltan} paréntesis de cierre sin abrir."
        )
    iguales = [i for i, token in enumerate(tokens) if token == ("op", "=")]
    if len(iguales) > 1:
        raise ValueError("Usa una sola igualdad, por ejemplo x^2 = 2.")
    lados = [tokens] if not iguales else [tokens[:iguales[0]], tokens[iguales[0] + 1:]]
    if any(not lado for lado in lados):
        raise ValueError("Completa ambos lados de la igualdad, por ejemplo x^2 = 2.")
    textos = [_a_python(_insertar_productos(_envolver_funciones_sin_parentesis(lado))) for lado in lados]
    return textos[0], (textos[1] if len(textos) == 2 else None)


# ---------------------------------------------------------------------------
# 2. Validación: árbol canónico con solo nodos permitidos
# ---------------------------------------------------------------------------

def _analizar_lado(texto):
    try:
        return ast.parse(texto, mode="eval").body
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError(
            "La expresión está incompleta o tiene operadores seguidos. "
            "Revisa que cada operador tenga sus dos términos."
        ) from exc


def _canonico(nodo, profundidad=0):
    """Copia el árbol validando cada nodo y usando nombres canónicos."""
    if profundidad > PROFUNDIDAD_MAXIMA:
        raise ValueError("La expresión tiene demasiadas operaciones anidadas.")
    siguiente = profundidad + 1
    if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
        asegurar_finito(nodo.value, "Una constante de la expresión")
        return ast.Constant(nodo.value)
    if isinstance(nodo, ast.Name) and (nodo.id == VARIABLE or nodo.id in CONSTANTES):
        return ast.Name(nodo.id, ast.Load())
    if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
        return ast.BinOp(_canonico(nodo.left, siguiente), type(nodo.op)(), _canonico(nodo.right, siguiente))
    if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, ast.UAdd):
        return _canonico(nodo.operand, siguiente)
    if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, ast.USub):
        return ast.UnaryOp(ast.USub(), _canonico(nodo.operand, siguiente))
    if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name) and not nodo.keywords:
        nombre = nodo.func.id
        argumentos = nodo.args
        if nombre == "si":
            if len(argumentos) != 3:
                raise ValueError("Usa si(condición, valor si se cumple, valor si no), por ejemplo si(x < 0, -x, x).")
            condicion = argumentos[0]
            if not isinstance(condicion, ast.Compare) or not all(type(op) in _COMPARACIONES for op in condicion.ops):
                raise ValueError("La condición de si(...) debe ser una comparación, por ejemplo x < 0.")
            condicion = ast.Compare(
                _canonico(condicion.left, siguiente), [type(op)() for op in condicion.ops],
                [_canonico(termino, siguiente) for termino in condicion.comparators],
            )
            return ast.Call(ast.Name("si", ast.Load()), [condicion, _canonico(argumentos[1], siguiente),
                                                          _canonico(argumentos[2], siguiente)], [])
        if nombre == "log" and len(argumentos) == 1:
            nombre = "ln"
        if nombre == "raiz" and len(argumentos) == 1:
            nombre = "sqrt"
        if nombre in FUNCIONES:
            esperados = FUNCIONES[nombre][1]
            if len(argumentos) != esperados:
                ejemplo = {"raiz": "raiz(x, 3)", "log": "log(x, 2)"}.get(nombre, f"{nombre}(x)")
                raise ValueError(f"{nombre} recibe {esperados} argumento(s), por ejemplo {ejemplo}.")
            return ast.Call(ast.Name(nombre, ast.Load()), [_canonico(a, siguiente) for a in argumentos], [])
    if isinstance(nodo, ast.Compare):
        raise ValueError(
            "Las comparaciones solo van dentro de si(condición, valor, otro valor). "
            "Los métodos buscan raíces; no resuelven inecuaciones."
        )
    raise ValueError(
        "Usa solo números, x, pi, e, + − * / ^, paréntesis y funciones permitidas: "
        + ", ".join(nombres_disponibles()) + "."
    )


# ---------------------------------------------------------------------------
# 3. Construcción simplificada de nodos (para derivar y mostrar)
# ---------------------------------------------------------------------------

def C(valor):
    if isinstance(valor, float) and valor.is_integer() and abs(valor) < 1e15:
        valor = int(valor)
    return ast.Constant(valor)


def _valor(nodo):
    return nodo.value if isinstance(nodo, ast.Constant) else None


def _es(nodo, valor):
    return isinstance(nodo, ast.Constant) and nodo.value == valor


def _igual(a, b):
    return ast.dump(a) == ast.dump(b)


def _es_negacion(nodo):
    return isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, ast.USub)


def llamar(nombre, *argumentos):
    return ast.Call(ast.Name(nombre, ast.Load()), list(argumentos), [])


def neg(a):
    if _valor(a) is not None:
        return C(-a.value)
    if _es_negacion(a):
        return a.operand
    return ast.UnaryOp(ast.USub(), a)


def suma(a, b):
    va, vb = _valor(a), _valor(b)
    if va is not None and vb is not None:
        return C(va + vb)
    if va == 0:
        return b
    if vb == 0:
        return a
    if _es_negacion(b):
        return resta(a, b.operand)
    if vb is not None and vb < 0:
        return resta(a, C(-vb))
    if _es_negacion(a):
        return resta(b, a.operand)
    return ast.BinOp(a, ast.Add(), b)


def resta(a, b):
    va, vb = _valor(a), _valor(b)
    if va is not None and vb is not None:
        return C(va - vb)
    if vb == 0:
        return a
    if va == 0:
        return neg(b)
    if _igual(a, b):
        return C(0)
    if _es_negacion(b):
        return suma(a, b.operand)
    if vb is not None and vb < 0:
        return suma(a, C(-vb))
    return ast.BinOp(a, ast.Sub(), b)


def producto(a, b):
    va, vb = _valor(a), _valor(b)
    if va == 0 or vb == 0:
        return C(0)
    if va is not None and vb is not None:
        return C(va * vb)
    if va == 1:
        return b
    if vb == 1:
        return a
    if va == -1:
        return neg(b)
    if vb == -1:
        return neg(a)
    if _es_negacion(a):
        return neg(producto(a.operand, b))
    if _es_negacion(b):
        return neg(producto(a, b.operand))
    if vb is not None:  # constante al frente: 3x en lugar de x·3
        return producto(b, a)
    if va is not None and va < 0:
        return neg(producto(C(-va), b))
    if (va is not None and isinstance(b, ast.BinOp) and isinstance(b.op, ast.Mult)
            and _valor(b.left) is not None):
        return producto(C(va * b.left.value), b.right)
    if isinstance(b, ast.BinOp) and isinstance(b.op, ast.Div) and _es(b.left, 1):
        return cociente(a, b.right)
    if isinstance(a, ast.BinOp) and isinstance(a.op, ast.Div) and _es(a.left, 1):
        return cociente(b, a.right)
    if _igual(a, b):
        return potencia(a, C(2))
    return ast.BinOp(a, ast.Mult(), b)


def cociente(a, b):
    va, vb = _valor(a), _valor(b)
    if va == 0:
        return C(0)
    if vb == 1:
        return a
    if va is not None and vb not in (None, 0):
        resultado = va / vb
        if float(resultado).is_integer():
            return C(resultado)
    if _es_negacion(a):
        return neg(cociente(a.operand, b))
    if _es_negacion(b):
        return neg(cociente(a, b.operand))
    if _igual(a, b):
        return C(1)
    return ast.BinOp(a, ast.Div(), b)


def potencia(a, b):
    va, vb = _valor(a), _valor(b)
    if vb == 0:
        return C(1)
    if vb == 1:
        return a
    if va is not None and vb is not None and isinstance(vb, int) and isinstance(va, int) and 0 <= vb <= 20:
        return C(va ** vb)
    if isinstance(a, ast.BinOp) and isinstance(a.op, ast.Pow) and vb is not None and _valor(a.right) is not None:
        return potencia(a.left, C(a.right.value * vb))
    return ast.BinOp(a, ast.Pow(), b)


def depende_de_x(nodo):
    return any(isinstance(n, ast.Name) and n.id == VARIABLE for n in ast.walk(nodo))


# ---------------------------------------------------------------------------
# 4. Derivación simbólica
# ---------------------------------------------------------------------------

def _derivada_externa(nombre, u, argumentos):
    """Derivada de la función externa evaluada en u (sin multiplicar por u')."""
    if nombre == "sin":
        return llamar("cos", u)
    if nombre == "cos":
        return neg(llamar("sin", u))
    if nombre == "tan":
        return potencia(llamar("sec", u), C(2))
    if nombre == "sec":
        return producto(llamar("sec", u), llamar("tan", u))
    if nombre == "csc":
        return neg(producto(llamar("csc", u), llamar("cot", u)))
    if nombre == "cot":
        return neg(potencia(llamar("csc", u), C(2)))
    if nombre == "asin":
        return cociente(C(1), llamar("sqrt", resta(C(1), potencia(u, C(2)))))
    if nombre == "acos":
        return neg(cociente(C(1), llamar("sqrt", resta(C(1), potencia(u, C(2))))))
    if nombre == "atan":
        return cociente(C(1), suma(C(1), potencia(u, C(2))))
    if nombre == "sinh":
        return llamar("cosh", u)
    if nombre == "cosh":
        return llamar("sinh", u)
    if nombre == "tanh":
        return cociente(C(1), potencia(llamar("cosh", u), C(2)))
    if nombre == "sqrt":
        return cociente(C(1), producto(C(2), llamar("sqrt", u)))
    if nombre == "cbrt":
        return cociente(C(1), producto(C(3), potencia(llamar("cbrt", u), C(2))))
    if nombre == "raiz":
        indice = argumentos[1]
        if depende_de_x(indice):
            raise ValueError("No se deriva raiz(u, n) cuando el índice depende de x; usa u^(1/n).")
        return cociente(llamar("raiz", u, indice), producto(indice, u))
    if nombre == "exp":
        return llamar("exp", u)
    if nombre == "ln":
        return cociente(C(1), u)
    if nombre == "log":
        base = argumentos[1]
        if depende_de_x(base):
            raise ValueError("No se deriva log(u, b) cuando la base depende de x; usa ln(u)/ln(b).")
        return cociente(C(1), producto(u, llamar("ln", base)))
    if nombre == "log10":
        return cociente(C(1), producto(u, llamar("ln", C(10))))
    if nombre == "log2":
        return cociente(C(1), producto(u, llamar("ln", C(2))))
    if nombre == "abs":
        return cociente(u, llamar("abs", u))
    raise ValueError(f"No hay regla de derivación para {nombre}.")


def derivar(nodo):
    """Aplica las reglas de derivación respecto de x y simplifica."""
    if not depende_de_x(nodo):
        return C(0)
    if isinstance(nodo, ast.Name):
        return C(1)
    if isinstance(nodo, ast.UnaryOp):
        return neg(derivar(nodo.operand))
    if isinstance(nodo, ast.BinOp):
        u, v = nodo.left, nodo.right
        if isinstance(nodo.op, ast.Add):
            return suma(derivar(u), derivar(v))
        if isinstance(nodo.op, ast.Sub):
            return resta(derivar(u), derivar(v))
        if isinstance(nodo.op, ast.Mult):
            if not depende_de_x(u):
                return producto(u, derivar(v))
            if not depende_de_x(v):
                return producto(v, derivar(u))
            return suma(producto(derivar(u), v), producto(u, derivar(v)))
        if isinstance(nodo.op, ast.Div):
            if not depende_de_x(v):
                return cociente(derivar(u), v)
            return cociente(resta(producto(derivar(u), v), producto(u, derivar(v))), potencia(v, C(2)))
        if isinstance(nodo.op, ast.Pow):
            if not depende_de_x(v):
                exponente = resta(v, C(1))
                return producto(producto(v, potencia(u, exponente)), derivar(u))
            if not depende_de_x(u):
                factor = nodo if (isinstance(u, ast.Name) and u.id == "e") else producto(nodo, llamar("ln", u))
                return producto(factor, derivar(v))
            return producto(nodo, suma(producto(derivar(v), llamar("ln", u)),
                                       cociente(producto(v, derivar(u)), u)))
    if isinstance(nodo, ast.Call):
        nombre = nodo.func.id
        if nombre == "si":
            condicion, verdadero, falso = nodo.args
            return llamar("si", condicion, derivar(verdadero), derivar(falso))
        u = nodo.args[0]
        externa = _derivada_externa(nombre, u, nodo.args)
        interna = derivar(u)
        if isinstance(externa, ast.BinOp) and isinstance(externa.op, ast.Div) and _es(externa.left, 1):
            return cociente(interna, externa.right)
        return producto(externa, interna) if _valor(interna) is None else producto(interna, externa)
    raise ValueError("No se pudo derivar la expresión.")


def derivada_numerica(funcion, x):
    """Diferencia centrada f'(x) ≈ (f(x+h) − f(x−h)) / 2h con h ∝ ε^(1/3)."""
    h = 6.0554544523933395e-06 * max(1.0, abs(x))
    return (funcion(x + h) - funcion(x - h)) / (2 * h)


# ---------------------------------------------------------------------------
# 5. Traducción del árbol a funciones de Python (sin eval)
# ---------------------------------------------------------------------------

def _compilar(nodo):
    if isinstance(nodo, ast.Constant):
        valor = float(nodo.value)
        return lambda x: valor
    if isinstance(nodo, ast.Name):
        if nodo.id == VARIABLE:
            return lambda x: x
        valor = CONSTANTES[nodo.id]
        return lambda x: valor
    if isinstance(nodo, ast.UnaryOp):
        interno = _compilar(nodo.operand)
        return lambda x: -interno(x)
    if isinstance(nodo, ast.BinOp):
        izquierda, derecha = _compilar(nodo.left), _compilar(nodo.right)
        if isinstance(nodo.op, ast.Add):
            return lambda x: izquierda(x) + derecha(x)
        if isinstance(nodo.op, ast.Sub):
            return lambda x: izquierda(x) - derecha(x)
        if isinstance(nodo.op, ast.Mult):
            return lambda x: izquierda(x) * derecha(x)
        if isinstance(nodo.op, ast.Div):
            return lambda x: izquierda(x) / derecha(x)
        return lambda x: _potencia(izquierda(x), derecha(x))
    if isinstance(nodo, ast.Call) and nodo.func.id == "si":
        condicion, verdadero, falso = nodo.args
        terminos = [_compilar(condicion.left)] + [_compilar(t) for t in condicion.comparators]
        operaciones = [_COMPARACIONES[type(op)][2] for op in condicion.ops]
        rama_si, rama_no = _compilar(verdadero), _compilar(falso)

        def por_tramos(x):
            izquierda = terminos[0](x)
            for operar, termino in zip(operaciones, terminos[1:]):
                derecha = termino(x)
                if not operar(izquierda, derecha):
                    return rama_no(x)  # solo se evalúa la rama elegida
                izquierda = derecha
            return rama_si(x)
        return por_tramos
    funcion = FUNCIONES[nodo.func.id][0]
    argumentos = [_compilar(a) for a in nodo.args]
    if len(argumentos) == 1:
        unico = argumentos[0]
        return lambda x: funcion(unico(x))
    primero, segundo = argumentos
    return lambda x: funcion(primero(x), segundo(x))


# ---------------------------------------------------------------------------
# 6. Escritura del árbol como texto
# ---------------------------------------------------------------------------

_SUPERINDICES = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def formatear_numero(valor, bonito=False):
    """Entero sin decimales; real con la precisión mínima que lo reproduce."""
    if isinstance(valor, float) and valor.is_integer() and abs(valor) < 1e15:
        valor = int(valor)
    texto = str(valor) if isinstance(valor, int) else repr(float(valor))
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto.replace("-", "−") if bonito else texto


def _precedencia(nodo):
    if isinstance(nodo, ast.BinOp):
        return {ast.Add: 1, ast.Sub: 1, ast.Mult: 2, ast.Div: 2, ast.Pow: 4}[type(nodo.op)]
    if isinstance(nodo, ast.UnaryOp) or (isinstance(nodo, ast.Constant) and nodo.value < 0):
        return 3
    return 5


def a_texto(nodo, bonito=False):
    """Texto editable (bonito=False) o notación legible (bonito=True)."""
    def entre(nodo_hijo, condicion):
        texto = escribir(nodo_hijo)
        return f"({texto})" if condicion else texto

    def escribir(n):
        if isinstance(n, ast.Constant):
            return formatear_numero(n.value, bonito)
        if isinstance(n, ast.Name):
            return "π" if (bonito and n.id == "pi") else n.id
        if isinstance(n, ast.UnaryOp):
            return ("−" if bonito else "-") + entre(n.operand, _precedencia(n.operand) in (1, 3))
        if isinstance(n, ast.Compare):
            partes = [escribir(n.left)]
            for op, termino in zip(n.ops, n.comparators):
                simbolo = _COMPARACIONES[type(op)][1 if bonito else 0]
                partes.append(f" {simbolo} {escribir(termino)}")
            return "".join(partes)
        if isinstance(n, ast.Call):
            nombre = n.func.id
            argumentos = ", ".join(escribir(a) for a in n.args)
            if bonito and nombre in ("sqrt", "cbrt"):
                signo = "√" if nombre == "sqrt" else "∛"
                unico = n.args[0]
                return signo + (escribir(unico) if _precedencia(unico) == 5 and not isinstance(unico, ast.Call)
                                else f"({argumentos})")
            if bonito and nombre == "abs":
                return f"|{argumentos}|"
            return f"{nombre}({argumentos})"
        p_izq, p_der = _precedencia(n.left), _precedencia(n.right)
        if isinstance(n.op, ast.Add):
            return f"{escribir(n.left)} + {entre(n.right, p_der == 3)}"
        if isinstance(n.op, ast.Sub):
            return f"{escribir(n.left)} {'−' if bonito else '-'} {entre(n.right, p_der in (1, 3))}"
        if isinstance(n.op, ast.Mult):
            izquierda = entre(n.left, p_izq == 1)
            derecha = entre(n.right, p_der in (1, 3))
            if bonito:
                # 2π·x se escribe 2πx: un coeficiente constante sin x se antepone.
                coeficiente = (isinstance(n.left, ast.Constant) and n.left.value >= 0) or (
                    not depende_de_x(n.left) and "·" not in izquierda and p_izq >= 2
                    and isinstance(n.right, ast.Name)
                )
                juntar = (coeficiente
                          and not isinstance(n.right, ast.Constant)
                          and not (isinstance(n.right, ast.BinOp) and isinstance(n.right.op, (ast.Mult, ast.Div))
                                   and isinstance(n.right.left, ast.Constant)))
                return f"{izquierda}{derecha}" if juntar else f"{izquierda}·{derecha}"
            return f"{izquierda}*{derecha}"
        if isinstance(n.op, ast.Div):
            return f"{entre(n.left, p_izq == 1)}/{entre(n.right, p_der in (1, 2, 3))}"
        base = entre(n.left, p_izq <= 4)
        exponente = n.right
        if (bonito and isinstance(exponente, ast.Constant) and isinstance(exponente.value, int)
                and -99 <= exponente.value <= 99):
            return base + str(exponente.value).translate(_SUPERINDICES)
        return f"{base}^{entre(exponente, _precedencia(exponente) < 4)}"

    return escribir(nodo)


# ---------------------------------------------------------------------------
# 7. Objeto público
# ---------------------------------------------------------------------------

class Expresion:
    """Función real de x lista para evaluar, derivar y mostrar."""

    def __init__(self, arbol, es_igualdad=False, limitar=True):
        # Las derivadas pueden crecer más que la entrada; solo se limita lo escrito.
        if limitar and sum(1 for _ in ast.walk(arbol)) > NODOS_MAXIMOS:
            raise ValueError("La expresión es demasiado compleja. Simplifícala.")
        self.arbol = arbol
        self.es_igualdad = es_igualdad
        self._evaluar = _compilar(arbol)
        self._derivada = None

    @property
    def texto(self):
        return a_texto(self.arbol)

    @property
    def bonito(self):
        return a_texto(self.arbol, bonito=True)

    @property
    def depende_de_x(self):
        return depende_de_x(self.arbol)

    def __call__(self, x):
        x = asegurar_finito(x, "x")
        try:
            valor = self._evaluar(x)
        except (ValueError, OverflowError, ZeroDivisionError, TypeError) as exc:
            raise ValueError(
                f"No se puede evaluar f(x) en x = {formatear_numero(x)}: "
                "hay una operación fuera del dominio real, división entre cero "
                "o un valor demasiado grande. Revisa la función y el intervalo."
            ) from exc
        if isinstance(valor, complex) or not math.isfinite(valor):
            raise ValueError(
                f"No se puede evaluar f(x) en x = {formatear_numero(x)}: "
                "el resultado no es un número real finito."
            )
        return float(valor)

    def intentar(self, x):
        """Evalúa sin lanzar errores: devuelve None fuera del dominio."""
        try:
            return self(x)
        except ValueError:
            return None

    def derivada(self):
        if self._derivada is None:
            self._derivada = Expresion(derivar(self.arbol), limitar=False)
        return self._derivada


def analizar(texto):
    """Convierte el texto en una Expresion. Una igualdad A = B pasa a A − B."""
    izquierda, derecha = normalizar(texto)
    arbol = _canonico(_analizar_lado(izquierda))
    if derecha is not None:
        arbol = ast.BinOp(arbol, ast.Sub(), _canonico(_analizar_lado(derecha)))
    return Expresion(arbol, es_igualdad=derecha is not None)


def evaluar_valor(texto, contexto="El valor"):
    """Lee un número que puede escribirse como expresión: pi/2, sqrt(2), 2,5."""
    if texto is None or not str(texto).strip():
        raise ValueError(f"{contexto} está vacío. Escribe un número.")
    texto = str(texto).strip()
    if re.fullmatch(r"[+-]?\d+,\d+", texto):
        texto = texto.replace(",", ".")
    try:
        expresion = analizar(texto)
    except ValueError as exc:
        raise ValueError(f"{contexto}: {exc}") from exc
    if expresion.es_igualdad or expresion.depende_de_x:
        raise ValueError(f"{contexto} debe ser un número o una operación sin x, por ejemplo pi/2.")
    return expresion(0.0)
