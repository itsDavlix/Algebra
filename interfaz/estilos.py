"""Módulo de estilos compartidos para los modos claro y oscuro."""

import tkinter.font as tkfont
from tkinter import ttk

# Acentos morados suaves y fondos neutros para ambos temas.
AZUL_OSCURO = "#51417D"
AZUL = "#6946AD"
AZUL_HOVER = "#5B3D94"
AZUL_CLARO = "#F2EFF9"
AZUL_BORDE = "#DDD6EE"
BLANCO = "#FFFFFF"
TEXTO = "#1E293B"
TEXTO_SUAVE = "#64748B"
VERDE = "#15803D"
ROJO = "#B91C1C"

_PALETAS = {
    False: {
        "fondo": "#F3F6FA",
        "superficie": BLANCO,
        "campo": BLANCO,
        "tarjeta": "#F8FAFC",
        "borde": AZUL_BORDE,
        "texto": TEXTO,
        "texto_suave": TEXTO_SUAVE,
        "titulo": "#51417D",
        "azul": AZUL,
        "azul_hover": AZUL_HOVER,
        "seleccion": "#E8E1F5",
        "verde": VERDE,
        "rojo": ROJO,
        "fila_alterna": "#F7F9FC",
        "detalle": "#F8FAFC",
        "decision": "#F0ECF8",
        "parada_ok": "#ECFDF3",
        "parada_no": "#FEF2F2",
        "rejilla": "#E8EDF4",
        "boton_deshabilitado": "#F1F5F9",
        "texto_deshabilitado": "#94A3B8",
        "barra": "#CBD5E1",
        "barra_matriz": "#E4DDF1",
    },
    True: {
        "fondo": "#0B1220",
        "superficie": "#111C2E",
        "campo": "#0B1220",
        "tarjeta": "#172338",
        "borde": "#334155",
        "texto": "#E5E7EB",
        "texto_suave": "#A8B3C5",
        "titulo": "#BFDBFE",
        "azul": "#A995E8",
        "azul_hover": "#B9A8F0",
        "seleccion": "#3A3154",
        "verde": "#4ADE80",
        "rojo": "#F87171",
        "fila_alterna": "#263244",
        "detalle": "#202B3A",
        "decision": "#302744",
        "parada_ok": "#143B2B",
        "parada_no": "#4A2228",
        "rejilla": "#334155",
        "boton_deshabilitado": "#273449",
        "texto_deshabilitado": "#94A3B8",
        "barra": "#475569",
        "barra_matriz": "#263244",
    },
}


def _elegir_fuente(estilo, candidatas, por_defecto):
    """Devuelve la primera fuente instalada del sistema para Windows y Mac."""
    instaladas = set(tkfont.families(estilo.master))
    return next((f for f in candidatas if f in instaladas), por_defecto)


def configurar_estilo(estilo, oscuro=False):
    """Aplica la paleta elegida a ttk y a los widgets clásicos creados después."""
    try:
        estilo.theme_use("clam")
    except Exception:
        pass

    p = _PALETAS[bool(oscuro)]
    base = _elegir_fuente(estilo, ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial"), "Helvetica")
    mono = _elegir_fuente(estilo, ("Consolas", "Menlo", "Courier New"), "Courier")
    raiz = estilo.master
    raiz.configure(background=p["fondo"])
    raiz.option_add("*Text.background", p["campo"])
    raiz.option_add("*Text.foreground", p["texto"])
    raiz.option_add("*Text.relief", "flat")
    raiz.option_add("*Text.borderWidth", 1)
    raiz.option_add("*Text.highlightThickness", 1)
    raiz.option_add("*Text.highlightBackground", p["borde"])
    raiz.option_add("*Text.highlightColor", p["azul"])
    raiz.option_add("*Text.selectBackground", p["seleccion"])
    raiz.option_add("*Text.selectForeground", p["texto"])
    raiz.option_add("*Text.insertBackground", p["azul_hover"])
    raiz.option_add("*Text.padX", 8)
    raiz.option_add("*Text.padY", 6)
    raiz.option_add("*Text.font", (mono, 11))

    estilo.configure(
        ".", background=p["fondo"], foreground=p["texto"], font=(base, 10),
        bordercolor=p["borde"], focuscolor=p["azul"],
    )
    estilo.configure("TFrame", background=p["fondo"])
    estilo.configure("Panel.TFrame", background=p["superficie"])
    estilo.configure("Tarjeta.TFrame", background=p["tarjeta"])
    estilo.configure("TLabel", background=p["fondo"], foreground=p["texto"])
    estilo.configure("Panel.TLabel", background=p["superficie"], foreground=p["texto"])
    estilo.configure("Titulo.TLabel", font=(base, 20, "bold"), foreground=p["titulo"])
    estilo.configure("Subtitulo.TLabel", font=(base, 11), foreground=p["texto_suave"])
    estilo.configure("Ayuda.TLabel", font=(base, 9), foreground=p["texto_suave"])
    estilo.configure("Negrita.TLabel", font=(base, 10, "bold"), foreground=p["titulo"])
    estilo.configure("Valido.TLabel", foreground=p["verde"], font=(base, 10))
    estilo.configure("Error.TLabel", foreground=p["rojo"], font=(base, 10, "bold"))
    estilo.configure("Pendiente.TLabel", foreground=p["texto_suave"], font=(base, 10))
    estilo.configure(
        "Tarjeta.TLabel", background=p["tarjeta"], foreground=p["titulo"], font=(base, 10),
    )
    estilo.configure(
        "TarjetaTitulo.TLabel", background=p["tarjeta"], foreground=p["titulo"],
        font=(base, 10, "bold"),
    )
    for estilo_texto in ("Ayuda", "Negrita", "Valido", "Error", "Pendiente"):
        estilo.configure(f"Panel.{estilo_texto}.TLabel", background=p["superficie"])
    for estilo_texto in ("Tarjeta", "TarjetaTitulo"):
        estilo.configure(
            f"Panel.{estilo_texto}.TLabel", background=p["tarjeta"],
        )

    estilo.configure(
        "TLabelframe", background=p["superficie"], bordercolor=p["borde"],
        relief="flat", borderwidth=1, padding=12,
    )
    estilo.configure(
        "TLabelframe.Label", background=p["superficie"], foreground=p["titulo"],
        padding=(4, 1),
    )
    estilo.configure(
        "Seccion.TLabelframe", background=p["superficie"],
        bordercolor=p["borde"], relief="flat",
    )
    estilo.configure(
        "Seccion.TLabelframe.Label", background=p["superficie"], foreground=p["titulo"],
        font=(base, 11, "bold"), padding=(4, 1),
    )

    estilo.configure("TNotebook", background=p["fondo"], borderwidth=0, tabmargins=(0, 4, 0, 0))
    estilo.configure(
        "TNotebook.Tab", background=p["tarjeta"], foreground=p["titulo"],
        padding=(13, 7), font=(base, 10, "bold"), borderwidth=0,
    )
    estilo.map(
        "TNotebook.Tab",
        background=[("selected", p["azul"]), ("active", p["borde"])],
        foreground=[("selected", BLANCO if not oscuro else "#FFFFFF")],
    )

    estilo.configure(
        "TButton", padding=(10, 7), background=p["tarjeta"], foreground=p["titulo"],
        bordercolor=p["borde"], relief="flat", font=(base, 10),
    )
    estilo.map(
        "TButton",
        background=[("active", p["seleccion"]), ("disabled", p["boton_deshabilitado"])],
        foreground=[("disabled", p["texto_deshabilitado"])],
    )
    estilo.configure(
        "Accion.TButton", padding=10, background=p["azul"], foreground="#FFFFFF",
        font=(base, 10, "bold"), bordercolor=p["azul"], relief="flat",
    )
    estilo.configure(
        "Panel.TButton", padding=(10, 7), background=p["tarjeta"],
        foreground=p["titulo"], bordercolor=p["borde"], relief="flat",
        font=(base, 10),
    )
    estilo.configure(
        "Panel.Accion.TButton", padding=10, background=p["azul"],
        foreground="#FFFFFF", font=(base, 10, "bold"),
        bordercolor=p["azul"], relief="flat",
    )
    estilo.map(
        "Accion.TButton",
        background=[("active", p["azul_hover"]), ("disabled", p["borde"])],
        foreground=[("disabled", "#FFFFFF")],
    )
    estilo.map(
        "Panel.TButton",
        background=[("active", p["seleccion"]), ("disabled", p["boton_deshabilitado"])],
        foreground=[("disabled", p["texto_deshabilitado"])],
    )
    estilo.map(
        "Panel.Accion.TButton",
        background=[("active", p["azul_hover"]), ("disabled", p["borde"])],
        foreground=[("disabled", "#FFFFFF")],
    )

    estilo.configure(
        "TEntry", fieldbackground=p["campo"], foreground=p["texto"],
        bordercolor=p["borde"], padding=5,
    )
    estilo.configure(
        "Panel.TEntry", fieldbackground=p["campo"], foreground=p["texto"],
        bordercolor=p["borde"], padding=5,
    )
    estilo.map("TEntry", bordercolor=[("focus", p["azul"])])
    estilo.map("Panel.TEntry", bordercolor=[("focus", p["azul"])])
    estilo.configure(
        "TSpinbox", fieldbackground=p["campo"], foreground=p["texto"],
        bordercolor=p["borde"], padding=4, arrowsize=12,
    )
    estilo.map("TSpinbox", bordercolor=[("focus", p["azul"])])
    for prefijo in ("", "Panel."):
        estilo.configure(
            f"{prefijo}Matriz.Control.TButton", padding=(4, 1), width=2,
            background=p["tarjeta"], foreground=p["titulo"],
            bordercolor=p["borde"], relief="flat",
        )
        estilo.map(
            f"{prefijo}Matriz.Control.TButton",
            background=[("active", p["seleccion"])],
            foreground=[("disabled", p["texto_deshabilitado"])],
        )
        estilo.configure(
            f"{prefijo}Matriz.Valor.TLabel", background=p["campo"], foreground=p["texto"],
            padding=(5, 1), relief="solid",
        )
    estilo.configure(
        "TCombobox", fieldbackground=p["campo"], foreground=p["texto"],
        bordercolor=p["borde"], padding=4, arrowsize=12,
    )
    estilo.map(
        "TCombobox", fieldbackground=[("readonly", p["campo"])],
        bordercolor=[("focus", p["azul"])],
    )
    estilo.configure("TRadiobutton", background=p["fondo"], foreground=p["texto"], font=(base, 10))
    estilo.map(
        "TRadiobutton", foreground=[("disabled", p["texto_deshabilitado"])],
        background=[("active", p["tarjeta"])],
    )
    estilo.configure(
        "TScrollbar", background=p["barra"], troughcolor=p["tarjeta"], bordercolor=p["fondo"],
        relief="flat", arrowsize=0, width=9,
    )
    for orientacion in ("Vertical", "Horizontal"):
        estilo.configure(
            f"Matriz.{orientacion}.TScrollbar",
            background=p["azul"], troughcolor=p["seleccion"],
            bordercolor=p["superficie"], relief="flat",
            arrowsize=0, width=13,
        )
        estilo.map(
            f"Matriz.{orientacion}.TScrollbar",
            background=[("active", p["azul_hover"])],
        )

    estilo.configure(
        "Biseccion.Treeview", background=p["superficie"], fieldbackground=p["superficie"],
        foreground=p["texto"], rowheight=32,
    )
    estilo.map(
        "Biseccion.Treeview", background=[("selected", p["seleccion"])],
        foreground=[("selected", p["texto"])],
    )
    estilo.configure(
        "Biseccion.Treeview.Heading", background=p["tarjeta"],
        foreground=p["texto_suave"], font=(base, 10, "bold"),
    )
    estilo.map("Biseccion.Treeview.Heading", background=[("active", p["seleccion"])])
    for orientacion in ("Vertical", "Horizontal"):
        estilo.configure(
            f"Biseccion.{orientacion}.TScrollbar", background=p["barra"],
            troughcolor=p["superficie"], bordercolor=p["superficie"],
        )


def actualizar_widgets(raiz, oscuro=False):
    """Actualiza los widgets Tk clásicos y las etiquetas de tabla ya creados."""
    p = _PALETAS[bool(oscuro)]

    def recorrer(padre):
        dentro_de_panel = isinstance(padre, ttk.LabelFrame)
        for widget in padre.winfo_children():
            clase = widget.winfo_class()
            en_panel = dentro_de_panel or isinstance(widget, ttk.LabelFrame)
            if clase == "Text":
                widget.configure(
                    background=p["campo"], foreground=p["texto"],
                    insertbackground=p["azul_hover"],
                    highlightbackground=p["borde"], highlightcolor=p["azul"],
                    selectbackground=p["seleccion"], selectforeground=p["texto"],
                )
                if getattr(widget, "resultado_destacado", False) is True:
                    widget.tag_configure("respuesta", background=p["decision"], foreground=p["azul_hover"])
                    widget.tag_configure("advertencia", background=p["parada_no"], foreground=p["rojo"])
                    widget.tag_configure("seccion", foreground=p["azul_hover"])
            elif clase == "Canvas":
                configurar_colores = getattr(widget, "configurar_colores", None)
                if configurar_colores is not None:
                    configurar_colores(p["barra_matriz"], p["azul"])
                else:
                    widget.configure(background=p["superficie"])
            if isinstance(widget, ttk.Treeview):
                estilos_fila = {
                    "fila_par": (p["superficie"], p["texto"]),
                    "fila_impar": (p["fila_alterna"], p["texto"]),
                    "detalle": (p["detalle"], p["texto_suave"]),
                    "decision": (p["decision"], p["azul_hover"]),
                    "parada_ok": (p["parada_ok"], p["verde"]),
                    "parada_no": (p["parada_no"], p["rojo"]),
                }
                for nombre, (fondo, texto) in estilos_fila.items():
                    widget.tag_configure(nombre, background=fondo, foreground=texto)
            if en_panel:
                estilo_actual = str(widget.cget("style")) if isinstance(widget, ttk.Widget) else ""
                if estilo_actual.startswith("Panel."):
                    estilo_actual = estilo_actual[len("Panel."):]
                if clase == "TLabel":
                    variante = estilo_actual if estilo_actual.endswith(".TLabel") else "TLabel"
                    widget.configure(style=f"Panel.{variante}")
                elif clase == "TFrame" and estilo_actual in ("", "TFrame"):
                    widget.configure(style="Panel.TFrame")
                elif clase == "TButton":
                    variante = (
                        estilo_actual if estilo_actual.startswith("Matriz.")
                        else "Accion.TButton" if estilo_actual == "Accion.TButton"
                        else "TButton"
                    )
                    widget.configure(style=f"Panel.{variante}")
                elif clase == "TEntry" and estilo_actual in ("", "TEntry"):
                    widget.configure(style="Panel.TEntry")
            recorrer(widget)

    recorrer(raiz)
