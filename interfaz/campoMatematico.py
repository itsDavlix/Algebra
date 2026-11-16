"""Campos de entrada matemáticos: escritura natural, atajos y validación en vivo.

CampoMatematico (funciones de x):
- Autocompletado al escribir letras (Tab/Enter acepta, ↑↓ elige, Esc cierra).
- Atajos con Ctrl (⌘ en Mac): R √, L ln, E exp, P π, S sin, K cos, T tan,
  B |x|, 6 potencia. Si hay texto seleccionado, la función lo envuelve.
- Paréntesis automáticos y vista previa en notación legible con ✓ o el error.

CampoValor (números): admite 2,5 · pi/2 · sqrt(2) · 1e-6 y muestra su valor.
"""

import re
import tkinter as tk
from tkinter import ttk

from interfaz.estilos import PALETA, fuente
from nucleo.expresiones import DESCRIPCIONES, analizar, evaluar_valor, nombres_disponibles

RETARDO_VALIDACION = 220

ATAJOS = {
    "r": ("sqrt", "raíz cuadrada"), "l": ("ln", "logaritmo natural"), "e": ("exp", "exponencial"),
    "p": ("pi", "π"), "s": ("sin", "seno"), "k": ("cos", "coseno"), "t": ("tan", "tangente"),
    "b": ("abs", "valor absoluto"), "6": ("^", "potencia"),
}


def _modificador(widget):
    return "Command" if widget.tk.call("tk", "windowingsystem") == "aqua" else "Control"


def texto_atajos(widget):
    tecla_mod = "⌘" if _modificador(widget) == "Command" else "Ctrl+"
    simbolos = {"sqrt": "√", "pi": "π", "abs": "|x|", "^": "xⁿ"}
    return "   ".join(f"{tecla_mod}{tecla.upper()} {simbolos.get(nombre, nombre)}"
                      for tecla, (nombre, _) in ATAJOS.items())


class CampoMatematico(ttk.Frame):
    """Entrada de una función de x con sugerencias y validación en vivo."""

    def __init__(self, padre, etiqueta="f(x) =", al_cambiar=None, permitir_vacio=False,
                 texto_vacio="", ancho=40, panel=False, al_enter=None):
        super().__init__(padre, style="Panel.TFrame" if panel else "TFrame")
        self.al_cambiar = al_cambiar
        self.al_enter = al_enter
        self.permitir_vacio = permitir_vacio
        self.texto_vacio = texto_vacio
        self.expresion = None
        self.error = ""
        self._programado = None
        self._sugerencias = []
        self._indice = 0
        self._ultimo_texto = None
        prefijo = "Panel." if panel else ""
        self.columnconfigure(1, weight=1)
        self.etiqueta = ttk.Label(self, text=etiqueta, style=f"{prefijo}Formula.TLabel")
        self.etiqueta.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.variable = tk.StringVar()
        self.entrada = ttk.Entry(self, textvariable=self.variable, style="Formula.TEntry",
                                 font=fuente(12, mono=True), width=ancho)
        self.entrada.grid(row=0, column=1, sticky="ew")
        self.entrada.entrada_matematica = True
        self.vista = ttk.Label(self, text=texto_vacio, style=f"{prefijo}Pendiente.TLabel",
                               font=fuente(11), anchor="w")
        self.vista.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        self._crear_ventana_sugerencias()
        self.variable.trace_add("write", lambda *_: self._programar_validacion())
        self.entrada.bind("<KeyPress>", self._tecla, add="+")
        self.entrada.bind("<FocusOut>", lambda _e: self.after(120, self._ocultar_sugerencias), add="+")
        modificador = _modificador(self)
        for tecla in ATAJOS:
            self.entrada.bind(f"<{modificador}-{tecla}>", lambda e, t=tecla: self._atajo(t, e))
            if tecla.isalpha():
                self.entrada.bind(f"<{modificador}-{tecla.upper()}>", lambda e, t=tecla: self._atajo(t, e))

    # ------------------------------------------------------------------ API
    def obtener(self):
        return self.variable.get()

    def establecer(self, texto):
        self.variable.set(texto)
        self.entrada.icursor("end")
        if self._programado is not None:
            self.after_cancel(self._programado)
        self._validar()

    def focus_set(self):
        self.entrada.focus_set()

    # ---------------------------------------------------------- validación
    def _programar_validacion(self):
        if self._programado is not None:
            self.after_cancel(self._programado)
        self._programado = self.after(RETARDO_VALIDACION, self._validar)
        self._actualizar_sugerencias()

    def _validar(self):
        self._programado = None
        texto = self.variable.get()
        if texto == self._ultimo_texto:
            return
        self._ultimo_texto = texto
        if not texto.strip():
            self.expresion, self.error = None, ""
            self.entrada.state(["!invalid"])
            self.vista.configure(text=self.texto_vacio, foreground=PALETA["texto_suave"])
        else:
            try:
                self.expresion = analizar(texto)
                self.error = ""
            except ValueError as exc:
                self.expresion, self.error = None, str(exc)
            if self.expresion is not None:
                self.entrada.state(["!invalid"])
                self.vista.configure(text=f"✓  {self.expresion.bonito}", foreground=PALETA["exito"])
            else:
                self.entrada.state(["invalid"])
                self.vista.configure(text=f"✗  {self.error}", foreground=PALETA["error"])
        if self.al_cambiar:
            self.al_cambiar(self.expresion)

    def mostrar_nota(self, texto, color=None):
        """Permite a la vista sustituir la línea inferior (p. ej. derivada automática)."""
        self.vista.configure(text=texto, foreground=color or PALETA["texto_suave"])

    # ------------------------------------------------------------- edición
    def _insertar(self, nombre):
        entrada = self.entrada
        if nombre == "^":
            entrada.insert("insert", "^")
            return "break"
        if nombre in ("pi", "e"):
            entrada.insert("insert", nombre)
            return "break"
        if entrada.selection_present():
            inicio, fin = entrada.index("sel.first"), entrada.index("sel.last")
            seleccionado = entrada.get()[inicio:fin]
            entrada.delete(inicio, fin)
            entrada.insert(inicio, f"{nombre}({seleccionado})")
            entrada.icursor(inicio + len(nombre) + len(seleccionado) + 2)
        else:
            posicion = entrada.index("insert")
            entrada.insert(posicion, f"{nombre}()")
            entrada.icursor(posicion + len(nombre) + 1)
        return "break"

    def _atajo(self, tecla, evento=None):
        # En Windows, AltGr llega como Ctrl+Alt: en teclados en español escribe
        # símbolos como € o ^. Si Alt también está pulsado, no es un atajo.
        if evento is not None and self.tk.call("tk", "windowingsystem") == "win32" and evento.state & 0x20000:
            return None
        if str(self.entrada.cget("state")) != "normal" or "readonly" in self.entrada.state():
            return "break"
        self._ocultar_sugerencias()
        return self._insertar(ATAJOS[tecla][0])

    def _tecla(self, evento):
        if self._sugerencias_visibles():
            if evento.keysym in ("Down", "Up"):
                self._indice = (self._indice + (1 if evento.keysym == "Down" else -1)) % len(self._sugerencias)
                self._pintar_sugerencias()
                return "break"
            if evento.keysym in ("Tab", "Return", "KP_Enter"):
                self._aceptar(self._sugerencias[self._indice])
                return "break"
            if evento.keysym == "Escape":
                self._ocultar_sugerencias()
                return "break"
        if evento.keysym in ("Return", "KP_Enter") and self.al_enter:
            if self._programado is not None:
                self.after_cancel(self._programado)
                self._validar()
            self.al_enter()
            return "break"
        entrada = self.entrada
        texto = entrada.get()
        posicion = entrada.index("insert")
        if evento.char == "(":
            if entrada.selection_present():
                inicio, fin = entrada.index("sel.first"), entrada.index("sel.last")
                seleccionado = texto[inicio:fin]
                entrada.delete(inicio, fin)
                entrada.insert(inicio, f"({seleccionado})")
                entrada.icursor(inicio + len(seleccionado) + 2)
            else:
                entrada.insert(posicion, "()")
                entrada.icursor(posicion + 1)
            return "break"
        if evento.char == ")" and texto[posicion:posicion + 1] == ")":
            entrada.icursor(posicion + 1)
            return "break"
        if evento.keysym == "BackSpace" and not entrada.selection_present() and posicion > 0:
            if texto[posicion - 1:posicion + 1] == "()":
                entrada.delete(posicion - 1, posicion + 1)
                return "break"
        return None

    # -------------------------------------------------------- sugerencias
    def _crear_ventana_sugerencias(self):
        self.ventana = tk.Toplevel(self)
        self.ventana.withdraw()
        self.ventana.overrideredirect(True)
        self.ventana.configure(background=PALETA["borde_fuerte"])
        self.marco_sugerencias = tk.Frame(self.ventana, background=PALETA["tarjeta"])
        self.marco_sugerencias.pack(padx=1, pady=1)
        self.filas = []
        self.pie = tk.Label(self.ventana, text="Tab o Enter para completar · Esc para cerrar",
                            background=PALETA["superficie"], foreground=PALETA["texto_tenue"],
                            font=fuente(8), anchor="w", padx=8, pady=3)
        self.pie.pack(fill="x", padx=1, pady=(0, 1))

    def _palabra_actual(self):
        texto = self.entrada.get()[:self.entrada.index("insert")]
        coincidencia = re.search(r"[A-Za-z_][A-Za-z_0-9]*$", texto)
        return coincidencia.group(0) if coincidencia else ""

    def _actualizar_sugerencias(self):
        if self.focus_get() is not self.entrada:
            self._ocultar_sugerencias()
            return
        palabra = self._palabra_actual().lower()
        if not palabra or palabra == "x":
            self._ocultar_sugerencias()
            return
        candidatos = [n for n in nombres_disponibles() if n.startswith(palabra) and n != palabra]
        # «xs» -> sugiere funciones para la parte final («s»).
        if not candidatos and palabra.startswith("x"):
            candidatos = [n for n in nombres_disponibles() if n.startswith(palabra.lstrip("x"))]
        if not candidatos:
            self._ocultar_sugerencias()
            return
        self._sugerencias = candidatos[:7]
        self._indice = 0
        self._pintar_sugerencias()
        x = self.entrada.winfo_rootx()
        y = self.entrada.winfo_rooty() + self.entrada.winfo_height() + 2
        self.ventana.geometry(f"+{x}+{y}")
        self.ventana.deiconify()
        self.ventana.lift()

    def _pintar_sugerencias(self):
        for fila in self.filas:
            fila.destroy()
        self.filas = []
        for indice, nombre in enumerate(self._sugerencias):
            activo = indice == self._indice
            fondo = PALETA["acento_suave"] if activo else PALETA["tarjeta"]
            fila = tk.Frame(self.marco_sugerencias, background=fondo, cursor="hand2")
            fila.pack(fill="x")
            muestra = nombre if nombre in ("pi", "e") else f"{nombre}( )"
            tk.Label(fila, text=muestra, background=fondo, foreground=PALETA["texto"],
                     font=fuente(11, mono=True), width=10, anchor="w", padx=8, pady=3).pack(side="left")
            tk.Label(fila, text=DESCRIPCIONES.get(nombre, ""), background=fondo,
                     foreground=PALETA["texto_suave"], font=fuente(9), anchor="w", padx=8).pack(side="left")
            for widget in (fila, *fila.winfo_children()):
                widget.bind("<Button-1>", lambda _e, n=nombre: self._aceptar(n))
            self.filas.append(fila)

    def _sugerencias_visibles(self):
        return bool(self._sugerencias) and self.ventana.winfo_viewable()

    def _aceptar(self, nombre):
        palabra = self._palabra_actual()
        posicion = self.entrada.index("insert")
        prefijo = palabra
        if not nombre.startswith(palabra.lower()):
            prefijo = palabra.lstrip("x")
        self.entrada.delete(posicion - len(prefijo), posicion)
        self._ocultar_sugerencias()
        self._insertar(nombre)
        self.entrada.focus_set()

    def _ocultar_sugerencias(self):
        self._sugerencias = []
        try:
            self.ventana.withdraw()
        except tk.TclError:
            pass


class CampoValor(ttk.Frame):
    """Entrada numérica con validación en vivo; acepta operaciones sin x."""

    def __init__(self, padre, etiqueta, contexto=None, ancho=12, al_cambiar=None, panel=True, al_enter=None):
        super().__init__(padre, style="Panel.TFrame" if panel else "TFrame")
        prefijo = "Panel." if panel else ""
        self.contexto = contexto or f"El valor {etiqueta}"
        self.al_cambiar = al_cambiar
        self.variable = tk.StringVar()
        self.etiqueta = ttk.Label(self, text=etiqueta, style=f"{prefijo}Formula.TLabel")
        self.etiqueta.grid(row=0, column=0, sticky="w")
        self.entrada = ttk.Entry(self, textvariable=self.variable, width=ancho, font=fuente(11, mono=True))
        self.entrada.configure(width=1)  # el ancho lo decide la columna, no el texto
        self.entrada.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        self.nota = ttk.Label(self, text="", style=f"{prefijo}Tenue.TLabel")
        self.nota.grid(row=2, column=0, sticky="w")
        self.nota.grid_remove()  # solo ocupa alto cuando muestra algo
        self.columnconfigure(0, weight=1)
        self.variable.trace_add("write", lambda *_: self._validar())
        if al_enter:
            self.entrada.bind("<Return>", lambda _e: al_enter())
            self.entrada.bind("<KP_Enter>", lambda _e: al_enter())

    def obtener(self):
        return evaluar_valor(self.variable.get(), self.contexto)

    def habilitar(self, activo):
        self.entrada.state(["!disabled"] if activo else ["disabled"])

    def establecer(self, texto):
        self.variable.set(texto)

    def _validar(self):
        texto = self.variable.get().strip()
        valor = None
        if not texto:
            self.entrada.state(["!invalid"])
            self.nota.configure(text="")
        else:
            try:
                valor = evaluar_valor(texto, self.contexto)
            except ValueError:
                self.entrada.state(["invalid"])
                self.nota.configure(text="valor no válido", foreground=PALETA["error"])
            else:
                self.entrada.state(["!invalid"])
                simple = re.fullmatch(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?", texto)
                self.nota.configure(text="" if simple else f"= {valor:.6g}", foreground=PALETA["texto_tenue"])
        if self.nota.cget("text"):
            self.nota.grid()
        else:
            self.nota.grid_remove()
        if self.al_cambiar:
            self.al_cambiar()
