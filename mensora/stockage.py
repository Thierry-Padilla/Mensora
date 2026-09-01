"""Accès à la base de données SQLite locale de Mensora.

Ce module porte une responsabilité unique : persister les opérations financières
et leur journal d'audit. Les règles métier restent dans ``mensora.metier``.
"""

import sqlite3
from datetime import datetime
from decimal import Decimal

from mensora.metier import normaliser_montant, valider_operation


# ---------------------------------------------------------------------------
# Connexion et schéma
# ---------------------------------------------------------------------------


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

    # Le journal est séparé des opérations : supprimer une opération ne doit
    # jamais supprimer la trace de ce qui a été modifié ou supprimé.
    connexion.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            date_action TEXT NOT NULL,
            ancienne_date TEXT NOT NULL,
            ancien_type TEXT NOT NULL,
            ancienne_categorie TEXT NOT NULL,
            ancien_montant_centimes INTEGER NOT NULL,
            ancien_detail TEXT NOT NULL DEFAULT '',
            nouvelle_date TEXT,
            nouveau_type TEXT,
            nouvelle_categorie TEXT,
            nouveau_montant_centimes INTEGER,
            nouveau_detail TEXT
        )
        """
    )


# ---------------------------------------------------------------------------
# Conversion monétaire
# ---------------------------------------------------------------------------


def convertir_montant_en_centimes(montant):
    """Convertir un montant Decimal normalisé en nombre entier de centimes."""
    return int(montant * 100)


def convertir_centimes_en_montant(centimes):
    """Convertir un nombre entier de centimes en montant Decimal normalisé."""
    return normaliser_montant(Decimal(centimes) / 100)


def ligne_vers_operation(ligne):
    """Convertir une ligne SQLite en dictionnaire d'opération métier."""
    return {
        "id": ligne[0],
        "date": ligne[1],
        "type": ligne[2],
        "categorie": ligne[3],
        "montant": convertir_centimes_en_montant(ligne[4]),
        "detail": ligne[5],
    }


# ---------------------------------------------------------------------------
# CRUD des opérations
# ---------------------------------------------------------------------------


def ajouter_operation(connexion, operation):
    """Valider puis ajouter une opération et retourner son identifiant SQLite."""
    valide, message = valider_operation(operation)
    if not valide:
        raise ValueError(f"Opération invalide: {message}")

    montant_centimes = convertir_montant_en_centimes(
        normaliser_montant(operation["montant"])
    )

    cursor = connexion.cursor()
    cursor.execute(
        """
        INSERT INTO operations (date, type, categorie, montant_centimes, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            operation["date"],
            operation["type"],
            operation["categorie"],
            montant_centimes,
            operation.get("detail", ""),
        ),
    )
    connexion.commit()
    return cursor.lastrowid


def lister_operations(connexion):
    """Lister toutes les opérations, converties en dictionnaires métier."""
    cursor = connexion.cursor()
    cursor.execute(
        """
        SELECT id, date, type, categorie, montant_centimes, detail
        FROM operations
        ORDER BY id
        """
    )

    return [ligne_vers_operation(ligne) for ligne in cursor.fetchall()]


def modifier_operation(connexion, operation_id, nouvelle_operation):
    """Modifier une opération et journaliser son état avant/après."""
    valide, message = valider_operation(nouvelle_operation)
    if not valide:
        raise ValueError(f"Nouvelle opération invalide: {message}")

    # L'état actuel doit être capturé avant l'UPDATE : après modification,
    # SQLite ne permettrait plus de reconstruire fidèlement l'ancien état.
    ligne = connexion.execute(
        """
        SELECT id, date, type, categorie, montant_centimes, detail
        FROM operations
        WHERE id = ?
        """,
        (operation_id,),
    ).fetchone()

    if ligne is None:
        raise ValueError(f"Aucune opération trouvée avec l'ID {operation_id}.")

    ancienne_operation = ligne_vers_operation(ligne)
    montant_centimes = convertir_montant_en_centimes(
        normaliser_montant(nouvelle_operation["montant"])
    )

    # UPDATE + audit forment une seule transaction métier. Si le journal
    # échoue, la modification est annulée afin d'éviter un historique incomplet.
    try:
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
                operation_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Aucune opération trouvée avec l'ID {operation_id}.")

        ajouter_log_audit(
            connexion,
            operation_id,
            "modification",
            ancienne_operation,
            nouvelle_operation,
        )
        connexion.commit()
    except Exception:
        connexion.rollback()
        raise


def supprimer_operation(connexion, operation_id):
    """Supprimer une opération tout en conservant sa trace dans l'audit."""
    # IMPORTANT : on lit d'abord l'opération. Une fois DELETE exécuté, son état
    # précédent n'existe plus dans la table ``operations``.
    ligne = connexion.execute(
        """
        SELECT id, date, type, categorie, montant_centimes, detail
        FROM operations
        WHERE id = ?
        """,
        (operation_id,),
    ).fetchone()

    if ligne is None:
        raise ValueError(f"Aucune opération trouvée avec l'ID {operation_id}.")

    ancienne_operation = ligne_vers_operation(ligne)

    # DELETE + audit sont atomiques : soit les deux sont validés, soit aucun.
    try:
        cursor = connexion.cursor()
        cursor.execute(
            "DELETE FROM operations WHERE id = ?",
            (operation_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Aucune opération trouvée avec l'ID {operation_id}.")

        ajouter_log_audit(
            connexion,
            operation_id,
            "suppression",
            ancienne_operation,
            None,
        )
        connexion.commit()
    except Exception:
        connexion.rollback()
        raise


# ---------------------------------------------------------------------------
# Journal d'audit
# ---------------------------------------------------------------------------


def ajouter_log_audit(
    connexion,
    operation_id,
    action,
    ancienne_operation,
    nouvelle_operation,
):
    """Ajouter une entrée dans le journal d'audit sans valider la transaction."""
    date_action = datetime.now().isoformat(timespec="seconds")
    ancien_montant_centimes = convertir_montant_en_centimes(
        normaliser_montant(ancienne_operation["montant"])
    )

    if nouvelle_operation is not None:
        nouvelle_date = nouvelle_operation["date"]
        nouveau_type = nouvelle_operation["type"]
        nouvelle_categorie = nouvelle_operation["categorie"]
        nouveau_montant_centimes = convertir_montant_en_centimes(
            normaliser_montant(nouvelle_operation["montant"])
        )
        nouveau_detail = nouvelle_operation.get("detail", "")
    else:
        # Une suppression n'a pas d'état "après" : SQLite stocke donc NULL.
        nouvelle_date = None
        nouveau_type = None
        nouvelle_categorie = None
        nouveau_montant_centimes = None
        nouveau_detail = None

    connexion.execute(
        """
        INSERT INTO audit_logs (
            operation_id,
            action,
            date_action,
            ancienne_date,
            ancien_type,
            ancienne_categorie,
            ancien_montant_centimes,
            ancien_detail,
            nouvelle_date,
            nouveau_type,
            nouvelle_categorie,
            nouveau_montant_centimes,
            nouveau_detail
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            operation_id,
            action,
            date_action,
            ancienne_operation["date"],
            ancienne_operation["type"],
            ancienne_operation["categorie"],
            ancien_montant_centimes,
            ancienne_operation.get("detail", ""),
            nouvelle_date,
            nouveau_type,
            nouvelle_categorie,
            nouveau_montant_centimes,
            nouveau_detail,
        ),
    )

def lister_operations_par_mois(connexion, annee, mois):
    """Lister les opérations correspondant à un mois et une année."""

    cursor = connexion.cursor()
    cursor.execute(
        """
        SELECT id, date, type, categorie, montant_centimes, detail
        FROM operations
        WHERE substr(date, 7, 4) = ?
          AND substr(date, 4, 2) = ?
        ORDER BY id
        """,
        (
            str(annee),
            f"{mois:02d}",
        ),
    )

    return [
        ligne_vers_operation(ligne)
        for ligne in cursor.fetchall()
    ]

def lister_logs_audit_par_mois(connexion, annee, mois):
    """Lister les logs d'audit concernant un mois et une année."""

    cursor = connexion.cursor()
    cursor.execute(
        """
        SELECT
            id,
            operation_id,
            action,
            date_action,
            ancienne_date,
            ancien_type,
            ancienne_categorie,
            ancien_montant_centimes,
            ancien_detail,
            nouvelle_date,
            nouveau_type,
            nouvelle_categorie,
            nouveau_montant_centimes,
            nouveau_detail
        FROM audit_logs
        WHERE (
            substr(ancienne_date, 7, 4) = ?
            AND substr(ancienne_date, 4, 2) = ?
        )
        OR (
            nouvelle_date IS NOT NULL
            AND substr(nouvelle_date, 7, 4) = ?
            AND substr(nouvelle_date, 4, 2) = ?
        )
        ORDER BY id
        """,
        (
            str(annee),
            f"{mois:02d}",
            str(annee),
            f"{mois:02d}",
        ),
    )
    lignes = cursor.fetchall()

    return [
        ligne_vers_log_audit(ligne)
        for ligne in lignes
    ]
    cursor.execute(
        """
        SELECT
            id,
            operation_id,
            action,
            date_action,
            ancienne_date,
            ancien_type,
            ancienne_categorie,
            ancien_montant_centimes,
            ancien_detail,
            nouvelle_date,
            nouveau_type,
            nouvelle_categorie,
            nouveau_montant_centimes,
            nouveau_detail
        FROM audit_logs
        WHERE (
            substr(ancienne_date, 7, 4) = ?
            AND substr(ancienne_date, 4, 2) = ?
        )
        OR (
            nouvelle_date IS NOT NULL
            AND substr(nouvelle_date, 7, 4) = ?
            AND substr(nouvelle_date, 4, 2) = ?
        )
        ORDER BY id
        """,
        (
            str(annee),
            f"{mois:02d}",
            str(annee),
            f"{mois:02d}",
        ),
    )

def ligne_vers_log_audit(ligne):
    """Convertir une ligne SQLite en dictionnaire de log d'audit."""
    return {
        "id": ligne[0],
        "operation_id": ligne[1],
        "action": ligne[2],
        "date_action": ligne[3],
        "ancienne_date": ligne[4],
        "ancien_type": ligne[5],
        "ancienne_categorie": ligne[6],
        "ancien_montant": convertir_centimes_en_montant(ligne[7]),
        "ancien_detail": ligne[8],
        "nouvelle_date": ligne[9],
        "nouveau_type": ligne[10],
        "nouvelle_categorie": ligne[11],
        "nouveau_montant": (
            convertir_centimes_en_montant(ligne[12])
            if ligne[12] is not None
            else None
        ),
        "nouveau_detail": ligne[13],
    }