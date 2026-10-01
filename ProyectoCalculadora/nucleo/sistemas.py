"""Módulo de sistemas lineales: eliminación Gauss-Jordan y combinación lineal."""

from nucleo.numeros import EPSILON, limpiar_numero, asegurar_finito
from nucleo.matrices import dimensiones, matriz_ampliada_a_texto, matriz_a_texto


class ErrorSistemaIncompatible(ValueError):
    """Error que conserva el procedimiento realizado antes de detectar incompatibilidad."""

    def __init__(self, mensaje, pasos=None):
        super().__init__(mensaje)
        self.pasos = pasos or []


def resolver_sistema_gauss_jordan_con_pasos(a, b):
    """Resuelve A·X=B por Gauss-Jordan y retorna también el procedimiento completo."""
    filas_a, columnas_a = dimensiones(a)
    filas_b, columnas_b = dimensiones(b)
    if filas_a != filas_b:
        raise ValueError("Para resolver A · X = B, A y B deben tener la misma cantidad de filas.")

    aumentada = [
        [asegurar_finito(valor, "Coeficiente del sistema") for valor in a[i]]
        + [asegurar_finito(valor, "Término independiente") for valor in b[i]]
        for i in range(filas_a)
    ]
    ancho = columnas_a + columnas_b
    fila_pivote = 0
    columnas_pivote = []
    pasos = [
        "PASO 1. Formar la matriz aumentada [A | B].\n\n"
        + matriz_ampliada_a_texto(aumentada, columnas_a)
    ]
    numero_paso = 2

    for columna in range(columnas_a):
        mejor_fila, mejor_valor = None, 0.0
        for i in range(fila_pivote, filas_a):
            valor = abs(aumentada[i][columna])
            if valor > mejor_valor and valor > EPSILON:
                mejor_valor, mejor_fila = valor, i

        if mejor_fila is None:
            pasos.append(
                f"PASO {numero_paso}. En la columna {columna + 1} no hay pivote no nulo; "
                "esa variable queda libre."
            )
            numero_paso += 1
            continue

        if mejor_fila != fila_pivote:
            aumentada[fila_pivote], aumentada[mejor_fila] = aumentada[mejor_fila], aumentada[fila_pivote]
            pasos.append(
                f"PASO {numero_paso}. Intercambiar F{fila_pivote + 1} ↔ F{mejor_fila + 1}.\n\n"
                + matriz_ampliada_a_texto(aumentada, columnas_a)
            )
            numero_paso += 1

        pivote = aumentada[fila_pivote][columna]
        if abs(pivote - 1.0) > EPSILON:
            aumentada[fila_pivote] = [
                asegurar_finito(valor / pivote, "Valor durante Gauss-Jordan")
                for valor in aumentada[fila_pivote]
            ]
            pasos.append(
                f"PASO {numero_paso}. Normalizar F{fila_pivote + 1}:\n"
                f"F{fila_pivote + 1} ← F{fila_pivote + 1} ÷ ({limpiar_numero(pivote)}).\n\n"
                + matriz_ampliada_a_texto(aumentada, columnas_a)
            )
            numero_paso += 1

        for i in range(filas_a):
            if i == fila_pivote:
                continue
            factor = aumentada[i][columna]
            if abs(factor) > EPSILON:
                nueva_fila = []
                for j in range(ancho):
                    producto = asegurar_finito(
                        factor * aumentada[fila_pivote][j],
                        "Producto durante Gauss-Jordan",
                    )
                    nueva_fila.append(
                        asegurar_finito(
                            aumentada[i][j] - producto,
                            "Valor durante Gauss-Jordan",
                        )
                    )
                aumentada[i] = nueva_fila
                signo = "−" if factor >= 0 else "+"
                magnitud = limpiar_numero(abs(factor))
                pasos.append(
                    f"PASO {numero_paso}. Eliminar la entrada de F{i + 1}, columna {columna + 1}:\n"
                    f"F{i + 1} ← F{i + 1} {signo} ({magnitud})F{fila_pivote + 1}.\n\n"
                    + matriz_ampliada_a_texto(aumentada, columnas_a)
                )
                numero_paso += 1

        columnas_pivote.append(columna)
        fila_pivote += 1
        if fila_pivote == filas_a:
            break

    for fila in aumentada:
        if all(abs(valor) <= EPSILON for valor in fila[:columnas_a]):
            if any(abs(valor) > EPSILON for valor in fila[columnas_a:]):
                pasos.append(
                    f"PASO {numero_paso}. Aparece una fila con 0 en todos los coeficientes "
                    "pero un término independiente distinto de 0. El sistema es incompatible."
                )
                raise ErrorSistemaIncompatible(
                    "No existe una solución: los datos de A y B hacen que el sistema sea incompatible.",
                    pasos,
                )

    solucion = [[0.0] * columnas_b for _ in range(columnas_a)]
    for indice_fila, columna_variable in enumerate(columnas_pivote):
        for j in range(columnas_b):
            solucion[columna_variable][j] = aumentada[indice_fila][columnas_a + j]

    tipo = "unica" if len(columnas_pivote) == columnas_a else "infinitas"
    detalle_tipo = (
        "Cada variable tiene pivote, así que la solución es única."
        if tipo == "unica"
        else "Hay columnas sin pivote; existen infinitas soluciones. Para mostrar una solución particular, las variables libres se fijan en 0."
    )
    pasos.append(
        f"PASO {numero_paso}. Leer la solución de la matriz reducida.\n"
        f"{detalle_tipo}\n\nX =\n{matriz_a_texto(solucion)}"
    )
    return solucion, tipo, columnas_pivote, pasos


def resolver_sistema_gauss_jordan(a, b):
    """Resuelve A·X=B por Gauss-Jordan conservando la API original."""
    solucion, tipo, columnas_pivote, _ = resolver_sistema_gauss_jordan_con_pasos(a, b)
    return solucion, tipo, columnas_pivote


def verificar_combinacion_lineal_con_pasos(generadores, objetivo):
    """Determina si el objetivo es combinación lineal y explica el sistema planteado."""
    if not generadores:
        raise ValueError("Agrega al menos un vector en la lista de vectores generadores.")

    dimension = len(objetivo)
    for vector in generadores:
        if len(vector) != dimension:
            raise ValueError(
                "Todos los vectores generadores y el vector objetivo deben tener "
                "la misma cantidad de componentes."
            )

    a = [[vector[i] for vector in generadores] for i in range(dimension)]
    b = [[valor] for valor in objetivo]

    ecuacion = " + ".join(f"c{i + 1}·v{i + 1}" for i in range(len(generadores)))
    pasos_previos = [
        "PASO 1. Plantear la combinación lineal buscada:\n"
        f"{ecuacion} = vector objetivo.",
        "PASO 2. Colocar los vectores generadores como columnas de A y resolver A·c = b.\n\n"
        f"A =\n{matriz_a_texto(a)}\n\n"
        f"b =\n{matriz_a_texto(b)}",
    ]

    try:
        solucion, tipo, _, pasos_gauss = resolver_sistema_gauss_jordan_con_pasos(a, b)
    except ErrorSistemaIncompatible as error:
        pasos = pasos_previos + [
            paso.replace("PASO ", "GAUSS-JORDAN · PASO ", 1) for paso in error.pasos
        ]
        pasos.append(
            "CONCLUSIÓN. El sistema para los coeficientes es incompatible; por lo tanto, "
            "el vector objetivo NO es combinación lineal de los generadores."
        )
        return False, None, None, pasos

    coeficientes = [fila[0] for fila in solucion]
    pasos = pasos_previos + [
        paso.replace("PASO ", "GAUSS-JORDAN · PASO ", 1) for paso in pasos_gauss
    ]
    expresion = " + ".join(
        f"({limpiar_numero(c)})v{i + 1}" for i, c in enumerate(coeficientes)
    )
    pasos.append(
        "CONCLUSIÓN. Se encontraron coeficientes que satisfacen la ecuación:\n"
        f"{expresion} = vector objetivo."
    )
    return True, coeficientes, tipo, pasos


def verificar_combinacion_lineal(generadores, objetivo):
    """Versión compatible con la API original, sin devolver el texto del procedimiento."""
    es_combinacion, coeficientes, tipo, _ = verificar_combinacion_lineal_con_pasos(
        generadores, objetivo
    )
    return es_combinacion, coeficientes, tipo
