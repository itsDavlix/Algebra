"""Pruebas de formato de vector y validación de números."""

import unittest

from nucleo.numeros import convertir_numero, limpiar_numero, escala_de, umbral_cero
from nucleo.vectores import (
    vector_a_texto, producto_punto_con_pasos, producto_cruz_con_pasos,
    norma_vector_con_pasos, vectores_linealmente_independientes,
    vectores_linealmente_independientes_con_pasos,
)


class PruebasVectores(unittest.TestCase):
    """Comprueba formato relativo y rechazo de dígitos ajenos a ASCII."""

    def test_formato_relativo_a_escala(self):
        """Conserva vectores pequeños y limpia componentes insignificantes."""
        self.assertEqual(vector_a_texto([1e-11, 2e-11]), "(1e-11, 2e-11)")
        self.assertEqual(vector_a_texto([1, 1e-12]), "(1, 0)")

    def test_ajuste_entero_relativo_no_convierte_a_cero(self):
        """El ajuste a entero se compara con el entero cercano, no con cero."""
        self.assertEqual(limpiar_numero(1e-11), "0")
        self.assertEqual(limpiar_numero(1e-11, escala=1e-11), "1e-11")
        self.assertEqual(escala_de([[1e-11], [-2e-11]]), 2e-11)
        self.assertEqual(escala_de([]), 0.0)
        self.assertEqual(umbral_cero(2e-11), 2e-21)

    def test_digitos_unicode_no_se_aceptan(self):
        """Acepta solo dígitos ASCII en la entrada numérica controlada."""
        with self.assertRaisesRegex(ValueError, "número válido"):
            convertir_numero("٣")

    def test_producto_punto_y_comprobacion(self):
        """Calcula el producto punto y verifica la simetría."""
        resultado, pasos = producto_punto_con_pasos([1, 2, 3], [4, 5, 6])
        self.assertEqual(resultado, 32)
        self.assertTrue(any("COMPROBACIÓN" in paso for paso in pasos))

    def test_producto_cruz_ortogonal_en_r3(self):
        """El producto cruz resultante es ortogonal a ambos vectores."""
        resultado, pasos = producto_cruz_con_pasos([1, 2, 3], [4, 5, 6])
        self.assertEqual(resultado, [-3, 6, -3])
        self.assertTrue(any("ortogonal" in paso.lower() for paso in pasos))
        with self.assertRaisesRegex(ValueError, "R³"):
            producto_cruz_con_pasos([1, 2], [3, 4])

    def test_norma_con_raiz_cuadrada(self):
        """Calcula la norma euclidiana y verifica el cuadrado resultante."""
        resultado, pasos = norma_vector_con_pasos([3, 4])
        self.assertEqual(resultado, 5)
        self.assertTrue(any("COMPROBACIÓN" in paso for paso in pasos))

    def test_independencia_por_rango(self):
        """Clasifica conjuntos independientes y dependientes mediante su rango."""
        independientes, pasos = vectores_linealmente_independientes_con_pasos(
            [[1, 0], [0, 1]],
        )
        self.assertTrue(independientes)
        self.assertTrue(any("COMPROBACIÓN" in paso for paso in pasos))
        dependientes, _ = vectores_linealmente_independientes_con_pasos(
            [[1, 2], [2, 4]],
        )
        self.assertFalse(dependientes)
        self.assertTrue(vectores_linealmente_independientes([[1, 0], [0, 1]]))
