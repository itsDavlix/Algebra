
import tkinter as tk
from tkinter import ttk, messagebox


# Actualiza áreas de salida que pueden estar bloqueadas para edición.
def mostrar_texto(caja, texto):
    """Reemplaza de forma segura el contenido de un Text usado como salida."""
    estado_anterior = str(caja.cget("state"))
    if estado_anterior == "disabled":
        caja.configure(state="normal")
    caja.delete("1.0", "end")
    caja.insert("1.0", texto)
    if getattr(caja, "resultado_destacado", False) is True:
        _marcar_resultado(caja, texto)
    caja.see("1.0")
    if estado_anterior == "disabled":
        caja.configure(state="disabled")


def mostrar_error(error):
    """Muestra un error de validación en una ventana emergente."""
    messagebox.showerror("Revisa los datos", str(error))


def _marcar_resultado(caja, texto):
    """Distingue la respuesta inicial de sus explicaciones sin alterar el texto."""
    lineas = texto.splitlines()
    if lineas and lineas[0].startswith(("RESPUESTA", "SIN CONVERGENCIA", "SIN SOLUCIÓN", "NO SE PUDO")):
        fin = next((i for i, linea in enumerate(lineas) if not linea.strip()), len(lineas))
        etiqueta = "respuesta" if lineas[0].startswith("RESPUESTA") else "advertencia"
        caja.tag_add(etiqueta, "1.0", f"{fin + 1}.0")
        for indice, linea in enumerate(lineas[:fin], 1):
            if linea.startswith("x ≈"):
                caja.tag_add("valor_raiz", f"{indice}.0", f"{indice}.end")
    for indice, linea in enumerate(lineas, 1):
        if linea.startswith(("COMPROBACIÓN", "EXPLICACIÓN", "DATOS", "FÓRMULA", "ITERACIÓN", "PASO ")):
            caja.tag_add("seccion", f"{indice}.0", f"{indice}.end")
        elif linea.startswith("AVISO:"):
            caja.tag_add("advertencia", f"{indice}.0", f"{indice}.end")


def crear_area_resultado(padre, alto=10, fuente=("TkFixedFont", 11), destacado=False):
    """Crea un widget Text de solo salida, con barra de desplazamiento vertical."""
    marco = ttk.Frame(padre)
    marco.columnconfigure(0, weight=1)
    marco.rowconfigure(0, weight=1)

    texto = tk.Text(
        marco, width=52, height=alto, wrap="word", font=fuente, state="disabled",
    )
    if destacado:
        texto.resultado_destacado = True
        texto.configure(padx=12, pady=10, spacing1=2, spacing3=4, relief="flat")
        texto.tag_configure("respuesta", font=("TkFixedFont", 12, "bold"),
                            background="#F0ECF8", foreground="#51417D")
        texto.tag_configure("advertencia", font=("TkFixedFont", 11, "bold"),
                            background="#FEF2F2", foreground="#B91C1C")
        texto.tag_configure("valor_raiz", font=("TkFixedFont", 16, "bold"))
        texto.tag_configure("seccion", font=("TkDefaultFont", 11, "bold"),
                            spacing1=12, spacing3=6)
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
