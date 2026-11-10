"""Paleta flotante que escribe en el último campo de datos seleccionado."""

import re
import tkinter as tk
from tkinter import ttk

from interfaz.ayudas import AyudaEmergente


class BarraMatematica:
    """Conserva el campo y su selección al pulsar los botones de la paleta."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.ventana = None
        self.destino = None
        self.al_cerrar = None
        self.botones = []
        raiz.bind_all("<FocusIn>", self._recordar_campo, add="+")
        raiz.bind_all("<<NotebookTabChanged>>", self._cambiar_pestana, add="+")

    @property
    def visible(self):
        return self.ventana is not None and self.ventana.winfo_exists() and self.ventana.state() != "withdrawn"

    def _editable(self, widget):
        return (
            isinstance(widget, (tk.Entry, ttk.Entry, tk.Text))
            and widget.winfo_exists()
            and str(widget.cget("state")) == "normal"
        )

    def _recordar_campo(self, evento):
        if self._editable(evento.widget):
            self.destino = evento.widget
            # Mantiene la selección al activar la ventana flotante.
            self.destino.configure(exportselection=False)
            self._actualizar_botones()

    def _cambiar_pestana(self, _evento=None):
        self.destino = None
        self._actualizar_botones()

    def alternar(self):
        if self.visible:
            self.ocultar()
            return
        if self.ventana is None or not self.ventana.winfo_exists():
            self._crear()
        self.ventana.deiconify()
        self.ventana.lift()
        self._actualizar_botones()

    def ocultar(self, _evento=None):
        if self.ventana is not None:
            self.ventana.withdraw()
        if self.al_cerrar:
            self.al_cerrar()

    def _crear(self):
        self.ventana = tk.Toplevel(self.raiz)
        self.ventana.withdraw()
        self.ventana.title("Símbolos matemáticos")
        self.ventana.transient(self.raiz)
        self.ventana.resizable(False, False)
        self.ventana.protocol("WM_DELETE_WINDOW", self.ocultar)
        self.ventana.bind("<Escape>", self.ocultar)
        contenido = ttk.Frame(self.ventana, padding=12)
        contenido.pack(fill="both", expand=True)
        self.estado = ttk.Label(contenido, wraplength=440, style="Ayuda.TLabel")
        self.estado.pack(fill="x", pady=(0, 8))
        grupos = (
            ("Funciones (ángulos en radianes)", (
                ("sen", "sin(", ")"), ("cos", "cos(", ")"), ("tan", "tan(", ")"),
                ("arccos", "acos(", ")"),
                ("√", "sqrt(", ")"), ("|x|", "abs(", ")"),
                ("ln", "log(", ")"), ("log₁₀", "log10(", ")"), ("exp", "exp(", ")"),
            ), "expresion"),
            ("Operaciones y constantes", (
                ("×", "*", ""), ("÷", "/", ""), ("xʸ", "**", ""),
                ("^", "^", ""),
                ("x²", "**2", ""), ("( )", "(", ")"), ("=", " = ", ""),
                ("x", "x", ""), ("π", "pi", ""), ("e", "e", ""),
            ), "expresion"),
            ("Condiciones de funciones por tramos", (
                ("<", " < ", ""), (">", " > ", ""),
                ("≤", " <= ", ""), ("≥", " >= ", ""),
                ("≠", " != ", ""), ("==", " == ", ""),
                ("si(…)", "si(x < 0, -x, x)", ""),
            ), "expresion"),
            ("Números", tuple((n, n, "") for n in "7894561230") + (
                (".", ".", ""), ("+", "+", ""), ("−", "-", ""),
                ("×10ⁿ", "e-", ""),
            ), "numero"),
            ("Separadores de vectores y matrices", (
                ("Espacio", " ", ""), (",", ",", ""),
                (";", ";", ""), ("Nueva fila", "\n", ""),
            ), "separador"),
        )
        self.botones.clear()
        for titulo, opciones, tipo in grupos:
            marco = ttk.LabelFrame(contenido, text=titulo, padding=5)
            marco.pack(fill="x", pady=(0, 6))
            for indice, (etiqueta, prefijo, sufijo) in enumerate(opciones):
                boton = ttk.Button(
                    marco, text=etiqueta, width=7, takefocus=False,
                    command=lambda p=prefijo, s=sufijo: self.insertar(p, s),
                )
                boton.grid(row=indice // 5, column=indice % 5, padx=2, pady=2, sticky="ew")
                marco.columnconfigure(indice % 5, weight=1)
                ayuda = {
                    "**": "Elevado a: escribe la base, pulsa xʸ y escribe el exponente. Ejemplo: 2**3 = 8.",
                    "^": "Elevado a: escribe la base, pulsa ^ y escribe el exponente. Ejemplo: 2^3 = 8.",
                    "cos(": "Coseno: cos(x), con el ángulo en radianes.",
                    "acos(": "Coseno inverso: arccos(x). Admite valores entre -1 y 1 y devuelve radianes.",
                }.get(prefijo)
                AyudaEmergente(boton, ayuda or "Inserta: " + (prefijo + "…" + sufijo if sufijo else repr(prefijo)))
                self.botones.append((boton, tipo, prefijo))
        ttk.Button(contenido, text="Cerrar", command=self.ocultar, takefocus=False).pack(anchor="e")
        ttk.Label(
            contenido, text="Tramos: si(x < 0, -x, x). Las comparaciones se usan dentro de si(…).\n"
            "Los métodos buscan raíces de funciones continuas, no soluciones de inecuaciones.",
            wraplength=440, style="Ayuda.TLabel",
        ).pack(fill="x", pady=(6, 0))
        self.ventana.update_idletasks()
        x = min(self.raiz.winfo_rootx() + self.raiz.winfo_width() - self.ventana.winfo_reqwidth(),
                self.raiz.winfo_screenwidth() - self.ventana.winfo_reqwidth())
        y = min(self.raiz.winfo_rooty() + 70,
                self.raiz.winfo_screenheight() - self.ventana.winfo_reqheight())
        self.ventana.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _actualizar_botones(self):
        if self.ventana is None:
            return
        campo = self.destino
        disponible = self._editable(campo) and campo.winfo_viewable()
        expresion = disponible and getattr(campo, "entrada_matematica", False)
        self.estado.configure(text=(
            "Selecciona primero el campo donde quieres escribir."
            if not disponible else
            "Escribe en la ecuación seleccionada. Selecciona texto para envolverlo en una función."
            if expresion else
            "Escribe en el campo seleccionado. Las funciones se habilitan en Bisección y Regula Falsi."
        ))
        for boton, tipo, prefijo in self.botones:
            habilitado = disponible and (
                tipo == "numero" or (tipo == "expresion" and expresion)
                or (tipo == "separador" and (
                    (expresion and prefijo in (" ", ","))
                    or (not expresion and getattr(campo, "entrada_lista", False)
                        and (prefijo not in ("\n", ";") or isinstance(campo, tk.Text)))
                ))
            )
            boton.state(["!disabled" if habilitado else "disabled"])

    def insertar(self, prefijo, sufijo=""):
        """Inserta en el cursor; las funciones envuelven el texto seleccionado."""
        campo = self.destino
        if not self._editable(campo) or not campo.winfo_viewable():
            self._actualizar_botones()
            return
        if isinstance(campo, tk.Text):
            seleccion = campo.tag_ranges("sel")
            inicio = str(seleccion[0]) if seleccion else campo.index("insert")
            texto = campo.get(*seleccion) if seleccion else ""
            if seleccion:
                campo.delete(*seleccion)
            campo.insert(inicio, prefijo + (texto if sufijo else "") + sufijo)
            cursor = f"{inicio}+{len(prefijo) + (len(texto) + len(sufijo) if texto and sufijo else 0)}c"
            campo.mark_set("insert", cursor)
            campo.tag_remove("sel", "1.0", "end")
            campo.see("insert")
        else:
            seleccion = campo.selection_present()
            inicio = campo.index("sel.first") if seleccion else campo.index("insert")
            fin = campo.index("sel.last") if seleccion else inicio
            contenido = campo.get()
            texto = contenido[inicio:fin]
            if texto and prefijo in ("**", "**2", "^"):
                prefijo, sufijo = "(", ")" + prefijo
            if getattr(campo, "entrada_matematica", False) and (
                sufijo or prefijo in ("x", "pi", "e") or prefijo.startswith("si(")
            ):
                if re.search(r"(?:\d|\)|\bx|\bpi|\be)\s*$", contenido[:inicio]):
                    prefijo = "*" + prefijo
                if re.match(r"\s*(?:\d|x\b|pi\b|e\b|[a-z]+\(|\()", contenido[fin:]):
                    if sufijo:
                        sufijo += "*"
                    else:
                        prefijo += "*"
            if seleccion:
                campo.delete(inicio, fin)
            campo.insert(inicio, prefijo + (texto if sufijo else "") + sufijo)
            campo.icursor(inicio + len(prefijo) + (len(texto) + len(sufijo) if texto and sufijo else 0))
            campo.selection_clear()
            campo.xview("insert")
        campo.focus_set()
