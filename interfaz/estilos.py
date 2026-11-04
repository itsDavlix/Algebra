"""Módulo de estilos: apariencia visual azul y blanca compartida por toda la interfaz."""

import tkinter.font as tkfont

# Paleta: azules para acciones y estructura, blanco para el fondo, gris azulado para textos.
AZUL_OSCURO = "#1E3A8A"   # títulos y pestaña activa
AZUL = "#2563EB"          # botones principales
AZUL_HOVER = "#1D4ED8"    # botón al pasar el cursor
AZUL_CLARO = "#EFF6FF"    # tarjetas y zonas de apoyo
AZUL_BORDE = "#BFDBFE"    # bordes suaves
BLANCO = "#FFFFFF"
TEXTO = "#0F172A"
TEXTO_SUAVE = "#475569"
VERDE = "#15803D"         # validación correcta
ROJO = "#B91C1C"          # validación fallida


def _elegir_fuente(estilo, candidatas, por_defecto):
    """Devuelve la primera fuente instalada del sistema para verse bien en Windows y Mac."""
    instaladas = set(tkfont.families(estilo.master))
    return next((f for f in candidatas if f in instaladas), por_defecto)


def configurar_estilo(estilo):
    """Aplica el tema, los colores y las tipografías a todos los widgets ttk."""
    # Selecciona un tema compatible y fuentes disponibles en el sistema.
    try:
        estilo.theme_use("clam")
    except Exception:
        pass

    base = _elegir_fuente(estilo, ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial"), "Helvetica")
    mono = _elegir_fuente(estilo, ("Consolas", "Menlo", "Courier New"), "Courier")

    # Ajusta el fondo y la apariencia de los widgets Text clásicos.
    raiz = estilo.master
    raiz.configure(background=BLANCO)
    raiz.option_add("*Text.background", BLANCO)
    raiz.option_add("*Text.foreground", TEXTO)
    raiz.option_add("*Text.relief", "flat")
    raiz.option_add("*Text.borderWidth", 1)
    raiz.option_add("*Text.highlightThickness", 1)
    raiz.option_add("*Text.highlightBackground", AZUL_BORDE)
    raiz.option_add("*Text.highlightColor", AZUL)
    raiz.option_add("*Text.selectBackground", AZUL_BORDE)
    raiz.option_add("*Text.selectForeground", TEXTO)
    raiz.option_add("*Text.insertBackground", AZUL)
    raiz.option_add("*Text.padX", 8)
    raiz.option_add("*Text.padY", 6)
    raiz.option_add("*Text.font", (mono, 11))

    # Define los colores y fuentes generales de los componentes.
    estilo.configure(".", background=BLANCO, foreground=TEXTO, font=(base, 10),
                     bordercolor=AZUL_BORDE, focuscolor=AZUL)
    estilo.configure("TFrame", background=BLANCO)
    estilo.configure("Tarjeta.TFrame", background=AZUL_CLARO)
    estilo.configure("TLabel", background=BLANCO, foreground=TEXTO)

    # Distingue títulos, ayuda, validaciones y tarjetas informativas.
    estilo.configure("Titulo.TLabel", font=(base, 20, "bold"), foreground=AZUL_OSCURO)
    estilo.configure("Subtitulo.TLabel", font=(base, 11), foreground=TEXTO_SUAVE)
    estilo.configure("Ayuda.TLabel", font=(base, 9), foreground=TEXTO_SUAVE)
    estilo.configure("Negrita.TLabel", font=(base, 10, "bold"), foreground=AZUL_OSCURO)
    estilo.configure("Valido.TLabel", foreground=VERDE, font=(base, 10))
    estilo.configure("Error.TLabel", foreground=ROJO, font=(base, 10, "bold"))
    estilo.configure("Pendiente.TLabel", foreground=TEXTO_SUAVE, font=(base, 10))
    estilo.configure("Tarjeta.TLabel", background=AZUL_CLARO, foreground=AZUL_OSCURO, font=(base, 10))
    estilo.configure("TarjetaTitulo.TLabel", background=AZUL_CLARO, foreground=AZUL_OSCURO, font=(base, 10, "bold"))

    # Secciones con borde azul suave.
    estilo.configure("TLabelframe", background=BLANCO, bordercolor=AZUL_BORDE, relief="solid", borderwidth=1)
    estilo.configure("TLabelframe.Label", background=BLANCO, foreground=AZUL_OSCURO)
    estilo.configure("Seccion.TLabelframe", background=BLANCO, bordercolor=AZUL_BORDE)
    estilo.configure("Seccion.TLabelframe.Label", background=BLANCO, foreground=AZUL_OSCURO,
                     font=(base, 11, "bold"))

    # Pestañas: la activa en azul sólido, las demás en azul claro.
    estilo.configure("TNotebook", background=BLANCO, borderwidth=0, tabmargins=(0, 4, 0, 0))
    estilo.configure("TNotebook.Tab", background=AZUL_CLARO, foreground=AZUL_OSCURO,
                     padding=(16, 8), font=(base, 10, "bold"), borderwidth=0)
    estilo.map("TNotebook.Tab",
               background=[("selected", AZUL), ("active", AZUL_BORDE)],
               foreground=[("selected", BLANCO)])

    # Botones: secundarios en azul claro, principales en azul sólido.
    estilo.configure("TButton", padding=8, background=AZUL_CLARO, foreground=AZUL_OSCURO,
                     bordercolor=AZUL_BORDE, relief="flat", font=(base, 10))
    estilo.map("TButton", background=[("active", AZUL_BORDE), ("disabled", "#F1F5F9")],
               foreground=[("disabled", "#94A3B8")])
    estilo.configure("Accion.TButton", padding=10, background=AZUL, foreground=BLANCO,
                     font=(base, 10, "bold"), bordercolor=AZUL)
    estilo.map("Accion.TButton", background=[("active", AZUL_HOVER), ("disabled", "#BFDBFE")],
               foreground=[("disabled", BLANCO)])

    # Campos de entrada y opciones.
    estilo.configure("TEntry", fieldbackground=BLANCO, bordercolor=AZUL_BORDE, padding=5)
    estilo.map("TEntry", bordercolor=[("focus", AZUL)])
    estilo.configure("TRadiobutton", background=BLANCO, foreground=TEXTO, font=(base, 10))
    estilo.map("TRadiobutton", foreground=[("disabled", "#94A3B8")],
               background=[("active", AZUL_CLARO)])
    estilo.configure("TScrollbar", background=AZUL_BORDE, troughcolor=AZUL_CLARO, bordercolor=BLANCO)