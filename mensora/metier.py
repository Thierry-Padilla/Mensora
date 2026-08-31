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

    try:
        # L'interface acceptera la virgule française comme séparateur décimal.
        montant_converti = Decimal(str(montant_operation).replace(",", "."))
    except InvalidOperation:
        return (False, "Le montant doit être un nombre valide.")

    if not montant_converti.is_finite():
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

    Le regroupement par catégorie concerne actuellement les dépenses. Le
    regroupement équivalent des revenus reste la prochaine évolution métier.
    """

    total_revenu = 0
    total_depense = 0
    total_categorie = {}

    for operation in operations:
        if operation["type"] == "revenu":
            total_revenu += operation["montant"]

        elif operation["type"] == "depense":
            total_depense += operation["montant"]
            categorie = operation["categorie"]
            montant = operation["montant"]
            if categorie in total_categorie:
                total_categorie[categorie] += montant
            else:
                total_categorie[categorie] = montant

    reste = total_revenu - total_depense
    return total_revenu, total_depense, reste, total_categorie
