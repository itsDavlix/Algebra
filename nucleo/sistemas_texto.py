"""Lectura de sistemas lineales escritos como ecuaciones o como matriz aumentada.

Acepta, una ecuación por línea:
    -3x - y + 4z + 5w = -6          (variables de una letra)
    10x₁ − x₂ + 2x₃ = 6             (variables con subíndice: x1, x₁, x_1)
    2.5a + b/2 = 1                  (decimales y fracciones como coeficientes)
    (1/2)x₂ − (1/3)w = 7/5          (coeficientes entre paréntesis, como en los documentos)
o filas numéricas «a₁ a₂ … aₙ | b» (o con el término independiente al final).
"""

import re
from fractions import Fraction

_SUBINDICES = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_VARIABLE = r"[a-zA-Z](?:_?\d+)?"
_DECIMAL = r"(?:\d+(?:\.\d+)?|\.\d+)"
_FRACCION = _DECIMAL + r"(?:/" + _DECIMAL + r")?"
# Coeficiente suelto (3, 2.5, 1/3) o entre paréntesis ((1/2), (−3/4)), como se copian de Word.
_COEFICIENTE = r"\([+-]?" + _FRACCION + r"\)|" + _FRACCION
_TERMINO = re.compile(
    r"([+-])?\s*(" + _COEFICIENTE + r")?\s*\*?\s*(" + _VARIABLE + r")"
    r"(?:\s*/\s*(" + _DECIMAL + r"))?"
)
_NUMERO = re.compile(r"([+-])?(" + _COEFICIENTE + r")")


def _normalizar(texto):
    return (texto.translate(_SUBINDICES).replace("−", "-").replace("–", "-")
            .replace("·", "*").replace("×", "*").replace(",", "."))


def _numero(texto):
    """Valor exacto (Fraction) de 3, −2.5, 1/3, (1/2) o (−3/4): 0.75 es 3/4 exactamente."""
    texto = texto.replace(" ", "")
    signo = 1
    if texto[:1] in "+-":
        signo, texto = (-1 if texto[0] == "-" else 1), texto[1:]
    if texto.startswith("(") and texto.endswith(")"):
        texto = texto[1:-1]
        if texto[:1] in "+-":
            signo, texto = signo * (-1 if texto[0] == "-" else 1), texto[1:]
    if "/" in texto:
        numerador, denominador = texto.split("/")
        if Fraction(denominador) == 0:
            raise ValueError("Hay una división entre cero en un coeficiente.")
        return signo * Fraction(numerador) / Fraction(denominador)
    return signo * Fraction(texto)


def _nombre(variable):
    return variable.replace("_", "")


def _orden_natural(nombre):
    letra = re.match(r"[a-zA-Z]+", nombre).group(0)
    numero = re.search(r"\d+", nombre)
    orden_letras = {"x": 0, "y": 1, "z": 2, "w": 3}
    return (orden_letras.get(letra, 10 + ord(letra.lower())), int(numero.group(0)) if numero else -1)


def _lado(texto, numero_linea):
    """Devuelve ({variable: coeficiente}, constante) de un lado de la ecuación."""
    texto = texto.strip()
    if not texto:
        raise ValueError(f"Línea {numero_linea}: falta un lado de la ecuación.")
    coeficientes, constante = {}, Fraction(0)
    posicion = 0
    sin_espacios = texto.replace(" ", "")
    while posicion < len(sin_espacios):
        termino = _TERMINO.match(sin_espacios, posicion)
        if termino and termino.end() > posicion:
            signo, coeficiente, variable, divisor = termino.groups()
            valor = _numero(coeficiente) if coeficiente else Fraction(1)
            if divisor:
                valor /= _numero(divisor)
            if signo == "-":
                valor = -valor
            nombre = _nombre(variable)
            coeficientes[nombre] = coeficientes.get(nombre, 0) + valor
            posicion = termino.end()
            continue
        numero = _NUMERO.match(sin_espacios, posicion)
        if numero and numero.end() > posicion:
            constante += _numero(numero.group(0))
            posicion = numero.end()
            continue
        raise ValueError(f"Línea {numero_linea}: no se entiende «{sin_espacios[posicion:posicion + 8]}». "
                         "Escribe términos como 3x, -y o 2.5z.")
    return coeficientes, constante


def leer_sistema(texto, exacto=False):
    """Devuelve (variables, A, b). Lanza ValueError con la línea del problema.

    Con exacto=True, A y b son Fraction (0.75 → 3/4, 181/60 tal cual) para operar
    sin redondeo; por defecto son float, como siempre.
    """
    lineas = [linea.strip() for linea in _normalizar(texto).splitlines() if linea.strip()]
    if not lineas:
        raise ValueError("Escribe el sistema: una ecuación por línea, por ejemplo 2x + y = 3.")
    if all("=" not in linea and re.search(r"[a-zA-Z]", linea) is None for linea in lineas):
        return _convertir(*_leer_matriz_aumentada(lineas), exacto)
    filas = []
    for numero_linea, linea in enumerate(lineas, 1):
        if linea.count("=") != 1:
            raise ValueError(f"Línea {numero_linea}: cada ecuación necesita exactamente un «=».")
        izquierda, derecha = linea.split("=")
        ci, ki = _lado(izquierda, numero_linea)
        cd, kd = _lado(derecha, numero_linea)
        coeficientes = dict(ci)
        for variable, valor in cd.items():
            coeficientes[variable] = coeficientes.get(variable, 0) - valor
        filas.append((coeficientes, kd - ki))
    variables = sorted({v for coeficientes, _ in filas for v in coeficientes}, key=_orden_natural)
    if not variables:
        raise ValueError("No se encontraron incógnitas en el sistema.")
    A = [[Fraction(coeficientes.get(v, 0)) for v in variables] for coeficientes, _ in filas]
    b = [Fraction(termino) for _, termino in filas]
    return _convertir(variables, A, b, exacto)


def _convertir(variables, A, b, exacto):
    if exacto:
        return variables, A, b
    return variables, [[float(a) for a in fila] for fila in A], [float(x) for x in b]


def _leer_matriz_aumentada(lineas):
    A, b = [], []
    for numero_linea, linea in enumerate(lineas, 1):
        partes = linea.replace("|", " ").split()
        try:
            valores = [_numero(p) for p in partes]
        except ValueError as exc:
            raise ValueError(f"Fila {numero_linea}: hay un valor que no es un número.") from exc
        if len(valores) < 2:
            raise ValueError(f"Fila {numero_linea}: escribe los coeficientes y el término independiente.")
        A.append(valores[:-1])
        b.append(valores[-1])
    if len({len(fila) for fila in A}) != 1:
        raise ValueError("Todas las filas deben tener la misma cantidad de coeficientes.")
    n = len(A[0])
    variables = [f"x{i + 1}" for i in range(n)]
    return variables, A, b


def nombre_bonito(variable):
    """x1 -> x₁ para mostrar."""
    return re.sub(r"\d+", lambda m: m.group(0).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")), variable)


def ecuacion_texto(fila, termino, variables, formato=None):
    """Escribe una fila como ecuación legible: 10x₁ − x₂ + 2x₃ = 6.

    formato(valor) → texto del número (p. ej. fracciones «1/3» en modo exacto); por defecto «:g».
    """
    formato = formato or (lambda valor: f"{valor:g}")
    partes = []
    for coeficiente, variable in zip(fila, variables):
        if coeficiente == 0:
            continue
        magnitud = abs(coeficiente)
        texto_coef = "" if magnitud == 1 else formato(magnitud)
        if "/" in texto_coef:
            texto_coef = f"({texto_coef})"
        signo = "−" if coeficiente < 0 else "+"
        if not partes:
            partes.append(("−" if coeficiente < 0 else "") + texto_coef + nombre_bonito(variable))
        else:
            partes.append(f" {signo} {texto_coef}{nombre_bonito(variable)}")
    izquierda = "".join(partes) or "0"
    return f"{izquierda} = {formato(termino)}".replace("-", "−")


def leer_matriz_texto(texto, nombre="A"):
    """Matriz por filas; cada entrada puede ser 3, -2.5, 1/3, pi o sqrt(2)."""
    from nucleo.expresiones import evaluar_valor

    lineas = [linea.strip() for linea in str(texto).replace(";", "\n").splitlines() if linea.strip()]
    if not lineas:
        raise ValueError(f"Escribe la matriz {nombre}: una fila por línea, valores separados por espacios.")
    matriz = []
    for i, linea in enumerate(lineas, 1):
        partes = [p for p in re.split(r"[\s,]+|\|", linea.strip("[] ")) if p]
        fila = []
        for j, parte in enumerate(partes, 1):
            fila.append(evaluar_valor(parte, f"La entrada [{i},{j}] de {nombre}"))
        matriz.append(fila)
    if len({len(f) for f in matriz}) != 1:
        raise ValueError(f"La matriz {nombre} no es rectangular: todas las filas deben tener los mismos elementos.")
    return matriz


def leer_vector(texto, n, nombre="x⁽⁰⁾"):
    """Vector con n componentes separadas por comas o espacios; vacío = vector cero."""
    from nucleo.expresiones import evaluar_valor

    partes = [p for p in re.split(r"[\s;]+|,\s*", str(texto).strip("()[] ")) if p]
    if not partes:
        return [0.0] * n
    if len(partes) != n:
        raise ValueError(f"{nombre} debe tener {n} componentes; tiene {len(partes)}.")
    return [evaluar_valor(p, f"La componente {i} de {nombre}") for i, p in enumerate(partes, 1)]
