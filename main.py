"""Point d'entrée temporaire de Mensora.

La démonstration en console sera remplacée par le lancement de l'interface
graphique lorsque le backend aura été validé.
"""

from mensora.metier import calculer_totaux


OPERATIONS_EXEMPLE = [
    {
        "id": 1,
        "date": "01/08/2026",
        "type": "revenu",
        "categorie": "Retraite",
        "montant": 1000,
        "detail": "",
    },
    {
        "id": 2,
        "date": "10/08/2026",
        "type": "depense",
        "categorie": "Courses",
        "montant": 300,
        "detail": "",
    },
    {
        "id": 3,
        "date": "10/08/2026",
        "type": "depense",
        "categorie": "Essence",
        "montant": 30,
        "detail": "",
    },
    {
        "id": 4,
        "date": "11/08/2026",
        "type": "depense",
        "categorie": "Essence",
        "montant": 50,
        "detail": "",
    },
]


def main():
    """Exécuter la démonstration actuelle du backend."""

    print(calculer_totaux(OPERATIONS_EXEMPLE))


if __name__ == "__main__":
    main()
