"""Textos del procedimiento de cada método, generados por iteración y bajo demanda.

La interfaz pagina la tabla y solo pide el detalle de la fila seleccionada,
así no se construye ni se dibuja todo el procedimiento de una vez.
Cada línea es (texto, estilo) con estilo en: titulo, formula, normal, ok,
error, aviso, tenue.
"""

from nucleo.expresiones import analizar

_SUBINDICES = str.maketrans("0123456789+-", "₀₁₂₃₄₅₆₇₈₉₊₋")


def sub(numero):
    return str(numero).translate(_SUBINDICES)


def n(valor):
    if valor is None:
        return "—"
    return f"{valor:.10g}".replace("-", "−")


def p(valor):
    """Número entre paréntesis si es negativo, para sustituir en fórmulas."""
    texto = n(valor)
    return f"({texto})" if texto.startswith("−") else texto


def nt(valor):
    """Formato compacto para celdas de tabla: 8 cifras significativas."""
    if valor is None:
        return "—"
    return f"{valor:.8g}".replace("-", "−")


def porcentaje(valor):
    return "—" if valor is None else f"{valor:.4g} %"


FORMULAS = {
    "Bisección": "c = (a + b) / 2",
    "Regula Falsi": "c = b − f(b)·(b − a) / (f(b) − f(a))",
    "Newton-Raphson": "xₙ₊₁ = xₙ − f(xₙ) / f′(xₙ)",
    "Secante": "xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) / (f(xₙ) − f(xₙ₋₁))",
}

COLUMNAS = {
    "Bisección": (("n", "n", 44), ("a", "a", 110), ("b", "b", 110), ("c", "c", 120),
                  ("fc", "f(c)", 120), ("cota", "(b−a)/2", 100), ("ea", "εa", 80)),
    "Regula Falsi": (("n", "n", 44), ("a", "a", 110), ("b", "b", 110), ("c", "c", 120),
                     ("fc", "f(c)", 120), ("paso", "|Δc|", 100), ("ea", "εa", 80)),
    "Newton-Raphson": (("n", "n", 44), ("xn", "xₙ", 120), ("fx", "f(xₙ)", 115), ("dfx", "f′(xₙ)", 110),
                       ("sig", "xₙ₊₁", 120), ("paso", "|Δx|", 100), ("ea", "εa", 80)),
    "Secante": (("n", "n", 44), ("xa", "xₙ₋₁", 110), ("xn", "xₙ", 110), ("fx", "f(xₙ)", 110),
                ("sig", "xₙ₊₁", 120), ("paso", "|Δx|", 100), ("ea", "εa", 80)),
}


def fila(metodo, paso):
    """Valores de una fila de la tabla de iteraciones."""
    if metodo == "Bisección":
        return (paso.numero, nt(paso.a), nt(paso.b), nt(paso.c), nt(paso.fc), nt(paso.error),
                porcentaje(paso.error_relativo))
    if metodo == "Regula Falsi":
        return (paso.numero, nt(paso.a), nt(paso.b), nt(paso.c), nt(paso.fc), nt(paso.error),
                porcentaje(paso.error_relativo))
    if metodo == "Newton-Raphson":
        return (paso.numero, nt(paso.actual), nt(paso.valor_actual), nt(paso.pendiente),
                nt(paso.siguiente), nt(paso.error), porcentaje(paso.error_relativo))
    return (paso.numero, nt(paso.anterior), nt(paso.actual), nt(paso.valor_actual),
            nt(paso.siguiente), nt(paso.error), porcentaje(paso.error_relativo))


def _bonita(texto):
    try:
        return analizar(texto).bonito
    except ValueError:
        return texto


def resumen(metodo, resultado):
    """Datos, condiciones, fórmula y criterio de parada del método."""
    lineas = [("Datos del ejercicio", "titulo"), (f"f(x) = {_bonita(resultado.expresion)}", "formula")]
    if metodo in ("Bisección", "Regula Falsi"):
        a, b = resultado.intervalo_inicial
        lineas.append((f"Intervalo inicial [a, b] = [{n(a)}, {n(b)}]", "formula"))
    else:
        nombres = ("x₀", "x₁")
        for nombre, valor in zip(nombres, resultado.iniciales):
            lineas.append((f"{nombre} = {n(valor)}", "formula"))
        if metodo == "Newton-Raphson":
            origen = "calculada con las reglas de derivación" if resultado.derivada_automatica else "escrita"
            lineas.append((f"f′(x) = {_bonita(resultado.derivada)}   ({origen})", "formula"))
    lineas.append((f"Tolerancia: {n(resultado.tolerancia)}", "formula"))

    lineas += [("", "normal"), ("Fórmula", "titulo"), (FORMULAS[metodo], "formula")]
    condiciones = {
        "Bisección": ["f continua en [a, b] y f(a)·f(b) < 0 (teorema de Bolzano).",
                      "Cada paso divide el intervalo a la mitad y conserva la mitad con cambio de signo.",
                      "Parada: la cota del error (b − a)/2 ≤ tolerancia, o f(c) = 0."],
        "Regula Falsi": ["f continua en [a, b] y f(a)·f(b) < 0 (teorema de Bolzano).",
                         "c es el corte con el eje x de la recta que une (a, f(a)) y (b, f(b)).",
                         "Parada: |c_nuevo − c_anterior| ≤ tolerancia y |f(c)| ≤ tolerancia, o f(c) = 0."],
        "Newton-Raphson": ["Se traza la tangente en (xₙ, f(xₙ)); su corte con el eje x es xₙ₊₁.",
                           "Requiere f′(xₙ) ≠ 0. No garantiza convergencia: depende de x₀.",
                           "Parada: |xₙ₊₁ − xₙ| ≤ tolerancia y |f(xₙ₊₁)| ≤ tolerancia, o f = 0."],
        "Secante": ["Sustituye la derivada por la pendiente de la recta entre los dos últimos puntos.",
                    "Requiere f(xₙ) ≠ f(xₙ₋₁). No exige cambio de signo ni garantiza convergencia.",
                    "Parada: |xₙ₊₁ − xₙ| ≤ tolerancia y |f(xₙ₊₁)| ≤ tolerancia, o f = 0."],
    }[metodo]
    lineas += [(texto, "normal") for texto in condiciones]
    if metodo == "Bisección":
        lineas.append((f"Iteraciones necesarias: n ≥ log₂((b − a)/tol) → n = {resultado.iteraciones_teoricas}",
                       "formula"))

    lineas += [("", "normal"), ("Resultado", "titulo")]
    estado = "ok" if resultado.convergio else "error"
    lineas.append(("Convergencia alcanzada." if resultado.convergio
                   else "Sin convergencia: el último valor no se acepta como raíz.", estado))
    lineas.append((f"Motivo de parada: {resultado.motivo}", "normal"))
    advertencia = getattr(resultado, "advertencia", "")
    if advertencia:
        lineas.append((advertencia, "aviso"))
    estancado = getattr(resultado, "extremo_estancado", "")
    if estancado:
        lineas.append((f"El extremo {estancado} no cambió en las últimas 5 iteraciones: Regula Falsi "
                       "avanza solo por un lado y el error real puede ser mayor que el estimado.", "aviso"))
    lineas += [("", "normal"), ("Selecciona una fila de la tabla para ver su desarrollo.", "tenue")]
    return lineas


def _parada(resultado, paso, total):
    if paso.numero == total:
        return [(f"Parada: {resultado.motivo}", "ok" if resultado.convergio else "error")]
    return [("No se cumple el criterio de parada: se continúa.", "tenue")]


def detalle(metodo, resultado, indice):
    """Desarrollo de la iteración número indice (base 0) con valores sustituidos."""
    paso = resultado.iteraciones[indice]
    total = len(resultado.iteraciones)
    k = paso.numero
    lineas = [(f"Iteración {k}", "titulo")]
    if metodo in ("Bisección", "Regula Falsi"):
        lineas += [
            (f"Intervalo actual: [a, b] = [{n(paso.a)}, {n(paso.b)}]", "formula"),
            (f"f(a) = {n(paso.fa)}     f(b) = {n(paso.fb)}", "formula"),
        ]
        if metodo == "Bisección":
            lineas += [
                ("1. Punto medio", "normal"),
                (f"   c = (a + b) / 2 = ({n(paso.a)} + {p(paso.b)}) / 2 = {n(paso.c)}", "formula"),
            ]
        else:
            lineas += [
                ("1. Corte de la recta secante con el eje x", "normal"),
                ("   c = b − f(b)·(b − a) / (f(b) − f(a))", "formula"),
                (f"     = {n(paso.b)} − {p(paso.fb)}·({n(paso.b)} − {p(paso.a)}) / "
                 f"({n(paso.fb)} − {p(paso.fa)})", "formula"),
                (f"     = {n(paso.c)}", "formula"),
            ]
        lineas += [("2. Evaluamos la función", "normal"), (f"   f(c) = {n(paso.fc)}", "formula")]
        if metodo == "Bisección":
            lineas += [("3. Cota del error", "normal"),
                       (f"   (b − a)/2 = {n(paso.error)}", "formula")]
        else:
            lineas += [("3. Cambio respecto de la aproximación anterior", "normal"),
                       (f"   |c_k − c_k−1| = {n(paso.error)}", "formula")]
        if paso.error_relativo is not None:
            lineas.append((f"   εa = |c_k − c_k−1| / |c_k| · 100 = {porcentaje(paso.error_relativo)}", "formula"))
        if paso.numero != total:
            if (paso.fa < 0) != (paso.fc < 0):
                lineas += [("4. Elegimos el subintervalo con cambio de signo", "normal"),
                           (f"   f(a)·f(c) < 0  →  la raíz está en [a, c]  →  b = {n(paso.c)}", "formula")]
            else:
                lineas += [("4. Elegimos el subintervalo con cambio de signo", "normal"),
                           (f"   f(c)·f(b) < 0  →  la raíz está en [c, b]  →  a = {n(paso.c)}", "formula")]
        return lineas + [("", "normal")] + _parada(resultado, paso, total)

    if metodo == "Newton-Raphson":
        xn, xs = f"x{sub(k - 1)}", f"x{sub(k)}"
        lineas += [
            (f"Partimos de {xn} = {n(paso.actual)}", "formula"),
            ("1. Evaluamos la función y su derivada", "normal"),
            (f"   f({xn}) = {n(paso.valor_actual)}", "formula"),
            (f"   f′({xn}) = {n(paso.pendiente)}", "formula"),
            ("2. Sustituimos en la fórmula de Newton", "normal"),
            (f"   {xs} = {xn} − f({xn}) / f′({xn})", "formula"),
            (f"      = {n(paso.actual)} − {p(paso.valor_actual)} / {p(paso.pendiente)}", "formula"),
            (f"      = {n(paso.siguiente)}", "formula"),
        ]
    else:
        xa, xn, xs = f"x{sub(k - 1)}", f"x{sub(k)}", f"x{sub(k + 1)}"
        lineas += [
            (f"Partimos de {xa} = {n(paso.anterior)} y {xn} = {n(paso.actual)}", "formula"),
            ("1. Evaluamos la función", "normal"),
            (f"   f({xn}) = {n(paso.valor_actual)}", "formula"),
            (f"   Pendiente de la secante = (f({xn}) − f({xa})) / ({xn} − {xa}) = {n(paso.pendiente)}", "formula"),
            ("2. Sustituimos en la fórmula de la secante", "normal"),
            (f"   {xs} = {xn} − f({xn})·({xn} − {xa}) / (f({xn}) − f({xa}))", "formula"),
            (f"      = {n(paso.actual)} − {p(paso.valor_actual)} / {p(paso.pendiente)}", "formula"),
            (f"      = {n(paso.siguiente)}", "formula"),
        ]
    lineas += [
        ("3. Comprobamos", "normal"),
        (f"   f({xs}) = {n(paso.valor_siguiente)}", "formula"),
        (f"   |{xs} − {xn}| = {n(paso.error)}", "formula"),
    ]
    if paso.error_relativo is not None:
        lineas.append((f"   εa = |{xs} − {xn}| / |{xs}| · 100 = {porcentaje(paso.error_relativo)}", "formula"))
    return lineas + [("", "normal")] + _parada(resultado, paso, total)


# ---------------------------------------------------------------------------
# Comparación entre métodos
# ---------------------------------------------------------------------------

ORDEN_TEORICO = {"Bisección": "1 (r = ½)", "Regula Falsi": "1", "Newton-Raphson": "2", "Secante": "1.618"}

EXPLICACION_PAR = {
    ("Bisección", "Regula Falsi"): (
        "Bisección divide el intervalo a la mitad en cada paso: converge linealmente con razón ½ y "
        "su cota (b − a)/2 es una garantía del error. Regula Falsi usa la recta secante y suele "
        "llegar antes, pero si un extremo queda fijo avanza solo por un lado y su paso no acota el error."
    ),
    ("Newton-Raphson", "Secante"): (
        "Newton converge cuadráticamente (p = 2) pero evalúa f y f′ en cada paso. Secante evita la "
        "derivada y converge con p ≈ 1.618 (razón áurea): suele necesitar más iteraciones pero menos "
        "evaluaciones por iteración."
    ),
}


def aproximaciones(resultado):
    """Sucesión de aproximaciones: c₁, c₂, … en métodos cerrados; x₀, x₁, … en abiertos."""
    if hasattr(resultado, "intervalo_inicial"):
        return [paso.c for paso in resultado.iteraciones]
    return list(resultado.iniciales) + [paso.siguiente for paso in resultado.iteraciones]


def evaluaciones(nombre, resultado):
    """Evaluaciones de f (y f′) realizadas: el costo real de cada método."""
    pasos = len(resultado.iteraciones)
    if nombre == "Newton-Raphson":
        return 1 + 2 * pasos          # f(x₀) + [f′(xₙ), f(xₙ₊₁)] por paso
    return 2 + pasos                  # f en los dos valores iniciales + una por paso


def estimar_orden(resultado):
    """Orden de convergencia observado p ≈ ln(eₙ₊₁/eₙ) / ln(eₙ/eₙ₋₁), con eₖ = |xₖ − x*|.

    Usa la raíz final como x* y los últimos tres errores decrecientes que aún
    no están dominados por el redondeo. Es una estimación, no una prueba.
    """
    import math

    if not resultado.convergio:
        return None
    raiz = resultado.raiz
    piso = 1e-12 * max(1.0, abs(raiz))
    errores = [abs(x - raiz) for x in aproximaciones(resultado)]
    validos = [e for e in errores if e > piso]
    for i in range(len(validos) - 3, -1, -1):
        e0, e1, e2 = validos[i:i + 3]
        if e0 > e1 > e2 > 0:
            denominador = math.log(e1 / e0)
            if denominador != 0:
                return math.log(e2 / e1) / denominador
    return None


def comparacion(resultados):
    """Tabla comparativa y verificación cruzada de dos métodos ({nombre: resultado})."""
    (nombre_a, a), (nombre_b, b) = list(resultados.items())[:2]

    def fila_comparada(titulo, valor_a, valor_b):
        return (f"{titulo:<20}{valor_a:>17}{valor_b:>17}", "formula")

    def orden(resultado):
        p_obs = estimar_orden(resultado)
        return "—" if p_obs is None else f"{p_obs:.3f}"

    corto = {"Newton-Raphson": "Newton", "Regula Falsi": "Regula Falsi"}
    lineas = [
        (f"Comparación {nombre_a} vs {nombre_b}", "titulo"),
        (f"{'':<20}{corto.get(nombre_a, nombre_a):>17}{corto.get(nombre_b, nombre_b):>17}", "tenue"),
        fila_comparada("Raíz", n(a.raiz), n(b.raiz)),
        fila_comparada("f(raíz)", f"{a.valor_funcion:.3g}", f"{b.valor_funcion:.3g}"),
        fila_comparada("Convergió", "sí" if a.convergio else "no", "sí" if b.convergio else "no"),
        fila_comparada("Iteraciones", str(len(a.iteraciones)), str(len(b.iteraciones))),
        fila_comparada("Evaluaciones de f", str(evaluaciones(nombre_a, a)), str(evaluaciones(nombre_b, b))),
        fila_comparada("Orden observado p", orden(a), orden(b)),
        fila_comparada("Orden teórico", ORDEN_TEORICO[nombre_a], ORDEN_TEORICO[nombre_b]),
        ("", "normal"),
        ("Verificación cruzada", "titulo"),
    ]
    tolerancia = max(a.tolerancia, b.tolerancia)
    if a.convergio and b.convergio:
        diferencia = abs(a.raiz - b.raiz)
        lineas.append((f"|x_{corto.get(nombre_a, nombre_a)} − x_{corto.get(nombre_b, nombre_b)}| = "
                       f"{n(diferencia)}", "formula"))
        if diferencia <= 2 * tolerancia:
            lineas.append(("✓ Coinciden dentro de la tolerancia: dos métodos distintos confirman la raíz.", "ok"))
        else:
            lineas.append(("⚠ Llegan a raíces distintas: con estos valores iniciales cada método "
                           "encontró una raíz diferente de f.", "aviso"))
    else:
        fallido = " y ".join(nombre for nombre, r in ((nombre_a, a), (nombre_b, b)) if not r.convergio)
        lineas.append((f"✗ No se puede confirmar: {fallido} no convergió. Revisa sus motivos de parada.", "error"))
    explicacion = EXPLICACION_PAR.get((nombre_a, nombre_b)) or EXPLICACION_PAR.get((nombre_b, nombre_a))
    lineas += [("", "normal"), ("Cómo leerlo", "titulo")]
    if explicacion:
        lineas.append((explicacion, "normal"))
    lineas.append(("El orden observado se estima con los últimos errores eₖ = |xₖ − x*|; es aproximado.", "tenue"))
    return lineas
