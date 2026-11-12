"""Pestaña Inicio: guía rápida de uso de la calculadora."""

from tkinter import ttk

from interfaz.ayudas import crear_area_resultado, mostrar_texto


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
            "Elige una pestaña, ingresa los datos y pulsa la operación que necesitas. "
            "En las ecuaciones, la respuesta aparece destacada al inicio; debajo encontrarás "
            "la comprobación y las explicaciones paso a paso.\n\n"
            "FUNCIONES DISPONIBLES\n"
            "• Vectores: suma, resta, multiplicación por escalar, producto punto, producto cruz "
            "en R³, norma, combinación lineal e independencia lineal.\n\n"
            "• Matrices: suma, resta, multiplicación por escalar y entre matrices, inversa, "
            "transpuesta, rango y determinantes por cofactores o LU con pivoteo parcial.\n\n"
            "• Ecuaciones A·X = B: resolución por Gauss-Jordan, identificación de solución única, "
            "infinitas soluciones o sistema incompatible, y comprobación de una X propuesta. "
            "Si hay infinitas soluciones, se muestra su forma paramétrica.\n\n"
            "• Bisección: búsqueda de raíces dividiendo un intervalo con cambio de signo. "
            "Al resolver se proponen automáticamente el intervalo, la tolerancia y las iteraciones.\n\n"
            "• Regula Falsi: búsqueda de raíces por falsa posición, con parámetros automáticos "
            "y avisos de estancamiento. Junto con Bisección, ofrece gráfica, zoom al ampliarla "
            "y una tabla de iteraciones desplegables. Ambos métodos requieren continuidad en el intervalo.\n\n"
            "• Métodos abiertos: elige Newton-Raphson o Secante. Newton-Raphson necesita "
            "un valor inicial x0 y la derivada f'(x); Secante necesita dos valores distintos, x0 y x1. "
            "Puedes ajustar la tolerancia y el máximo de iteraciones. "
            "La salida explica las sustituciones numéricas y el motivo de parada. "
            "Después de resolver, pulsa Graficar y ver puntos para explorar la curva, las tangentes o secantes, "
            "las coordenadas y una explicación de cada iteración. Estos métodos pueden no converger.\n\n"
            "• Números romanos: suma, resta, multiplicación y división exacta con números romanos estándar.\n\n"
            "• Programa anterior: selecciona y ejecuta un archivo .py elaborado previamente.\n\n"
            "CÓMO INGRESAR LOS DATOS\n"
            "• Vectores: separa los componentes con espacios o comas, por ejemplo 1 2 3 o 1, 2, 3. "
            "Para un conjunto de generadores, escribe un vector por línea.\n\n"
            "• Matrices: en la pestaña Matrices, escribe cada elemento en su casilla y ajusta las filas "
            "y columnas con los controles. En Ecuaciones A·X = B, escribe una fila por línea y "
            "separa sus elementos con espacios.\n\n"
            "• Ecuaciones en x: escribe una expresión, como x^3 - 2*x - 5, o una igualdad, como x^2 = 2. "
            "Usa * para multiplicar, ^ o ** para potencias y punto decimal. "
            "Se admiten funciones como sin, cos, sqrt, exp y log, además de pi y e; los ángulos van en radianes.\n\n"
            "• Derivada para Newton-Raphson: deriva la función igualada a cero. "
            "Por ejemplo, para x^3 - 2*x - 5 = 0, escribe 3*x^2 - 2 y prueba con x0 = 2. "
            "Para g(x) = h(x), introduce la derivada de g(x) − h(x).\n\n"
            "• Números romanos: usa formas como IV, XIV, XL o MCMXC.\n\n"
            "HERRAMIENTAS Y RESULTADOS\n"
            "• Mostrar símbolos abre una paleta para insertar operadores, funciones y constantes "
            "en el campo seleccionado.\n"
            "• Activar modo oscuro cambia la apariencia de la aplicación y sus gráficas.\n"
            "• En las pestañas de raíces, Cargar ejemplo prepara un ejercicio y Limpiar permite empezar de nuevo.\n"
            "• Revisa el estado de convergencia y el motivo de parada: una última aproximación "
            "sin convergencia no se presenta como una raíz confirmada.\n\n"
            "El programa usa únicamente Python estándar, sin bibliotecas externas."
        )
        area, guia = crear_area_resultado(marco, alto=24, fuente=("TkDefaultFont", 11))
        area.pack(fill="both", expand=True)
        guia.configure(padx=10, pady=8, spacing3=4, relief="flat")
        mostrar_texto(guia, texto)
        guia.tag_configure("titulo_guia", font=("TkDefaultFont", 12, "bold"),
                           spacing1=10, spacing3=8)
        for numero, linea in enumerate(texto.splitlines(), 1):
            if linea in ("FUNCIONES DISPONIBLES", "CÓMO INGRESAR LOS DATOS", "HERRAMIENTAS Y RESULTADOS"):
                guia.tag_add("titulo_guia", f"{numero}.0", f"{numero}.end")
