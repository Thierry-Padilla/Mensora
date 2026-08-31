# Mensora

Mensora est une application Python locale destinée à simplifier la gestion d'un budget mensuel pour une personne peu à l'aise avec l'informatique.

## Statut

Projet pédagogique en développement backend. Mensora n'est pas encore une application utilisable ni une V1 terminée.

Le premier socle métier est opérationnel et testé : validation d'une opération, calcul des revenus, calcul des dépenses, calcul du reste et regroupement des dépenses par catégorie.

## Fonctionnalités actuellement présentes

- validation des dates, avec refus des dates futures ;
- validation des types et des catégories autorisées ;
- validation des montants positifs avec prise en charge des centimes ;
- commentaire obligatoire pour certaines catégories ;
- calcul des revenus, des dépenses et du reste ;
- regroupement des dépenses par catégorie ;
- tests automatisés avec la bibliothèque standard.

SQLite, le CRUD, le journal d'audit, la navigation mensuelle, l'interface graphique, l'export PDF et l'exécutable Windows ne sont pas encore implémentés.

## Stack actuelle

- Python 3.13.3 ;
- bibliothèque standard Python ;
- `unittest` pour les tests ;
- environnement virtuel local `.venv`.

Aucune dépendance externe n'est nécessaire à ce stade.

## Architecture actuelle

```text
Mensora/
├── main.py
├── mensora/
│   ├── __init__.py
│   └── metier.py
└── tests/
    └── test_metier.py
```

- `main.py` est le point d'entrée temporaire de la démonstration ;
- `mensora/metier.py` contient les règles métier testables ;
- `tests/test_metier.py` protège les comportements déjà implémentés.

## Installation locale

Depuis PowerShell :

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Lancement

```powershell
python .\main.py
```

Avec les données fictives actuelles, le programme affiche :

```text
(1000, 380, 620, {'Courses': 300, 'Essence': 80})
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Données personnelles

Le dépôt contient uniquement du code et des données fictives. Les futures bases SQLite, archives PDF et données financières réelles sont exclues de Git et devront rester sur l'ordinateur de l'utilisateur.

## Prochaine étape

Faire évoluer les calculs pour regrouper séparément les catégories de revenus et de dépenses, puis normaliser les montants validés avant la persistance.

## Roadmap V1

1. Finaliser le modèle métier et ses tests.
2. Ajouter la persistance SQLite et les opérations CRUD.
3. Ajouter le journal des modifications et suppressions.
4. Implémenter la logique mensuelle.
5. Construire l'interface Tkinter.
6. Ajouter l'archivage PDF automatique.
7. Produire et vérifier l'exécutable Windows et son démarrage automatique.

## Utilisation du code

Ce dépôt est public à des fins de consultation et de démonstration. Aucune licence open source n'est accordée.
