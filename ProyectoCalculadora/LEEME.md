# Calculadora: determinantes

Ejecutá `python main.py` con Python 3 y Tkinter disponible. No se agregaron dependencias externas.

En la pestaña Matrices, ingresá una matriz cuadrada en A y pulsá **Determinante de A**. La ventana muestra la recomendación de eficiencia antes de elegir **Cofactores** o **LU con pivoteo parcial**. Marcá una opción y pulsá **Calcular**. No hace falta completar B.

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
