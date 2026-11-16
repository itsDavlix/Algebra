"""Plano cartesiano interactivo sobre tkinter.Canvas, sin bibliotecas externas.

- Marcas «bonitas» (1, 2, 5 × 10ⁿ) con cuadrícula mayor y menor.
- Zoom con la rueda centrado en el cursor (Shift: solo x; Ctrl/⌘: solo y),
  arrastre para mover, vista estándar y modo expandido.
- Curva muestreada por píxel; el trazo se corta fuera del dominio y en polos.
- Capas del método (bandas, segmentos, puntos) y puntos seleccionables con
  lectura de coordenadas.
"""

import math
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk

from interfaz.estilos import PALETA, fuente, mezclar, muescas_rueda


@dataclass
class PuntoGrafico:
    """Punto seleccionable: forma 'anillo', 'rombo', 'cuadrado', 'punto' o 'cruz'."""

    clave: str
    x: float
    y: float
    forma: str
    color: str
    etiqueta: str = ""
    descripcion: str = ""


@dataclass
class Capa:
    """Elemento dibujado por un método.

    tipo: 'banda' (x0..x1 sombreado), 'segmento' (p→q), 'vertical' (x),
    'texto' (en p). Las coordenadas son del plano, no de la pantalla.
    """

    tipo: str
    p: tuple = (0.0, 0.0)
    q: tuple = (0.0, 0.0)
    color: str = ""
    ancho: float = 1.0
    discontinua: bool = False
    texto: str = ""
    opciones: dict = field(default_factory=dict)


def paso_bonito(rango):
    """Redondea un paso a 1, 2 o 5 × 10ⁿ."""
    if rango <= 0 or not math.isfinite(rango):
        return 1.0
    base = 10 ** math.floor(math.log10(rango))
    mantisa = rango / base
    factor = 1 if mantisa < 1.5 else 2 if mantisa < 3.5 else 5 if mantisa < 7.5 else 10
    return factor * base


def formatear_marca(valor, paso):
    decimales = max(0, -math.floor(math.log10(paso) + 1e-9))
    if abs(valor) >= 1e6 or (valor != 0 and abs(valor) < 1e-4):
        texto = f"{valor:.3g}"
    else:
        texto = f"{valor:.{decimales}f}"
    if texto in ("-0", "-0.0"):
        texto = "0"
    return texto.replace("-", "−")


class PlanoCartesiano(tk.Canvas):
    """Lienzo con vista (x0, x1, y0, y1) y redibujado por demanda."""

    ZOOM_BOTON = 1.4

    def __init__(self, padre, al_seleccionar=None, al_cambiar_vista=None, al_expandir=None,
                 al_clic=None, **kwargs):
        super().__init__(padre, background=PALETA["plano"], highlightthickness=1,
                         highlightbackground=PALETA["borde"], cursor="fleur", **kwargs)
        self.colores_propios = True
        self.al_seleccionar = al_seleccionar
        self.al_cambiar_vista = al_cambiar_vista
        self.al_expandir = al_expandir
        self.al_clic = al_clic  # clic sin arrastre en una zona vacía: recibe (x, y) del plano
        self.vista = (-10.0, 10.0, -6.0, 6.0)
        self.vista_estandar = self.vista
        self.funcion = None
        self.curvas_extra = []
        self.capas = []
        self.puntos = []
        self.seleccionado = None
        self.resaltado = None
        self.expandido = False
        self.ajuste_automatico = True
        self._ocupado = []
        self._arrastre = None
        self._pendiente = None
        self._aviso_vista = None
        self._tam = (1, 1)
        self._construir_controles()
        self.bind("<Configure>", self._al_redimensionar)
        self.bind("<ButtonPress-1>", self._presionar)
        self.bind("<B1-Motion>", self._arrastrar)
        self.bind("<ButtonRelease-1>", self._soltar)
        self.bind("<Motion>", self._mover)
        self.bind("<Leave>", self._salir)
        self.bind("<MouseWheel>", self._rueda)
        self.bind("<Button-4>", lambda e: self._rueda(e, 120))
        self.bind("<Button-5>", lambda e: self._rueda(e, -120))
        self.bind("<Double-Button-1>", lambda e: self.vista_inicial())

    # ------------------------------------------------------------------ API
    def definir_funcion(self, funcion, curvas_extra=()):
        self.funcion = funcion
        self.curvas_extra = list(curvas_extra)
        self.programar_dibujo()

    def definir_capas(self, capas):
        self.capas = list(capas)
        self.programar_dibujo()

    def definir_puntos(self, puntos):
        self.puntos = list(puntos)
        claves = {p.clave for p in self.puntos}
        if self.seleccionado not in claves:
            self.seleccionado = None
        self.programar_dibujo()

    def seleccionar(self, clave, centrar=False):
        self.seleccionado = clave
        punto = self._punto(clave)
        if punto and centrar:
            x0, x1, y0, y1 = self.vista
            visible = x0 < punto.x < x1 and y0 < punto.y < y1
            if not visible:
                ancho, alto = x1 - x0, y1 - y0
                self.vista = (punto.x - ancho / 2, punto.x + ancho / 2, punto.y - alto / 2, punto.y + alto / 2)
                self._vista_cambiada()
        self.programar_dibujo()

    def encuadrar(self, x0, x1, y0, y1, como_estandar=True):
        if not all(math.isfinite(v) for v in (x0, x1, y0, y1)) or x1 <= x0 or y1 <= y0:
            return
        self.vista = (x0, x1, y0, y1)
        if como_estandar:
            self.vista_estandar = self.vista
        self.ajuste_automatico = True
        self._vista_cambiada()
        self.programar_dibujo()

    def vista_inicial(self):
        self.encuadrar(*self.vista_estandar, como_estandar=False)

    def zoom(self, factor, px=None, py=None, eje="ambos"):
        ancho, alto = self._tam
        px = ancho / 2 if px is None else px
        py = alto / 2 if py is None else py
        cx, cy = self.a_plano(px, py)
        x0, x1, y0, y1 = self.vista
        fx = factor if eje in ("ambos", "x") else 1
        fy = factor if eje in ("ambos", "y") else 1
        nueva = (cx + (x0 - cx) * fx, cx + (x1 - cx) * fx, cy + (y0 - cy) * fy, cy + (y1 - cy) * fy)
        if (nueva[1] - nueva[0]) < 1e-12 or (nueva[1] - nueva[0]) > 1e12:
            return
        if (nueva[3] - nueva[2]) < 1e-12 or (nueva[3] - nueva[2]) > 1e12:
            return
        self.vista = nueva
        self.ajuste_automatico = False
        self._vista_cambiada()
        self.programar_dibujo()

    # ------------------------------------------------------ transformaciones
    def a_pantalla(self, x, y):
        ancho, alto = self._tam
        x0, x1, y0, y1 = self.vista
        return (x - x0) / (x1 - x0) * ancho, alto - (y - y0) / (y1 - y0) * alto

    def a_plano(self, px, py):
        ancho, alto = self._tam
        x0, x1, y0, y1 = self.vista
        return x0 + px / ancho * (x1 - x0), y0 + (alto - py) / alto * (y1 - y0)

    # -------------------------------------------------------------- dibujo
    def programar_dibujo(self):
        if self._pendiente is None:
            self._pendiente = self.after_idle(self.dibujar)

    def dibujar(self):
        self._pendiente = None
        self.delete("all")
        self._ocupado = []
        ancho, alto = self._tam
        if ancho < 4 or alto < 4:
            return
        self._dibujar_cuadricula()
        for capa in self.capas:
            if capa.tipo == "banda":
                self._dibujar_capa(capa)
        self._dibujar_ejes()
        for color, funcion, grosor in self.curvas_extra:
            self._dibujar_curva(funcion, color, grosor)
        if self.funcion is not None:
            self._dibujar_curva(self.funcion, PALETA["curva"], 1.6)
        for capa in self.capas:
            if capa.tipo != "banda":
                self._dibujar_capa(capa)
        destacados = [self._punto(c) for c in (self.resaltado, self.seleccionado) if self._punto(c)]
        for punto in self.puntos:
            if punto not in destacados:
                self._dibujar_punto(punto, False)
        for punto in destacados:
            self._dibujar_punto(punto, True)
        # Etiquetas por prioridad; las que chocan con otras se omiten.
        prioridad = destacados[::-1] + [p for p in self.puntos if p.clave == "sol"] + \
            [p for p in self.puntos if p not in destacados and p.clave != "sol"]
        vistos = set()
        for punto in prioridad:
            if punto.etiqueta and punto.clave not in vistos:
                vistos.add(punto.clave)
                self._dibujar_etiqueta(punto, punto in destacados)

    def _marcas(self, inicio, fin, paso):
        primero = math.ceil(inicio / paso)
        ultimo = math.floor(fin / paso)
        if ultimo - primero > 2000:
            return []
        return [k * paso for k in range(primero, ultimo + 1)]

    def _pasos(self):
        ancho, alto = self._tam
        x0, x1, y0, y1 = self.vista
        paso_x = paso_bonito((x1 - x0) / max(2, ancho / 90))
        paso_y = paso_bonito((y1 - y0) / max(2, alto / 60))
        return paso_x, paso_y

    @staticmethod
    def _subdivisiones(paso):
        mantisa = round(paso / 10 ** math.floor(math.log10(paso)))
        return 4 if mantisa == 2 else 5

    def _dibujar_cuadricula(self):
        ancho, alto = self._tam
        x0, x1, y0, y1 = self.vista
        paso_x, paso_y = self._pasos()
        for paso, color in ((None, PALETA["rejilla_menor"]), (1, PALETA["rejilla_mayor"])):
            px_paso = paso_x if paso else paso_x / self._subdivisiones(paso_x)
            py_paso = paso_y if paso else paso_y / self._subdivisiones(paso_y)
            for x in self._marcas(x0, x1, px_paso):
                sx = round(self.a_pantalla(x, 0)[0]) + 0.5
                self.create_line(sx, 0, sx, alto, fill=color)
            for y in self._marcas(y0, y1, py_paso):
                sy = round(self.a_pantalla(0, y)[1]) + 0.5
                self.create_line(0, sy, ancho, sy, fill=color)

    def _texto_con_fondo(self, x, y, texto, color, anchor, tamano=9, mono=True, cursiva=False,
                         evitar=False):
        """Texto con fondo del plano. Con evitar=True no se dibuja si choca con otro."""
        estilo = ("Times", tamano + 3, "italic") if cursiva else fuente(tamano, mono=mono)
        item = self.create_text(x, y, text=texto, fill=color, anchor=anchor, font=estilo)
        caja = self.bbox(item)
        if caja and evitar and any(self._choca(caja, otra) for otra in self._ocupado):
            self.delete(item)
            return None
        if caja:
            self._ocupado.append(caja)
            fondo = self.create_rectangle(caja[0] - 2, caja[1] - 1, caja[2] + 2, caja[3] + 1,
                                          fill=PALETA["plano"], outline="")
            self.tag_lower(fondo, item)
        return item

    @staticmethod
    def _choca(a, b, margen=2):
        return not (a[2] + margen < b[0] or b[2] + margen < a[0] or a[3] + margen < b[1] or b[3] + margen < a[1])

    def _dibujar_ejes(self):
        ancho, alto = self._tam
        x0, x1, y0, y1 = self.vista
        ox, oy = self.a_pantalla(0, 0)
        eje_y_visible, eje_x_visible = 0 <= ox <= ancho, 0 <= oy <= alto
        color = PALETA["ejes"]
        if eje_x_visible:
            self.create_line(0, oy, ancho - 2, oy, fill=color, width=1.2, arrow="last",
                             arrowshape=(9, 10, 4))
            self._texto_con_fondo(ancho - 8, oy + 8, "x", color, "ne", cursiva=True)
        if eje_y_visible:
            self.create_line(ox, alto, ox, 2, fill=color, width=1.2, arrow="last", arrowshape=(9, 10, 4))
            self._texto_con_fondo(ox + 9, 6, "y", color, "nw", cursiva=True)
        paso_x, paso_y = self._pasos()
        # Las cifras se pegan al borde cuando el eje sale de la vista.
        fila = min(max(oy + 5, 4), alto - 18)
        columna = min(max(ox - 6, 36), ancho - 6)
        suave = PALETA["texto_suave"]
        for x in self._marcas(x0, x1, paso_x):
            if abs(x) < paso_x / 2:
                continue
            sx = self.a_pantalla(x, 0)[0]
            if 16 < sx < ancho - 30:
                if eje_x_visible:
                    self.create_line(sx, oy - 3, sx, oy + 3, fill=color)
                self._texto_con_fondo(sx, fila, formatear_marca(x, paso_x), suave, "n")
        for y in self._marcas(y0, y1, paso_y):
            if abs(y) < paso_y / 2:
                continue
            sy = self.a_pantalla(0, y)[1]
            if 18 < sy < alto - 20:
                if eje_y_visible:
                    self.create_line(ox - 3, sy, ox + 3, sy, fill=color)
                self._texto_con_fondo(columna, sy, formatear_marca(y, paso_y), suave, "e")
        if eje_x_visible and eje_y_visible:
            self._texto_con_fondo(ox - 5, oy + 5, "0", suave, "ne")

    def _evaluar(self, funcion, x):
        try:
            y = funcion(x)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        return y if y is not None and math.isfinite(y) else None

    def _dibujar_curva(self, funcion, color, grosor):
        ancho, alto = self._tam
        limite = alto * 8
        tramo = []
        anterior = None
        paso = 0.75
        px = 0.0
        while px <= ancho + paso:
            x, _ = self.a_plano(px, 0)
            y = self._evaluar(funcion, x)
            if y is None:
                self._trazar(tramo, color, grosor)
                tramo, anterior = [], None
            else:
                sy = self.a_pantalla(x, y)[1]
                if anterior is not None and abs(sy - anterior[1]) > alto:
                    # Salto grande: ¿polo o pendiente pronunciada? Se mira el punto medio.
                    xm, _ = self.a_plano(px - paso / 2, 0)
                    ym = self._evaluar(funcion, xm)
                    y_ant = self.a_plano(0, anterior[1])[1]
                    if ym is None or not (min(y, y_ant) - 1e-9 <= ym <= max(y, y_ant) + 1e-9):
                        self._trazar(tramo, color, grosor)
                        tramo = []
                tramo.append((px, max(-limite, min(alto + limite, sy))))
                anterior = (px, sy)
            px += paso
        self._trazar(tramo, color, grosor)

    def _trazar(self, tramo, color, grosor):
        if len(tramo) >= 2:
            self.create_line(*[c for punto in tramo for c in punto], fill=color, width=grosor,
                             capstyle="round", joinstyle="round")

    def _dibujar_capa(self, capa):
        ancho, alto = self._tam
        color = capa.color or PALETA["tangente"]
        guiones = (5, 4) if capa.discontinua else None
        if capa.tipo == "banda":
            sx0 = self.a_pantalla(capa.p[0], 0)[0]
            sx1 = self.a_pantalla(capa.q[0], 0)[0]
            relleno = mezclar(color, PALETA["plano"], capa.opciones.get("opacidad", 0.12))
            self.create_rectangle(max(-5, sx0), -5, min(ancho + 5, sx1), alto + 5, fill=relleno, outline="")
            for sx in (sx0, sx1):
                if -5 <= sx <= ancho + 5:
                    self.create_line(sx, 0, sx, alto, fill=mezclar(color, PALETA["plano"], 0.45), dash=(3, 3))
        elif capa.tipo == "segmento":
            p = self.a_pantalla(*capa.p)
            q = self.a_pantalla(*capa.q)
            if all(math.isfinite(v) and abs(v) < 1e6 for v in (*p, *q)):
                self.create_line(*p, *q, fill=color, width=capa.ancho, dash=guiones)
        elif capa.tipo == "vertical":
            sx = self.a_pantalla(capa.p[0], 0)[0]
            self.create_line(sx, 0, sx, alto, fill=color, width=capa.ancho, dash=guiones)
        elif capa.tipo == "texto":
            sx, sy = self.a_pantalla(*capa.p)
            if capa.opciones.get("arriba"):
                # Rótulos de valores iniciales en el borde superior, lejos de las cifras del eje.
                sy = 8
            self._texto_con_fondo(sx + capa.opciones.get("dx", 6), sy + capa.opciones.get("dy", 0 if capa.opciones.get("arriba") else -6),
                                  capa.texto, color, capa.opciones.get("anchor", "sw"), tamano=10, mono=False)

    def _dibujar_punto(self, punto, destacado):
        sx, sy = self.a_pantalla(punto.x, punto.y)
        ancho, alto = self._tam
        if not (-20 < sx < ancho + 20 and -20 < sy < alto + 20):
            return
        r = 6.5 if destacado else 5
        relleno = PALETA["plano"]
        if punto.forma == "anillo":
            self.create_oval(sx - r, sy - r, sx + r, sy + r, outline=punto.color, width=2, fill=relleno)
        elif punto.forma == "rombo":
            r += 1
            self.create_polygon(sx, sy - r, sx + r, sy, sx, sy + r, sx - r, sy, outline=punto.color,
                                width=2, fill=relleno)
        elif punto.forma == "cuadrado":
            r -= 0.5
            self.create_rectangle(sx - r, sy - r, sx + r, sy + r, outline=punto.color, width=2, fill=relleno)
        elif punto.forma == "cruz":
            self.create_line(sx - r, sy - r, sx + r, sy + r, fill=punto.color, width=2)
            self.create_line(sx - r, sy + r, sx + r, sy - r, fill=punto.color, width=2)
        else:
            r = 4.5 if destacado else 3.5
            self.create_oval(sx - r, sy - r, sx + r, sy + r, outline="", fill=punto.color)
        self._ocupado.append((sx - r, sy - r, sx + r, sy + r))
        if destacado:
            halo = r + 6
            self.create_oval(sx - halo, sy - halo, sx + halo, sy + halo,
                             outline=mezclar(punto.color, PALETA["plano"], 0.45), width=1)

    def _dibujar_etiqueta(self, punto, destacado):
        sx, sy = self.a_pantalla(punto.x, punto.y)
        ancho, alto = self._tam
        if not (0 < sx < ancho and 0 < sy < alto):
            return
        for dx, dy, anchor in ((9, -8, "sw"), (-9, -8, "se"), (9, 8, "nw"), (-9, 8, "ne")):
            if self._texto_con_fondo(sx + dx, sy + dy, punto.etiqueta, punto.color, anchor,
                                     tamano=9, mono=False, evitar=True):
                return
        if destacado:
            self._texto_con_fondo(sx + 9, sy - 8, punto.etiqueta, punto.color, "sw", tamano=9, mono=False)

    # ------------------------------------------------------------ controles
    def _construir_controles(self):
        self.marco_controles = tk.Frame(self, background=PALETA["borde"])
        botones = (("+", "Acercar", lambda: self.zoom(1 / self.ZOOM_BOTON)),
                   ("−", "Alejar", lambda: self.zoom(self.ZOOM_BOTON)),
                   ("⌂", "Vista estándar (doble clic)", self.vista_inicial),
                   ("⤢", "Expandir la gráfica", self._alternar_expandido))
        self.botones = {}
        for simbolo, ayuda, accion in botones:
            boton = tk.Label(self.marco_controles, text=simbolo, width=2, font=fuente(12),
                             background=PALETA["tarjeta"], foreground=PALETA["texto"], cursor="hand2",
                             padx=4, pady=1)
            boton.pack(side="top", pady=(0, 1))
            boton.bind("<Button-1>", lambda _e, a=accion: a())
            boton.bind("<Enter>", lambda _e, b=boton: b.configure(background=PALETA["hover"]))
            boton.bind("<Leave>", lambda _e, b=boton: b.configure(background=PALETA["tarjeta"]))
            boton.ayuda = ayuda
            self.botones[simbolo] = boton
        self.lectura = tk.Label(self, text="", font=fuente(9, mono=True), background=PALETA["superficie"],
                                foreground=PALETA["texto_suave"], padx=8, pady=3,
                                highlightthickness=1, highlightbackground=PALETA["borde"])
        self.marco_controles.place(relx=1.0, x=-8, y=8, anchor="ne")
        self.lectura.place(x=8, rely=1.0, y=-8, anchor="sw")

    def _alternar_expandido(self):
        self.expandido = not self.expandido
        self.botones["⤢"].configure(text="⤡" if self.expandido else "⤢")
        if self.al_expandir:
            self.al_expandir(self.expandido)

    # -------------------------------------------------------------- eventos
    def _al_redimensionar(self, evento):
        anterior = self._tam
        self._tam = (max(1, evento.width), max(1, evento.height))
        if anterior != (1, 1) and anterior[0] > 1 and not self.ajuste_automatico:
            # Conserva la escala al cambiar el tamaño: amplía la porción visible.
            x0, x1, y0, y1 = self.vista
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            ex = (x1 - x0) / anterior[0] * self._tam[0] / 2
            ey = (y1 - y0) / anterior[1] * self._tam[1] / 2
            self.vista = (cx - ex, cx + ex, cy - ey, cy + ey)
            self._vista_cambiada()
        self.programar_dibujo()

    def _vista_cambiada(self):
        if self.al_cambiar_vista is None:
            return
        if self._aviso_vista is not None:
            self.after_cancel(self._aviso_vista)
        self._aviso_vista = self.after(250, self._avisar_vista)

    def _avisar_vista(self):
        self._aviso_vista = None
        if self.al_cambiar_vista:
            self.al_cambiar_vista(self.vista)

    def _punto(self, clave):
        return next((p for p in self.puntos if p.clave == clave), None) if clave else None

    def _punto_cercano(self, px, py, radio=9):
        mejor, distancia = None, radio
        for punto in self.puntos:
            sx, sy = self.a_pantalla(punto.x, punto.y)
            d = math.hypot(sx - px, sy - py)
            if d <= distancia:
                mejor, distancia = punto, d
        return mejor

    def _presionar(self, evento):
        self.focus_set()
        self._arrastre = (evento.x, evento.y, self.vista, False)

    def _arrastrar(self, evento):
        if not self._arrastre:
            return
        x, y, vista, movido = self._arrastre
        dx, dy = evento.x - x, evento.y - y
        if not movido and abs(dx) + abs(dy) < 4:
            return
        ancho, alto = self._tam
        x0, x1, y0, y1 = vista
        desplazamiento_x = dx / ancho * (x1 - x0)
        desplazamiento_y = dy / alto * (y1 - y0)
        self.vista = (x0 - desplazamiento_x, x1 - desplazamiento_x, y0 + desplazamiento_y, y1 + desplazamiento_y)
        self._arrastre = (x, y, vista, True)
        self.ajuste_automatico = False
        self.configure(cursor="fleur")
        self._vista_cambiada()
        self.programar_dibujo()

    def _soltar(self, evento):
        movido = self._arrastre[3] if self._arrastre else False
        self._arrastre = None
        if not movido:
            punto = self._punto_cercano(evento.x, evento.y)
            if punto:
                self.seleccionado = punto.clave
                self.programar_dibujo()
                if self.al_seleccionar:
                    self.al_seleccionar(punto.clave)
            elif self.al_clic:
                self.al_clic(*self.a_plano(evento.x, evento.y))

    def redondear_a_pixel(self, x):
        """Redondea x a la resolución de un píxel: 1.5 en lugar de 1.4987634."""
        ancho = self._tam[0]
        pixel = (self.vista[1] - self.vista[0]) / max(1, ancho)
        decimales = max(0, math.ceil(-math.log10(pixel))) if pixel > 0 else 6
        texto = f"{round(x, decimales):.{decimales}f}"
        if "." in texto:
            texto = texto.rstrip("0").rstrip(".")
        return "0" if texto in ("-0", "") else texto

    def _mover(self, evento):
        if self._arrastre and self._arrastre[3]:
            return
        punto = self._punto_cercano(evento.x, evento.y)
        clave = punto.clave if punto else None
        if clave != self.resaltado:
            self.resaltado = clave
            self.programar_dibujo()
        self.configure(cursor="hand2" if punto else "fleur")
        x, y = self.a_plano(evento.x, evento.y)
        if punto:
            texto = f"{punto.descripcion or punto.etiqueta}  ({punto.x:.6g}, {punto.y:.6g})"
        else:
            fx = self._evaluar(self.funcion, x) if self.funcion else None
            if fx is not None and abs(self.a_pantalla(x, fx)[1] - evento.y) <= 6:
                texto = f"sobre f   x = {x:.6g}   f(x) = {fx:.6g}"
            else:
                texto = f"x = {x:.6g}   y = {y:.6g}"
        self.lectura.configure(text=texto)

    def _salir(self, _evento):
        if self.resaltado is not None:
            self.resaltado = None
            self.programar_dibujo()
        self.lectura.configure(text="")

    def _rueda(self, evento, delta=None):
        delta = evento.delta if delta is None else delta
        if delta == 0:
            return
        pasos = max(-3.0, min(3.0, muescas_rueda(self, delta)))
        factor = math.exp(-0.18 * pasos)
        estado = getattr(evento, "state", 0)
        eje = "x" if estado & 0x0001 else "y" if estado & (0x0004 | 0x0008) else "ambos"
        self.zoom(factor, evento.x, evento.y, eje)
        return "break"
