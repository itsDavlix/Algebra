"""Módulo de estilos: apariencia visual compartida por toda la interfaz."""


def configurar_estilo(estilo):
    try:
        estilo.theme_use("clam")
    except Exception:
        pass

    estilo.configure("Titulo.TLabel", font=("Segoe UI", 19, "bold"))
    estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 11))
    estilo.configure("Ayuda.TLabel", font=("Segoe UI", 9), foreground="#555555")
    estilo.configure("Seccion.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
    estilo.configure("TButton", padding=7)
    estilo.configure("Accion.TButton", padding=9)