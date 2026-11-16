"""Ventana aparte con el plano cartesiano para un `Dibujo` (vectores o sistemas 2×2)."""

from tkinter import ttk

from interfaz.componentes import abrir_ventana
from interfaz.dibujos import encuadre_proporcional
from interfaz.motorGrafica import PlanoCartesiano


def abrir_plano(dueno, clave, titulo, dibujo):
    ventana = abrir_ventana(dueno, clave, titulo, tamano="860x600")
    marco = ttk.Frame(ventana, padding=16)
    marco.pack(fill="both", expand=True)
    marco.columnconfigure(0, weight=1)
    marco.rowconfigure(0, weight=1)
    plano = PlanoCartesiano(marco)
    plano.grid(row=0, column=0, sticky="nsew")
    plano.definir_funcion(None, dibujo.curvas)
    plano.definir_capas(dibujo.capas)
    plano.definir_puntos(dibujo.puntos)

    def ajustar(_evento=None):
        """Misma escala en x e y: un ángulo recto se ve recto; se rehace al cambiar el tamaño."""
        if plano.ajuste_automatico and plano.winfo_width() > 60:
            plano.encuadrar(*encuadre_proporcional(dibujo.encuadre, plano.winfo_width(), plano.winfo_height()))
    plano.bind("<Configure>", ajustar, add="+")
    ventana.after(60, ajustar)
    ttk.Label(marco, text=dibujo.nota, style="Ayuda.TLabel", wraplength=800, justify="left").grid(
        row=1, column=0, sticky="w", pady=(10, 0))
    ttk.Label(marco, text="Rueda: zoom · arrastrar: mover · doble clic: vista estándar",
              style="Tenue.TLabel").grid(row=2, column=0, sticky="w", pady=(4, 0))
    ventana.plano = plano
    return ventana
