"""Pruebas de conversión canónica y operaciones con números romanos."""

import unittest

from nucleo.romanos import entero_a_romano, operar_romanos, romano_a_entero


class PruebasRomanos(unittest.TestCase):
    """Comprueba la conversión completa del rango romano admitido."""

    def test_conversion_ida_y_vuelta_del_rango_completo(self):
        """Cada entero de 1 a 3999 vuelve a su valor después de conversión."""
        for numero in range(1, 4000):
            with self.subTest(numero=numero):
                self.assertEqual(romano_a_entero(entero_a_romano(numero)), numero)

    def test_formas_no_canonicas_se_rechazan(self):
        """No permite repeticiones ni sustracciones fuera de la forma estándar."""
        for texto in ("IIII", "IC", "VX", "MMMM", "IIV"):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                romano_a_entero(texto)

    def test_division_exacta_y_no_exacta(self):
        """Solo representa cocientes enteros positivos."""
        self.assertEqual(operar_romanos("X", "II", "/"), ("V", 5))
        with self.assertRaisesRegex(ValueError, "entero exacto"):
            operar_romanos("V", "II", "/")

