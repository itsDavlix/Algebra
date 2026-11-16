"""Lo que cada método dibuja en el plano: valores iniciales, iteraciones y resultado."""

import math

from interfaz.estilos import PALETA, mezclar
from interfaz.motorGrafica import Capa, PuntoGrafico
from interfaz.raices.configuracion import evaluar
from nucleo import procedimientos

CERRADOS = ("Bisección", "Regula Falsi")


def capas_previas(metodo, funcion, valores):
    """Valores iniciales antes de resolver: intervalo sombreado o rectas verticales en x₀, x₁."""
    capas = []
    semilla = PALETA["semilla"]
    if metodo in CERRADOS and {"a", "b"} <= valores.keys():
        a, b = valores["a"], valores["b"]
        if a < b:
            capas.append(Capa("banda", (a, 0), (b, 0), PALETA["intervalo"]))
            capas.append(Capa("texto", (a, 0), texto="a", color=semilla,
                              opciones={"dx": -10, "arriba": True, "anchor": "ne"}))
            capas.append(Capa("texto", (b, 0), texto="b", color=semilla,
                              opciones={"dx": 4, "arriba": True, "anchor": "nw"}))
            if metodo == "Regula Falsi" and funcion is not None:
                fa, fb = evaluar(funcion, a), evaluar(funcion, b)
                if fa is not None and fb is not None:
                    capas.append(Capa("segmento", (a, fa), (b, fb), PALETA["tangente"], discontinua=True))
        return capas
    for clave in ("x0", "x1"):
        if clave in valores:
            x = valores[clave]
            capas.append(Capa("vertical", (x, 0), color=mezclar(semilla, PALETA["plano"], 0.5), discontinua=True))
            capas.append(Capa("texto", (x, 0), texto="x₀" if clave == "x0" else "x₁", color=semilla,
                              opciones={"dx": 5, "arriba": True, "anchor": "nw"}))
    return capas


def puntos_relevantes(metodo, resultado, funcion):
    """Puntos que deben verse tras resolver: inicio del método y raíz."""
    puntos = [(resultado.raiz, 0.0)]
    if metodo in CERRADOS:
        for x in resultado.intervalo_inicial:
            y = evaluar(funcion, x)
            puntos.append((x, y if y is not None else 0.0))
    else:
        for x in resultado.iniciales:
            y = evaluar(funcion, x)
            puntos.append((x, y if y is not None else 0.0))
        for paso in resultado.iteraciones[:3]:
            puntos.append((paso.actual, paso.valor_actual))
    return [(x, y) for x, y in puntos if math.isfinite(x) and math.isfinite(y)]


def puntos_del_metodo(metodo, resultado):
    """Aproximaciones numeradas y la raíz (o el último valor sin convergencia)."""
    puntos = []
    semilla = PALETA["semilla"]
    sub = procedimientos.sub
    if metodo in CERRADOS:
        for indice, paso in enumerate(resultado.iteraciones):
            etiqueta = f"c{sub(paso.numero)}" if indice < 6 else ""
            puntos.append(PuntoGrafico(f"i{indice}", paso.c, 0.0, "punto", semilla, etiqueta,
                                       f"Iteración {paso.numero}: c"))
    else:
        desplazamiento = 1 if metodo == "Secante" else 0
        for indice, x in enumerate(resultado.iniciales):
            puntos.append(PuntoGrafico(f"s{indice}", x, 0.0, "punto", semilla, f"x{sub(indice)}", "Valor inicial"))
        for indice, paso in enumerate(resultado.iteraciones):
            numero = paso.numero + desplazamiento
            etiqueta = f"x{sub(numero)}" if numero < 6 else ""
            puntos.append(PuntoGrafico(f"i{indice}", paso.siguiente, 0.0, "punto", semilla, etiqueta,
                                       f"Iteración {paso.numero}: x{sub(numero)}"))
    color = PALETA["exito"] if resultado.convergio else PALETA["error"]
    etiqueta = f"x* ≈ {resultado.raiz:.8g}" if resultado.convergio else "sin convergencia"
    y = 0.0 if resultado.convergio else resultado.valor_funcion
    puntos.append(PuntoGrafico("sol", resultado.raiz, y, "anillo", color, etiqueta, "Resultado del método"))
    return puntos


def capas_resultado(metodo, resultado, funcion, elegido=None):
    """Intervalo y secante (cerrados) o tangentes/secantes (abiertos); resalta la iteración elegida."""
    if resultado is None:
        return []
    pasos = resultado.iteraciones
    if metodo in CERRADOS:
        indice = elegido if elegido is not None else (len(pasos) - 1 if pasos else None)
        if indice is None:
            return []
        paso = pasos[indice]
        guia = mezclar(PALETA["semilla"], PALETA["plano"], 0.6)
        capas = [
            Capa("banda", (paso.a, 0), (paso.b, 0), PALETA["intervalo"], opciones={"opacidad": 0.16}),
            Capa("segmento", (paso.a, 0), (paso.a, paso.fa), guia, discontinua=True),
            Capa("segmento", (paso.b, 0), (paso.b, paso.fb), guia, discontinua=True),
        ]
        if metodo == "Regula Falsi":
            capas.append(Capa("segmento", (paso.a, paso.fa), (paso.b, paso.fb), PALETA["tangente"], ancho=1.4))
        capas += [
            Capa("segmento", (paso.c, 0), (paso.c, paso.fc), PALETA["tangente"], discontinua=True),
            Capa("texto", (paso.a, 0), texto="a", color=PALETA["semilla"], opciones={"dx": -6, "arriba": True, "anchor": "ne"}),
            Capa("texto", (paso.b, 0), texto="b", color=PALETA["semilla"], opciones={"dx": 6, "arriba": True, "anchor": "nw"}),
        ]
        return capas
    capas = []
    tenue = mezclar(PALETA["tangente"], PALETA["plano"], 0.35)
    for indice, paso in enumerate(pasos):
        enfocado = elegido is not None and indice == elegido
        color = PALETA["tangente"] if (elegido is None or enfocado) else tenue
        ancho = 1.6 if enfocado else 1.0
        if metodo == "Newton-Raphson":
            capas.append(Capa("segmento", (paso.actual, 0), (paso.actual, paso.valor_actual),
                              mezclar(color, PALETA["plano"], 0.5), discontinua=True))
            capas.append(Capa("segmento", (paso.actual, paso.valor_actual), (paso.siguiente, 0), color,
                              ancho=ancho, discontinua=not enfocado))
        else:
            fa = evaluar(funcion, paso.anterior) if funcion else None
            if fa is None:
                continue
            capas.append(Capa("segmento", (paso.anterior, fa), (paso.siguiente, 0), color, ancho=ancho,
                              discontinua=not enfocado))
            capas.append(Capa("segmento", (paso.actual, 0), (paso.actual, paso.valor_actual),
                              mezclar(color, PALETA["plano"], 0.5), discontinua=True))
    return capas
