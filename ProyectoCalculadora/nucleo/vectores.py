"""Módulo de vectores: lectura, formato y operaciones algebraicas en R^n."""

import re

from nucleo.numeros import convertir_numero, limpiar_numero, asegurar_finito

MAX_COMPONENTES = 200


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
    return "(" + ", ".join(limpiar_numero(x) for x in vector) + ")"


def _validar_misma_dimension(v1, v2):
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
