"""Determinantes por expansión de cofactores y factorización LU con pivoteo."""

from fractions import Fraction
from math import factorial
from nucleo.matrices import dimensiones, leer_matriz
from nucleo.numeros import asegurar_finito


# La cota limita el trabajo factorial sin impedir matrices grandes con muchos ceros.
MAX_EXPANSIONES = 100000


# Valida el tamaño y conserva los valores como fracciones para evitar redondeos.
def _preparar(matriz):
    """Valida una matriz cuadrada y copia sus valores como racionales exactos."""
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError("El determinante requiere una matriz cuadrada.")
    # Los racionales evitan descartar pivotes pequeños y errores de cancelación.
    # Se conserva exactamente el valor numérico recibido por el núcleo.
    return [[Fraction(asegurar_finito(valor)) for valor in fila] for fila in matriz]


def recomendar_metodo(matriz):
    """Devuelve una recomendación previa basada en el orden, sin calcular el determinante."""
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError("El determinante requiere una matriz cuadrada.")
    if filas <= 3:
        return ("cofactores", "Se recomiendan cofactores: para órdenes de 1 a 3, "
                "las fórmulas cortas suelen requerir menos trabajo que factorizar LU.")
    return ("lu", "Se recomienda LU: requiere O(n³) operaciones aritméticas, frente "
            "a O(n!) de cofactores en el peor caso. Es una estimación general; "
            "los ceros pueden reducir mucho el trabajo de cofactores.")


def determinante_adaptativo(matriz):
    """Usa el método más seguro para matrices grandes sin perder exactitud."""
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        raise ValueError("El determinante requiere una matriz cuadrada.")
    if filas <= 6:
        return determinante_cofactores(matriz)
    return determinante_lu(matriz)


def _crear_expansor_cofactores():
    """Crea una expansión memoizada con un límite compartido por todo el cálculo."""
    expansiones = 0
    memo = {}

    def expandir(actual):
        """Resuelve los casos base y construye los menores con su signo alternado."""
        nonlocal expansiones
        key = tuple(tuple(fila) for fila in actual)
        if key in memo:
            return memo[key]
        expansiones += 1
        if expansiones > MAX_EXPANSIONES:
            raise ValueError(f"Cofactores superó el límite de {MAX_EXPANSIONES} expansiones. "
                             "Seleccioná LU para calcular esta matriz.")
        n = len(actual)
        if n == 1:
            resultado = actual[0][0]
        elif n == 2:
            resultado = actual[0][0] * actual[1][1] - actual[0][1] * actual[1][0]
        else:
            # Una fila nula da determinante cero; los demás ceros no generan menores.
            fila = max(range(n), key=lambda i: actual[i].count(0))
            total = Fraction(0)
            for columna, valor in enumerate(actual[fila]):
                if valor == 0:
                    continue
                menor = [r[:columna] + r[columna + 1:]
                         for i, r in enumerate(actual) if i != fila]
                total += (-1) ** (fila + columna) * valor * expandir(menor)
            resultado = total
        memo[key] = resultado
        return resultado

    return expandir


def determinante_cofactores(matriz):
    """Expande por la fila con más ceros y memoiza subdeterminantes repetidos."""
    expandir = _crear_expansor_cofactores()
    return expandir(_preparar(matriz))


def determinante_lu(matriz):
    """Calcula det(A) = (-1)^intercambios · producto(diagonal(U)), con PA = LU."""
    u = _preparar(matriz)
    n = len(u)
    signo = 1

    # El pivoteo parcial elige el mayor valor absoluto disponible en cada columna.
    for columna in range(n):
        pivote = max(range(columna, n), key=lambda i: abs(u[i][columna]))
        if u[pivote][columna] == 0:
            return Fraction(0)
        if pivote != columna:
            u[columna], u[pivote] = u[pivote], u[columna]
            signo *= -1

        # Los multiplicadores son las entradas de L, cuya diagonal vale uno.
        # Basta conservar U porque det(L) = 1; la matriz original no se modifica.
        for fila in range(columna + 1, n):
            factor = u[fila][columna] / u[columna][columna]
            u[fila][columna] = Fraction(0)
            for j in range(columna + 1, n):
                u[fila][j] -= factor * u[columna][j]

    # Cada intercambio cambia el signo del determinante una sola vez.
    resultado = Fraction(signo)
    for i in range(n):
        resultado *= u[i][i]
    return resultado


def determinante(matriz, metodo):
    """Ejecuta únicamente el método elegido y rechaza opciones desconocidas."""
    if metodo == "cofactores":
        return determinante_cofactores(matriz)
    if metodo == "lu":
        return determinante_lu(matriz)
    if metodo == "auto":
        return determinante_adaptativo(matriz)
    raise ValueError("Seleccioná cofactores o LU.")


def formatear_determinante(valor):
    """Muestra enteros exactos o una aproximación sin redondear valores pequeños a cero."""
    if valor.denominator == 1:
        return str(valor.numerator)
    try:
        aproximado = asegurar_finito(valor)
    except ValueError:
        return str(valor)
    # La fracción preserva valores que no se pueden representar como decimales finitos.
    if aproximado == 0 and valor != 0:
        return str(valor)
    return f"≈ {aproximado:.12g}"

# ---------------------------------------------------------------------------
# Eficiencia estimada y procedimiento paso a paso
# ---------------------------------------------------------------------------

def estimar_costos(orden):
    """Devuelve (operaciones_cofactores, operaciones_lu) como estimación por orden n.

    Cofactores sin ceros realiza del orden de n! multiplicaciones; LU realiza
    alrededor de n³/3. Son cifras de referencia, no mediciones exactas.
    """
    if isinstance(orden, bool) or not isinstance(orden, int) or orden <= 0:
        raise ValueError("El orden debe ser un entero positivo.")
    return factorial(orden), max(1, round(orden ** 3 / 3))


def resumen_eficiencia(matriz):
    """Texto comparativo que se muestra ANTES de que el usuario elija el método."""
    n, _ = dimensiones(matriz)
    metodo, motivo = recomendar_metodo(matriz)
    cofactores, lu = estimar_costos(n)
    nombre = "Cofactores" if metodo == "cofactores" else "LU"
    return (metodo,
            f"Más eficiente para una matriz {n}×{n}: {nombre}.\n"
            f"• Cofactores ≈ {cofactores:,} operaciones (crece como n!).\n"
            f"• LU ≈ {lu:,} operaciones (crece como n³).\n{motivo}")


def _texto(valor):
    """Escribe un racional como entero o fracción a/b, sin decimales ocultos."""
    return str(valor.numerator) if valor.denominator == 1 else f"{valor.numerator}/{valor.denominator}"


def _matriz_texto(matriz):
    """Alinea una matriz de racionales en columnas para mostrarla en pantalla."""
    celdas = [[_texto(v) for v in fila] for fila in matriz]
    ancho = max(len(c) for fila in celdas for c in fila)
    return "\n".join("│ " + "  ".join(c.rjust(ancho) for c in fila) + " │" for fila in celdas)


def _pasos_cofactores(matriz):
    """Describe la expansión, mostrando los menores de tamaño manejable."""
    a = _preparar(matriz)
    expandir = _crear_expansor_cofactores()
    n = len(a)
    if n <= 2:
        valor_total = expandir(a)
        if n == 1:
            formula = "det(A) = a₁₁"
        else:
            formula = (
                f"det(A) = a₁₁·a₂₂ − a₁₂·a₂₁ = "
                f"({_texto(a[0][0])})·({_texto(a[1][1])}) − "
                f"({_texto(a[0][1])})·({_texto(a[1][0])})"
            )
        return valor_total, [f"PASO 2. Caso directo de orden {n}.\n{formula} = {_texto(valor_total)}"]

    expandir(a)
    # Se repite el criterio de determinante_cofactores: fila con más ceros.
    fila = max(range(n), key=lambda i: a[i].count(0))
    terminos, lineas = [], []
    for columna, elemento in enumerate(a[fila]):
        if elemento == 0:
            continue
        menor = [r[:columna] + r[columna + 1:] for i, r in enumerate(a) if i != fila]
        det_menor = expandir(menor)
        signo = (-1) ** (fila + columna)
        termino = signo * elemento * det_menor
        terminos.append(termino)
        detalle_menor = (
            "\n" + _matriz_texto(menor)
            if len(menor) <= 6
            else f" (menor de orden {len(menor)}; se omite la impresión completa)"
        )
        signo_texto = "+" if signo > 0 else "−"
        lineas.append(
            f"a[{fila + 1},{columna + 1}] = {_texto(elemento)}; "
            f"M[{fila + 1},{columna + 1}] ={detalle_menor}\n"
            f"det(M) = {_texto(det_menor)}; "
            f"término = ({signo_texto})·({_texto(elemento)})·"
            f"({_texto(det_menor)}) = {_texto(termino)}"
        )
    total = sum(terminos, Fraction(0))
    return total, [
        f"PASO 2. Se expande por la fila {fila + 1} (la que tiene más ceros).\n"
        "Los elementos nulos se omiten porque no aportan términos.",
        "PASO 3. Términos aᵢⱼ·(−1)ⁱ⁺ʲ·det(Mᵢⱼ):\n" + "\n".join(lineas or ["(todos los elementos son cero)"]),
        "PASO 4. Suma de los términos = " + (" + ".join(_texto(t) for t in terminos) or "0")
        + f" = {_texto(total)}",
    ]


def _pasos_lu(matriz):
    """Describe cada columna de la eliminación: pivote, intercambio y multiplicadores."""
    u = _preparar(matriz)
    n = len(u)
    signo, pasos = 1, []
    for columna in range(n):
        pivote = max(range(columna, n), key=lambda i: abs(u[i][columna]))
        if u[pivote][columna] == 0:
            pasos.append(f"PASO {columna + 2}. Columna {columna + 1} sin pivote (todo cero): "
                         "la matriz es singular y det(A) = 0.")
            return Fraction(0), pasos
        texto = f"PASO {columna + 2}. Columna {columna + 1}: pivote {_texto(u[pivote][columna])}"
        if pivote != columna:
            u[columna], u[pivote] = u[pivote], u[columna]
            signo *= -1
            texto += f" (se intercambian las filas {columna + 1} y {pivote + 1}; el signo cambia)"
        multiplicadores = []
        for fila in range(columna + 1, n):
            factor = u[fila][columna] / u[columna][columna]
            multiplicadores.append(f"l[{fila + 1},{columna + 1}] = {_texto(factor)}")
            u[fila][columna] = Fraction(0)
            for j in range(columna + 1, n):
                u[fila][j] -= factor * u[columna][j]
        if multiplicadores:
            texto += (
                "\nMultiplicadores: " + ", ".join(multiplicadores)
                if n <= 10
                else f"\nSe anulan las {len(multiplicadores)} entradas debajo del pivote."
            )
        if n <= 8:
            texto += "\nU parcial =\n" + _matriz_texto(u)
        else:
            texto += "\nU parcial omitida para mantener legible la salida de una matriz grande."
        pasos.append(texto)
    diagonal = [u[i][i] for i in range(n)]
    resultado = Fraction(signo)
    for d in diagonal:
        resultado *= d
    pasos.append(f"PASO {n + 2}. det(A) = {signo} · "
                 + " · ".join(_texto(d) for d in diagonal) + f" = {_texto(resultado)}")
    return resultado, pasos


def determinante_con_pasos(matriz, metodo):
    """Calcula con el método elegido y devuelve (valor, lista_de_pasos, comprobación)."""
    if metodo not in ("cofactores", "lu"):
        raise ValueError("Seleccioná cofactores o LU.")
    n, _ = dimensiones(matriz)
    pasos = ["PASO 1. La matriz es cuadrada de orden " + str(n) + "; se puede calcular el determinante."]
    valor, detalle = _pasos_cofactores(matriz) if metodo == "cofactores" else _pasos_lu(matriz)
    pasos += detalle

    # Contrasta con el otro método solo cuando su costo no resulta excesivo.
    otro = "lu" if metodo == "cofactores" else "cofactores"
    if otro == "cofactores" and n > 7:
        comprobacion = "COMPROBACIÓN omitida: verificar con cofactores sería demasiado lento para este orden."
    else:
        contraste = determinante(matriz, otro)
        ok = contraste == valor
        comprobacion = (f"COMPROBACIÓN. Con {otro.upper()} se obtiene {_texto(contraste)}. "
                        + ("✓ Ambos métodos coinciden." if ok else "✗ Los métodos no coinciden."))
    return valor, pasos, comprobacion


def validar_entrada_determinante(texto):
    """Revisa el texto por etapas y devuelve (matriz o None, lista de comprobaciones).

    Cada comprobación es una tupla (estado, descripción, detalle): el estado es
    True si se cumple, False si falla y None si aún no se pudo evaluar.
    """
    descripciones = [
        "Hay datos escritos",
        "Cada entrada es un número real finito (sin comas sueltas ni filas vacías)",
        "Todas las filas tienen la misma cantidad de elementos",
        "La matriz es cuadrada (n × n)",
    ]
    resultado = [[None, d, ""] for d in descripciones]

    # Etapa 1: el campo no puede estar vacío.
    if not str(texto).strip():
        resultado[0][0] = False
        resultado[0][2] = "Escribí una matriz, una fila por línea."
        return None, [tuple(r) for r in resultado]
    resultado[0][0] = True

    # Etapas 2 y 3: la lectura reporta la posición exacta del primer error.
    try:
        matriz = leer_matriz(texto, "matriz A")
    except ValueError as error:
        indice = 2 if "rectangular" in str(error) else 1
        for i in range(indice):
            resultado[i][0] = True
        resultado[indice][0] = False
        resultado[indice][2] = str(error)
        return None, [tuple(r) for r in resultado]
    resultado[1][0] = resultado[2][0] = True

    # Etapa 4: el determinante solo existe para matrices cuadradas.
    filas, columnas = dimensiones(matriz)
    if filas != columnas:
        resultado[3][0] = False
        resultado[3][2] = f"La matriz es {filas}×{columnas}; el determinante requiere filas = columnas."
        return None, [tuple(r) for r in resultado]
    resultado[3][0] = True
    resultado[3][2] = f"Orden {filas}×{filas}."
    return matriz, [tuple(r) for r in resultado]