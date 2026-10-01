"""Pestaña para operaciones con números romanos y procedimiento paso a paso."""

from tkinter import ttk

from nucleo.romanos import operar_romanos_con_pasos, romano_a_entero
from interfaz.ayudas import mostrar_texto, mostrar_error, crear_area_resultado, AyudaEmergente


class PestanaRomanos(ttk.Frame):
    """Permite sumar, restar, multiplicar y dividir números romanos."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_entrada()
        self._construir_resultado()

    def _construir_entrada(self):
        marco = ttk.LabelFrame(
            self,
            text="Operaciones con números romanos",
            style="Seccion.TLabelframe",
            padding=14,
        )
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        ttk.Label(marco, text="Número romano A:").pack(anchor="w")
        self.ent_a = ttk.Entry(marco)
        self.ent_a.pack(fill="x", pady=(2, 10))
        self.ent_a.insert(0, "XIV")
        AyudaEmergente(self.ent_a, "Ejemplos válidos: IV, IX, XIV, XL, MCMXC.")

        ttk.Label(marco, text="Número romano B:").pack(anchor="w")
        self.ent_b = ttk.Entry(marco)
        self.ent_b.pack(fill="x", pady=(2, 12))
        self.ent_b.insert(0, "VI")

        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=4)
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        ttk.Button(botones, text="Sumar (A + B)", command=lambda: self._operar("+")).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Restar (A − B)", command=lambda: self._operar("-")).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Multiplicar (A × B)", command=lambda: self._operar("*")).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(botones, text="Dividir (A ÷ B)", command=lambda: self._operar("/")).grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        ttk.Button(marco, text="Limpiar", command=self._limpiar).pack(fill="x", pady=(10, 0))

        ttk.Label(
            marco,
            text=(
                "Se usa la notación romana estándar de I a MMMCMXCIX (1 a 3999). "
                "La división debe producir un entero exacto."
            ),
            style="Ayuda.TLabel",
            wraplength=390,
            justify="left",
        ).pack(anchor="w", pady=(14, 0))

    def _construir_resultado(self):
        marco = ttk.LabelFrame(self, text="Resultado y procedimiento paso a paso", style="Seccion.TLabelframe", padding=14)
        marco.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        marco_resultado, self.txt_resultado = crear_area_resultado(marco, alto=20)
        marco_resultado.pack(fill="both", expand=True)

    def _operar(self, simbolo):
        try:
            texto_a = self.ent_a.get()
            texto_b = self.ent_b.get()
            resultado_romano, resultado_decimal, pasos = operar_romanos_con_pasos(
                texto_a, texto_b, simbolo
            )
            separador = "\n\n" + "─" * 52 + "\n\n"
            decimal_comprobado = romano_a_entero(resultado_romano)
            comprobado = decimal_comprobado == resultado_decimal
            pasos.append(
                "COMPROBACIÓN. Convertir el resultado romano de nuevo a decimal debe conservar el valor:\n"
                f"{resultado_romano} = {decimal_comprobado}\n"
                + ("✓ La comprobación es correcta." if comprobado else "✗ La comprobación no coincide.")
            )
            salida = (
                f"RESULTADO ROMANO: {resultado_romano}\n"
                f"RESULTADO DECIMAL: {resultado_decimal}\n\n"
                + separador.join(pasos)
            )
            mostrar_texto(self.txt_resultado, salida)
        except ValueError as error:
            mostrar_error(error)

    def _limpiar(self):
        self.ent_a.delete(0, "end")
        self.ent_b.delete(0, "end")
        mostrar_texto(self.txt_resultado, "")
