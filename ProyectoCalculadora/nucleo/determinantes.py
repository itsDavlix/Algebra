"""Determinantes por expansión de cofactores y factorización LU con pivoteo."""

from fractions import Fraction
from math import factorial
from decimal import Decimal, localcontext
from nucleo.matrices import dimensiones, leer_matriz
from nucleo.numeros import asegurar_finito, limpiar_numero


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
    """Escribe racionales como enteros o decimales breves, nunca como fracciones."""
    if valor.denominator == 1:
        return str(valor.numerator)
    try:
        return limpiar_numero(valor.numerator / valor.denominator)
    except (OverflowError, ValueError):
        # El cálculo sigue siendo exacto; Decimal permite mostrar razones
        # enormes sin convertirlas primero a un float que podría desbordarse.
        with localcontext() as contexto:
            contexto.prec = 12
            return format(
                Decimal(valor.numerator) / Decimal(valor.denominator),
                ".6g",
            )


def _matriz_texto(matriz):
    """Alinea una matriz de racionales en columnas para mostrarla en pantalla."""
    celdas = [[_texto(v) for v in fila] for fila in matriz]
    ancho = max(len(c) for fila in celdas for c in fila)
    return "\n".join("│ " + "  ".join(c.rjust(ancho) for c in fila) + " │" for fila in celdas)


def _explicar_determinante_menor(menor, valor):
    """Muestra la cuenta explícita cuando el menor es de orden uno o dos."""
    if len(menor) == 1:
        return f"det(M) = {_texto(menor[0][0])}"
    if len(menor) == 2:
        return (
            f"det(M) = ({_texto(menor[0][0])})·({_texto(menor[1][1])}) − "
            f"({_texto(menor[0][1])})·({_texto(menor[1][0])}) = {_texto(valor)}"
        )
    return f"det(M) = {_texto(valor)} (calculado recursivamente por cofactores)"


def _pasos_cofactores(matriz):
    """Explica la expansión y desarrolla por completo los menores 2×2."""
    a = _preparar(matriz)
    expandir = _crear_expansor_cofactores()
    n = len(a)
    if n <= 2:
        valor_total = expandir(a)
        if n == 1:
            formula = f"det(A) = a₁₁ = {_texto(a[0][0])}"
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
    cantidad_ceros = a[fila].count(0)
    texto_ceros = "cero" if cantidad_ceros == 1 else "ceros"
    terminos, lineas = [], []
    for columna, elemento in enumerate(a[fila]):
        if elemento == 0:
            continue
        menor = [r[:columna] + r[columna + 1:] for i, r in enumerate(a) if i != fila]
        det_menor = expandir(menor)
        signo = (-1) ** (fila + columna)
        termino = signo * elemento * det_menor
        terminos.append(termino)
        cofactor = signo * det_menor
        detalle_menor = (
            "\n" + _matriz_texto(menor)
            if len(menor) <= 6
            else f" (menor de orden {len(menor)}; se omite la impresión completa)"
        )
        signo_texto = "+" if signo > 0 else "−"
        lineas.append(
            f"Elemento a[{fila + 1},{columna + 1}] = {_texto(elemento)}.\n"
            f"Menor M[{fila + 1},{columna + 1}] ={detalle_menor}\n"
            f"Cofactor C[{fila + 1},{columna + 1}] = "
            f"({signo_texto}1)·det(M) = ({signo_texto}1)·"
            f"({_texto(det_menor)}) = {_texto(cofactor)}.\n"
            f"Término a·C = ({_texto(elemento)})·({_texto(cofactor)}) "
            f"= {_texto(termino)}.\n"
            f"{_explicar_determinante_menor(menor, det_menor)}"
        )
    total = sum(terminos, Fraction(0))
    return total, [
        f"PASO 2. Elegir la fila {fila + 1}, que contiene {cantidad_ceros} {texto_ceros} "
        "y reduce la cantidad de términos.",
        "PASO 3. Aplicar la expansión por cofactores:\n"
        f"det(A) = Σⱼ a[{fila + 1},j]·C[{fila + 1},j], "
        "donde C[i,j] = (−1)^(i+j)·det(M[i,j]).\n"
        "El signo alterna según la posición; los elementos cero aportan cero.\n\n"
        + "\n\n".join(lineas or ["Todos los elementos de la fila elegida son cero."]),
        "PASO 4. Sumar los términos obtenidos:\n"
        + (" + ".join(f"({_texto(t)})" for t in terminos) or "0")
        + f" = {_texto(total)}",
    ]


def _pasos_lu(matriz):
    """Explica pivotes, intercambios y operaciones elementales de la eliminación LU."""
    u = _preparar(matriz)
    n = len(u)
    signo, pasos = 1, []
    pasos.append(
        "PASO 2. Iniciar la eliminación por filas.\n"
        "En cada columna se elige como pivote el elemento de mayor valor absoluto "
        "entre las filas restantes. Este proceso equivale a PA = LU; como L tiene "
        "diagonal de unos, det(L) = 1.\n\nU inicial =\n" + _matriz_texto(u)
    )
    for columna in range(n):
        pivote = max(range(columna, n), key=lambda i: abs(u[i][columna]))
        if u[pivote][columna] == 0:
            pasos.append(
                f"Columna {columna + 1}: todas las entradas disponibles son cero. "
                "No existe pivote, por lo tanto la matriz es singular y det(A) = 0."
            )
            return Fraction(0), pasos
        texto = (
            f"PASO {columna + 3}. Columna {columna + 1}: el pivote elegido es "
            f"U[{pivote + 1},{columna + 1}] = {_texto(u[pivote][columna])}, "
            "el de mayor valor absoluto en esta columna."
        )
        if pivote != columna:
            u[columna], u[pivote] = u[pivote], u[columna]
            signo *= -1
            texto += (
                f"\nIntercambiar F{columna + 1} ↔ F{pivote + 1}. "
                f"Cada intercambio cambia el signo: s = {signo}.\n"
                "U después del intercambio =\n" + _matriz_texto(u)
            )
        operaciones = []
        for fila in range(columna + 1, n):
            factor = u[fila][columna] / u[columna][columna]
            if factor == 0:
                continue
            valor_eliminado = u[fila][columna]
            operaciones.append(
                f"F{fila + 1} ← F{fila + 1} − "
                f"({_texto(factor)})F{columna + 1}; "
                f"{_texto(valor_eliminado)} − "
                f"({_texto(factor)})({_texto(u[columna][columna])}) = 0."
            )
            u[fila][columna] = Fraction(0)
            for j in range(columna + 1, n):
                u[fila][j] -= factor * u[columna][j]
            if n <= 8:
                operaciones[-1] += "\nU después de la operación =\n" + _matriz_texto(u)
        texto += "\n" + (
            "\n".join(operaciones)
            if operaciones else "No hay elementos debajo del pivote que deban eliminarse."
        )
        if n > 8 and operaciones:
            texto += (
                f"\nSe aplicaron {len(operaciones)} operaciones de fila en esta columna; "
                "se omiten las matrices intermedias por tamaño."
            )
        pasos.append(texto)
    diagonal = [u[i][i] for i in range(n)]
    resultado = Fraction(signo)
    for d in diagonal:
        resultado *= d
    pasos.append(
        "PASO FINAL. La matriz quedó triangular superior, por lo que su determinante "
        "es el producto de la diagonal. Se corrige por el signo de los intercambios:\n"
        f"det(A) = s·∏uᵢᵢ = ({signo})·"
        + "·".join(_texto(d) for d in diagonal)
        + f" = {_texto(resultado)}."
    )
    return resultado, pasos


def determinante_con_pasos(matriz, metodo):
    """Calcula con el método elegido y devuelve (valor, lista_de_pasos, comprobación)."""
    if metodo not in ("cofactores", "lu"):
        raise ValueError("Seleccioná cofactores o LU.")
    n, _ = dimensiones(matriz)
    pasos = [
        "PASO 1. Validar que A sea cuadrada.\n"
        f"A tiene {n} filas y {n} columnas; por lo tanto, el determinante está definido.\n\n"
        "A =\n" + _matriz_texto(_preparar(matriz))
    ]
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