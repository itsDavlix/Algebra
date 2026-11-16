"""Newton-Raphson y Secante para ecuaciones reales, sin bibliotecas externas."""

from dataclasses import dataclass
from typing import Optional

from nucleo.biseccion import MAX_ITERACIONES, _numero
from nucleo.expresiones import analizar, derivada_numerica
from nucleo.numeros import asegurar_finito

# Una aproximación cuya magnitud supera este límite se considera divergente.
LIMITE_DIVERGENCIA = 1e12


METODOS_ABIERTOS = ("Newton-Raphson", "Secante")


@dataclass(frozen=True)
class IteracionAbierta:
    numero: int
    anterior: Optional[float]
    actual: float
    valor_actual: float
    pendiente: float
    siguiente: float
    valor_siguiente: float
    error: float
    error_relativo: Optional[float] = None


@dataclass(frozen=True)
class ResultadoAbierto:
    metodo: str
    expresion: str
    tolerancia: float
    raiz: float
    valor_funcion: float
    error: Optional[float]
    iteraciones: tuple
    convergio: bool
    motivo: str
    derivada: str = ""
    derivada_automatica: bool = False
    advertencia: str = ""
    iniciales: tuple = ()


def resolver_metodo_abierto(ecuacion, metodo, x0, x1=None, derivada="",
                           tolerancia=1e-6, max_iteraciones=100):
    """Selecciona un método sin exigir un intervalo con cambio de signo.

    Newton requiere la expresión de f'(x); Secante, dos semillas distintas.
    La tolerancia absoluta se aplica al paso y al residuo: ambos deben ser
    pequeños. No representa una cota del error real ni garantiza convergencia.
    """
    if metodo not in METODOS_ABIERTOS:
        raise ValueError("Selecciona Newton-Raphson o Secante.")
    x0 = asegurar_finito(x0, "El valor inicial x0")
    tolerancia = asegurar_finito(tolerancia, "La tolerancia")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if type(max_iteraciones) is not int or not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}.")
    funcion = analizar(ecuacion)
    expresion = funcion.texto
    funcion_derivada = None
    texto_derivada = ""
    automatica = False
    advertencia = ""
    if metodo == "Newton-Raphson":
        if derivada is not None and not isinstance(derivada, str):
            raise ValueError("La derivada debe escribirse como texto, por ejemplo 3x^2 - 1.")
        if derivada and derivada.strip():
            funcion_derivada = analizar(derivada)
        else:
            # Derivada simbólica con las reglas del cálculo (nucleo.expresiones).
            funcion_derivada = funcion.derivada()
            automatica = True
        texto_derivada = funcion_derivada.texto
        if not automatica:
            advertencia = _comprobar_derivada(funcion, funcion_derivada, x0)
        iniciales = (x0,)
    else:
        x1 = asegurar_finito(x1, "El valor inicial x1")
        if x0 == x1:
            raise ValueError("Secante requiere valores iniciales x0 y x1 distintos.")
        iniciales = (x0, x1)

    pasos = []
    error = None

    def resultado(x, fx, convergio, motivo):
        return ResultadoAbierto(
            metodo, expresion, tolerancia, x, fx, error, tuple(pasos), convergio, motivo,
            texto_derivada, automatica, advertencia, iniciales,
        )

    actual, valor_actual = x0, funcion(x0)
    if valor_actual == 0:
        error = 0.0
        return resultado(actual, valor_actual, True, "x0 es una raíz en la precisión de cálculo.")
    anterior, valor_anterior = None, None
    if metodo == "Secante":
        anterior, valor_anterior = actual, valor_actual
        actual, valor_actual = x1, funcion(x1)
        if valor_actual == 0:
            error = 0.0
            return resultado(actual, valor_actual, True, "x1 es una raíz en la precisión de cálculo.")

    for numero in range(1, max_iteraciones + 1):
        if funcion_derivada is not None:
            pendiente = funcion_derivada(actual)
            if pendiente == 0:
                return resultado(actual, valor_actual, False,
                                 "La derivada es cero. Elige otro valor inicial.")
            desplazamiento = valor_actual / pendiente
        else:
            if valor_actual == valor_anterior:
                return resultado(actual, valor_actual, False,
                                 "f(x_n) y f(x_n−1) son iguales; el denominador de Secante es cero.")
            # Escala las evaluaciones para evitar desbordar al restarlas.
            escala = max(abs(valor_actual), abs(valor_anterior))
            diferencia = valor_actual / escala - valor_anterior / escala
            distancia = asegurar_finito(actual - anterior, "La distancia entre aproximaciones")
            if distancia == 0 or diferencia == 0:
                return resultado(actual, valor_actual, False,
                                 "Se agotó la precisión numérica para calcular la secante.")
            desplazamiento = (valor_actual / escala) / diferencia * distancia
            pendiente = asegurar_finito((diferencia / distancia) * escala, "La pendiente secante")
        siguiente = asegurar_finito(actual - desplazamiento, "La siguiente aproximación")
        valor_siguiente = funcion(siguiente)
        error = asegurar_finito(abs(siguiente - actual), "El error aproximado")
        error_relativo = None if siguiente == 0 else error / abs(siguiente) * 100
        pasos.append(IteracionAbierta(
            numero, anterior, actual, valor_actual, pendiente, siguiente, valor_siguiente,
            error, error_relativo,
        ))
        if valor_siguiente == 0:
            return resultado(siguiente, valor_siguiente, True, "f(x) = 0 en la precisión de cálculo.")
        if error <= tolerancia and abs(valor_siguiente) <= tolerancia:
            return resultado(siguiente, valor_siguiente, True,
                             "El paso y el residuo absoluto cumplen la tolerancia.")
        if siguiente == actual:
            return resultado(siguiente, valor_siguiente, False,
                             "La aproximación se estancó sin cumplir la tolerancia del residuo.")
        if abs(siguiente) > LIMITE_DIVERGENCIA * max(1.0, abs(x0)):
            return resultado(siguiente, valor_siguiente, False,
                             "Las aproximaciones crecen sin control: el método diverge desde "
                             "este valor inicial. Elige otro más cercano a la raíz.")
        desplazamiento = 1 if metodo == "Secante" else 0
        repetida = _iteracion_repetida(pasos, tolerancia)
        if repetida is not None:
            return resultado(siguiente, valor_siguiente, False,
                             f"Ciclo detectado: x{numero + desplazamiento} repite a "
                             f"x{repetida + desplazamiento} y el método "
                             "oscila sin acercarse a una raíz. Elige otro valor inicial.")
        anterior, valor_anterior = actual, valor_actual
        actual, valor_actual = siguiente, valor_siguiente

    return resultado(actual, valor_actual, False,
                     "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia.")


def _comprobar_derivada(funcion, derivada, x0):
    """Compara la derivada escrita con una diferencia centrada en x0."""
    try:
        escrita = derivada(x0)
        estimada = derivada_numerica(funcion, x0)
    except ValueError:
        return ""
    escala = max(1.0, abs(estimada))
    if abs(escrita - estimada) > 1e-4 * escala:
        return (f"La derivada escrita vale {escrita:.6g} en x0, pero la pendiente estimada de f "
                f"es {estimada:.6g}. Revisa f'(x) o deja el campo vacío para calcularla "
                "automáticamente.")
    return ""


def _iteracion_repetida(pasos, tolerancia):
    """Devuelve el índice de una aproximación anterior que vuelve a aparecer.

    Solo compara con puntos que no son el inmediato anterior: si el método
    converge, el último paso ya habría cumplido la tolerancia.
    """
    if len(pasos) < 2:
        return None
    ultimo = pasos[-1].siguiente
    candidatos = [(0, pasos[0].actual)] + [(p.numero, p.siguiente) for p in pasos[:-2]]
    for indice, valor in candidatos:
        if abs(ultimo - valor) <= max(tolerancia, 1e-12 * abs(valor)) and abs(pasos[-1].valor_siguiente) > tolerancia:
            return indice
    return None


def formatear_resultado_abierto(resultado):
    """Presenta primero la respuesta y después justifica cada aproximación."""
    n = lambda valor: f"{valor:.10g}"
    estado = "Convergencia alcanzada" if resultado.convergio else "Aproximación sin convergencia"
    error = "no disponible" if resultado.error is None else n(resultado.error)
    lineas = [
        "RESPUESTA · RAÍZ APROXIMADA" if resultado.convergio else "SIN CONVERGENCIA · ÚLTIMA APROXIMACIÓN",
        f"x ≈ {_numero(resultado.raiz)}",
        f"{estado} · Método: {resultado.metodo}",
        "", "COMPROBACIÓN",
        "Al sustituir la aproximación calculada (antes de redondear):",
        f"f(x) = {n(resultado.valor_funcion)}",
        f"Residuo |f(x)| = {n(abs(resultado.valor_funcion))}",
        "El residuo mide cuánto falta para que la ecuación valga cero; no es el error en x.",
        "", "EXPLICACIÓN · CRITERIO DE PARADA",
        f"Iteraciones: {len(resultado.iteraciones)}",
        f"Último cambio |x_nuevo − x_actual|: {error}",
        f"Tolerancia absoluta (paso y residuo): {n(resultado.tolerancia)}",
        f"Motivo: {resultado.motivo}",
        "Se detiene con éxito si f(x) vale cero en la precisión de cálculo, o si tanto el cambio "
        "en x como el residuo cumplen la tolerancia.",
        "El cambio entre aproximaciones no es una cota del error real en la raíz.",
        "", "DATOS DEL EJERCICIO", f"Método: {resultado.metodo}",
        f"Resolver f(x) = 0, donde f(x) = {resultado.expresion}",
        "", "FÓRMULA DEL MÉTODO",
        ("Newton: x_nuevo = x_actual − f(x_actual)/f'(x_actual)"
         if resultado.metodo == "Newton-Raphson" else
         "Secante: x_nuevo = x_actual − f(x_actual)(x_actual−x_anterior)"
         "/(f(x_actual)−f(x_anterior))"),
        ("Evaluamos la función y su derivada en el valor actual para obtener la siguiente aproximación."
         if resultado.metodo == "Newton-Raphson" else
         "Unimos los dos puntos anteriores con una recta; su corte con el eje x da la siguiente aproximación."),
        "", "EXPLICACIÓN PASO A PASO",
    ]
    if not resultado.convergio:
        lineas.insert(3, "Este valor todavía no se acepta como raíz.")
    if not resultado.iteraciones:
        lineas.append("No se realizaron iteraciones. " + resultado.motivo)
    for paso in resultado.iteraciones:
        lineas.extend(["", f"ITERACIÓN {paso.numero}"])
        if paso.anterior is not None and resultado.metodo == "Secante":
            lineas.append(f"Tomamos x_anterior = {n(paso.anterior)} y x_actual = {n(paso.actual)}.")
        else:
            lineas.append(f"Partimos de x_actual = {n(paso.actual)}.")
        pendiente = "Derivada f'(x_actual)" if resultado.metodo == "Newton-Raphson" else "Pendiente de la recta secante"
        lineas.extend([
            f"1. Evaluamos: f({n(paso.actual)}) = {n(paso.valor_actual)}.",
            f"   {pendiente} = {n(paso.pendiente)}.",
            "2. Sustituimos en x_nuevo = x_actual − f(x_actual)/pendiente:",
            f"   x_nuevo ≈ ({n(paso.actual)}) − ({n(paso.valor_actual)})/({n(paso.pendiente)})",
            f"   x_nuevo ≈ {n(paso.siguiente)}",
            f"3. Comprobamos: f(x_nuevo) = {n(paso.valor_siguiente)}.",
            f"   Cambio absoluto = |({n(paso.siguiente)}) − ({n(paso.actual)})| ≈ {n(paso.error)}.",
            ("4. Parada: " + resultado.motivo if paso.numero == len(resultado.iteraciones)
             else "4. Continuamos: todavía no se cumplen los criterios de parada."),
        ])
    lineas.extend(["", "Los valores mostrados están redondeados; los cálculos conservan la precisión de coma flotante."])
    return "\n".join(lineas)
