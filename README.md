# INF1007-Projet2-Supermarche
Travail sur les bases de données

## Présentation du projet

Ce projet INF1007 consiste à développer une application Python
de prédiction de prix dans un contexte de supermarché.

L'application propose un jeu intitulé
« Devine le prix en trois essais ».

Le joueur doit retrouver un prix cible en trois tentatives maximum.

## Fonctionnalités

- Interface graphique réalisée avec Tkinter.
- Validation des données numériques et catégorielles.
- Trois tentatives maximum pour deviner le prix.
- Tolérance de 5 % autour du prix cible.
- Indices pour guider le joueur.
- Simulation avec visualisation graphique.
- Enregistrement des parties dans un fichier CSV.
- Consultation de l'historique des parties.

## État actuel du développement

Les modules de validation, de jeu et d'historique disposent
de 15 tests automatisés réussis avec pytest.

L'application utilise actuellement un prix cible temporaire
de 120 dollars.

L'intégration du modèle de prédiction développé par Davy
sera réalisée ultérieurement.

## Lancement de l'application

Ouvrir un terminal à la racine du projet.

Pour lancer l'application :

    python3 -m src.main

L'application comporte trois onglets :
- Jeu : deviner le prix en trois essais.
- Simulation : visualiser les résultats graphiquement.
- Historique : consulter les parties enregistrées.

## Tests automatisés

Les tests sont réalisés avec pytest.

Pour lancer tous les tests :

    python3 -m pytest tests/ -v

Pour tester uniquement la logique du jeu :

    python3 -m pytest tests/test_jeu.py -v

Les tests vérifient :
- La validation des variables.
- La tolérance de 5 %.
- La limite de trois essais.
- La gestion des saisies invalides.
- La sauvegarde de l'historique.
- La mise à jour des parties sans doublons.


## Installation des dépendances

Le projet nécessite Python 3 et les bibliothèques
externes indiquées dans requirements.txt.

Pour les installer :

    python3 -m pip install -r requirements.txt

L'interface utilise également Tkinter, qui doit
être disponible dans l'installation de Python.

## Organisation du projet

- src/ : code source de l'application.
- tests/ : tests automatisés avec pytest.
- README.md : documentation du projet.
- requirements.txt : bibliothèques nécessaires.
- historique_parties.csv : historique des manches.
- supermarket_sales - Sheet1.csv : données du supermarché.

