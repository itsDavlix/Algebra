"""Sistema visual único de la calculadora: paleta grafito con tinte morado.

Todos los colores, fuentes y estilos ttk se definen aquí. Las demás piezas
de la interfaz leen PALETA y FUENTES en lugar de escribir colores a mano.
"""

import tkinter.font as tkfont
from tkinter import ttk


PALETA = {
    # Superficies, de la más profunda a la más elevada.
    "lateral": "#0D0B13",
    "fondo": "#110F18",
    "superficie": "#17151F",
    "tarjeta": "#1D1A27",
    "campo": "#13111A",
    "hover": "#221F2E",
    "borde": "#2D2939",
    "borde_fuerte": "#3D3750",
    # Texto.
    "texto": "#E8E6EF",
    "texto_suave": "#A19DB2",
    "texto_tenue": "#6F6A82",
    # Acento único y estados.
    "acento": "#8B7CF6",
    "acento_hover": "#9D90F8",
    "acento_presionado": "#7A6AE6",
    "acento_suave": "#2A2440",
    "sobre_acento": "#FFFFFF",
    "exito": "#5FD39A",
    "exito_suave": "#15291F",
    "error": "#F07A7A",
    "error_suave": "#2E1719",
    "aviso": "#E3B341",
    "aviso_suave": "#2B2313",
    # Plano cartesiano: cada color significa siempre lo mismo.
    "plano": "#13111A",
    "rejilla_menor": "#1F1C2A",
    "rejilla_mayor": "#332E43",
    "ejes": "#A9A3BE",
    "curva": "#B3A6FF",
    "derivada": "#6E6590",
    "tangente": "#5FB8DA",
    "semilla": "#E3B341",
    "raiz": "#F1EFF6",
    "maximo": "#F2A5C0",
    "minimo": "#6FD3C1",
    "inflexion": "#C9C4D8",
    "intervalo": "#8B7CF6",
}

# Se completan al configurar el estilo, según las fuentes instaladas.
FUENTES = {"base": "Helvetica", "mono": "Courier"}

# Alias que conservan los nombres usados por módulos anteriores.
AZUL = PALETA["acento"]
AZUL_OSCURO = PALETA["acento_presionado"]
BLANCO = "#FFFFFF"
TEXTO = PALETA["texto"]
VERDE = PALETA["exito"]
ROJO = PALETA["error"]


def mezclar(color, fondo, proporcion):
    """Mezcla dos colores #RRGGBB. Tk no admite transparencia en Canvas."""
    c1 = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    c2 = [int(fondo[i:i + 2], 16) for i in (1, 3, 5)]
    mezcla = [round(a * proporcion + b * (1 - proporcion)) for a, b in zip(c1, c2)]
    return "#" + "".join(f"{v:02X}" for v in mezcla)


def muescas_rueda(widget, delta):
    """Convierte el delta de la rueda en «muescas» (1 = un clic de rueda).

    Tk 8.7+ usa 120 por muesca en todas las plataformas (los trackpads envían
    fracciones). Tk 8.6 en macOS envía ±1 por muesca; en Windows, ±120.
    """
    import tkinter as tk

    if tk.TkVersion >= 8.7 or widget.tk.call("tk", "windowingsystem") != "aqua":
        return delta / 120
    return float(delta)


def fuente(tamano=10, peso="normal", mono=False):
    return (FUENTES["mono" if mono else "base"], tamano, peso)


def _elegir_fuente(raiz, candidatas, por_defecto):
    instaladas = set(tkfont.families(raiz))
    return next((f for f in candidatas if f in instaladas), por_defecto)


def configurar_estilo(estilo, oscuro=None):
    """Aplica la paleta única a ttk y a los widgets clásicos creados después.

    El parámetro oscuro se conserva solo por compatibilidad: ya no hay tema claro.
    """
    try:
        estilo.theme_use("clam")
    except Exception:
        pass
    p = PALETA
    raiz = estilo.master
    FUENTES["base"] = _elegir_fuente(
        raiz, ("SF Pro Text", "Segoe UI Variable Text", "Segoe UI", "Inter", "Helvetica Neue", "Arial"),
        "Helvetica")
    FUENTES["mono"] = _elegir_fuente(
        raiz, ("SF Mono", "Menlo", "Cascadia Mono", "Consolas", "DejaVu Sans Mono"), "Courier")
    base, mono = FUENTES["base"], FUENTES["mono"]

    raiz.configure(background=p["fondo"])
    for clave, valor in (
        ("*Text.background", p["campo"]), ("*Text.foreground", p["texto"]),
        ("*Text.relief", "flat"), ("*Text.borderWidth", 0),
        ("*Text.highlightThickness", 1), ("*Text.highlightBackground", p["borde"]),
        ("*Text.highlightColor", p["acento"]), ("*Text.selectBackground", p["acento_suave"]),
        ("*Text.selectForeground", p["texto"]), ("*Text.insertBackground", p["acento_hover"]),
        ("*Text.padX", 10), ("*Text.padY", 8), ("*Text.font", (mono, 11)),
        ("*Entry.background", p["campo"]), ("*Entry.foreground", p["texto"]),
        ("*Entry.insertBackground", p["acento_hover"]),
        ("*TCombobox*Listbox.background", p["tarjeta"]),
        ("*TCombobox*Listbox.foreground", p["texto"]),
        ("*TCombobox*Listbox.selectBackground", p["acento_suave"]),
        ("*TCombobox*Listbox.selectForeground", p["texto"]),
        ("*Menu.background", p["tarjeta"]), ("*Menu.foreground", p["texto"]),
        ("*Menu.activeBackground", p["acento_suave"]), ("*Menu.activeForeground", p["texto"]),
    ):
        raiz.option_add(clave, valor)

    bordes = dict(bordercolor=p["borde"], lightcolor=p["borde"], darkcolor=p["borde"])
    estilo.configure(
        ".", background=p["fondo"], foreground=p["texto"], font=(base, 10),
        focuscolor=p["acento"], troughcolor=p["campo"], selectbackground=p["acento_suave"],
        selectforeground=p["texto"], insertcolor=p["acento_hover"], **bordes,
    )

    # Marcos.
    estilo.configure("TFrame", background=p["fondo"])
    estilo.configure("Lateral.TFrame", background=p["lateral"])
    estilo.configure("Panel.TFrame", background=p["superficie"])
    estilo.configure("Tarjeta.TFrame", background=p["superficie"], relief="solid", borderwidth=1, **bordes)
    estilo.configure("Plano.TFrame", background=p["plano"])
    estilo.configure("TSeparator", background=p["borde"])

    # Texto.
    etiquetas = {
        "TLabel": dict(foreground=p["texto"]),
        "Titulo.TLabel": dict(font=(base, 17, "bold")),
        "Subtitulo.TLabel": dict(font=(base, 10), foreground=p["texto_suave"]),
        "Seccion.TLabel": dict(font=(base, 9, "bold"), foreground=p["texto_suave"]),
        "Ayuda.TLabel": dict(font=(base, 9), foreground=p["texto_suave"]),
        "Tenue.TLabel": dict(font=(base, 9), foreground=p["texto_tenue"]),
        "Negrita.TLabel": dict(font=(base, 10, "bold")),
        "Formula.TLabel": dict(font=(mono, 10), foreground=p["texto_suave"]),
        "Valor.TLabel": dict(font=(mono, 11)),
        "Resultado.TLabel": dict(font=(mono, 20, "bold")),
        "Valido.TLabel": dict(foreground=p["exito"], font=(base, 9)),
        "Exito.TLabel": dict(foreground=p["exito"], font=(base, 10, "bold")),
        "Error.TLabel": dict(foreground=p["error"], font=(base, 9)),
        "Aviso.TLabel": dict(foreground=p["aviso"], font=(base, 9)),
        "Pendiente.TLabel": dict(foreground=p["texto_suave"], font=(base, 9)),
        "Tarjeta.TLabel": dict(font=(base, 10)),
        "TarjetaTitulo.TLabel": dict(font=(base, 10, "bold")),
    }
    for nombre, opciones in etiquetas.items():
        estilo.configure(nombre, background=p["fondo"], **opciones)
        estilo.configure(f"Panel.{nombre}", background=p["superficie"], **opciones)
    estilo.configure("Lateral.TLabel", background=p["lateral"], foreground=p["texto_tenue"],
                     font=(base, 9, "bold"))
    estilo.configure("Marca.TLabel", background=p["lateral"], foreground=p["texto"],
                     font=(base, 13, "bold"))

    # Secciones con título.
    for nombre in ("TLabelframe", "Seccion.TLabelframe"):
        estilo.configure(nombre, background=p["superficie"], relief="solid", borderwidth=1,
                         padding=14, **bordes)
        estilo.configure(f"{nombre}.Label", background=p["superficie"], foreground=p["texto_suave"],
                         font=(base, 10, "bold"), padding=(2, 0))

    # Pestañas internas (se usan en algunos módulos).
    estilo.configure("TNotebook", background=p["fondo"], borderwidth=0, tabmargins=(0, 0, 0, 0))
    estilo.configure("TNotebook.Tab", background=p["fondo"], foreground=p["texto_suave"],
                     padding=(14, 7), font=(base, 10), borderwidth=0, **bordes)
    estilo.map("TNotebook.Tab", background=[("selected", p["superficie"]), ("active", p["hover"])],
               foreground=[("selected", p["texto"])])

    # Botones: secundario por defecto, uno de acento por vista, fantasma para iconos.
    for prefijo, fondo_base in (("", p["tarjeta"]), ("Panel.", p["tarjeta"])):
        estilo.configure(f"{prefijo}TButton", padding=(12, 6), background=fondo_base,
                         foreground=p["texto"], relief="flat", font=(base, 10), **bordes)
        estilo.map(f"{prefijo}TButton",
                   background=[("pressed", p["borde"]), ("active", p["hover"]),
                               ("disabled", p["superficie"])],
                   foreground=[("disabled", p["texto_tenue"])],
                   bordercolor=[("focus", p["borde_fuerte"])])
        estilo.configure(f"{prefijo}Accion.TButton", padding=(14, 7), background=p["acento"],
                         foreground=p["sobre_acento"], font=(base, 10, "bold"), relief="flat",
                         bordercolor=p["acento"], lightcolor=p["acento"], darkcolor=p["acento"])
        estilo.map(f"{prefijo}Accion.TButton",
                   background=[("pressed", p["acento_presionado"]), ("active", p["acento_hover"]),
                               ("disabled", p["borde"])],
                   lightcolor=[("active", p["acento_hover"])], darkcolor=[("active", p["acento_hover"])],
                   foreground=[("disabled", p["texto_tenue"])])
    estilo.configure("Fantasma.TButton", padding=(8, 4), background=p["superficie"],
                     foreground=p["texto_suave"], relief="flat", bordercolor=p["superficie"],
                     lightcolor=p["superficie"], darkcolor=p["superficie"])
    estilo.map("Fantasma.TButton", background=[("active", p["hover"])],
               foreground=[("active", p["texto"]), ("disabled", p["texto_tenue"])])
    estilo.configure("Icono.TButton", padding=(4, 2), width=2, background=p["tarjeta"],
                     foreground=p["texto"], font=(base, 12), relief="flat", **bordes)
    estilo.map("Icono.TButton", background=[("active", p["hover"])])

    # Campos.
    campo = dict(fieldbackground=p["campo"], foreground=p["texto"], padding=(8, 5),
                 insertcolor=p["acento_hover"], **bordes)
    for nombre in ("TEntry", "Panel.TEntry", "TSpinbox", "TCombobox"):
        estilo.configure(nombre, **campo)
        estilo.map(nombre, bordercolor=[("focus", p["acento"]), ("invalid", p["error"])],
                   lightcolor=[("focus", p["acento"])], darkcolor=[("focus", p["acento"])],
                   fieldbackground=[("readonly", p["campo"]), ("disabled", p["superficie"])],
                   foreground=[("disabled", p["texto_tenue"])])
    estilo.configure("Formula.TEntry", **{**campo, "padding": (10, 8)})
    estilo.map("Formula.TEntry", bordercolor=[("focus", p["acento"]), ("invalid", p["error"])],
               lightcolor=[("focus", p["acento"])], darkcolor=[("focus", p["acento"])])
    estilo.configure("TSpinbox", arrowsize=11, arrowcolor=p["texto_suave"], background=p["tarjeta"])
    estilo.configure("TCombobox", arrowsize=11, arrowcolor=p["texto_suave"], background=p["tarjeta"])

    for nombre, fondo_control in (("TRadiobutton", p["fondo"]), ("Panel.TRadiobutton", p["superficie"]),
                                  ("TCheckbutton", p["fondo"]), ("Panel.TCheckbutton", p["superficie"])):
        estilo.configure(nombre, background=fondo_control, foreground=p["texto"], font=(base, 10),
                         indicatorbackground=p["campo"], indicatorforeground=p["acento"])
        estilo.map(nombre, background=[("active", fondo_control)],
                   indicatorbackground=[("selected", p["acento"])],
                   foreground=[("disabled", p["texto_tenue"])])

    # Barras de desplazamiento discretas.
    for orientacion in ("Vertical", "Horizontal"):
        for prefijo in ("", "Matriz.", "Biseccion.", "Tabla."):
            estilo.configure(f"{prefijo}{orientacion}.TScrollbar", background=p["borde"],
                             troughcolor=p["superficie"], bordercolor=p["superficie"],
                             lightcolor=p["borde"], darkcolor=p["borde"], arrowsize=0, width=8,
                             relief="flat", gripcount=0)
            estilo.map(f"{prefijo}{orientacion}.TScrollbar",
                       background=[("active", p["borde_fuerte"]), ("pressed", p["acento"])])
    estilo.configure("TScrollbar", arrowsize=0, width=8)

    # Controles de tamaño de matriz.
    for prefijo in ("", "Panel."):
        estilo.configure(f"{prefijo}Matriz.Control.TButton", padding=(4, 1), width=2,
                         background=p["tarjeta"], foreground=p["texto"], relief="flat", **bordes)
        estilo.map(f"{prefijo}Matriz.Control.TButton", background=[("active", p["hover"])],
                   foreground=[("disabled", p["texto_tenue"])])
        estilo.configure(f"{prefijo}Matriz.Valor.TLabel", background=p["campo"],
                         foreground=p["texto"], padding=(5, 1), relief="flat")

    # Tablas.
    for nombre in ("Tabla.Treeview", "Biseccion.Treeview", "Treeview"):
        estilo.configure(nombre, background=p["superficie"], fieldbackground=p["superficie"],
                         foreground=p["texto"], rowheight=26, font=(mono, 10), borderwidth=0,
                         relief="flat", **{k: p["superficie"] for k in ("bordercolor", "lightcolor", "darkcolor")})
        estilo.map(nombre, background=[("selected", p["acento_suave"])],
                   foreground=[("selected", p["texto"])])
        estilo.configure(f"{nombre}.Heading", background=p["tarjeta"], foreground=p["texto_suave"],
                         font=(base, 9, "bold"), relief="flat", padding=(6, 5), **bordes)
        estilo.map(f"{nombre}.Heading", background=[("active", p["hover"])])
    estilo.layout("Tabla.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])


def actualizar_widgets(raiz, oscuro=None):
    """Colorea los widgets Tk clásicos y las etiquetas de tabla ya creados."""
    p = PALETA

    def recorrer(padre):
        dentro_de_panel = isinstance(padre, ttk.LabelFrame) or getattr(padre, "es_panel", False)
        for widget in padre.winfo_children():
            clase = widget.winfo_class()
            en_panel = dentro_de_panel or isinstance(widget, ttk.LabelFrame)
            if clase == "Text" and not getattr(widget, "colores_propios", False):
                widget.configure(
                    background=p["campo"], foreground=p["texto"], insertbackground=p["acento_hover"],
                    highlightbackground=p["borde"], highlightcolor=p["acento"],
                    selectbackground=p["acento_suave"], selectforeground=p["texto"],
                )
                if getattr(widget, "resultado_destacado", False) is True:
                    widget.tag_configure("respuesta", background=p["acento_suave"], foreground=p["texto"])
                    widget.tag_configure("advertencia", background=p["error_suave"], foreground=p["error"])
                    widget.tag_configure("seccion", foreground=p["acento_hover"])
            elif clase == "Canvas" and not getattr(widget, "colores_propios", False):
                configurar_colores = getattr(widget, "configurar_colores", None)
                if configurar_colores is not None:
                    configurar_colores(p["superficie"], p["borde_fuerte"])
                else:
                    widget.configure(background=p["superficie"] if en_panel else p["fondo"],
                                     highlightthickness=0)
            if isinstance(widget, ttk.Treeview):
                for nombre, (fondo, texto) in {
                    "fila_par": (p["superficie"], p["texto"]),
                    "fila_impar": (mezclar(p["tarjeta"], p["superficie"], 0.5), p["texto"]),
                    "detalle": (p["campo"], p["texto_suave"]),
                    "decision": (p["acento_suave"], p["texto"]),
                    "parada_ok": (p["exito_suave"], p["exito"]),
                    "parada_no": (p["error_suave"], p["error"]),
                }.items():
                    widget.tag_configure(nombre, background=fondo, foreground=texto)
            if en_panel and isinstance(widget, ttk.Widget):
                estilo_actual = str(widget.cget("style"))
                if estilo_actual.startswith("Panel."):
                    estilo_actual = estilo_actual[len("Panel."):]
                if clase == "TLabel":
                    variante = estilo_actual if estilo_actual.endswith(".TLabel") else "TLabel"
                    widget.configure(style=f"Panel.{variante}")
                elif clase == "TFrame" and estilo_actual in ("", "TFrame"):
                    widget.configure(style="Panel.TFrame")
                elif clase == "TButton" and estilo_actual in ("", "TButton", "Accion.TButton"):
                    widget.configure(style=f"Panel.{estilo_actual or 'TButton'}")
                elif clase == "TButton" and estilo_actual.startswith("Matriz."):
                    widget.configure(style=f"Panel.{estilo_actual}")
                elif clase == "TEntry" and estilo_actual in ("", "TEntry"):
                    widget.configure(style="Panel.TEntry")
                elif clase in ("TRadiobutton", "TCheckbutton") and estilo_actual in ("", clase):
                    widget.configure(style=f"Panel.{clase}")
            recorrer(widget)

    recorrer(raiz)
