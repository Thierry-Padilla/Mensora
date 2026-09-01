"""Accès à la base de données SQLite locale de Mensora."""

import sqlite3
from mensora.metier import normaliser_montant, valider_operation


def ouvrir_connexion(chemin_base):
    """Ouvrir une connexion SQLite vers le chemin reçu."""
    return sqlite3.connect(chemin_base)


def initialiser_base(connexion):
    """Créer les tables nécessaires au fonctionnement de Mensora."""
    connexion.execute(
        """
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            categorie TEXT NOT NULL,
            montant_centimes INTEGER NOT NULL,
            detail TEXT NOT NULL DEFAULT ''
        )
        """
    )


def convertir_montant_en_centimes(montant):
    """Convertir un montant Decimal normalisé en nombre entier de centimes."""
    return int(montant * 100)

def ajouter_operation(connexion, operation):
    """Ajouter une opération à la base de données."""
    # Valider l'opération avant de l'ajouter
    valide, message = valider_operation(operation)
    if not valide:
        raise ValueError(f"Opération invalide: {message}")
    
    montant_centimes = convertir_montant_en_centimes(normaliser_montant(operation["montant"]))
    connexion_cursor = connexion.cursor()
    connexion_cursor.execute(
        """
        INSERT INTO operations (date, type, categorie, montant_centimes, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            operation["date"],
            operation["type"],
            operation["categorie"],
            montant_centimes,
            operation.get("detail", "")
        )
    )
    connexion.commit()
    return connexion_cursor.lastrowid  # Retourne l'ID de la dernière opération insérée