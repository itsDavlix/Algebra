"""Módulo de sistemas lineales: eliminación Gauss-Jordan y combinación lineal."""

from nucleo.numeros import limpiar_numero, asegurar_finito, escala_de, umbral_cero
from nucleo.matrices import (
    dimensiones, matriz_ampliada_a_texto, matriz_a_texto,
    _buscar_pivote, _normalizar_fila, _eliminar_columna,
    _texto_paso_gauss_jordan,
)


class ErrorSistemaIncompatible(ValueError):
    """Error que conserva el procedimiento realizado antes de detectar incompatibilidad."""

    def __init__(self, mensaje, pasos=None):
        super().__init__(mensaje)
        self.pasos = pasos or []


def _reducir_sistema(a, b):
    """Reduce [A | B], identifica pivotes y conserva cada paso del procedimiento."""
    filas_a, columnas_a = dimensiones(a)
    filas_b, columnas_b = dimensiones(b)
    if filas_a != filas_b:
        raise ValueError("Para resolver A · X = B, A y B deben tener la misma cantidad de filas.")

    aumentada = [
        [asegurar_finito(valor, "Coeficiente del sistema") for valor in a[i]]
        + [asegurar_finito(valor, "Término independiente") for valor in b[i]]
        for i in range(filas_a)
    ]
    umbral_a = umbral_cero(escala_de(a))
    umbrales_b = [umbral_cero(max(abs(fila[j]) for fila in b)) for j in range(columnas_b)]
    ancho = columnas_a + columnas_b
    fila_pivote = 0
    columnas_pivote = []
    pasos = [
        "PASO 1. Formar la matriz aumentada [A | B].\n\n"
        + matriz_ampliada_a_texto(aumentada, columnas_a)
    ]
    numero_paso = 2

    # Busca pivotes y los intercambia para evitar dividir por valores nulos.
    for columna in range(columnas_a):
        mejor_fila = _buscar_pivote(
            aumentada, fila_pivote, columna, umbral_a,
        )
        if mejor_fila is None:
            pasos.append(
                f"PASO {numero_paso}. En la columna {columna + 1} no hay pivote no nulo; "
                "esa variable queda libre."
            )
            numero_paso += 1
            continue

        if mejor_fila != fila_pivote:
            aumentada[fila_pivote], aumentada[mejor_fila] = aumentada[mejor_fila], aumentada[fila_pivote]
            pasos.append(_texto_paso_gauss_jordan(
                numero_paso,
                f"Intercambiar F{fila_pivote + 1} ↔ F{mejor_fila + 1}.",
                aumentada, columnas_a,
            ))
            numero_paso += 1

        pivote = aumentada[fila_pivote][columna]
        if pivote != 1.0:
            _normalizar_fila(aumentada, fila_pivote, pivote)
            pasos.append(_texto_paso_gauss_jordan(
                numero_paso, f"Normalizar F{fila_pivote + 1}:",
                aumentada, columnas_a,
                f"F{fila_pivote + 1} ← F{fila_pivote + 1} ÷ ({limpiar_numero(pivote, escala_de(a))}).",
            ))
            numero_paso += 1

        cambios = _eliminar_columna(
            aumentada, fila_pivote, columna, umbral_a, ancho,
        )
        for indice_fila, factor in cambios:
            signo = "−" if factor >= 0 else "+"
            magnitud = limpiar_numero(abs(factor), abs(factor))
            pasos.append(_texto_paso_gauss_jordan(
                numero_paso,
                f"Eliminar la entrada de F{indice_fila + 1}, columna {columna + 1}:",
                aumentada, columnas_a,
                f"F{indice_fila + 1} ← F{indice_fila + 1} {signo} ({magnitud})F{fila_pivote + 1}.",
            ))
            numero_paso += 1

        columnas_pivote.append(columna)
        fila_pivote += 1
        if fila_pivote == filas_a:
            break

    # Una fila 0 = valor no nulo demuestra que el sistema es incompatible.
    # Las filas con pivote representan ecuaciones válidas ya normalizadas;
    # solo las restantes pueden representar una contradicción 0 = b.
    for fila in aumentada[fila_pivote:]:
        if all(abs(valor) <= umbral_a for valor in fila[:columnas_a]):
            if any(abs(valor) > umbrales_b[j] for j, valor in enumerate(fila[columnas_a:])):
                pasos.append(
                    f"PASO {numero_paso}. Aparece una fila con 0 en todos los coeficientes "
                    "pero un término independiente distinto de 0. El sistema es incompatible."
                )
                raise ErrorSistemaIncompatible(
                    "No existe una solución: los datos de A y B hacen que el sistema sea incompatible.",
                    pasos,
                )

    return aumentada, columnas_pivote, pasos, numero_paso, filas_a, columnas_a, columnas_b


def _texto_solucion_general(reducida, columnas_pivote, columnas_a, columnas_b, nombre_variable):
    """Construye ecuaciones paramétricas a partir de una matriz reducida."""
    libres = [i for i in range(columnas_a) if i not in columnas_pivote]
    bloques = []
    for indice_b in range(columnas_b):
        ecuaciones = []
        if columnas_b > 1:
            ecuaciones.append(f"Para la columna b{indice_b + 1}:")
        fila_por_pivote = {
            columna: indice_fila
            for indice_fila, columna in enumerate(columnas_pivote)
        }
        parametro_por_columna = {
            columna: indice_libre
            for indice_libre, columna in enumerate(libres, 1)
        }
        for columna in range(columnas_a):
            if columna in parametro_por_columna:
                ecuaciones.append(
                    f"{nombre_variable}{columna + 1} = "
                    f"t{parametro_por_columna[columna]}"
                )
                continue
            fila = fila_por_pivote[columna]
            constante = reducida[fila][columnas_a + indice_b]
            expresion = limpiar_numero(constante, abs(constante))
            for columna_libre, indice_libre in parametro_por_columna.items():
                coeficiente = -reducida[fila][columna_libre]
                if coeficiente == 0:
                    continue
                signo = " + " if coeficiente > 0 else " − "
                magnitud = abs(coeficiente)
                factor = "" if magnitud == 1 else f"{limpiar_numero(magnitud, magnitud)}·"
                expresion += f"{signo}{factor}t{indice_libre}"
            ecuaciones.append(f"{nombre_variable}{columna + 1} = {expresion}")
        bloques.append("\n".join(ecuaciones))
    return "\n\n".join(bloques)


def solucion_general_texto(a, b, nombre_variable="x"):
    """Devuelve la forma paramétrica de las soluciones de A·X=B."""
    if not isinstance(nombre_variable, str) or not nombre_variable:
        raise ValueError("El nombre de variable debe ser un texto no vacío.")
    reducida, pivotes, _, _, _, columnas_a, columnas_b = _reducir_sistema(a, b)
    return _texto_solucion_general(
        reducida, pivotes, columnas_a, columnas_b, nombre_variable,
    )


# Reduce la matriz aumentada y registra las operaciones de fila realizadas.
def resolver_sistema_gauss_jordan_con_pasos(a, b, nombre_variable="x"):
    """Resuelve A·X=B por Gauss-Jordan y retorna también el procedimiento completo."""
    if not isinstance(nombre_variable, str) or not nombre_variable:
        raise ValueError("El nombre de variable debe ser un texto no vacío.")
    (
        reducida, columnas_pivote, pasos, numero_paso,
        _, columnas_a, columnas_b,
    ) = _reducir_sistema(a, b)
    # Coloca cada resultado en la variable correspondiente a su columna pivote.
    solucion = [[0.0] * columnas_b for _ in range(columnas_a)]
    for indice_fila, columna_variable in enumerate(columnas_pivote):
        for j in range(columnas_b):
            solucion[columna_variable][j] = reducida[indice_fila][columnas_a + j]

    tipo = "unica" if len(columnas_pivote) == columnas_a else "infinitas"
    detalle_tipo = (
        "Cada variable tiene pivote, así que la solución es única."
        if tipo == "unica"
        else "Hay columnas sin pivote; existen infinitas soluciones. Para mostrar una solución particular, las variables libres se fijan en 0."
    )
    paso_solucion = (
        f"PASO {numero_paso}. Leer la solución de la matriz reducida.\n"
        f"{detalle_tipo}\n\nX =\n{matriz_a_texto(solucion)}"
    )
    if tipo == "infinitas":
        paso_solucion += "\n\nSolución general:\n" + _texto_solucion_general(
            reducida, columnas_pivote, columnas_a, columnas_b, nombre_variable,
        )
    pasos.append(paso_solucion)
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

    # Cada generador pasa a ser una columna del sistema A·c = objetivo.
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
        solucion, tipo, _, pasos_gauss = resolver_sistema_gauss_jordan_con_pasos(
            a, b, nombre_variable="c",
        )
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
    escala_coeficientes = escala_de(coeficientes)
    pasos = pasos_previos + [
        paso.replace("PASO ", "GAUSS-JORDAN · PASO ", 1) for paso in pasos_gauss
    ]
    expresion = " + ".join(
        f"({limpiar_numero(c, escala_coeficientes)})v{i + 1}"
        for i, c in enumerate(coeficientes)
    )
    pasos.append(
        "CONCLUSIÓN. Se encontraron coeficientes que satisfacen la ecuación:\n"
        f"{expresion} = vector objetivo."
        + (
            "\n\nFamilia de coeficientes:\n"
            + solucion_general_texto(a, b, nombre_variable="c")
            if tipo == "infinitas" else ""
        )
    )
    return True, coeficientes, tipo, pasos


def verificar_combinacion_lineal(generadores, objetivo):
    """Versión compatible con la API original, sin devolver el texto del procedimiento."""
    es_combinacion, coeficientes, tipo, _ = verificar_combinacion_lineal_con_pasos(
        generadores, objetivo
    )
    return es_combinacion, coeficientes, tipo
