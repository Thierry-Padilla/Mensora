"""Tests de la logique indépendante de l'affichage Tkinter."""

import unittest
from datetime import date

from mensora.interface.fenetre_principale import formater_mois


class FormatMoisTests(unittest.TestCase):
    def test_formater_mois_en_francais(self):
        cas = (
            (date(2026, 1, 1), "Janvier 2026"),
            (date(2026, 9, 1), "Septembre 2026"),
            (date(2026, 12, 1), "Décembre 2026"),
        )

        for date_affichee, texte_attendu in cas:
            with self.subTest(date_affichee=date_affichee):
                self.assertEqual(formater_mois(date_affichee), texte_attendu)
