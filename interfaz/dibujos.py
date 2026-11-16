"""Qué se dibuja en el plano para vectores y sistemas 2×2 (sin Tk: se puede probar aparte).

Cada función devuelve un `Dibujo` con curvas, capas, puntos, el encuadre (x0, x1, y0, y1)
y una nota que explica lo que se ve.
"""

import math
from dataclasses import dataclass, field

from interfaz.estilos import PALETA
from interfaz.motorGrafica import Capa, PuntoGrafico
from nucleo.procedimientos_matrices import numero

COLOR_1 = PALETA["tangente"]
COLOR_2 = PALETA["semilla"]
COLOR_RESULTADO = PALETA["acento_hover"]


@dataclass
class Dibujo:
    capas: list = field(default_factory=list)
    puntos: list = field(default_factory=list)
    curvas: list = field(default_factory=list)   # (color, f(x), grosor)
    encuadre: tuple = (-3.0, 3.0, -2.0, 2.0)   # contenido; ver encuadre_proporcional
    nota: str = ""


def _encuadre(puntos, margen=0.0):
    """Rectángulo mínimo que contiene los puntos y el origen (la proporción la ajusta la ventana)."""
    xs = [0.0] + [p[0] for p in puntos]
    ys = [0.0] + [p[1] for p in puntos]
    return (min(xs), max(xs), min(ys), max(ys))


def encuadre_proporcional(encuadre, ancho_px, alto_px, margen=0.18):
    """Amplía el rectángulo al tamaño del lienzo con la misma escala en x e y (ángulos reales)."""
    x0, x1, y0, y1 = encuadre
    ancho, alto = x1 - x0, y1 - y0
    if max(ancho, alto) < 1e-9:      # solo el origen: se muestra una ventana pequeña alrededor
        ancho = alto = 2.0
    ancho, alto = max(ancho, 1e-9), max(alto, 1e-9)
    ancho_px, alto_px = max(ancho_px, 50), max(alto_px, 50)
    escala = min(ancho_px / (ancho * (1 + 2 * margen)), alto_px / (alto * (1 + 2 * margen)))
    mx, my = ancho_px / escala / 2, alto_px / escala / 2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return (cx - mx, cx + mx, cy - my, cy + my)


def _flecha(a, b, color, discontinua=False, ancho=2.2):
    return Capa("flecha", tuple(a), tuple(b), color, ancho=ancho, discontinua=discontinua)


def _punta(clave, v, etiqueta, color, descripcion):
    return PuntoGrafico(clave, v[0], v[1], "punto", color, etiqueta, descripcion)


def admite_plano_vectores(operacion, v1, v2):
    """Se dibuja solo en R² y para las operaciones que tienen una lectura geométrica."""
    if operacion not in ("V₁ + V₂", "V₁ − V₂", "k · V₁", "V₁ · V₂", "‖V₁‖"):
        return False
    usados = [v for v in (v1, v2 if operacion in ("V₁ + V₂", "V₁ − V₂", "V₁ · V₂") else None) if v is not None]
    return bool(usados) and all(len(v) == 2 for v in usados)


def dibujo_vectores(operacion, v1, v2=None, k=None):
    o = (0.0, 0.0)
    capas = [_flecha(o, v1, COLOR_1)]
    puntos = [_punta("v1", v1, f"V₁ ({numero(v1[0])}, {numero(v1[1])})", COLOR_1, "Vector V₁")]
    alcance = [v1]
    if operacion in ("V₁ + V₂", "V₁ − V₂", "V₁ · V₂"):
        capas.append(_flecha(o, v2, COLOR_2))
        puntos.append(_punta("v2", v2, f"V₂ ({numero(v2[0])}, {numero(v2[1])})", COLOR_2, "Vector V₂"))
        alcance.append(v2)
    if operacion == "V₁ + V₂":
        suma = (v1[0] + v2[0], v1[1] + v2[1])
        capas.append(_flecha(v1, suma, COLOR_2, discontinua=True, ancho=1.4))      # regla del paralelogramo
        capas.append(_flecha(v2, suma, COLOR_1, discontinua=True, ancho=1.4))
        capas.append(_flecha(o, suma, COLOR_RESULTADO, ancho=2.8))
        puntos.append(_punta("res", suma, f"V₁ + V₂ ({numero(suma[0])}, {numero(suma[1])})", COLOR_RESULTADO,
                             "Diagonal del paralelogramo"))
        alcance.append(suma)
        nota = "Regla del paralelogramo: la suma es la diagonal; V₂ se traslada al extremo de V₁."
    elif operacion == "V₁ − V₂":
        dif = (v1[0] - v2[0], v1[1] - v2[1])
        capas.append(_flecha(v2, v1, COLOR_RESULTADO, discontinua=True, ancho=1.8))
        capas.append(_flecha(o, dif, COLOR_RESULTADO, ancho=2.8))
        puntos.append(_punta("res", dif, f"V₁ − V₂ ({numero(dif[0])}, {numero(dif[1])})", COLOR_RESULTADO,
                             "Mismo vector que va del extremo de V₂ al de V₁"))
        alcance.append(dif)
        nota = "V₁ − V₂ va del extremo de V₂ al extremo de V₁ (línea punteada); se muestra también desde el origen."
    elif operacion == "k · V₁":
        kv = (k * v1[0], k * v1[1])
        capas.append(_flecha(o, kv, COLOR_RESULTADO, ancho=2.8))
        puntos.append(_punta("res", kv, f"k·V₁ ({numero(kv[0])}, {numero(kv[1])})", COLOR_RESULTADO,
                             "Vector escalado"))
        alcance.append(kv)
        nota = ("Misma dirección" if k > 0 else "Sentido contrario" if k < 0 else "Vector nulo") + \
            f"; la longitud se multiplica por |k| = {numero(abs(k))}."
    elif operacion == "‖V₁‖":
        nota = f"‖V₁‖ = √({numero(v1[0])}² + {numero(v1[1])}²) = {numero(math.hypot(*v1))}: longitud de la flecha."
    else:
        n1, n2 = math.hypot(*v1), math.hypot(*v2)
        if n1 and n2:
            cos = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
            nota = (f"V₁ · V₂ = ‖V₁‖‖V₂‖cos θ → θ = {numero(math.degrees(math.acos(cos)))}°"
                    + ("  (perpendiculares)" if abs(cos) < 1e-12 else ""))
        else:
            nota = "Con un vector nulo el ángulo no está definido."
    return Dibujo(capas=capas, puntos=puntos, encuadre=_encuadre(alcance), nota=nota)


# ---------------------------------------------------------------- sistemas 2×2
def admite_plano_sistema(A):
    return len(A) == 2 and len(A[0]) == 2


def _recta(a, b, c):
    """a·x + b·y = c como (función de x) o ('v', x) si es vertical."""
    if abs(b) > 1e-12:
        return lambda x: (c - a * x) / b
    return ("v", c / a) if abs(a) > 1e-12 else None


def dibujo_sistema(A, b, trayectoria=None):
    """Las dos rectas, su intersección y, si hay un método iterativo, el camino de las aproximaciones.

    trayectoria: [(k, (x₁, x₂))] con k = 0 para el valor inicial.
    """
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    curvas, capas, puntos, alcance = [], [], [], []
    for i, color in enumerate((COLOR_1, COLOR_2)):
        recta = _recta(A[i][0], A[i][1], b[i])
        if recta is None:
            continue
        if isinstance(recta, tuple):
            capas.append(Capa("vertical", (recta[1], 0), color=color, ancho=1.8))
            alcance.append((recta[1], 0.0))
        else:
            curvas.append((color, recta, 1.8))
    if abs(det) > 1e-12:
        x = (b[0] * A[1][1] - A[0][1] * b[1]) / det
        y = (A[0][0] * b[1] - b[0] * A[1][0]) / det
        puntos.append(PuntoGrafico("sol", x, y, "anillo", COLOR_RESULTADO,
                                   f"({numero(x)}, {numero(y)})", "Intersección: solución del sistema"))
        alcance.append((x, y))
        nota = "Cada ecuación es una recta; la solución es el punto donde se cortan."
    else:
        compatible = abs(A[0][0] * b[1] - A[1][0] * b[0]) < 1e-12 and abs(A[0][1] * b[1] - A[1][1] * b[0]) < 1e-12
        nota = ("Rectas coincidentes: infinitas soluciones." if compatible
                else "Rectas paralelas: el sistema no tiene solución.")
        alcance.append((1.0, 1.0))
    if trayectoria:
        previo = None
        for k, (x, y) in ((k, (v[0], v[1])) for k, v in trayectoria):
            if not (math.isfinite(x) and math.isfinite(y)) or max(abs(x), abs(y)) > 1e6:
                break
            if previo is not None:
                capas.append(Capa("segmento", previo, (x, y), PALETA["derivada"], ancho=1.2, discontinua=True))
            puntos.append(PuntoGrafico(f"k{k}", x, y, "punto", PALETA["semilla"], f"x⁽{k}⁾" if k < 5 else "",
                                       f"Iteración {k}: ({numero(x)}, {numero(y)})"))
            previo = (x, y)
            if k < 6:
                alcance.append((x, y))
        nota += " Los puntos amarillos son las aproximaciones sucesivas."
    return Dibujo(capas=capas, puntos=puntos, curvas=curvas, encuadre=_encuadre(alcance), nota=nota)
