"""Pestaña Inicio: guía rápida de uso de la calculadora."""

from tkinter import ttk

from interfaz.ayudas import crear_area_resultado, mostrar_texto
from interfaz.estilos import PALETA, fuente


class PestanaInicio(ttk.Frame):
    """Explica el formato de entrada y qué operaciones ofrece cada módulo."""

    def __init__(self, padre):
        super().__init__(padre, padding=16)
        self._construir()

    def _construir(self):
        # La guía se adapta al ancho y permite recorrer todo el contenido.
        marco = ttk.LabelFrame(self, text="Bienvenido a CalcuMaxing", style="Seccion.TLabelframe", padding=18)
        marco.pack(fill="both", expand=True)

        texto = (
            "Elige una herramienta en el menú lateral, escribe los datos y pulsa la operación. "
            "Los resultados muestran primero la respuesta y debajo el procedimiento.\n\n"
            "ÁLGEBRA LINEAL\n"
            "• Vectores: suma, resta, escalar, producto punto, producto cruz en R³, norma, "
            "combinación lineal e independencia lineal, con pasos y comprobaciones.\n"
            "• Matrices: det(A) por cofactores o LU (comprobado con el otro método), A⁻¹ justificada con "
            "det(A) ≠ 0 y verificada con A·A⁻¹ = I, transpuesta, rango y operaciones entre matrices. "
            "Las entradas aceptan fracciones como 1/3 y se pueden mostrar fracciones exactas.\n"
            "• Sistemas lineales: escribe las ecuaciones tal cual (−3x − y + 4z + 5w = −6). Gauss-Jordan "
            "(directo) o Jacobi y Gauss-Seidel (iterativos) con análisis de det(A), dominancia diagonal y "
            "radio espectral ρ(T), reordenamiento de ecuaciones y gráfica de convergencia.\n\n"
            "RAÍCES DE ECUACIONES\n"
            "• Escribe f(x) y la gráfica aparece al instante con sus raíces, máximos, mínimos, "
            "inflexiones y el corte con el eje y.\n"
            "• «Ejercicios ▾» carga los ejercicios del banco y de la clase, ordenados por dificultad y con "
            "el método recomendado y su justificación.\n"
            "• Elige una raíz y pulsa «Sugerir valores»: el intervalo o los valores iniciales se "
            "obtienen de la propia función y se explica por qué sirven (Bolzano, Fourier).\n"
            "• Antes de resolver se validan las condiciones del método. Después, la tabla de "
            "iteraciones se recorre por páginas y cada fila muestra su desarrollo con los valores "
            "sustituidos y se resalta en la gráfica.\n"
            "• Newton-Raphson calcula la derivada automáticamente; si escribes una, se comprueba.\n"
            "• Plano: rueda para acercar (Shift: solo x; Ctrl o ⌘: solo y), arrastra para moverte, "
            "doble clic para volver a la vista estándar y ⤢ para expandir.\n\n"
            "CÓMO ESCRIBIR\n"
            "• Funciones: 2x, 3(x+1), sin x, x², √x, e^(-x), ln(x), log(x, 2), raiz(x, 3), |x| con abs(x). "
            "Igualdades como cos x = x se resuelven como cos x − x = 0. Los ángulos van en radianes.\n"
            "• Al escribir letras aparecen sugerencias (Tab o Enter completa). Atajos: Ctrl o ⌘ + R √, "
            "L ln, E exp, P π, S sin, K cos, T tan, B |x|, 6 potencia.\n"
            "• Por tramos: si(x < 0, -x, x).\n"
            "• Valores numéricos: admiten 2,5 · pi/2 · sqrt(2) · 1e-6.\n"
            "• Vectores: separa con espacios o comas. Matrices: un valor por casilla.\n\n"
            "Todo el cálculo usa únicamente la biblioteca estándar de Python."
        )
        area, guia = crear_area_resultado(marco, alto=24, fuente=fuente(11))
        area.pack(fill="both", expand=True)
        guia.configure(padx=10, pady=8, spacing3=4, relief="flat")
        mostrar_texto(guia, texto)
        guia.tag_configure("titulo_guia", font=fuente(12, "bold"), foreground=PALETA["acento_hover"],
                           spacing1=10, spacing3=8)
        for numero, linea in enumerate(texto.splitlines(), 1):
            if linea in ("ÁLGEBRA LINEAL", "RAÍCES DE ECUACIONES", "CÓMO ESCRIBIR"):
                guia.tag_add("titulo_guia", f"{numero}.0", f"{numero}.end")
