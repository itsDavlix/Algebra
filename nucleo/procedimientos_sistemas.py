"""Textos paso a paso de Gauss-Jordan, Jacobi y Gauss-Seidel, en el orden de la clase.

Cada función devuelve líneas (texto, estilo) como nucleo.procedimientos.
Formato de sustitución igual al de la presentación:
    x₂⁽²⁾ = (25 + x₁ + x₃ − 3x₄) / 11 = (25 + 0.600000 − 1.100000 − 3(1.875000)) / 11 = 1.715909
"""

import re
from fractions import Fraction

from nucleo.sistemas_texto import ecuacion_texto, nombre_bonito

_SUPER = str.maketrans("0123456789+-()k", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾ᵏ")
CIFRAS = 6   # la presentación usa 6 decimales; los cálculos conservan doble precisión


def sup(k):
    return f"({k})".translate(_SUPER)


def d(valor, decimales=CIFRAS):
    """Número con decimales fijos y signo menos tipográfico."""
    if valor is None:
        return "—"
    texto = f"{valor:.{decimales}f}"
    if float(texto) == 0:
        texto = f"{0:.{decimales}f}"
    return texto.replace("-", "−")


def g(valor, cifras=8):
    return f"{valor:.{cifras}g}".replace("-", "−")


def coef(valor):
    """Coeficiente sin decimales innecesarios: 3, 2.5, 1/3 si es fracción exacta."""
    if float(valor).is_integer():
        return str(int(valor))
    fraccion = Fraction(valor).limit_denominator(1000)
    if abs(float(fraccion) - valor) < 1e-12:
        return f"{fraccion.numerator}/{fraccion.denominator}"
    return g(valor, 6)


def vector(valores, decimales=CIFRAS):
    return "(" + ", ".join(d(v, decimales) for v in valores) + ")"


# ---------------------------------------------------------------- despejes
def despeje(A, b, variables, i):
    """xᵢ = (bᵢ − Σⱼ≠ᵢ aᵢⱼ xⱼ) / aᵢᵢ escrito con los signos simplificados."""
    partes = [coef(b[i]).replace("-", "−")]
    for j, a in enumerate(A[i]):
        if j == i or a == 0:
            continue
        signo = "−" if a > 0 else "+"     # se resta aᵢⱼxⱼ
        magnitud = abs(a)
        partes.append(f" {signo} {'' if magnitud == 1 else coef(magnitud)}{nombre_bonito(variables[j])}")
    return f"{nombre_bonito(variables[i])} = ({''.join(partes)}) / {coef(A[i][i])}".replace("-", "−")


def sustitucion_texto(A, b, i, sustitucion):
    """Lado derecho con los valores sustituidos, como en la diapositiva."""
    partes = [coef(b[i]).replace("-", "−")]
    for j, a, valor, _nuevo in sustitucion.terminos:
        if a == 0:
            continue
        signo = "−" if a > 0 else "+"
        magnitud = abs(a)
        if magnitud == 1:
            # Coeficiente 1: se combina el signo, como en «25 + 0.6 − 1.1».
            if valor < 0:
                signo = "+" if signo == "−" else "−"
            termino = d(abs(valor))
        else:
            termino = f"{coef(magnitud)}({d(valor)})"
        partes.append(f" {signo} {termino}")
    return f"({''.join(partes)}) / {coef(A[i][i])}".replace("-", "−")


# ---------------------------------------------------------------- iterativos
FORMULAS_ITERATIVAS = {
    "Jacobi": "xᵢ⁽ᵏ⁺¹⁾ = [bᵢ − Σⱼ≠ᵢ aᵢⱼ xⱼ⁽ᵏ⁾] / aᵢᵢ",
    "Gauss-Seidel": "xᵢ⁽ᵏ⁺¹⁾ = [bᵢ − Σⱼ<ᵢ aᵢⱼ xⱼ⁽ᵏ⁺¹⁾ − Σⱼ>ᵢ aᵢⱼ xⱼ⁽ᵏ⁾] / aᵢᵢ",
}
PRINCIPIOS = {
    "Jacobi": "Cada incógnita se calcula usando exclusivamente los valores de la iteración anterior; "
              "todas las componentes nuevas se forman antes de reemplazar el vector.",
    "Gauss-Seidel": "Las incógnitas se actualizan en orden y cada valor nuevo se usa de inmediato en "
                    "los cálculos siguientes de la misma iteración.",
}


def columnas_iterativas(variables):
    return (("k", "k", 44), *[(f"x{i}", nombre_bonito(v), 110) for i, v in enumerate(variables)],
            ("cambio", "‖Δx‖∞", 100), ("residuo", "‖b − Ax‖∞", 100))


def filas_iterativas(resultado):
    filas = [(0, *[d(v) for v in resultado.x0], "—", g(_residuo_inicial(resultado), 4))]
    for paso in resultado.iteraciones:
        filas.append((paso.k, *[d(v) for v in paso.x], g(paso.cambio, 4), g(paso.residuo, 4)))
    return filas


def _residuo_inicial(resultado):
    return max(abs(bi - sum(a * x for a, x in zip(fila, resultado.x0))) for fila, bi in zip(resultado.A, resultado.b))


def tabla_dominancia(A, variables):
    lineas = []
    for i, fila in enumerate(A):
        fuera = [abs(v) for j, v in enumerate(fila) if j != i]
        suma = sum(fuera)
        cumple = abs(fila[i]) > suma
        sumandos = " + ".join(coef(v) for v in fuera)
        lineas.append((f"Fila {i + 1}: |{coef(fila[i])}| {'>' if cumple else '≤'} {sumandos} = {coef(suma)}"
                       f"   {'✓' if cumple else '✗'}", "formula"))
    return lineas


def resumen_iterativo(resultado):
    r = resultado
    v = r.variables
    lineas = [("1. Sistema de ecuaciones", "titulo")]
    lineas += [(ecuacion_texto(fila, bi, v), "formula") for fila, bi in zip(r.A, r.b)]
    if r.reordenado:
        lineas.append((f"Ecuaciones reordenadas (orden original {', '.join(str(p + 1) for p in r.reordenado)}): "
                       "reordenar no cambia la solución.", "aviso"))
    lineas += [("", "normal"), ("2. Verificación de la dominancia diagonal", "titulo"),
               ("|aᵢᵢ| > Σⱼ≠ᵢ |aᵢⱼ| en cada fila (condición suficiente, no necesaria):", "normal")]
    lineas += tabla_dominancia(r.A, v)
    if r.estrictamente_dominante:
        lineas.append(("El sistema es estrictamente diagonalmente dominante por filas: la convergencia de "
                       "Jacobi y Gauss-Seidel está garantizada.", "ok"))
    else:
        lineas.append(("No es estrictamente dominante: la convergencia no está garantizada por esta "
                       "condición; decide el radio espectral.", "aviso"))
    if r.radio_espectral is not None:
        rho = r.radio_espectral
        nombre_t = "T_J = −D⁻¹(L + U)" if r.metodo == "Jacobi" else "T_GS = −(D + L)⁻¹U"
        lineas.append((f"Radio espectral de {nombre_t}: ρ(T) ≈ {rho:.4f} "
                       + ("< 1 → el método converge desde cualquier x⁽⁰⁾." if rho < 1 else
                          "≥ 1 → el método no converge en general."), "ok" if rho < 1 else "error"))
    lineas += [("", "normal"), ("3. Despeje de las variables", "titulo")]
    lineas += [(despeje(r.A, r.b, v, i), "formula") for i in range(len(v))]
    lineas.append((f"Vector inicial: X⁽⁰⁾ = {vector(r.x0)}", "formula"))
    lineas += [("", "normal"), (f"4. Método de {r.metodo}", "titulo"), (PRINCIPIOS[r.metodo], "normal"),
               (FORMULAS_ITERATIVAS[r.metodo], "formula"),
               ("Parada: ‖x⁽ᵏ⁺¹⁾ − x⁽ᵏ⁾‖∞ ≤ ε y ‖b − Ax⁽ᵏ⁺¹⁾‖∞ ≤ ε, con ε = " + g(r.tolerancia) + ".", "normal"),
               ("", "normal"), ("5. Resultado", "titulo")]
    lineas.append(("Convergencia alcanzada." if r.convergio else "Sin convergencia: el último vector no se "
                   "acepta como solución.", "ok" if r.convergio else "error"))
    lineas.append((f"Motivo: {r.motivo}", "normal"))
    if r.iteraciones:
        ultimo = r.iteraciones[-1]
        lineas.append((f"X⁽{ultimo.k}⁾ ≈ {vector(ultimo.x, 8)}".replace("⁽" + str(ultimo.k) + "⁾", sup(ultimo.k)),
                       "formula"))
        lineas.append((f"Residuo ‖b − AX‖∞ = {g(ultimo.residuo, 4)}", "formula"))
    lineas += [("", "normal"), ("Selecciona una fila de la tabla para ver sus sustituciones.", "tenue")]
    return lineas


def detalle_iterativo(resultado, indice):
    """Sustituciones de la iteración k = indice + 1 (indice 0 = x⁽⁰⁾)."""
    r = resultado
    if indice == 0:
        return [("Iteración 0", "titulo"), (f"X⁽⁰⁾ = {vector(r.x0)}", "formula"),
                ("Es el vector inicial; si no hay otra estimación se usa el vector cero.", "normal")]
    paso = r.iteraciones[indice - 1]
    k = paso.k
    anterior = r.x0 if indice == 1 else r.iteraciones[indice - 2].x
    lineas = [(f"Iteración {k}", "titulo")]
    if r.metodo == "Jacobi":
        lineas.append((f"Se usan únicamente los valores de X{sup(k - 1)} = {vector(anterior)} en las "
                       f"{len(r.variables)} fórmulas.", "normal"))
    else:
        lineas.append((f"Se parte de X{sup(k - 1)} = {vector(anterior)} y cada valor nuevo se usa de inmediato "
                       "en las fórmulas siguientes.", "normal"))
    for sustitucion in paso.sustituciones:
        i = sustitucion.indice
        nombre = nombre_bonito(r.variables[i])
        lineas.append((f"{nombre}{sup(k)} = {sustitucion_texto(r.A, r.b, i, sustitucion)} = {d(sustitucion.valor)}",
                       "formula"))
        if r.metodo == "Gauss-Seidel":
            nuevos = [nombre_bonito(r.variables[j]) + sup(k) for j, a, _v, nuevo in sustitucion.terminos if nuevo and a]
            if nuevos:
                lineas.append((f"   usa {', '.join(nuevos)} recién calculado(s)", "tenue"))
    lineas += [("", "normal"), (f"Por tanto, X{sup(k)} ≈ {vector(paso.x)}", "formula"),
               (f"‖X{sup(k)} − X{sup(k - 1)}‖∞ = {g(paso.cambio, 6)}     ‖b − AX{sup(k)}‖∞ = {g(paso.residuo, 6)}",
                "formula")]
    if paso.k == len(r.iteraciones):
        lineas += [("", "normal"), (f"Parada: {r.motivo}", "ok" if r.convergio else "error")]
    return lineas


def comparacion_iterativa(jacobi, seidel):
    def fila(titulo, a, b):
        return (f"{titulo:<24}{a:>16}{b:>16}", "formula")

    lineas = [("Comparación Jacobi vs Gauss-Seidel", "titulo"),
              (f"{'':<24}{'Jacobi':>16}{'Gauss-Seidel':>16}", "tenue"),
              fila("Convergió", "sí" if jacobi.convergio else "no", "sí" if seidel.convergio else "no"),
              fila("Iteraciones", str(len(jacobi.iteraciones)), str(len(seidel.iteraciones))),
              fila("ρ(T)", g(jacobi.radio_espectral, 4) if jacobi.radio_espectral is not None else "—",
                   g(seidel.radio_espectral, 4) if seidel.radio_espectral is not None else "—"),
              fila("Residuo final", g(jacobi.iteraciones[-1].residuo, 3) if jacobi.iteraciones else "—",
                   g(seidel.iteraciones[-1].residuo, 3) if seidel.iteraciones else "—"),
              ("", "normal"), ("Verificación cruzada", "titulo")]
    if jacobi.convergio and seidel.convergio:
        diferencia = max(abs(a - b) for a, b in zip(jacobi.solucion, seidel.solucion))
        lineas.append((f"max |x_J − x_GS| = {g(diferencia, 4)}", "formula"))
        lineas.append(("✓ Coinciden dentro de la tolerancia: ambos métodos confirman la solución."
                       if diferencia <= 2 * max(jacobi.tolerancia, seidel.tolerancia)
                       else "⚠ Las soluciones difieren más que la tolerancia.",
                       "ok" if diferencia <= 2 * max(jacobi.tolerancia, seidel.tolerancia) else "aviso"))
    else:
        fallidos = " y ".join(n for n, r in (("Jacobi", jacobi), ("Gauss-Seidel", seidel)) if not r.convergio)
        lineas.append((f"✗ {fallidos} no convergió: no se puede confirmar la solución con ambos.", "error"))
    lineas += [("", "normal"), ("Cómo leerlo", "titulo"),
               ("Gauss-Seidel suele converger más rápido porque aprovecha los valores recién calculados "
                "(su ρ(T) suele ser menor), pero no siempre: depende de la matriz y del orden de las ecuaciones.",
                "normal")]
    return lineas


# ---------------------------------------------------------------- Gauss-Jordan
def titulo_paso(texto):
    """Primera línea de un paso «PASO n. …» sin el número."""
    primera = texto.splitlines()[0]
    return re.sub(r"^PASO\s+\d+\.\s*", "", primera).strip()


def lineas_paso(texto):
    """Convierte el texto de un paso de Gauss-Jordan en líneas con estilo."""
    lineas = []
    for indice, linea in enumerate(texto.splitlines()):
        if indice == 0:
            lineas.append((linea, "titulo"))
        elif linea.strip().startswith(("[", "|")) or re.match(r"^\s*[−\-\d]", linea):
            lineas.append((linea, "formula"))
        elif linea.startswith(("F", "X =", "A⁻¹", "det")):
            lineas.append((linea, "formula"))
        else:
            lineas.append((linea, "normal"))
    return lineas


# ---------------------------------------------------------------- resultado directo
from dataclasses import dataclass as _dataclass


@_dataclass(frozen=True)
class ResultadoDirecto:
    """Gauss-Jordan sobre [A | b] con su verificación A·X = b."""

    variables: tuple
    A: tuple
    b: tuple
    solucion: tuple
    tipo: str            # «unica», «infinitas» o «incompatible»
    pasos: tuple
    residuos: tuple
    determinante: object

    @property
    def convergio(self):
        return self.tipo == "unica"

    @property
    def residuo(self):
        return max((abs(r) for r in self.residuos), default=0.0)


def resolver_directo(A, b, variables):
    """Resuelve por Gauss-Jordan, conserva los pasos y verifica sustituyendo en A·X = b."""
    from nucleo.determinantes import determinante
    from nucleo.sistemas import ErrorSistemaIncompatible, resolver_sistema_gauss_jordan_con_pasos

    det = determinante(A, "lu") if len(A) == len(A[0]) else None
    try:
        solucion, tipo, _pivotes, pasos = resolver_sistema_gauss_jordan_con_pasos(A, [[v] for v in b])
    except ErrorSistemaIncompatible as exc:
        return ResultadoDirecto(tuple(variables), tuple(map(tuple, A)), tuple(b), (), "incompatible",
                                tuple(exc.pasos) + (f"CONCLUSIÓN. {exc}",), (), det)
    x = [fila[0] for fila in solucion]
    residuos = tuple(bi - sum(a * xj for a, xj in zip(fila, x)) for fila, bi in zip(A, b))
    return ResultadoDirecto(tuple(variables), tuple(map(tuple, A)), tuple(b), tuple(x), tipo, tuple(pasos),
                            residuos, det)


def resumen_directo(resultado):
    r = resultado
    v = r.variables
    lineas = [("1. Sistema e incógnitas", "titulo")]
    lineas += [(ecuacion_texto(fila, bi, v), "formula") for fila, bi in zip(r.A, r.b)]
    lineas.append((f"Incógnitas: {', '.join(nombre_bonito(x) for x in v)}", "normal"))
    lineas += [("", "normal"), ("2. Forma matricial A·X = B", "titulo")]
    ancho = max(len(coef(a)) for fila in r.A for a in fila)
    for i, fila in enumerate(r.A):
        entradas = " ".join(coef(a).replace("-", "−").rjust(ancho) for a in fila)
        x = nombre_bonito(v[i]).ljust(3) if i < len(v) else "   "
        lineas.append((f"[ {entradas} ]   [ {x} ]   [ {coef(r.b[i]).replace('-', '−'):>5} ]", "formula"))
    if r.determinante is not None:
        det = r.determinante
        texto_det = coef(float(det)) if det == det else str(det)
        lineas.append((f"det(A) = {texto_det.replace('-', '−')} "
                       + ("≠ 0 → la solución es única." if det != 0 else "= 0 → no hay solución única."),
                       "ok" if det != 0 else "aviso"))
    lineas += [("", "normal"), ("3. Resultado", "titulo")]
    if r.tipo == "incompatible":
        lineas.append(("El sistema es incompatible: no tiene solución.", "error"))
    else:
        if r.tipo == "infinitas":
            lineas.append(("Infinitas soluciones: se muestra una solución particular (variables libres = 0).",
                           "aviso"))
        for nombre, valor in zip(v, r.solucion):
            lineas.append((f"{nombre_bonito(nombre)} = {g(valor, 10)}", "formula"))
        lineas += [("", "normal"), ("4. Verificación: se sustituye X en cada ecuación", "titulo")]
        for i, (fila, bi) in enumerate(zip(r.A, r.b)):
            suma = sum(a * x for a, x in zip(fila, r.solucion))
            lineas.append((f"Ecuación {i + 1}: {g(suma, 10)} = {g(bi, 10)}   (residuo {g(r.residuos[i], 2)})",
                           "formula"))
        lineas.append(("✓ A·X = B se cumple." if r.residuo <= 1e-9 * max(1.0, max(abs(x) for x in r.b))
                       else "⚠ El residuo no es despreciable: revisa el sistema.",
                       "ok" if r.residuo <= 1e-9 * max(1.0, max(abs(x) for x in r.b)) else "aviso"))
    lineas += [("", "normal"), ("Selecciona un paso de la tabla para ver la operación de filas.", "tenue")]
    return lineas
