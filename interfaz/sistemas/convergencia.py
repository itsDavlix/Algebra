"""Gráfica de convergencia de Jacobi y Gauss-Seidel sobre el plano cartesiano.

Dos modos, como en la presentación:
- «componentes»: evolución de cada xᵢ⁽ᵏ⁾ frente a k.
- «error»: log₁₀ ‖x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾‖∞ frente a k (comparación de convergencia).
"""

import math

from interfaz.estilos import PALETA
from interfaz.motorGrafica import Capa, PuntoGrafico
from nucleo.sistemas_texto import nombre_bonito

COLORES = ("curva", "tangente", "semilla", "maximo", "minimo", "inflexion", "acento_hover", "exito")
COLOR_METODO = {"Jacobi": "semilla", "Gauss-Seidel": "tangente"}


def _poligonal(puntos, color, ancho=1.6):
    return [Capa("segmento", p, q, color, ancho=ancho) for p, q in zip(puntos, puntos[1:])]


def capas_componentes(resultado):
    """Una poligonal por incógnita: (k, xᵢ⁽ᵏ⁾)."""
    capas, puntos, limites = [], [], []
    trayectoria = [resultado.x0] + [paso.x for paso in resultado.iteraciones]
    for i, nombre in enumerate(resultado.variables):
        color = PALETA[COLORES[i % len(COLORES)]]
        serie = [(k, x[i]) for k, x in enumerate(trayectoria) if math.isfinite(x[i]) and abs(x[i]) < 1e9]
        capas += _poligonal(serie, color)
        if serie:
            k, valor = serie[-1]
            puntos.append(PuntoGrafico(f"c{i}", k, valor, "punto", color, nombre_bonito(nombre),
                                       f"{nombre_bonito(nombre)} en k = {k}"))
        limites += serie
    return capas, puntos, limites


def capas_error(resultados):
    """log₁₀ del cambio entre iteraciones para uno o dos métodos."""
    capas, puntos, limites = [], [], []
    for metodo, resultado in resultados.items():
        color = PALETA[COLOR_METODO.get(metodo, "curva")]
        serie = [(paso.k, math.log10(paso.cambio)) for paso in resultado.iteraciones
                 if 0 < paso.cambio < math.inf]
        capas += _poligonal(serie, color)
        if serie:
            k, valor = serie[-1]
            puntos.append(PuntoGrafico(f"e{metodo}", k, valor, "punto", color, metodo,
                                       f"{metodo}: log₁₀‖Δx‖ = {valor:.2f} en k = {k}"))
        limites += serie
    if resultados:
        tolerancia = next(iter(resultados.values())).tolerancia
        nivel = math.log10(tolerancia)
        kmax = max((p[0] for p in limites), default=1)
        capas.append(Capa("segmento", (0, nivel), (kmax, nivel), PALETA["error"], discontinua=True))
        capas.append(Capa("texto", (kmax, nivel), texto="log₁₀ ε", color=PALETA["error"],
                          opciones={"dx": -4, "dy": -4, "anchor": "se"}))
        limites.append((0, nivel))
    return capas, puntos, limites


def encuadre(limites):
    if not limites:
        return -0.5, 5, -1, 1
    xs = [p[0] for p in limites] + [0]
    ys = [p[1] for p in limites]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    alto = max(y1 - y0, 1e-6)
    # Margen derecho amplio: las etiquetas de método van al final de cada curva.
    return x0 - 0.6, x1 + max(2, (x1 - x0) * 0.22), y0 - alto * 0.15, y1 + alto * 0.15
