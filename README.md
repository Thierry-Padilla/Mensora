# Mensora

Mensora est une application Python locale destinée à simplifier la gestion d'un budget mensuel pour une personne peu à l'aise avec l'informatique.

## Statut

Projet pédagogique en développement. Le backend local est opérationnel et la première fenêtre mensuelle Tkinter est en construction. Mensora n'est pas encore une V1 terminée.

Le socle backend est opérationnel et testé : règles métier, SQLite, opérations CRUD, journal d'audit et lectures mensuelles.

## Fonctionnalités actuellement présentes

- validation des dates, avec refus des dates futures ;
- validation des types et des catégories autorisées ;
- normalisation exacte des montants positifs avec deux décimales au maximum ;
- commentaire obligatoire pour certaines catégories ;
- calcul des revenus, des dépenses et du reste ;
- regroupement séparé des revenus et des dépenses par catégorie ;
- ajout, lecture, modification et suppression dans SQLite ;
- journalisation des modifications et suppressions ;
- lecture des opérations et des journaux par mois ;
- premier squelette de la fenêtre mensuelle Tkinter ;
- tests automatisés avec la bibliothèque standard.

Les formulaires GUI, la navigation entre les mois, l'affichage des données réelles, l'export PDF et l'exécutable Windows ne sont pas encore implémentés.

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
│   ├── metier.py
│   ├── stockage.py
│   └── interface/
│       ├── __init__.py
│       ├── application.py
│       └── fenetre_principale.py
└── tests/
    ├── test_interface.py
    ├── test_metier.py
    └── test_stockage.py
```

- `main.py` lance l'application graphique ;
- `mensora/metier.py` contient les règles métier testables ;
- `mensora/stockage.py` contient la persistance SQLite et l'audit ;
- `mensora/interface/` contient la fenêtre mensuelle Tkinter.

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

Le lancement ouvre la fenêtre mensuelle de Mensora.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Données personnelles

Le dépôt contient uniquement du code et des données fictives. Les futures bases SQLite, archives PDF et données financières réelles sont exclues de Git et devront rester sur l'ordinateur de l'utilisateur.

## Prochaine étape

Relier la fenêtre principale aux opérations et totaux du mois, sans commencer encore les formulaires d'ajout ou de modification.

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
