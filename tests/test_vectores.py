"""Pruebas de formato de vector y validación de números."""

import unittest

from nucleo.numeros import convertir_numero, limpiar_numero
from nucleo.vectores import vector_a_texto


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

    def test_digitos_unicode_no_se_aceptan(self):
        """Acepta solo dígitos ASCII en la entrada numérica controlada."""
        with self.assertRaisesRegex(ValueError, "número válido"):
            convertir_numero("٣")

