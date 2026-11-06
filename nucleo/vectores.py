"""Módulo de vectores: lectura, formato y operaciones algebraicas en R^n."""

import re

from nucleo.numeros import (
    convertir_numero, limpiar_numero, asegurar_finito, escala_de, EPSILON,
)
from nucleo.matrices import rango_matriz_con_pasos

MAX_COMPONENTES = 200


# Convierte los separadores permitidos en una lista de componentes.
def _separar_componentes(texto, nombre="vector"):
    texto = str(texto).strip()
    if not texto:
        raise ValueError(f"Escribe el {nombre} antes de continuar.")
    if texto.startswith(",") or texto.endswith(",") or re.search(r",\s*,", texto):
        raise ValueError(
            f"El {nombre} contiene una coma sin número. Corrige separadores como ',,' o comas al inicio/final."
        )
    return texto.replace(",", " ").split()


def leer_vector(texto, nombre="vector"):
    """Interpreta un vector separado por comas o espacios y valida cada componente."""
    partes = _separar_componentes(texto, nombre)
    if len(partes) > MAX_COMPONENTES:
        raise ValueError(
            f"El {nombre} tiene {len(partes)} componentes. El máximo permitido es {MAX_COMPONENTES}."
        )
    return [
        convertir_numero(parte, f"Componente {i} del {nombre}")
        for i, parte in enumerate(partes, start=1)
    ]


def vector_a_texto(vector):
    """Da formato (a, b, c, ...) a un vector para mostrarlo en pantalla."""
    if not vector:
        return "()"
    escala = escala_de(vector)
    return "(" + ", ".join(limpiar_numero(x, escala) for x in vector) + ")"


# Las operaciones entre dos vectores requieren dimensiones iguales.
def _validar_misma_dimension(v1, v2):
    if not isinstance(v1, (list, tuple)) or not isinstance(v2, (list, tuple)):
        raise ValueError("Los vectores deben ser listas o tuplas de números.")
    if not v1 or not v2:
        raise ValueError("Los vectores no pueden estar vacíos.")
    if len(v1) != len(v2):
        raise ValueError(
            f"Los vectores deben tener la misma dimensión: V1 tiene {len(v1)} componentes "
            f"y V2 tiene {len(v2)}."
        )


def sumar_vectores(v1, v2):
    _validar_misma_dimension(v1, v2)
    return [asegurar_finito(a + b, f"Resultado de la componente {i}") for i, (a, b) in enumerate(zip(v1, v2), 1)]


def restar_vectores(v1, v2):
    _validar_misma_dimension(v1, v2)
    return [asegurar_finito(a - b, f"Resultado de la componente {i}") for i, (a, b) in enumerate(zip(v1, v2), 1)]


def multiplicar_vector_escalar(vector, escalar):
    if not vector:
        raise ValueError("El vector no puede estar vacío.")
    escalar = asegurar_finito(escalar, "El escalar")
    return [
        asegurar_finito(escalar * componente, f"Resultado de la componente {i}")
        for i, componente in enumerate(vector, 1)
    ]


def producto_punto(v1, v2):
    """Calcula el producto punto de dos vectores de igual dimensión."""
    _validar_misma_dimension(v1, v2)
    total = 0.0
    for indice, (a, b) in enumerate(zip(v1, v2), 1):
        a = asegurar_finito(a, f"Componente {indice} de V1")
        b = asegurar_finito(b, f"Componente {indice} de V2")
        total = asegurar_finito(total + a * b, "Producto punto")
    return total


def producto_punto_con_pasos(v1, v2):
    """Calcula el producto punto, desarrolla las operaciones y lo comprueba."""
    resultado = producto_punto(v1, v2)
    valores_v1 = [asegurar_finito(valor, "Componente de V1") for valor in v1]
    valores_v2 = [asegurar_finito(valor, "Componente de V2") for valor in v2]
    escala_v1, escala_v2 = escala_de(valores_v1), escala_de(valores_v2)
    productos = [a * b for a, b in zip(valores_v1, valores_v2)]
    escala_productos = escala_de(productos)
    calculos = [
        f"({limpiar_numero(a, escala_v1)})({limpiar_numero(b, escala_v2)})"
        for a, b in zip(valores_v1, valores_v2)
    ]
    intercambiado = producto_punto(v2, v1)
    umbral = EPSILON * max(abs(resultado), abs(intercambiado))
    comprobado = abs(resultado - intercambiado) <= umbral
    pasos = [
        "PASO 1. Multiplicar las componentes correspondientes:\n"
        + " + ".join(calculos),
        "PASO 2. Sumar los productos:\n"
        + " + ".join(limpiar_numero(valor, escala_productos) for valor in productos)
        + f" = {limpiar_numero(resultado, escala_productos)}",
        "COMPROBACIÓN. El producto punto es simétrico: V1·V2 = V2·V1.\n"
        + ("✓ Los dos resultados coinciden." if comprobado else "✗ Los resultados no coinciden."),
    ]
    return resultado, pasos


def producto_cruz(v1, v2):
    """Calcula el producto cruz de dos vectores de R³."""
    _validar_misma_dimension(v1, v2)
    if len(v1) != 3:
        raise ValueError("El producto cruz solo está definido para vectores de R³.")
    u = [asegurar_finito(valor, "Componente de V1") for valor in v1]
    v = [asegurar_finito(valor, "Componente de V2") for valor in v2]
    return [
        asegurar_finito(u[1] * v[2] - u[2] * v[1], "Producto cruz"),
        asegurar_finito(u[2] * v[0] - u[0] * v[2], "Producto cruz"),
        asegurar_finito(u[0] * v[1] - u[1] * v[0], "Producto cruz"),
    ]


def producto_cruz_con_pasos(v1, v2):
    """Calcula el producto cruz y comprueba su ortogonalidad a ambos vectores."""
    resultado = producto_cruz(v1, v2)
    valores_v1 = [asegurar_finito(valor, "Componente de V1") for valor in v1]
    valores_v2 = [asegurar_finito(valor, "Componente de V2") for valor in v2]
    ortogonal_v1 = producto_punto(resultado, valores_v1)
    ortogonal_v2 = producto_punto(resultado, valores_v2)
    escala_v1 = asegurar_finito(
        sum(abs(a * b) for a, b in zip(resultado, valores_v1)),
        "Escala de comprobación de ortogonalidad",
    )
    escala_v2 = asegurar_finito(
        sum(abs(a * b) for a, b in zip(resultado, valores_v2)),
        "Escala de comprobación de ortogonalidad",
    )
    comprobado = (
        abs(ortogonal_v1) <= EPSILON * escala_v1
        and abs(ortogonal_v2) <= EPSILON * escala_v2
    )
    escala_u, escala_v = escala_de(valores_v1), escala_de(valores_v2)
    determinantes = [
        f"({limpiar_numero(valores_v1[1], escala_u)}·{limpiar_numero(valores_v2[2], escala_v)} "
        f"− {limpiar_numero(valores_v1[2], escala_u)}·{limpiar_numero(valores_v2[1], escala_v)})",
        f"({limpiar_numero(valores_v1[2], escala_u)}·{limpiar_numero(valores_v2[0], escala_v)} "
        f"− {limpiar_numero(valores_v1[0], escala_u)}·{limpiar_numero(valores_v2[2], escala_v)})",
        f"({limpiar_numero(valores_v1[0], escala_u)}·{limpiar_numero(valores_v2[1], escala_v)} "
        f"− {limpiar_numero(valores_v1[1], escala_u)}·{limpiar_numero(valores_v2[0], escala_v)})",
    ]
    pasos = [
        "PASO 1. Aplicar la fórmula del producto cruz en R³:\n"
        f"V1 × V2 = ({', '.join(determinantes)}) = {vector_a_texto(resultado)}",
        "COMPROBACIÓN. El resultado debe ser ortogonal a V1 y V2:\n"
        f"(V1 × V2)·V1 = {limpiar_numero(ortogonal_v1, escala_v1)}; "
        f"(V1 × V2)·V2 = {limpiar_numero(ortogonal_v2, escala_v2)}.\n"
        + ("✓ Ambos productos punto son cero a la escala de los datos."
           if comprobado else "✗ La ortogonalidad no se comprobó."),
    ]
    return resultado, pasos


def norma_vector(vector):
    """Calcula la norma euclidiana de un vector mediante raíz cuadrada."""
    if not isinstance(vector, (list, tuple)) or not vector:
        raise ValueError("El vector no puede estar vacío.")
    suma_cuadrados = 0.0
    for indice, valor in enumerate(vector, 1):
        valor = asegurar_finito(valor, f"Componente {indice} del vector")
        suma_cuadrados = asegurar_finito(
            suma_cuadrados + valor * valor, "Suma de cuadrados del vector",
        )
    return asegurar_finito(suma_cuadrados ** 0.5, "Norma del vector")


def norma_vector_con_pasos(vector):
    """Calcula la norma y comprueba que su cuadrado sea la suma de cuadrados."""
    resultado = norma_vector(vector)
    valores = [
        asegurar_finito(valor, f"Componente {indice} del vector")
        for indice, valor in enumerate(vector, 1)
    ]
    cuadrados = [valor * valor for valor in valores]
    suma = sum(cuadrados)
    comprobado = abs(resultado * resultado - suma) <= EPSILON * max(abs(suma), resultado ** 2)
    escala = escala_de(cuadrados)
    pasos = [
        "PASO 1. Elevar al cuadrado cada componente:\n"
        + " + ".join(limpiar_numero(valor, escala) for valor in cuadrados),
        f"PASO 2. Tomar la raíz cuadrada: ||V|| = ({limpiar_numero(suma, escala)})**0.5 "
        f"= {limpiar_numero(resultado, escala_de([resultado]))}.",
        "COMPROBACIÓN. Elevar la norma al cuadrado debe recuperar la suma de cuadrados.\n"
        + ("✓ La comprobación es correcta." if comprobado else "✗ La comprobación no coincide."),
    ]
    return resultado, pasos


def vectores_linealmente_independientes_con_pasos(vectores):
    """Determina la independencia lineal de vectores comparando su rango."""
    if not isinstance(vectores, (list, tuple)) or not vectores:
        raise ValueError("Agrega al menos un vector para comprobar independencia lineal.")
    if not isinstance(vectores[0], (list, tuple)):
        raise ValueError("Cada elemento del conjunto debe ser un vector.")
    dimension = len(vectores[0])
    if dimension == 0:
        raise ValueError("Los vectores no pueden estar vacíos.")
    vectores_validados = []
    for indice, vector in enumerate(vectores, 1):
        if not isinstance(vector, (list, tuple)) or len(vector) != dimension:
            raise ValueError(
                f"El vector {indice} debe tener {dimension} componentes, igual que los demás."
            )
        vectores_validados.append([
            asegurar_finito(componente, f"Componente del vector {indice}")
            for componente in vector
        ])
    matriz = [
        [vector[fila] for vector in vectores_validados]
        for fila in range(dimension)
    ]
    rango, pasos_rango = rango_matriz_con_pasos(matriz)
    independientes = rango == len(vectores)
    pasos = [
        f"PASO 1. Colocar los {len(vectores)} vectores como columnas de una matriz."
    ]
    pasos.extend(f"RANGO · {paso}" for paso in pasos_rango)
    pasos.append(
        "COMPROBACIÓN. El conjunto es linealmente independiente si rango(A) "
        f"es igual al número de vectores: {rango} {'=' if independientes else '≠'} "
        f"{len(vectores)}.\n"
        + ("✓ El conjunto es linealmente independiente."
           if independientes else "✓ El conjunto es linealmente dependiente.")
    )
    return independientes, pasos


def vectores_linealmente_independientes(vectores):
    """Devuelve si un conjunto de vectores es linealmente independiente."""
    resultado, _ = vectores_linealmente_independientes_con_pasos(vectores)
    return resultado
