"""Iterum · Álgebra lineal y métodos numéricos
Universidad Americana (UAM) - Álgebra Lineal (MTM0120)

DAVID ALEJANDRO ESPINOZA LARGAESPADA
ERICK ANTONIO ARANA ESPINOZA
JULIAN ALONSO TORREZ VALDIVIA

Características:
- Operaciones con vectores de dimensión n y combinación lineal.
- Operaciones con matrices: inversa, transpuesta, rango y determinantes.
- Sistemas lineales A·X = B: Gauss-Jordan, Jacobi y Gauss-Seidel con análisis de
  dominancia diagonal y radio espectral.
- Raíces de ecuaciones: Bisección, Regula Falsi, Newton-Raphson y Secante,
  con plano cartesiano interactivo, puntos notables y procedimiento paginado.
- Operaciones con números romanos.

Todo el cálculo usa únicamente la biblioteca estándar de Python."""

import os
import sys
import tkinter as tk
from tkinter import ttk


# Permite encontrar los módulos locales también al iniciar main.py directamente.
if __package__ is None or __package__ == "":
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from interfaz.ayudas import AyudaEmergente
from interfaz.estilos import PALETA, actualizar_widgets, configurar_estilo, fuente, muescas_rueda
from interfaz.motorGrafica import PlanoCartesiano
from interfaz.pestanaInicio import PestanaInicio
from interfaz.vistaVectores import VistaVectores
from interfaz.vistaMatrices import VistaMatrices
from interfaz.sistemas import VistaSistemas
from interfaz.raices import VistaRaiz
from interfaz.vistaRomanos import VistaRomanos


PIXELES_POR_MUESCA = 60
ANCHO_MINIMO = 1180          # por debajo, las vistas de tres columnas recortan tablas y botones
ANCHO_MENU_COMPACTO = 1320   # bajo este ancho el menú lateral muestra solo abreviaturas
ABREVIATURAS = {"Inicio": "Ini", "Vectores": "Vec", "Matrices": "Mat", "Sistemas lineales": "Sis",
                "Bisección / Regula Falsi": "B·RF", "Newton-Raphson / Secante": "N·S", "Números romanos": "Rom"}

SECCIONES = (
    (None, (("Inicio", lambda padre: PestanaInicio(padre)),)),
    ("ÁLGEBRA LINEAL", (
        ("Vectores", lambda padre: VistaVectores(padre)),
        ("Matrices", lambda padre: VistaMatrices(padre)),
        ("Sistemas lineales", lambda padre: VistaSistemas(padre)),
    )),
    ("RAÍCES DE ECUACIONES", (
        ("Bisección / Regula Falsi", lambda padre: VistaRaiz(padre, ("Bisección", "Regula Falsi"))),
        ("Newton-Raphson / Secante", lambda padre: VistaRaiz(padre, ("Newton-Raphson", "Secante"))),
    )),
    ("OTROS", (
        ("Números romanos", lambda padre: VistaRomanos(padre)),
    )),
)


class ElementoNavegacion(tk.Frame):
    """Fila del menú lateral con estados de reposo, cursor encima y activa."""

    def __init__(self, padre, texto, al_elegir):
        super().__init__(padre, background=PALETA["lateral"], cursor="hand2")
        self.texto = texto
        self.activo = False
        self.indicador = tk.Frame(self, width=3, background=PALETA["lateral"])
        self.indicador.pack(side="left", fill="y")
        self.etiqueta = tk.Label(self, text=texto, anchor="w", font=fuente(10), padx=12, pady=6,
                                 background=PALETA["lateral"], foreground=PALETA["texto_suave"])
        self.etiqueta.pack(side="left", fill="x", expand=True)
        self.ayuda = AyudaEmergente(self.etiqueta, "")
        for widget in (self, self.etiqueta):
            widget.bind("<Button-1>", lambda _e: al_elegir())
            widget.bind("<Enter>", lambda _e: (self._pintar(encima=True), self.ayuda._mostrar()), add="+")
            widget.bind("<Leave>", lambda _e: (self._pintar(), self.ayuda._ocultar()), add="+")

    def compactar(self, compacto):
        """En ventanas angostas: abreviatura con el nombre completo al pasar el cursor."""
        self.etiqueta.configure(text=ABREVIATURAS.get(self.texto, self.texto[:3]) if compacto else self.texto,
                                padx=8 if compacto else 12)
        self.ayuda.texto = self.texto if compacto else ""

    def marcar(self, activo):
        self.activo = activo
        self._pintar()

    def _pintar(self, encima=False):
        if self.activo:
            fondo, texto, barra = PALETA["acento_suave"], PALETA["texto"], PALETA["acento"]
        else:
            fondo = PALETA["hover"] if encima else PALETA["lateral"]
            texto, barra = (PALETA["texto"] if encima else PALETA["texto_suave"]), fondo
        for widget in (self, self.etiqueta):
            widget.configure(background=fondo)
        self.etiqueta.configure(foreground=texto, font=fuente(10, "bold" if self.activo else "normal"))
        self.indicador.configure(background=barra)


class AreaDesplazable(ttk.Frame):
    """Contenedor con barra vertical: si la vista no cabe, se desplaza en lugar de recortarse.

    El contenido ocupa todo el ancho y, como mínimo, todo el alto visible; si
    necesita más alto que la ventana, aparece la barra de desplazamiento.
    """

    def __init__(self, padre):
        super().__init__(padre)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.lienzo = tk.Canvas(self, background=PALETA["fondo"], highlightthickness=0, borderwidth=0,
                                yscrollincrement=1)
        self._objetivo = 0.0
        self._animacion = None
        self.lienzo.colores_propios = True
        self.lienzo.grid(row=0, column=0, sticky="nsew")
        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        self.barra.grid(row=0, column=1, sticky="ns")
        self.lienzo.configure(yscrollcommand=self._mover_barra)
        self.interior = ttk.Frame(self.lienzo)
        self._ventana = self.lienzo.create_window(0, 0, window=self.interior, anchor="nw")
        self.alto_minimo = None
        self.interior.bind("<Configure>", self._ajustar)
        self.lienzo.bind("<Configure>", self._ajustar)

    def _ajustar(self, _evento=None):
        ancho = self.lienzo.winfo_width()
        # Las vistas que se reparten el alto en proporciones (alto_minimo) ocupan
        # exactamente el alto visible; las demás, su alto natural. Solo si no
        # caben aparece la barra, para no recortar nada.
        minimo = self.alto_minimo if self.alto_minimo is not None else self.interior.winfo_reqheight()
        alto = max(self.lienzo.winfo_height(), minimo)
        self.lienzo.itemconfigure(self._ventana, width=ancho, height=alto)
        self.lienzo.configure(scrollregion=(0, 0, ancho, alto))

    def _mover_barra(self, primero, ultimo):
        if float(primero) <= 0.0 and float(ultimo) >= 1.0:
            self.barra.grid_remove()
        else:
            self.barra.grid()
        self.barra.set(primero, ultimo)

    def desplazar_pixeles(self, pixeles):
        """Desplaza con suavidad: acumula fracciones y anima hacia el destino."""
        if not self.barra.winfo_ismapped():
            return
        self._objetivo += pixeles
        if self._animacion is None:
            self._animacion = self.after(0, self._animar)

    def _animar(self):
        # Recorre un 35 % de la distancia pendiente en cada cuadro: movimiento suave que frena al final.
        paso = self._objetivo * 0.35
        if abs(paso) < 1:
            paso = (1 if self._objetivo > 0 else -1) if abs(self._objetivo) >= 1 else 0
        entero = int(round(paso))
        if entero:
            self.lienzo.yview_scroll(entero, "units")
            self._objetivo -= entero
        if abs(self._objetivo) >= 1:
            self._animacion = self.after(12, self._animar)
        else:
            self._objetivo = 0.0
            self._animacion = None


class CalculadoraAlgebraLineal(tk.Tk):
    """Ventana principal: menú lateral por categorías y área de trabajo."""

    def __init__(self):
        super().__init__()
        self.title("Iterum · Álgebra lineal y métodos numéricos")
        ancho_pantalla, alto_pantalla = self.winfo_screenwidth(), self.winfo_screenheight()
        ancho = min(1500, max(ANCHO_MINIMO, int(ancho_pantalla * 0.9)))
        ancho = min(ancho, ancho_pantalla)
        alto = min(1000, max(640, int(alto_pantalla * 0.9)))
        self.minsize(min(ANCHO_MINIMO, ancho_pantalla), min(640, alto))
        self.geometry(f"{ancho}x{alto}+{max(0, (ancho_pantalla - ancho) // 2)}+"
                      f"{max(0, (alto_pantalla - alto) // 2)}")
        configurar_estilo(ttk.Style(self))
        self.vistas = {}
        self.contenedores = {}
        self.elementos = {}
        self.actual = None
        self._construir_interfaz()
        self.mostrar("Inicio")
        self.bind_all("<MouseWheel>", self._rueda_global, add="+")
        self.bind_all("<Button-4>", lambda e: self._rueda_global(e, 120), add="+")
        self.bind_all("<Button-5>", lambda e: self._rueda_global(e, -120), add="+")

    def _rueda_global(self, evento, delta=None):
        """Desplazamiento de página fluido, encadenado como en la web.

        Sobre el plano la rueda hace zoom. Sobre tablas o textos con su propio
        desplazamiento, estos se mueven primero y, al llegar al borde, se mueve la página.
        """
        widget = self.winfo_containing(evento.x_root, evento.y_root)
        if widget is None or self.actual is None:
            return
        delta = evento.delta if delta is None else delta
        muescas = muescas_rueda(self, delta)
        contenedor = self.contenedores[self.actual]
        actual = widget
        while actual is not None and actual is not contenedor:
            if isinstance(actual, PlanoCartesiano):
                return
            if actual.winfo_class() in ("Text", "Treeview", "Listbox"):
                primero, ultimo = actual.yview()
                hacia_arriba = muescas > 0
                if (hacia_arriba and primero > 0.0) or (not hacia_arriba and ultimo < 1.0):
                    return  # el widget aún puede desplazarse por sí mismo
            actual = actual.master
        if actual is contenedor:
            contenedor.desplazar_pixeles(-muescas * PIXELES_POR_MUESCA)

    def _construir_interfaz(self):
        lateral = tk.Frame(self, background=PALETA["lateral"], width=214)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        self.lateral = lateral
        self._compacto = None
        self._textos_largos = []
        tk.Frame(self, background=PALETA["borde"], width=1).pack(side="left", fill="y")
        marca = tk.Frame(lateral, background=PALETA["lateral"])
        marca.pack(fill="x", padx=16, pady=(20, 18))
        nombre_app = tk.Label(marca, text="Iterum", font=fuente(14, "bold"), background=PALETA["lateral"],
                              foreground=PALETA["texto"])
        nombre_app.pack(anchor="w")
        self._textos_largos.append((nombre_app, "Iterum", "It"))
        subtitulo = tk.Label(marca, text="Álgebra lineal y métodos numéricos", font=fuente(9),
                             background=PALETA["lateral"], foreground=PALETA["texto_tenue"])
        subtitulo.pack(anchor="w")
        self._textos_largos.append((subtitulo, "Álgebra lineal y métodos numéricos", ""))
        for titulo, elementos in SECCIONES:
            if titulo:
                seccion = tk.Label(lateral, text=titulo, font=fuente(8, "bold"), background=PALETA["lateral"],
                                   foreground=PALETA["texto_tenue"], anchor="w", padx=16)
                seccion.pack(fill="x", pady=(14, 4))
                self._textos_largos.append((seccion, titulo, ""))
            for nombre, _ in elementos:
                elemento = ElementoNavegacion(lateral, nombre, lambda n=nombre: self.mostrar(n))
                elemento.pack(fill="x", padx=(0, 8))
                self.elementos[nombre] = elemento
        pie = tk.Label(lateral, text="Python estándar · sin bibliotecas externas", font=fuente(8),
                       background=PALETA["lateral"], foreground=PALETA["texto_tenue"], anchor="w",
                       padx=16, wraplength=190, justify="left")
        pie.pack(side="bottom", fill="x", pady=14)
        self._textos_largos.append((pie, "Python estándar · sin bibliotecas externas", ""))
        self.bind("<Configure>", self._al_redimensionar, add="+")
        self.area = ttk.Frame(self)
        self.area.pack(side="left", fill="both", expand=True)
        self.area.rowconfigure(0, weight=1)
        self.area.columnconfigure(0, weight=1)

    def _al_redimensionar(self, evento):
        if evento.widget is not self:
            return
        compacto = evento.width < ANCHO_MENU_COMPACTO
        if compacto == self._compacto:
            return
        self._compacto = compacto
        # Menú compacto: deja ~150 px más para tablas y gráficas en pantallas pequeñas.
        self.lateral.configure(width=64 if compacto else 214)
        for etiqueta, largo, corto in self._textos_largos:
            etiqueta.configure(text=corto if compacto else largo)
            if etiqueta.master is self.lateral:
                etiqueta.configure(padx=8 if compacto else 16)
        for elemento in self.elementos.values():
            elemento.compactar(compacto)

    def _fabrica(self, nombre):
        for _, elementos in SECCIONES:
            for nombre_elemento, fabrica in elementos:
                if nombre_elemento == nombre:
                    return fabrica
        raise KeyError(nombre)

    def mostrar(self, nombre):
        """Crea la vista la primera vez que se abre y la muestra."""
        if nombre not in self.vistas:
            contenedor = AreaDesplazable(self.area)
            vista = self._fabrica(nombre)(contenedor.interior)
            vista.pack(fill="both", expand=True)
            contenedor.alto_minimo = getattr(vista, "ALTO_MINIMO", None)
            self.contenedores[nombre] = contenedor
            self.vistas[nombre] = vista
            actualizar_widgets(vista)
        if self.actual is not None:
            self.contenedores[self.actual].grid_remove()
            self.elementos[self.actual].marcar(False)
        self.contenedores[nombre].grid(row=0, column=0, sticky="nsew")
        self.elementos[nombre].marcar(True)
        self.actual = nombre


if __name__ == "__main__":
    CalculadoraAlgebraLineal().mainloop()
