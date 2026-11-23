# Iterum · Álgebra lineal y métodos numéricos

Ejecuta `python main.py` con Python 3 y Tkinter. **No usa bibliotecas externas**: todo el cálculo, el análisis de funciones y el motor de gráficas están programados con la biblioteca estándar.

Pruebas: `python -m unittest discover -s tests -v`.

## Interfaz

- Paleta única grafito con tinte morado, definida en `interfaz/estilos.py` (`PALETA`). No hay modo claro: cada color tiene un significado fijo.
- **Para presentar resultados**: cada tabla y cada procedimiento tienen **⧉ Copiar** (la tabla completa sale tabulada y se pega directo en Excel o Word; el procedimiento sale como texto plano). En ventanas estrechas los botones pasan a solo icono con ayuda al pasar el cursor.
- **Diagnóstico en Sistemas lineales**: al escribir el sistema aparece el veredicto de los tres métodos (✓ funciona, ↻ funciona reordenando, ✗ no funciona) con su dato clave: det(A) e intercambios de fila para Gauss-Jordan; ρ(T), el mejor orden de ecuaciones y las iteraciones estimadas (k ≈ log ε / log ρ) para Jacobi y Gauss-Seidel. Al pasar el cursor se ve la explicación completa; con un clic se usa ese método y, si hace falta, se reordenan las ecuaciones. La búsqueda automática de orden llega a 6 ecuaciones; con 7, «Reordenar filas» la hace a pedido.
- **Matriz aumentada con la diagonal resaltada**: los aᵢᵢ en color, los ceros de la diagonal en rojo y, a la derecha de cada fila, |aᵢᵢ| frente a Σ|aᵢⱼ| (dominancia diagonal con números, no solo ✓/✗).
- **Gauss-Jordan explicado**: cada intercambio dice por qué se hace (pivote nulo o pivoteo parcial: el mayor |aᵢⱼ| de la columna) y cada normalización nombra su pivote. Cada paso muestra la matriz tal como queda tras *esa* operación, también en la inversa y el rango. El resumen lista los pivotes, los intercambios y comprueba det(A) = (−1)ˢ · ∏ pivotes; la verificación sustituye la solución en cada ecuación: «Ec. 1: 2(−1) − 3(3) + 1 + 4(−2) = −18 ✓».
- **Texto del banco tal cual**: se pueden pegar coeficientes como `(1/2)x₂` o `−(1/3)w`, el guion «–», superíndices (`eˣ`, `x⁴`, `e⁻ˣ`) y el punto como producto (`x.e^(−x)`). Una igualdad se ve como `f(x) = izq − (der) = 0`; si aparece `e(…)`, la vista previa avisa de un posible exponente perdido sin impedir resolver.
- **Dominio antes de iterar**: Bisección y Falsa posición rechazan un intervalo con un polo, un punto fuera del dominio o un hueco, y explican cuál («x = 1 está fuera del dominio… Bolzano no aplica»).
- **Fracciones exactas**: en Gauss-Jordan, el selector «0.25 | 1/4» de la tarjeta de resultado cambia entre decimales y fracciones exactas (hasta 10 incógnitas con datos racionales): pasos en fracciones, solución p/q ≈ decimal y residuo 0.
- **Ejercicios por Parte del banco**: el menú «Ejercicios ▾» agrupa por Parte I–IV (y la clase de Jacobi/Gauss-Seidel) y, dentro, por dificultad; cada ejercicio muestra su número (P1-E9).
- **Plano para álgebra lineal**: en Sistemas lineales, el modo **Plano** dibuja las dos rectas de un sistema 2×2, su intersección y, con Jacobi o Gauss-Seidel, el camino de las aproximaciones. En Vectores (R²), **◇ Ver en el plano** muestra suma (paralelogramo), resta, escalar, norma y el ángulo del producto punto, con la misma escala en ambos ejes.
- **Números romanos** se calcula al escribir, con el equivalente decimal de cada número y avisos en línea (sin ventanas emergentes).
- Menú lateral por categorías: Inicio · Álgebra lineal (Vectores, Matrices, Sistemas lineales) · Raíces de ecuaciones (Bisección / Regula Falsi y Newton-Raphson / Secante) · Otros (Números romanos). Cada vista se crea la primera vez que se abre.
- Las vistas de raíces se ajustan a la ventana como un panel de trabajo: la gráfica con los parámetros ocupa el 62 % del alto y la franja de resultados el 38 %. Al redimensionar, todo se escala sin recortarse. La tabla muestra tantas filas por página como quepan, y **⤢ Todas** / **⤢ Completo** abren la tabla entera o el procedimiento completo en ventanas aparte, redimensionables. Solo si la ventana baja de 680 px de alto aparece una barra de desplazamiento, suave y encadenada (sobre la gráfica, la rueda hace zoom).

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

**Ejercicios ▾** (en cada vista) carga los **49 ejercicios del banco** agrupados por Parte y por dificultad, con su número (P1-E9). Cada uno indica el método recomendado, los valores iniciales y la justificación, porque en el banco la elección del método se evalúa. `tests/test_banco_completo.py` los recorre todos: en el núcleo (fórmula, pasos, tolerancia 10⁻⁶, ≥ 8 cifras y comprobación contra un cálculo independiente con fracciones) y en la interfaz (cada uno se carga en su vista y se resuelve sin errores).

- **Parte I · 19 sistemas** con Gauss-Jordan. Los que piden aritmética exacta o la aconsejan (P1-E12, 13, 14, 15, 17, 19) se cargan en fracciones. P1-E14 tiene infinitas soluciones (rango 3). Variantes iterativas:
  - P1-E9, E10 y E11: Gauss-Seidel tras reordenar (en E10 y E11 Jacobi no converge en ningún orden).
  - P1-E17: Jacobi converge más rápido que Gauss-Seidel (ρ ≈ 0.54 frente a 0.63).
  - P1-E1: Jacobi diverge (ρ ≈ 2).
- **Parte II · 10 matrices:** det(A), A⁻¹ y A·A⁻¹ = I₄.
- **Parte III · 15 ecuaciones:** E1–E10 con el método justificado; E11–E15 con el método que sugiere el banco.
- **Parte IV · 5 ecuaciones fraccionarias o compuestas**, con su dominio. P4-E2 y P4-E5 no traen lado derecho en el documento: se toman como «= 0» (igualdad supuesta, indicada en el enunciado) y se resuelven por despeje exacto y numéricamente. P4-E2 (raíz triple) se guarda también con falsa posición como contraejemplo de estancamiento.
- **Clase de Jacobi y Gauss-Seidel:** el sistema guía y la actividad en parejas.

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
  - `vistaMatrices.py`, `vistaVectores.py`, `vistaRomanos.py`, `pestanaInicio.py`; `dibujos.py` (geometría de vectores y sistemas 2×2, sin Tk) y `ventanaPlano.py`.
- `tests/`: pruebas del núcleo, de los ejercicios y de las vistas con Tk real (se omiten si Tk no está disponible).
