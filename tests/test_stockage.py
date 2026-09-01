"""Tests de l'accès SQLite de Mensora."""

import sqlite3
import unittest
from decimal import Decimal

from mensora.stockage import (
    ajouter_operation,
    convertir_centimes_en_montant,
    convertir_montant_en_centimes,
    initialiser_base,
    ligne_vers_operation,
    modifier_operation,
    ouvrir_connexion,
    lister_operations,
    supprimer_operation,
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

    def test_lister_operations_retourne_toutes_les_operations(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)
        operations = [
            {
                "date": "10/08/2026",
                "type": "depense",
                "categorie": "Courses",
                "montant": Decimal("10.50"),
                "detail": "",
            },
            {
                "date": "11/08/2026",
                "type": "revenu",
                "categorie": "Retraite",
                "montant": Decimal("1000.00"),
                "detail": "",
            },
        ]
        for operation in operations:
            ajouter_operation(connexion, operation)
        lignes = lister_operations(connexion)
        self.assertEqual(len(lignes), 2)
        self.assertEqual(
            lignes[0],
            {
                "id": 1,
                "date": "10/08/2026",
                "type": "depense",
                "categorie": "Courses",
                "montant": Decimal("10.50"),
                "detail": "",
            },
        )
        self.assertEqual(
            lignes[1],
            {
                "id": 2,
                "date": "11/08/2026",
                "type": "revenu",
                "categorie": "Retraite",
                "montant": Decimal("1000.00"),
                "detail": "",
            },
        )
        connexion.close()

    def test_ligne_vers_operation_convertit_ligne_sqlite(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)
        operation = {
            "date": "10/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": Decimal("10.50"),
            "detail": "",
        }
        ajouter_operation(connexion, operation)
        ligne = connexion.execute(
            "SELECT id, date, type, categorie, montant_centimes, detail FROM operations"
        ).fetchone()
        operation_convertie = ligne_vers_operation(ligne)
        self.assertEqual(
            operation_convertie,
            {
                "id": 1,
                "date": "10/08/2026",
                "type": "depense",
                "categorie": "Courses",
                "montant": Decimal("10.50"),
                "detail": "",
            },
        )
        connexion.close()

    def test_modifier_operation_met_a_jour_operation_existante(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)
        operation = {
            "date": "10/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": Decimal("10.50"),
            "detail": "",
        }
        operation_id = ajouter_operation(connexion, operation)
        operation_modifiee = {
            "date": "11/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": Decimal("20.00"),
            "detail": "",
        }
        modifier_operation(connexion, operation_id, operation_modifiee)
        ligne = connexion.execute(
            "SELECT id, date, type, categorie, montant_centimes, detail FROM operations WHERE id = ?", (operation_id,)
        ).fetchone()
        self.assertEqual(
            ligne,
            (1, "11/08/2026", "depense", "Courses", 2000, ""),
        )
        connexion.close()

    def test_modifier_operation_refuse_id_inexistant(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)

        operation = {
            "date": "10/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": Decimal("10.50"),
            "detail": "",
        }

        ajouter_operation(connexion, operation)  # Ajout d'une opération pour avoir un ID

        operation_modifiee = {
            "date": "11/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": Decimal("20.00"),
            "detail": "",
        }

        with self.assertRaises(ValueError):
            modifier_operation(connexion, 999, operation_modifiee)

        operations = lister_operations(connexion)

        self.assertEqual(len(operations), 1)  # Vérifie qu'il y a bien une opération

        self.assertEqual(
            operations[0],
            {
                "id": 1,
                "date": "10/08/2026",
                "type": "depense",
                "categorie": "Courses",
                "montant": Decimal("10.50"),
                "detail": "",
            },
        )

        connexion.close()

    def test_supprimer_operation_supprime_operation_existante(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)
        operation = {
            "date": "10/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": Decimal("10.50"),
            "detail": "",
        }
        operation_id = ajouter_operation(connexion, operation)
        supprimer_operation(connexion, operation_id)
        ligne = connexion.execute(
            "SELECT id, date, type, categorie, montant_centimes, detail FROM operations WHERE id = ?", (operation_id,)
        ).fetchone()
        self.assertIsNone(ligne)
        connexion.close()

    def test_supprimer_operation_refuse_id_inexistant(self):
        connexion = ouvrir_connexion(":memory:")
        initialiser_base(connexion)
        operation = {
            "date": "10/08/2026",
            "type": "depense",
            "categorie": "Courses",
            "montant": Decimal("10.50"),
            "detail": "",
        }
        ajouter_operation(connexion, operation)  # Ajout d'une opération pour avoir un ID
        with self.assertRaises(ValueError):
            supprimer_operation(connexion, 999)  # ID inexistant
        operations = lister_operations(connexion)
        self.assertEqual(len(operations), 1)  # Vérifie qu'il y a bien une opération
        self.assertEqual(
            operations[0],
            {
                "id": 1,
                "date": "10/08/2026",
                "type": "depense",
                "categorie": "Courses",
                "montant": Decimal("10.50"),
                "detail": "",
            },
        )
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