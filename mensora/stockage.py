"""Accès à la base de données SQLite locale de Mensora."""

from decimal import Decimal
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

def convertir_centimes_en_montant(centimes):
    """Convertir un nombre entier de centimes en montant Decimal normalisé."""
    return normaliser_montant(Decimal(centimes) / 100)

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

def lister_operations(connexion):
    """Lister toutes les opérations de la base de données."""
    cursor = connexion.cursor()
    cursor.execute("""
        SELECT id, date, type, categorie, montant_centimes, detail
        FROM operations
        ORDER BY id
    """)
    lignes= cursor.fetchall()
    operations = []

    for ligne in lignes:
        operation = ligne_vers_operation(ligne)
        operations.append(operation)
    return operations

def ligne_vers_operation(ligne):
    """Convertir une ligne de la base de données en dictionnaire d'opération."""
    return {
        "id": ligne[0],
        "date": ligne[1],
        "type": ligne[2],
        "categorie": ligne[3],
        "montant": convertir_centimes_en_montant(ligne[4]),
        "detail": ligne[5],
    }

def modifier_operation(connexion, operation_id, nouvelle_operation):
    """Modifier une opération existante dans la base de données."""
    # Valider la nouvelle opération avant de la modifier
    valide, message = valider_operation(nouvelle_operation)
    if not valide:
        raise ValueError(f"Nouvelle opération invalide: {message}")

    montant_centimes = convertir_montant_en_centimes(normaliser_montant(nouvelle_operation["montant"]))
    cursor = connexion.cursor()
    cursor.execute(
        """
        UPDATE operations
        SET date = ?, type = ?, categorie = ?, montant_centimes = ?, detail = ?
        WHERE id = ?
        """,
        (
            nouvelle_operation["date"],
            nouvelle_operation["type"],
            nouvelle_operation["categorie"],
            montant_centimes,
            nouvelle_operation.get("detail", ""),
            operation_id
        )
    )
    if cursor.rowcount == 0:
        raise ValueError(f"Aucune opération trouvée avec l'ID {operation_id}.")
    connexion.commit()

def supprimer_operation(connexion, operation_id):
    """Supprimer une opération existante de la base de données."""
    cursor = connexion.cursor()
    cursor.execute("DELETE FROM operations WHERE id = ?", (operation_id,))
    if cursor.rowcount == 0:
        raise ValueError(f"Aucune opération trouvée avec l'ID {operation_id}.")
    connexion.commit()