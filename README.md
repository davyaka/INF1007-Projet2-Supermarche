# INF1007-Projet2-Supermarche
Travail sur les bases de données

## Ticket mystère au supermarché

Projet de Davy et Cindy : le joueur estime le montant d'une transaction à partir
d'indices, avec la quantité cachée, puis tente de retrouver la prédiction du modèle en trois essais.
Le code de l'application n'est pas encore implémenté.

## Structure

```text
donnees/          Données et consignes sur leur provenance
modeles/          Modèle sauvegardé et métadonnées JSON à produire
src/             Code Python à développer
tests/           Tests pytest à écrire au fil du travail
graphiques/      Graphiques d'exploration sauvegardés
DECISIONS.md     Choix, justifications et validations
JOURNAL_IA.md    Usages réels de l'IA et vérifications
requirements.txt Dépendances Python
```

Le guide PDF présent dans ce dépôt décrit la répartition et les étapes.
Les fichiers .gitkeep permettent à Git de conserver les dossiers encore vides.

## Préparer l'environnement (Windows)

Depuis la racine du dépôt :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Les commandes d'entraînement, de lancement et de test seront ajoutées quand les
modules correspondants seront disponibles. Les tests et la CI restent à créer.

## À compléter avant remise

- Source exacte et licence du jeu de données ; téléchargement ou redistribution.
- Installation vérifiée, versions utilisées et commandes de lancement.
- Structure des modules et classes, entrées et cible, préparation des données.
- Séparation entraînement/test, métrique, score et comparaison à la référence.
- Couverture réelle des tests et workflow GitHub Actions.
- Au moins trois pages de documentation officielle effectivement consultées.
- Outil du chapitre 7 utilisé et justification.
- Limites du modèle et avertissement pédagogique.

Le CSV local est ignoré par Git en attendant la confirmation de sa licence.

## Règles mises à jour : trois essais

La cible reste le total de la transaction (hypothèse du guide), pas le prix unitaire.
Le modèle calcule une seule estimation cachée par manche. Le joueur dispose de
trois propositions valides, avec un indice « plus élevé » ou « plus bas » après
chaque erreur. Une saisie invalide ne consomme pas de chance. La cible est révélée
à la victoire ou après la troisième erreur. Tolérance proposée : ±5 %, distincte
de l'incertitude du modèle. L'historique et le graphique masquent la cible active.
Le montant réel du CSV sert à évaluer le modèle, pas à déterminer la victoire.
Voir le guide mis à jour pour les détails et la répartition Davy/Cindy.
