"""Tests automatisés des règles métier de Mensora."""

import unittest
from datetime import date, timedelta
from decimal import Decimal

from mensora.metier import calculer_totaux, valider_operation


class ValidationOperationTests(unittest.TestCase):
    """Protéger le contrat public de ``valider_operation``."""

    def operation_valide(self, **modifications):
        operation = {
            "date": date.today().strftime("%d/%m/%Y"),
            "type": "depense",
            "categorie": "Courses",
            "montant": "10,50",
            "detail": "",
        }
        operation.update(modifications)
        return operation

    def test_operation_standard_est_valide(self):
        self.assertEqual(valider_operation(self.operation_valide()), (True, ""))

    def test_date_absente_est_refusee(self):
        operation = self.operation_valide()
        del operation["date"]

        self.assertEqual(
            valider_operation(operation),
            (False, "La date est obligatoire."),
        )

    def test_date_future_est_refusee(self):
        demain = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")

        self.assertEqual(
            valider_operation(self.operation_valide(date=demain)),
            (False, "La date ne peut pas être dans le futur."),
        )

    def test_type_invalide_est_refuse(self):
        self.assertEqual(
            valider_operation(self.operation_valide(type="salaire")),
            (False, "Le type doit être 'revenu' ou 'depense'."),
        )

    def test_categorie_incompatible_est_refusee(self):
        self.assertEqual(
            valider_operation(
                self.operation_valide(type="revenu", categorie="Courses")
            ),
            (False, "La catégorie n'est pas valide pour ce type d'opération."),
        )

    def test_montants_valides_sont_acceptes(self):
        for montant in (10, "10", "10,50", "10.50", "0,01"):
            with self.subTest(montant=montant):
                self.assertEqual(
                    valider_operation(self.operation_valide(montant=montant)),
                    (True, ""),
                )

    def test_montants_non_numeriques_sont_refuses(self):
        for montant in ("abc", "NaN", "Infinity"):
            with self.subTest(montant=montant):
                self.assertEqual(
                    valider_operation(self.operation_valide(montant=montant)),
                    (False, "Le montant doit être un nombre valide."),
                )

    def test_montants_non_positifs_sont_refuses(self):
        for montant in (0, "0,00", -5):
            with self.subTest(montant=montant):
                self.assertEqual(
                    valider_operation(self.operation_valide(montant=montant)),
                    (False, "Le montant doit être supérieur à 0."),
                )

    def test_commentaire_obligatoire_est_controle(self):
        for detail in (None, "", "   "):
            with self.subTest(detail=detail):
                self.assertEqual(
                    valider_operation(
                        self.operation_valide(categorie="Divers", detail=detail)
                    ),
                    (False, "Un commentaire est obligatoire pour cette catégorie."),
                )

    def test_commentaire_obligatoire_valide_est_accepte(self):
        self.assertEqual(
            valider_operation(
                self.operation_valide(categorie="Divers", detail="Boulangerie")
            ),
            (True, ""),
        )


class CalculTotauxTests(unittest.TestCase):
    """Protéger les calculs déjà implémentés par Thierry."""

    def test_scenario_mensora_initial(self):
        operations = [
            {"type": "revenu", "categorie": "Retraite", "montant": 1000},
            {"type": "depense", "categorie": "Courses", "montant": 300},
            {"type": "depense", "categorie": "Essence", "montant": 30},
            {"type": "depense", "categorie": "Essence", "montant": 50},
        ]

        self.assertEqual(
            calculer_totaux(operations),
            (1000, 380, 620, {"Courses": 300, "Essence": 80}),
        )

    def test_liste_vide(self):
        self.assertEqual(calculer_totaux([]), (0, 0, 0, {}))

    def test_calculs_decimal_sont_exacts(self):
        operations = [
            {
                "type": "revenu",
                "categorie": "Retraite",
                "montant": Decimal("1000.50"),
            },
            {
                "type": "depense",
                "categorie": "Courses",
                "montant": Decimal("0.10"),
            },
            {
                "type": "depense",
                "categorie": "Courses",
                "montant": Decimal("0.20"),
            },
        ]

        self.assertEqual(
            calculer_totaux(operations),
            (
                Decimal("1000.50"),
                Decimal("0.30"),
                Decimal("1000.20"),
                {"Courses": Decimal("0.30")},
            ),
        )


if __name__ == "__main__":
    unittest.main()

