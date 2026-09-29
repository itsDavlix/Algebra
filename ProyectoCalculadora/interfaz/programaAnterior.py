"""Pestaña Programa anterior: permite ejecutar un archivo .py elaborado previamente."""

import subprocess
import sys
from tkinter import ttk, filedialog, messagebox


class PestanaProgramaAnterior(ttk.Frame):
    """Selecciona y ejecuta, como proceso independiente, un script .py existente."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self._construir()

    def _construir(self):
        marco = ttk.LabelFrame(self, text="Abrir el programa anterior", style="Seccion.TLabelframe", padding=18)
        marco.pack(fill="both", expand=True)

        texto = (
            "Este módulo permite seleccionar otro archivo .py y ejecutarlo con el mismo "
            "intérprete de Python, para integrarlo con esta calculadora.\n\n"
            "1. Pulsa “Seleccionar y abrir .py”.\n"
            "2. Busca el archivo en tu computadora.\n"
            "3. El programa se abrirá en una ventana aparte."
        )
        ttk.Label(marco, text=texto, justify="left", wraplength=760, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 18))

        ttk.Button(marco, text="Seleccionar y abrir .py", style="Accion.TButton", command=self._accion_ejecutar).pack(anchor="w")

        self.lbl_estado = ttk.Label(marco, text="Todavía no se ha seleccionado ningún programa.", style="Ayuda.TLabel")
        self.lbl_estado.pack(anchor="w", pady=(14, 0))

    def _accion_ejecutar(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona el programa anterior",
            filetypes=[("Archivos Python", "*.py"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            subprocess.Popen([sys.executable, ruta])
            self.lbl_estado.config(text=f"En ejecución: {ruta}")
        except Exception as error:
            messagebox.showerror("No se pudo ejecutar", f"No fue posible ejecutar el archivo seleccionado.\n\n{error}")