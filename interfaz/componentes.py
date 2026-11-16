"""Piezas de interfaz reutilizadas por todas las vistas de métodos.

- tarjeta(): marco con borde de la paleta.
- SelectorSegmentado: alterna métodos dentro de una misma vista.
- TablaPaginada: tabla con tantas filas por página como quepan y ventana completa.
- PanelProcedimiento: texto del paso a paso y ventana con el procedimiento completo.
- MenuEjercicios: ejercicios guardados, agrupados por dificultad.
"""

import math
import tkinter as tk
from tkinter import ttk

from interfaz.estilos import PALETA, fuente, mezclar

ALTO_FILA = 26              # debe coincidir con rowheight de Tabla.Treeview
ALTO_ENCABEZADO_TABLA = 30


def tarjeta(padre, padding=14, **grid):
    marco = ttk.Frame(padre, style="Tarjeta.TFrame", padding=padding)
    marco.es_panel = True
    if grid:
        marco.grid(**grid)
    return marco


def numero_corto(valor, cifras=6):
    """Cifras significativas sin «−0» y con signo menos tipográfico."""
    texto = f"{valor:.{cifras}g}"
    return "0" if texto in ("-0", "0") or abs(valor) < 1e-12 else texto.replace("-", "−")


# ---------------------------------------------------------------- texto
def crear_texto_procedimiento(padre, fondo, tamano=10):
    """Área de texto de solo lectura con los estilos del procedimiento."""
    texto = tk.Text(padre, width=30, height=4, wrap="word", state="disabled", background=fondo,
                    foreground=PALETA["texto"], highlightthickness=0, borderwidth=0, padx=2, pady=4,
                    cursor="arrow", font=fuente(tamano))
    texto.colores_propios = True
    texto.tag_configure("titulo", font=fuente(tamano + 1, "bold"), foreground=PALETA["acento_hover"],
                        spacing1=6, spacing3=4)
    texto.tag_configure("formula", font=fuente(tamano, mono=True), foreground=PALETA["texto"])
    texto.tag_configure("normal", foreground=PALETA["texto_suave"], spacing1=3)
    texto.tag_configure("ok", foreground=PALETA["exito"], font=fuente(tamano, "bold"))
    texto.tag_configure("error", foreground=PALETA["error"], font=fuente(tamano, "bold"))
    texto.tag_configure("aviso", foreground=PALETA["aviso"])
    texto.tag_configure("tenue", foreground=PALETA["texto_tenue"])
    return texto


def escribir_lineas(texto, lineas):
    """lineas: [(texto, estilo)] con estilo en titulo, formula, normal, ok, error, aviso, tenue."""
    texto.configure(state="normal")
    texto.delete("1.0", "end")
    for contenido, estilo in lineas:
        texto.insert("end", contenido + "\n", estilo)
    texto.configure(state="disabled")
    texto.yview_moveto(0)


# ---------------------------------------------------------------- ventanas
def abrir_ventana(dueno, clave, titulo, tamano="980x640"):
    """Ventana aparte reutilizable: si ya está abierta, se limpia y se trae al frente."""
    ventanas = dueno.__dict__.setdefault("ventanas", {})
    ventana = ventanas.get(clave)
    if ventana is not None and ventana.winfo_exists():
        for hijo in ventana.winfo_children():
            hijo.destroy()
        ventana.title(titulo)
        ventana.deiconify()
        ventana.lift()
        return ventana
    ventana = tk.Toplevel(dueno)
    ventana.title(titulo)
    ventana.configure(background=PALETA["fondo"])
    ventana.geometry(tamano)
    ventana.minsize(520, 320)
    ventanas[clave] = ventana
    return ventana


def ventana_texto(dueno, clave, titulo, lineas):
    ventana = abrir_ventana(dueno, clave, titulo)
    marco = ttk.Frame(ventana, padding=16)
    marco.pack(fill="both", expand=True)
    marco.columnconfigure(0, weight=1)
    marco.rowconfigure(0, weight=1)
    texto = crear_texto_procedimiento(marco, PALETA["fondo"], tamano=11)
    texto.grid(row=0, column=0, sticky="nsew")
    barra = ttk.Scrollbar(marco, orient="vertical", command=texto.yview)
    barra.grid(row=0, column=1, sticky="ns")
    texto.configure(yscrollcommand=barra.set)
    escribir_lineas(texto, lineas)
    return ventana


# ---------------------------------------------------------------- selector
class SelectorSegmentado(tk.Frame):
    """Control segmentado: una opción activa, las demás atenuadas."""

    def __init__(self, padre, opciones, al_elegir):
        super().__init__(padre, background=PALETA["borde"])
        self.opciones = {}
        for opcion in opciones:
            etiqueta = tk.Label(self, text=opcion, font=fuente(10), padx=12, pady=5, cursor="hand2")
            etiqueta.pack(side="left", padx=(0 if not self.opciones else 1, 0), pady=1)
            etiqueta.bind("<Button-1>", lambda _e, o=opcion: al_elegir(o))
            self.opciones[opcion] = etiqueta

    def marcar(self, activa):
        for opcion, etiqueta in self.opciones.items():
            activo = opcion == activa
            etiqueta.configure(background=PALETA["acento_suave"] if activo else PALETA["tarjeta"],
                               foreground=PALETA["texto"] if activo else PALETA["texto_suave"],
                               font=fuente(10, "bold" if activo else "normal"))


# ---------------------------------------------------------------- tabla paginada
def _anclaje(columna):
    """(clave, título, ancho[, anclaje]): números a la derecha, «n»/«k» centradas, texto con «w»."""
    if len(columna) > 3:
        return columna[3]
    return "center" if columna[0] in ("n", "k", "fila") else "e"


class TablaPaginada(ttk.Frame):
    """Tabla cuyo número de filas por página depende del alto disponible.

    Las filas se entregan completas (lista de tuplas); solo se insertan las de
    la página visible. «⤢ Ver todas» abre todas en una ventana aparte.
    """

    def __init__(self, padre, titulo, al_elegir=None, titulo_ventana="Tabla completa", nota=""):
        super().__init__(padre, style="Tarjeta.TFrame", padding=14)
        self.es_panel = True
        self.al_elegir = al_elegir
        self.titulo_ventana = titulo_ventana
        self.nota = nota
        self.columnas = (("n", "n", 44),)
        self.filas = []
        self.etiquetas = None
        self.por_pagina = 12
        self.pagina = 0
        self.elegido = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        cabecera = ttk.Frame(self, style="Panel.TFrame")
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        cabecera.columnconfigure(0, weight=1)
        ttk.Label(cabecera, text=titulo, style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(cabecera, text="‹", width=2, style="Panel.TButton",
                   command=lambda: self.ir_a_pagina(self.pagina - 1)).grid(row=0, column=1)
        self.etiqueta_pagina = ttk.Label(cabecera, text="", style="Panel.Ayuda.TLabel", width=13,
                                         anchor="center")
        self.etiqueta_pagina.grid(row=0, column=2)
        ttk.Button(cabecera, text="›", width=2, style="Panel.TButton",
                   command=lambda: self.ir_a_pagina(self.pagina + 1)).grid(row=0, column=3)
        ttk.Button(cabecera, text="⤢ Ver todas", style="Panel.TButton",
                   command=self.abrir_completa).grid(row=0, column=4, padx=(8, 0))
        self.tabla = ttk.Treeview(self, columns=("n",), show="headings", height=2,
                                  style="Tabla.Treeview", selectmode="browse")
        self.tabla.tag_configure("par", background=PALETA["superficie"])
        self.tabla.tag_configure("impar", background=mezclar(PALETA["tarjeta"], PALETA["superficie"], 0.6))
        self.tabla.tag_configure("final_ok", foreground=PALETA["exito"])
        self.tabla.tag_configure("final_no", foreground=PALETA["error"])
        self.tabla.tag_configure("destacado", foreground=PALETA["acento_hover"])
        self.tabla.grid(row=1, column=0, sticky="nsew")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)
        self.tabla.bind("<Configure>", self._ajustar_filas)

    def configurar_columnas(self, columnas):
        """columnas: [(clave, título, ancho)]; la clave «n» va centrada y fija."""
        self.columnas = tuple(columnas)
        self.limpiar()
        self.tabla.configure(columns=[c[0] for c in columnas])
        for columna in columnas:
            clave, titulo, ancho = columna[:3]
            anclaje = _anclaje(columna)
            self.tabla.heading(clave, text=titulo, anchor=anclaje)
            self.tabla.column(clave, width=ancho, minwidth=40, anchor=anclaje, stretch=anclaje != "center")

    def definir_filas(self, filas, etiquetas=None):
        """etiquetas(indice) -> lista de etiquetas extra (final_ok, final_no, destacado)."""
        self.filas = list(filas)
        self.etiquetas = etiquetas
        self.elegido = None
        self.ir_a_pagina(0)

    def limpiar(self):
        self.filas = []
        self.elegido = None
        self.pagina = 0
        self.tabla.delete(*self.tabla.get_children())
        self.etiqueta_pagina.configure(text="")

    def ir_a_pagina(self, pagina, seleccionar=None):
        total = len(self.filas)
        paginas = max(1, math.ceil(total / self.por_pagina))
        self.pagina = max(0, min(paginas - 1, pagina))
        self.tabla.delete(*self.tabla.get_children())
        inicio = self.pagina * self.por_pagina
        for indice in range(inicio, min(total, inicio + self.por_pagina)):
            etiquetas = ["par" if indice % 2 == 0 else "impar"]
            if self.etiquetas:
                etiquetas += list(self.etiquetas(indice))
            self.tabla.insert("", "end", iid=str(indice), tags=etiquetas, values=self.filas[indice])
        if total == 0:
            self.etiqueta_pagina.configure(text="")
        else:
            self.etiqueta_pagina.configure(text=f"{inicio + 1}–{min(total, inicio + self.por_pagina)} de {total}")
        if seleccionar is not None and self.tabla.exists(str(seleccionar)):
            self.tabla.selection_set(str(seleccionar))
            self.tabla.see(str(seleccionar))

    def seleccionar(self, indice):
        self.ir_a_pagina(indice // self.por_pagina, seleccionar=indice)

    def _al_seleccionar(self, _evento=None):
        elegido = self.tabla.selection()
        if not elegido:
            return
        self.elegido = int(elegido[0])
        if self.al_elegir:
            self.al_elegir(self.elegido)

    def _ajustar_filas(self, evento):
        filas = max(3, (evento.height - ALTO_ENCABEZADO_TABLA) // ALTO_FILA)
        if filas == self.por_pagina:
            return
        primero = self.pagina * self.por_pagina
        self.por_pagina = filas
        if self.filas:
            ancla = self.elegido if self.elegido is not None else primero
            self.ir_a_pagina(ancla // filas, seleccionar=self.elegido)

    def abrir_completa(self):
        """Todas las filas en una ventana aparte; elegir ahí también elige aquí."""
        if not self.filas:
            return None
        titulo = self.titulo_ventana() if callable(self.titulo_ventana) else self.titulo_ventana
        ventana = abrir_ventana(self, "tabla", titulo)
        marco = ttk.Frame(ventana, padding=16)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)
        nota = self.nota() if callable(self.nota) else self.nota
        ttk.Label(marco, text=nota or f"{len(self.filas)} filas", style="Ayuda.TLabel", wraplength=900
                  ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        tabla = ttk.Treeview(marco, columns=[c[0] for c in self.columnas], show="headings",
                             style="Tabla.Treeview")
        for columna in self.columnas:
            clave, titulo_columna, ancho = columna[:3]
            anclaje = _anclaje(columna)
            tabla.heading(clave, text=titulo_columna, anchor=anclaje)
            tabla.column(clave, width=ancho, minwidth=40, anchor=anclaje, stretch=anclaje != "center")
        tabla.tag_configure("impar", background=mezclar(PALETA["tarjeta"], PALETA["superficie"], 0.6))
        for indice, fila in enumerate(self.filas):
            tabla.insert("", "end", iid=str(indice), values=fila, tags=("impar",) if indice % 2 else ())
        tabla.grid(row=1, column=0, sticky="nsew")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        barra.grid(row=1, column=1, sticky="ns")
        tabla.configure(yscrollcommand=barra.set)

        def sincronizar(_evento=None):
            elegido = tabla.selection()
            if elegido:
                self.seleccionar(int(elegido[0]))
        tabla.bind("<<TreeviewSelect>>", sincronizar)
        ttk.Label(marco, text="Al seleccionar una fila también se elige en la ventana principal.",
                  style="Tenue.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 0))
        return ventana


# ---------------------------------------------------------------- procedimiento
class PanelProcedimiento(ttk.Frame):
    """Paso a paso de la selección actual; «⤢ Completo» abre todo en otra ventana."""

    def __init__(self, padre, completo, titulo_ventana="Procedimiento", titulo="PROCEDIMIENTO"):
        super().__init__(padre, style="Tarjeta.TFrame", padding=14)
        self.es_panel = True
        self.completo = completo
        self.titulo_ventana = titulo_ventana
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        cabecera = ttk.Frame(self, style="Panel.TFrame")
        cabecera.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        cabecera.columnconfigure(0, weight=1)
        ttk.Label(cabecera, text=titulo, style="Panel.Seccion.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(cabecera, text="⤢ Completo", style="Panel.TButton",
                   command=self.abrir_completo).grid(row=0, column=1)
        self.texto = crear_texto_procedimiento(self, PALETA["superficie"])
        self.texto.grid(row=1, column=0, sticky="nsew")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.texto.yview)
        barra.grid(row=1, column=1, sticky="ns")
        self.texto.configure(yscrollcommand=barra.set)

    def mostrar(self, lineas):
        escribir_lineas(self.texto, lineas)

    def abrir_completo(self):
        titulo = self.titulo_ventana() if callable(self.titulo_ventana) else self.titulo_ventana
        return ventana_texto(self, "procedimiento", titulo, self.completo())


# ---------------------------------------------------------------- ejercicios
class MenuEjercicios(ttk.Menubutton):
    """Botón «Ejercicios ▾» con los ejercicios guardados por dificultad."""

    def __init__(self, padre, ejercicios, al_elegir):
        super().__init__(padre, text="Ejercicios ▾", style="TButton")
        self.menu = tk.Menu(self, tearoff=False, background=PALETA["tarjeta"], foreground=PALETA["texto"],
                            activebackground=PALETA["acento_suave"], activeforeground=PALETA["texto"],
                            font=fuente(10))
        self["menu"] = self.menu
        self.definir(ejercicios, al_elegir)

    def definir(self, ejercicios, al_elegir):
        self.menu.delete(0, "end")
        nivel_actual = None
        for ejercicio in ejercicios:
            if ejercicio.dificultad != nivel_actual:
                if nivel_actual is not None:
                    self.menu.add_separator()
                nivel_actual = ejercicio.dificultad
                self.menu.add_command(label=ejercicio.dificultad.upper(), state="disabled")
            self.menu.add_command(label=f"   {ejercicio.titulo}", command=lambda e=ejercicio: al_elegir(e))
