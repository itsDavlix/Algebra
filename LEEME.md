# Calculadora: determinantes

Ejecutá `python main.py` con Python 3 y Tkinter disponible. No se agregaron dependencias externas.

En la pestaña Matrices, ingresa cada elemento de A y B en su propia casilla y ajusta el número de filas y columnas con los controles. Así no necesitas separar valores con espacios. Si una casilla está vacía o tiene un valor inválido, el programa indica su posición. Para calcular un determinante, ingresa una matriz cuadrada en A y pulsa **Determinante de A**. La ventana muestra la recomendación de eficiencia antes de elegir **Cofactores** o **LU con pivoteo parcial**. Marca una opción y pulsa **Calcular**. No hace falta completar B.

## Organización del código

- `nucleo/determinantes.py`: validación, recomendación, expansión por cofactores, LU y formato del resultado. Cada bloque está documentado en castellano.
- `interfaz/pestanaMatrices.py`: botón y diálogo de selección; muestra el resultado y la explicación del método.
- `tests/test_determinantes.py`: casos conocidos, comparación independiente por Leibniz, pivoteo, entradas inválidas y magnitudes extremas.

## Criterio de eficiencia

Para órdenes de 1 a 3 se sugieren cofactores por sus fórmulas cortas. Para órdenes mayores se recomienda LU: O(n³) operaciones aritméticas frente a O(n!) en el peor caso de cofactores. Es una estimación, no una medición de tiempo. Los ceros pueden favorecer a cofactores; se elige la fila con más ceros y se omiten sus términos nulos. Cofactores se detiene después de 100000 llamadas recursivas con un mensaje que permite volver a elegir LU.

LU intercambia filas cuando hace falta y corrige el signo del determinante. Los multiplicadores de L no se almacenan porque su diagonal es unitaria y su determinante es uno.

Los cálculos utilizan racionales exactos a partir de los números que recibe el núcleo. La lectura existente convierte primero a números de coma flotante: no recupera precisión decimal perdida en esa conversión. El costo real también depende del tamaño de los racionales. Los resultados enteros se muestran exactamente y las aproximaciones decimales llevan el símbolo ≈; los valores fuera del rango decimal se muestran como fracciones.

## Verificación

Desde la carpeta del proyecto: `python -m unittest discover -s tests -v`.

## Método de bisección

Abre la pestaña **Bisección** para resolver una ecuación de una variable. Escribe una expresión igualada a cero (`x^3 - x - 2`) o una igualdad (`x^2 = 2`). Indica los extremos **a** y **b**, la tolerancia absoluta del error en **x** y el máximo de iteraciones. Pulsa **Resolver por bisección** o Enter. **Cargar ejemplo** restaura un caso listo para ejecutar y **Limpiar** vacía la ecuación, el intervalo y la salida.

Ejemplo: `x^3 - x - 2 = 0`, intervalo `[1, 2]`, tolerancia `1e-6` y máximo `100`. La raíz aproximada es `1.52138`. La salida incluye la aproximación, `f(x)`, la cota del error, el motivo de parada y cada iteración con sus extremos, punto medio y mitad conservada.

La pestaña solicita confirmar que la función es continua en `[a,b]` antes de calcular: es un requisito matemático que no se puede certificar automáticamente para estas expresiones. El ejemplo conocido activa la confirmación; modificar la ecuación o los extremos la desactiva para que se confirme de nuevo, y al limpiar también queda desactivada. La gráfica muestra los signos evaluados en los extremos, resalta el intervalo final que acota la raíz y señala la aproximación sobre el eje `x`. Si algunas muestras no pertenecen al dominio, las separa y avisa, aunque la ausencia de esos puntos tampoco demuestra continuidad. Las iteraciones se organizan en una tabla con anchos adaptables; expande cada fila para consultar el punto medio, las evaluaciones, la cota del error y la mitad conservada o el motivo de parada. Usa la rueda del ratón para recorrerlas; las barras de desplazamiento aparecen con un estilo más discreto cuando hacen falta. Pulsa **Ver tabla completa** para ocultar temporalmente la entrada y la gráfica, y dedicar el espacio de la pestaña al procedimiento; **Volver al resultado** restaura la vista.

- La función debe ser continua en todo `[a, b]`, con `a < b`. Los extremos deben tener signos opuestos o uno debe ser una raíz. Tener el mismo signo no demuestra que no existan raíces; elige otro intervalo.
- Usa `*` para multiplicar (`2*x`), `^` o `**` para potencias, paréntesis y punto decimal. Se acepta notación científica (`1e-6`). No se admite multiplicación implícita (`2x`).
- Funciones disponibles: `sin`/`sen`, `cos`, `tan`, `sqrt`/`raiz`, `exp`, `log`/`ln` (logaritmo natural), `log10` y `abs`, todas de un argumento. Constantes: `pi` y `e`. Los ángulos se expresan en radianes.
- La tolerancia debe ser positiva y el máximo de iteraciones, un entero entre 1 y 1000. No se utiliza el residuo `|f(x)|` como sustituto de la cota del error en la raíz.
- El algoritmo conserva la mitad con cambio de signo. Se detiene al encontrar `f(c) = 0` en la precisión de cálculo o al cumplir la tolerancia de la cota `max(c-a, b-c)`, equivalente a `(b-a)/2` en aritmética exacta.
- Al agotar las iteraciones o la precisión de coma flotante, muestra la última aproximación **sin afirmar convergencia**. Los errores de dominio en los puntos evaluados se informan; la aplicación no puede demostrar la continuidad en todos los puntos del intervalo.

La nueva función utiliza únicamente la biblioteca estándar. Las expresiones se interpretan con una lista de operaciones matemáticas permitidas, sin ejecutar código Python introducido por el usuario.

Archivos añadidos: `nucleo/biseccion.py` (evaluación y método), `interfaz/pestanaBiseccion.py` (interfaz) y `tests/test_biseccion.py` / `tests/test_biseccion_interfaz.py` (pruebas). La pestaña se registra en `main.py`.
