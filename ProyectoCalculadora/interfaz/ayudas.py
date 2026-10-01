
import tkinter as tk
from tkinter import ttk, messagebox


def mostrar_texto(caja, texto):
    """Reemplaza de forma segura el contenido de un Text usado como salida."""
    estado_anterior = str(caja.cget("state"))
    if estado_anterior == "disabled":
        caja.configure(state="normal")
    caja.delete("1.0", "end")
    caja.insert("1.0", texto)
    caja.see("1.0")
    if estado_anterior == "disabled":
        caja.configure(state="disabled")


def mostrar_error(error):
    """Muestra un error de validación en una ventana emergente."""
    messagebox.showerror("Revisa los datos", str(error))


def crear_area_resultado(padre, alto=10, fuente=("Consolas", 11)):
    """Crea un widget Text de solo salida, con barra de desplazamiento vertical."""
    marco = ttk.Frame(padre)
    marco.columnconfigure(0, weight=1)
    marco.rowconfigure(0, weight=1)

    texto = tk.Text(marco, height=alto, wrap="word", font=fuente, state="disabled")
    barra = ttk.Scrollbar(marco, orient="vertical", command=texto.yview)
    texto.configure(yscrollcommand=barra.set)
    texto.grid(row=0, column=0, sticky="nsew")
    barra.grid(row=0, column=1, sticky="ns")
    return marco, texto


class AyudaEmergente:
    """Ayuda emergente (tooltip) que aparece al pasar el cursor sobre un widget."""

    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self.ventana = None
        widget.bind("<Enter>", self._mostrar)
        widget.bind("<Leave>", self._ocultar)

    def _mostrar(self, _evento=None):
        if self.ventana or not self.texto:
            return
        x = self.widget.winfo_rootx() + 4
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.ventana = tk.Toplevel(self.widget)
        self.ventana.wm_overrideredirect(True)
        self.ventana.wm_geometry(f"+{x}+{y}")
        ttk.Label(
            self.ventana, text=self.texto, justify="left", padding=(6, 3),
            background="#fffbdd", relief="solid", borderwidth=1,
        ).pack()

    def _ocultar(self, _evento=None):
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None