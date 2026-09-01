# AGENTS.md — Mensora

Ce fichier complète les règles globales HELIX avec le contexte propre à Mensora. Il ne les remplace pas et ne les duplique pas.

## Objectif du projet

Mensora est une petite application locale de gestion financière mensuelle, conçue en priorité pour une personne peu à l'aise avec l'informatique. La V1 doit être simple, claire, fiable, présentable, testée et exécutable sous Windows.

Mensora est aussi un projet pédagogique et une preuve concrète des compétences Python de Thierry. Thierry doit pouvoir expliquer la logique métier, les choix techniques et le parcours des données.

## Phase actuelle

Interface Tkinter : premier squelette de la fenêtre mensuelle.

État vérifié :

- les règles métier, les totaux et la normalisation monétaire sont testés ;
- SQLite couvre les opérations CRUD, le journal d'audit et les lectures mensuelles ;
- les modifications et suppressions sont journalisées dans la même transaction ;
- la fenêtre principale affiche le mois courant, les actions principales, un tableau vide et les totaux à zéro ;
- `main.py` lance uniquement l'application graphique ;
- 39 tests automatisés passent ;
- aucune base réelle ni donnée financière personnelle n'est intégrée au dépôt.

Prochaine étape unique : alimenter la fenêtre avec les opérations et totaux du mois sans commencer encore les formulaires.

## Priorité

Milestone actif : terminer Mensora V1.0 sans dispersion. Toute idée qui n'aide pas concrètement à terminer cette V1 va au backlog.

## Stack

- Windows ;
- Python 3.13.3 ;
- bibliothèque standard en priorité : `datetime`, `sqlite3`, `calendar`, `decimal` et `tkinter` selon l'avancement ;
- ReportLab seulement au moment de l'export PDF ;
- PyInstaller seulement au moment du packaging Windows.

Ne pas installer les dépendances futures avant qu'elles soient nécessaires.

## Architecture actuelle

Le projet reste volontairement minimal :

- `main.py` : point d'entrée minimal de l'application ;
- `mensora/metier.py` : catégories, validation et calculs ;
- `mensora/stockage.py` : SQLite, CRUD, audit et lectures mensuelles ;
- `mensora/interface/application.py` : démarrage de Tkinter ;
- `mensora/interface/fenetre_principale.py` : fenêtre mensuelle ;
- `tests/test_metier.py` : tests automatisés des règles métier ;
- `tests/test_stockage.py` : tests du stockage et de l'audit ;
- `tests/test_interface.py` : logique d'interface testable sans affichage ;
- `.venv/` : environnement virtuel local non versionné ;
- aucun autre module tant qu'une responsabilité réelle ne justifie sa création.

Ordre de développement attendu : modèle métier, calculs, validation, SQLite, CRUD, journal d'audit, logique mensuelle, tests backend, interface Tkinter, PDF, exécutable, puis QA finale.

## Commandes

Depuis PowerShell, à la racine du projet :

```powershell
.\.venv\Scripts\Activate.ps1
python .\main.py
```

Tests :

```powershell
python -m unittest discover -s tests -v
```

Aucun linter ou formateur externe n'est configuré. Ne pas en annoncer avant sa mise en place réelle.

## Règles de collaboration propres à Mensora

- Mode par défaut : apprentissage.
- Thierry écrit la logique métier ayant une valeur pédagogique.
- Codex agit comme mentor, reviewer, debugger et support d'ingénierie.
- Donner des indices progressifs avant une solution complète, sauf demande explicite.
- Vérifier le fichier réel et exécuter le plus petit contrôle pertinent avant de confirmer un comportement.
- Ne pas réécrire `calculer_totaux()` si son comportement reste correct.
- Backend et tests avant l'interface graphique.
- Ne pas ajouter d'IA, de cloud, d'API bancaire, de serveur ou d'architecture distribuée à la V1.
- Ne pas créer de journal d'apprentissage local : utiliser le LearningLog transversal prévu par HELIX.
- Le dépôt public ne contient aucune licence open source ; ne pas en ajouter sans décision explicite de Thierry.

## Contrat d'interface V1

- L'interface est conçue pour une utilisation principalement à la souris, avec de gros contrôles lisibles.
- La date du jour est sélectionnée par défaut et reste modifiable au moyen d'un calendrier mensuel cliquable.
- Les dates passées et la date du jour sont sélectionnables ; les dates futures sont désactivées dans l'interface.
- Le type `revenu` ou `depense` et la catégorie sont choisis dans des contrôles cliquables, sans saisie libre.
- Le montant est le principal champ saisi au clavier.
- Le champ de détail reste caché pour les catégories qui n'en ont pas besoin et apparaît uniquement lorsqu'il est obligatoire.
- Ce champ permet soit de saisir un texte libre, soit de choisir une suggestion dans une courte liste, par exemple `Boulangerie` ou `Restaurant`.
- Les suggestions restent de simples détails : elles ne créent pas de nouvelles catégories.
- La liste de suggestions reste fixe pour la V1 ; aucun apprentissage automatique à partir de l'historique.

## Catégories V1

Revenus :

- `Retraite` : sans détail ;
- `Divers` : détail obligatoire, notamment pour un remboursement ou une rentrée exceptionnelle.

Dépenses sans détail :

- `Courses` ;
- `Essence` ;
- `Tabac` ;
- `Santé` ;
- `Retrait`.

Dépenses avec détail obligatoire :

- `Loisirs` ;
- `Factures`, avec des suggestions telles que `Free`, `Téléphone`, `Eau`, `Électricité`, `Assurance`, `Impôts` et `Autre charge` ;
- `Achats en ligne`, avec des suggestions telles que `Amazon`, `Cdiscount` et `Autre site` ;
- `Divers`, avec des suggestions telles que `Boulangerie`, `Restaurant` et `Autre`.

## Contrats métier essentiels

- Une opération contient : `id`, `date`, `type`, `categorie`, `montant` et `detail`.
- Les types autorisés sont `revenu` et `depense`.
- Les opérations sont la source de vérité ; les totaux sont toujours recalculés.
- Les totaux par catégorie sont calculés séparément pour les revenus et les dépenses.
- La validation retourne `(True, "")` ou `(False, "message explicite")`.
- Le montant accepte les centimes et doit être strictement positif.
- Une date doit être valide, antérieure ou égale à la date du jour ; toute date future est refusée par le backend.
- La catégorie `Divers` exige un détail non vide.
- Les catégories `Loisirs`, `Factures` et `Achats en ligne` exigent également un détail non vide.
- Un `Retrait` compte immédiatement comme une dépense ; les achats effectués ensuite avec ce liquide ne sont pas enregistrés séparément afin d'éviter un double comptage.
- Une seule base SQLite doit contenir tous les mois.
- Les modifications et suppressions sont enregistrées dans un journal d'audit séparé des opérations.
- Une suppression exige une confirmation de l'utilisateur.
- Les données doivent rester séparées de l'exécutable Windows.

## Archivage PDF V1

- SQLite reste la source de vérité et conserve les opérations sans limite artificielle.
- Au premier démarrage pendant un nouveau mois, Mensora génère automatiquement le PDF du mois terminé.
- Les PDF des éventuels mois manqués sont également créés au prochain démarrage.
- Un PDF est produit même pour un mois sans opération.
- Si une ancienne opération est modifiée ou supprimée, le PDF du mois concerné est régénéré.
- Les archives sont conservées sous `Documents\Mensora\Archives\<année>\<Mois><Année>.pdf`.

## Intégration Windows V1

- L'application est installée dans un emplacement stable, séparé des données.
- Un raccourci Mensora est placé sur le Bureau.
- Mensora démarre automatiquement avec Windows en arrière-plan.
- Une icône de zone de notification permet au minimum d'ouvrir l'application et de la quitter.
- L'ouverture depuis le raccourci affiche l'instance déjà active au lieu de lancer plusieurs instances.

## Données et sécurité

Mensora manipulera des données financières personnelles locales. Ne jamais ajouter une base réelle, des données personnelles ou des exports personnels au dépôt. Lorsque SQLite sera introduit, vérifier explicitement l'emplacement de la base et son exclusion de Git.

## Définition de terminé pour une tâche

Une tâche est terminée lorsque :

- le comportement demandé fonctionne ;
- les contrôles ou tests pertinents passent ;
- aucune régression bloquante connue ne subsiste ;
- Thierry comprend la logique pédagogique introduite ;
- le diff reste limité à la tâche ;
- la documentation reste factuelle.
