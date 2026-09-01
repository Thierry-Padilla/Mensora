"""Règles métier actuellement implémentées par Mensora.

Ce module ne contient ni interface graphique ni accès à la base de données.
Il peut ainsi être testé indépendamment du reste de l'application.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation


# Source unique des catégories pour la validation et, plus tard, l'interface.
CATEGORIES_PAR_TYPE = {
    "revenu": ["Retraite", "Divers"],
    "depense": [
        "Courses",
        "Essence",
        "Tabac",
        "Santé",
        "Loisirs",
        "Factures",
        "Achats en ligne",
        "Divers",
        "Retrait",
    ],
}

CATEGORIES_DETAIL_OBLIGATOIRE = (
    "Divers",
    "Loisirs",
    "Factures",
    "Achats en ligne",
)


def normaliser_montant(montant):
    """Convertir le montant en Decimal, en acceptant la virgule française.

    La fonction retourne un Decimal à deux décimales, ou None si la valeur
    n'est pas un nombre fini valide ou comporte plus de deux décimales.
    """
    texte_montant = str(montant).replace(",", ".")
    try:
        montant_decimal = Decimal(texte_montant)
        if not montant_decimal.is_finite():
            return None

        if montant_decimal.as_tuple().exponent < -2:
            return None
        return montant_decimal.quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        return None


def valider_operation(operation):
    """Valider une opération sans la modifier.

    La fonction retourne ``(True, "")`` lorsque tous les contrôles passent,
    sinon ``(False, "message explicite")`` dès la première erreur rencontrée.
    """

    date = operation.get("date")
    if not date:
        return (False, "La date est obligatoire.")

    try:
        date_convertie = datetime.strptime(date, "%d/%m/%Y").date()
        date_jour = datetime.today().date()
        if date_convertie > date_jour:
            return (False, "La date ne peut pas être dans le futur.")
    except (ValueError, TypeError):
        return (False, "La date doit être valide au format JJ/MM/AAAA.")

    type_operation = operation.get("type")
    if type_operation not in ["revenu", "depense"]:
        return (False, "Le type doit être 'revenu' ou 'depense'.")

    categorie_operation = operation.get("categorie")
    if categorie_operation not in CATEGORIES_PAR_TYPE[type_operation]:
        return (False, "La catégorie n'est pas valide pour ce type d'opération.")

    montant_operation = operation.get("montant")
    if montant_operation in (None, ""):
        return (False, "Le montant est obligatoire.")

    montant_converti = normaliser_montant(montant_operation)
    if montant_converti is None:
        return (False, "Le montant doit être un nombre valide.")

    if montant_converti <= 0:
        return (False, "Le montant doit être supérieur à 0.")

    detail_operation = operation.get("detail")
    if categorie_operation in CATEGORIES_DETAIL_OBLIGATOIRE:
        if not isinstance(detail_operation, str) or not detail_operation.strip():
            return (False, "Un commentaire est obligatoire pour cette catégorie.")

    return (True, "")


def calculer_totaux(operations):
    """Calculer les totaux à partir des opérations, source de vérité.

    Les revenus et les dépenses sont regroupés séparément par catégorie.
    """

    total_revenu = 0
    total_depense = 0
    totaux_categories_revenus = {}
    totaux_categories_depenses = {}

    for operation in operations:
        if operation["type"] == "revenu":
            total_revenu += operation["montant"]
            categorie = operation["categorie"]
            montant = operation["montant"]
            if categorie in totaux_categories_revenus:
                totaux_categories_revenus[categorie] += montant
            else:
                totaux_categories_revenus[categorie] = montant

        elif operation["type"] == "depense":
            total_depense += operation["montant"]
            categorie = operation["categorie"]
            montant = operation["montant"]
            if categorie in totaux_categories_depenses:
                totaux_categories_depenses[categorie] += montant
            else:
                totaux_categories_depenses[categorie] = montant

    reste = total_revenu - total_depense
    return (
        total_revenu,
        total_depense,
        reste,
        totaux_categories_revenus,
        totaux_categories_depenses,
    )
