"""Conversión y operaciones aritméticas con números romanos."""

import re


_PARES_ROMANOS = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)

_VALORES = {simbolo: valor for valor, simbolo in _PARES_ROMANOS if len(simbolo) == 1}
_PATRON_ROMANO = re.compile(
    r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
)


def entero_a_romano(numero):
    """Convierte un entero entre 1 y 3999 a notación romana canónica."""
    if isinstance(numero, bool) or not isinstance(numero, int):
        raise ValueError("El valor para convertir a romano debe ser un número entero.")
    if not 1 <= numero <= 3999:
        raise ValueError("Los números romanos admitidos van de 1 a 3999.")

    restante = numero
    partes = []
    for valor, simbolo in _PARES_ROMANOS:
        cantidad, restante = divmod(restante, valor)
        if cantidad:
            partes.append(simbolo * cantidad)
    return "".join(partes)


def romano_a_entero(texto):
    """Valida y convierte un número romano canónico a entero."""
    romano = texto.strip().upper()
    if not romano:
        raise ValueError("Escribe un número romano.")
    if not _PATRON_ROMANO.fullmatch(romano):
        raise ValueError(
            f"{texto!r} no es un número romano válido. Usa la forma estándar, por ejemplo: IV, IX, XIV o MCMXC."
        )

    total = 0
    anterior = 0
    for simbolo in reversed(romano):
        valor = _VALORES[simbolo]
        if valor < anterior:
            total -= valor
        else:
            total += valor
            anterior = valor
    return total


def pasos_romano_a_entero(texto):
    """Devuelve el entero y una explicación símbolo por símbolo de la conversión."""
    romano = texto.strip().upper()
    total = romano_a_entero(romano)
    terminos = []
    i = 0
    while i < len(romano):
        actual = _VALORES[romano[i]]
        if i + 1 < len(romano) and actual < _VALORES[romano[i + 1]]:
            siguiente = _VALORES[romano[i + 1]]
            valor = siguiente - actual
            terminos.append(f"{romano[i]}{romano[i + 1]} = {siguiente} - {actual} = {valor}")
            i += 2
        else:
            terminos.append(f"{romano[i]} = {actual}")
            i += 1
    return total, terminos


def pasos_entero_a_romano(numero):
    """Devuelve el romano y la descomposición usada para construirlo."""
    romano = entero_a_romano(numero)
    restante = numero
    partes = []
    for valor, simbolo in _PARES_ROMANOS:
        cantidad, nuevo_restante = divmod(restante, valor)
        if cantidad:
            for _ in range(cantidad):
                partes.append(f"{valor} → {simbolo}")
            restante = nuevo_restante
    return romano, partes


def operar_romanos(romano_a, romano_b, operacion):
    """Opera dos números romanos y retorna (resultado_romano, resultado_entero)."""
    a = romano_a_entero(romano_a)
    b = romano_a_entero(romano_b)

    if operacion == "+":
        resultado = a + b
    elif operacion == "-":
        resultado = a - b
    elif operacion == "*":
        resultado = a * b
    elif operacion == "/":
        if b == 0:
            raise ValueError("No se puede dividir entre cero.")
        if a % b != 0:
            raise ValueError(
                "La división no da un entero exacto. Esta calculadora solo representa resultados romanos enteros."
            )
        resultado = a // b
    else:
        raise ValueError("Operación romana no reconocida.")

    if resultado <= 0:
        raise ValueError("El resultado debe ser mayor que cero para representarse con números romanos.")
    if resultado > 3999:
        raise ValueError("El resultado supera 3999, límite de la notación romana admitida.")

    return entero_a_romano(resultado), resultado


def operar_romanos_con_pasos(romano_a, romano_b, operacion):
    """Realiza la operación romana y genera un procedimiento legible."""
    a, pasos_a = pasos_romano_a_entero(romano_a)
    b, pasos_b = pasos_romano_a_entero(romano_b)
    resultado_romano, resultado = operar_romanos(romano_a, romano_b, operacion)
    _, pasos_resultado = pasos_entero_a_romano(resultado)

    visible = {"*": "×", "/": "÷"}.get(operacion, operacion)
    pasos = [
        "PASO 1. Convertir A a decimal:\n"
        + "\n".join(f"  • {x}" for x in pasos_a)
        + f"\nA = {romano_a.strip().upper()} = {a}",
        "PASO 2. Convertir B a decimal:\n"
        + "\n".join(f"  • {x}" for x in pasos_b)
        + f"\nB = {romano_b.strip().upper()} = {b}",
        f"PASO 3. Realizar la operación en decimal:\n{a} {visible} {b} = {resultado}",
        "PASO 4. Convertir el resultado decimal nuevamente a romano:\n"
        + "\n".join(f"  • {x}" for x in pasos_resultado)
        + f"\nResultado: {resultado} = {resultado_romano}",
    ]
    return resultado_romano, resultado, pasos
