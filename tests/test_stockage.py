"""Tests de l'accès SQLite de Mensora."""

import sqlite3
import unittest
from decimal import Decimal

from mensora.stockage import (
    ajouter_operation,
    convertir_centimes_en_montant,
    convertir_montant_en_centimes,
    initialiser_base,
    ouvrir_connexion,
)

class OuvertureConnexionTests(unittest.TestCase):
    def test_ouvrir_connexion_en_memoire(self):
        connexion = ouvrir_connexion(":memory:")

        self.assertIsInstance(connexion, sqlite3.Connection)
        connexion.close()

    def test_initialiser_base_cree_table_operations(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)

        nombre_operations = connexion.execute(
            "SELECT COUNT(*) FROM operations"
        ).fetchone()

        self.assertEqual(nombre_operations, (0,))
        connexion.close()

    def test_table_operations_contient_les_colonnes_attendues(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)

        informations = connexion.execute(
            "PRAGMA table_info(operations)"
        ).fetchall()

        noms_colonnes = [information[1] for information in informations]

        self.assertEqual(
            noms_colonnes,
            ["id", "date", "type", "categorie", "montant_centimes", "detail"],
        )
        connexion.close()

    def test_ajouter_operation_enregistre_operation_valide(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)
        operation = {
            "date": "10/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": "10,50",
            "detail": "",
        }
        ajouter_operation(connexion, operation)
        ligne = connexion.execute(
            "SELECT id, date, type, categorie, montant_centimes, detail FROM operations"
            ).fetchone()
        self.assertEqual(
            ligne,
            (1, "10/08/2026", "depense", "Courses", 1050, ""),
        )
        connexion.close()

    def test_ajouter_operation_refuse_operation_invalide(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)
        operation_invalide = {
            "date": "10/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": -10,
            "detail": "",
        }
        with self.assertRaises(ValueError):
            ajouter_operation(connexion, operation_invalide)
        nombre_operations = connexion.execute(
            "SELECT COUNT(*) FROM operations"
        ).fetchone()
        self.assertEqual(nombre_operations, (0,))   
        connexion.close()

class ConversionMontantTests(unittest.TestCase):
    def test_convertir_montant_en_centimes(self):
        cas_valides = (
            (Decimal("10.50"), 1050),
            (Decimal("10.00"), 1000),
            (Decimal("0.01"), 1),
        )

        for montant, centimes_attendus in cas_valides:
            with self.subTest(montant=montant):
                self.assertEqual(
                    convertir_montant_en_centimes(montant),
                    centimes_attendus,
                )
    def test_convertir_centimes_en_montant(self):
        cas_valides = (
            (1050, Decimal("10.50")),
            (1000, Decimal("10.00")),
            (1, Decimal("0.01")),
        )

        for centimes, montant_attendu in cas_valides:
            with self.subTest(centimes=centimes):
                self.assertEqual(
                    convertir_centimes_en_montant(centimes),
                    montant_attendu,
                )