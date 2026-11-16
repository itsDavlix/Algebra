"""Datos de los cuatro métodos de raíces: parámetros, descripciones y estilos de puntos."""

CONFIGURACION = {
    "Bisección": dict(
        parametros=(("a", "a", "El extremo a"), ("b", "b", "El extremo b")),
        titulo_parametros="② INTERVALO [a, b]",
        descripcion="Método cerrado: divide [a, b] a la mitad y conserva la mitad con cambio de signo.",
        ejemplo=("x^3 - x - 2", {"a": "1", "b": "2"}),
    ),
    "Regula Falsi": dict(
        parametros=(("a", "a", "El extremo a"), ("b", "b", "El extremo b")),
        titulo_parametros="② INTERVALO [a, b]",
        descripcion="Método cerrado: une (a, f(a)) y (b, f(b)) con una recta y toma su corte con el eje x.",
        ejemplo=("x^3 - x - 2", {"a": "1", "b": "2"}),
    ),
    "Newton-Raphson": dict(
        parametros=(("x0", "x₀", "El valor inicial x₀"),),
        titulo_parametros="② VALOR INICIAL x₀",
        descripcion="Método abierto: sigue la tangente en cada punto hasta cortar el eje x.",
        ejemplo=("x^3 - x - 2", {"x0": "2"}),
    ),
    "Secante": dict(
        parametros=(("x0", "x₀", "El valor inicial x₀"), ("x1", "x₁", "El valor inicial x₁")),
        titulo_parametros="② VALORES INICIALES x₀, x₁",
        descripcion="Método abierto: aproxima la tangente con la recta que pasa por los dos últimos puntos.",
        ejemplo=("x^3 - x - 2", {"x0": "2", "x1": "1"}),
    ),
}

NOMBRE_PARAMETRO = {"a": "a", "b": "b", "x0": "x₀", "x1": "x₁"}

# Forma y color de cada tipo de punto notable en la gráfica.
ESTILO_PUNTO = {
    "raiz": ("anillo", "raiz"), "maximo": ("rombo", "maximo"), "minimo": ("rombo", "minimo"),
    "inflexion": ("cruz", "inflexion"), "corte_y": ("cuadrado", "inflexion"),
}
ETIQUETA_CORTA = {"raiz": "raíz", "maximo": "máx.", "minimo": "mín.", "inflexion": "infl.", "corte_y": "corte y"}


def evaluar(funcion, x):
    """f(x) o None si x está fuera del dominio."""
    try:
        return funcion(x)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
