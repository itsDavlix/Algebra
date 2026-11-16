# Iterum · Álgebra lineal y métodos numéricos

Ejecuta `python main.py` con Python 3 y Tkinter. **No usa bibliotecas externas**: todo el cálculo, el análisis de funciones y el motor de gráficas están programados con la biblioteca estándar.

Pruebas: `python -m unittest discover -s tests -v`.

## Interfaz

- Paleta única grafito con tinte morado, definida en `interfaz/estilos.py` (`PALETA`). No hay modo claro: cada color tiene un significado fijo.
- Menú lateral por categorías: Inicio · Álgebra lineal (Vectores, Matrices, Sistemas lineales) · Raíces de ecuaciones (Bisección / Regula Falsi y Newton-Raphson / Secante) · Otros (Números romanos). Cada vista se crea la primera vez que se abre.
- Las vistas de raíces se ajustan a la ventana como un panel de trabajo: la gráfica con los parámetros ocupa el 62 % del alto y la franja de resultados el 38 %. Al redimensionar, todo se escala sin recortarse. La tabla muestra tantas filas por página como quepan, y **⤢ Ver todas** / **⤢ Completo** abren la tabla entera o el procedimiento completo en ventanas aparte, redimensionables. Solo si la ventana baja de 680 px de alto aparece una barra de desplazamiento, suave y encadenada (sobre la gráfica, la rueda hace zoom).

## Raíces de ecuaciones

Los cuatro métodos usan la misma vista (`interfaz/vistaRaices.py`), agrupados en dos ventanas:

- **Bisección / Regula Falsi** (métodos cerrados): comparten f(x) y el intervalo [a, b].
- **Newton-Raphson / Secante** (métodos abiertos): comparten f(x) y x₀; Secante añade x₁.

Un selector alterna el método conservando la función, la gráfica, los valores y el resultado de cada uno. **Comparar ambos** resuelve con los dos y muestra la raíz, las iteraciones, las evaluaciones de f, el orden de convergencia observado (Bisección lineal con razón ½, Newton ≈ 2, Secante ≈ 1.618) y una verificación cruzada: si las raíces coinciden dentro de la tolerancia, dos métodos distintos confirman el resultado.

El flujo es el siguiente:

1. **Función (paso ①).** Escribe `f(x)` o una igualdad (`cos x = x` se resuelve como `cos x − x = 0`). La gráfica aparece al instante, sin valores iniciales; hasta entonces los parámetros están bloqueados.
2. **Puntos notables.** La lista lateral y la gráfica muestran raíces (círculo), máximos y mínimos (rombos), inflexiones (cruz) y el corte con el eje y (cuadrado). Al hacer clic en uno se centra y se explica cómo se obtuvo.
3. **Valores iniciales (paso ②).** Haz clic en la gráfica para colocarlos (en Bisección y Regula Falsi, dos clics fijan a y b y se ordenan solos; en Secante, x₀ y x₁; el valor se redondea a la resolución de la pantalla), escríbelos o pulsa **Sugerir valores**. La sugerencia sale de la raíz elegida y se justifica:
   - Bisección y Regula Falsi: un intervalo con extremos "limpios" y `f(a)·f(b) < 0` (Bolzano).
   - Newton-Raphson: un x₀ con `f(x₀)·f″(x₀) > 0` (condición de Fourier).
   - Secante: dos valores que rodean la raíz.

   Una raíz doble se detecta y se avisa que los métodos cerrados no la encierran.
4. **Validación previa.** Antes de resolver se comprueban las condiciones del método:
   - Bolzano y `a < b`.
   - Iteraciones teóricas de Bisección, `n ≥ log₂((b − a)/tol)`.
   - Newton: `f′(x₀) ≠ 0`.
   - Secante: `f(x₀) ≠ f(x₁)`.
   - Dominio de la función en los valores iniciales.

   Los valores también se dibujan en la gráfica.
5. **Resultado.** Una tarjeta muestra el estado (convergió o no), la raíz, f(x), el error, las iteraciones y el motivo de parada.
6. **Procedimiento paginado.** La tabla muestra 12 iteraciones por página. La fila elegida genera su desarrollo con los valores sustituidos y se resalta en la gráfica: intervalo, secante o tangente de esa iteración.

Detalles de cada método (`nucleo/`):

- **Bisección** (`biseccion.py`): `c = (a + b)/2`. Se detiene cuando la cota `(b − a)/2 ≤ tol` o cuando `f(c) = 0`. Informa el error relativo εa por paso y avisa de posibles polos.
- **Regula Falsi** (`reglafalsa.py`): `c = b − f(b)(b − a)/(f(b) − f(a))`. El procedimiento muestra esta fórmula con los valores sustituidos. Exige que tanto el paso como el residuo cumplan la tolerancia, y avisa si un extremo queda estancado.
- **Newton-Raphson** (`metodosabiertos.py`): `xₙ₊₁ = xₙ − f(xₙ)/f′(xₙ)`.
  - Por omisión, el campo f′(x) muestra la derivada calculada **simbólicamente** con las reglas del cálculo, en solo lectura y actualizada al cambiar f(x). **✎ Editar** permite escribirla a mano (partiendo de la calculada) y **↺ Automática** vuelve al cálculo automático.
  - La derivada escrita a mano se compara con una diferencia centrada y se avisa si no coincide.
  - Detecta ciclos y divergencia sin declarar convergencia.
- **Secante**: `xₙ₊₁ = xₙ − f(xₙ)(xₙ − xₙ₋₁)/(f(xₙ) − f(xₙ₋₁))`, con la misma detección de ciclos y divergencia.

## Plano cartesiano (`interfaz/motorGrafica.py`)

- Marcas en pasos 1–2–5 × 10ⁿ, cuadrícula mayor y menor, ejes con flechas y nombres. Las cifras se pegan al borde cuando el eje sale de la vista.
- Rueda: acerca o aleja centrado en el cursor (Shift: solo x; Ctrl o ⌘: solo y). Arrastra para moverte. Doble clic o ⌂ vuelve a la vista estándar, y ⤢ expande la gráfica.
- La curva se muestrea por píxel y se corta fuera del dominio y en los polos.
- Las etiquetas evitan superponerse, y la lectura inferior muestra las coordenadas del cursor, de la curva o del punto señalado.

## Escritura de funciones y valores

El evaluador propio (`nucleo/expresiones.py`) valida una lista blanca de operaciones y traduce el árbol a funciones de Python, sin `eval` y sin ejecutar código escrito por la persona.

- **Escritura natural:** `2x`, `3(x+1)`, `x(x−1)`, `sin x`, `sin 2x`, `x²`, `√x`, `π`. La vista previa muestra cómo se interpretó, por ejemplo `3(x + 1)²`.
- **Funciones:** `sin`/`sen`, `cos`, `tan`, `sec`, `csc`, `cot`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `sqrt`, `cbrt`, `raiz(x, n)`, `exp`, `ln`, `log(x)` (natural), `log(x, b)`, `log10`, `log2` y `abs`. Constantes: `pi` y `e`. Los ángulos van en radianes.
- **Por tramos:** `si(condición, valor, otro valor)`, por ejemplo `si(x < 0, -x, x)`. Solo se evalúa la rama elegida.
- **Raíces impares de negativos:** son reales; `(-8)^(1/3) = −2`.
- **Autocompletado** al escribir letras: Tab o Enter completa, ↑↓ elige y Esc cierra.
- **Atajos con Ctrl en Windows y Linux (⌘ en Mac):** la app detecta el sistema y muestra la tecla correcta. En Windows no interfieren con AltGr (Ctrl+Alt), que en teclados en español se usa para escribir símbolos como € o ^.

  | Tecla | Inserta |
  |---|---|
  | R | √ |
  | L | ln |
  | E | exp |
  | P | π |
  | S | sin |
  | K | cos |
  | T | tan |
  | B | \|x\| |
  | 6 | potencia |

  Con texto seleccionado, la función lo envuelve. Los paréntesis se cierran solos.
- **Campos numéricos:** aceptan `2,5`, `pi/2`, `sqrt(2)` o `1e-6`, y muestran el valor calculado.

## Álgebra lineal

Las tres vistas usan el mismo diseño que las de raíces: operación, datos, resultado, pasos paginados y procedimiento (con ventanas «⤢» para verlo completo).

- **Vectores:** suma, resta, escalar, producto punto, producto cruz en R³, norma, combinación lineal e independencia lineal. Las componentes aceptan `1/3`, `sqrt(2)` o `pi`.
- **Matrices:** det(A) por cofactores o LU (comprobado con el otro método), A⁻¹, transpuesta, rango, A ± B, A·B y k·A. Las entradas aceptan fracciones, y «Mostrar fracciones exactas» presenta, por ejemplo, `17/73` en lugar de `0.23287671`.
  - La inversa sigue el orden del banco de ejercicios: primero justifica con det(A) ≠ 0, luego reduce [A | I] → [I | A⁻¹] y por último verifica A·A⁻¹ = I con su error máximo.
- **Sistemas lineales A·X = B:** el sistema se escribe tal cual (`−3x − y + 4z + 5w = −6`, `10x₁ − x₂ + 2x₃ = 6` o filas `a b c | d`) y se muestra su matriz aumentada.
  - **Gauss-Jordan** (directo): pivoteo parcial, clasificación (única, infinitas o incompatible), forma A·X = B y verificación ecuación por ecuación.
  - **Jacobi** y **Gauss-Seidel** (iterativos), según la clase:
    1. Comprueban la dominancia diagonal fila por fila.
    2. Calculan el radio espectral ρ(T) de T_J = −D⁻¹(L + U) o T_GS = −(D + L)⁻¹U. Es el criterio exacto de convergencia; la dominancia es suficiente, pero no necesaria.
    3. Despejan cada incógnita.
    4. Muestran cada sustitución con el mismo formato de la presentación, por ejemplo `x₂⁽²⁾ = (25 + 0.600000 − 1.100000 − 3(1.875000)) / 11 = 1.715909`. En Gauss-Seidel indican qué valores nuevos se usaron.
    5. Se detienen cuando ‖x⁽ᵏ⁺¹⁾ − x⁽ᵏ⁾‖∞ ≤ ε y ‖b − Ax‖∞ ≤ ε.
  - **Reordenar filas** busca el orden de ecuaciones con menor ρ(T). Reordenar no cambia la solución y permite usar sistemas con ceros en la diagonal.
  - **Comparar J / GS** resuelve con ambos, compara iteraciones, ρ(T) y residuo, y verifica que coincidan.
  - La gráfica de convergencia muestra la evolución de cada xᵢ⁽ᵏ⁾ o log₁₀‖Δx‖ frente a k, para los dos métodos.

## Ejercicios guardados

**Ejercicios ▾** (en cada vista) carga ejercicios ordenados por dificultad (básico, intermedio, avanzado). Cada uno indica el método recomendado, los valores iniciales y la justificación, porque en el banco la elección del método se evalúa. Todos se verifican en `tests/test_ejercicios.py` con tolerancia 10⁻⁶.

- **Raíces:** las 10 ecuaciones de la Parte III del banco, repartidas por método:
  - Bisección: x³ − 4x − 9 en [2, 3]; eˣ − 3x² en [0, 1].
  - Regula Falsi: x·ln x − 1; ln(x + 2) + x² − 2.
  - Newton-Raphson: x³ + x − 1; x⁴ − 3x² − 3; cos x − x·eˣ; x² − 5 sin x.
  - Secante: e^(−x) − x² + 0.5; x·e^(−x) − 0.2.
- **Gauss-Jordan:** los 10 sistemas de la Parte I.
- **Jacobi / Gauss-Seidel:** el sistema guía y la actividad en parejas de la clase, más tres casos del banco:
  - Sistema 9: hay que reordenar.
  - Sistema 10: converge con Gauss-Seidel y no con Jacobi.
  - Sistema 1: ρ ≈ 2, no converge.
- **Matrices:** las 10 matrices de la Parte II (det(A) e inversa).

Al validar los documentos se encontraron errores en algunas diapositivas paso a paso. Las tablas de iteraciones son correctas; la calculadora reproduce las tablas.

| Lugar | Muestra | Valor correcto |
|---|---|---|
| Diapositiva 15 | x₂⁽²⁾ = 1.704545 | 1.715909 |
| Diapositiva 15 | x₄⁽²⁾ = 0.906818 | 0.885227 |
| Diapositiva 20 | x₄⁽¹⁾ = 0.751591 | 0.878864 |
| Diapositiva 21 | parte de ese valor erróneo | — |
| Documento de ejemplos, Gauss-Seidel, iteración 2 | sustituye x₃⁽²⁾ y x₄⁽²⁾ en la fórmula de x₂⁽²⁾ | x₃⁽¹⁾ y x₄⁽¹⁾ (el resultado 2.036938 sí es correcto) |

## Organización

- `nucleo/`: cálculo puro, sin interfaz.
  - `expresiones.py`: evaluador y derivación simbólica.
  - `analisis.py`: puntos notables y valores sugeridos.
  - `biseccion.py`, `reglafalsa.py`, `metodosabiertos.py`: métodos de raíces.
  - `iterativos.py`: Jacobi, Gauss-Seidel, dominancia, ρ(T) y reordenamiento.
  - `sistemas.py`, `matrices.py`, `determinantes.py`, `vectores.py`: álgebra lineal.
  - `procedimientos*.py`: textos paso a paso.
  - `sistemas_texto.py`: lectura de ecuaciones, matrices y vectores.
  - `ejercicios.py`: ejercicios guardados.
- `interfaz/`
  - `componentes.py`: tarjeta, selector, tabla paginada, panel de procedimiento, ventanas y menú de ejercicios, compartidos por todas las vistas.
  - `motorGrafica.py`, `campoMatematico.py`, `estilos.py`.
  - `raices/`: vista de raíces dividida en `vista.py` (estructura), `grafica.py` (función y plano), `resultados.py` (resolver, tabla y procedimiento), `validacion.py`, `capas.py` y `configuracion.py`.
  - `sistemas/`: `vista.py` y `convergencia.py`.
  - `vistaMatrices.py`, `vistaVectores.py`, `pestanaInicio.py`, `pestanaRomanos.py`.
- `tests/`: pruebas del núcleo, de los ejercicios y de las vistas con Tk real (se omiten si Tk no está disponible).
