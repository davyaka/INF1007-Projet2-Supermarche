# Journal d'utilisation de l'IA

Consigner les usages réels au fil du travail : au moins cinq entrées à la remise,
dont une vérification ayant changé une décision. Ne pas inventer de vérifications.

| Date | Outil | Ce que vous avez demandé | Réponse reçue | Vérification faite (documentation, test, exécution) | Décision (gardé, modifié, rejeté) |
|---|---|---|---|---|---|
| 2026-11-14 | Codex | Réaliser entraînement, évaluation et sauvegarde avec code simple | Régression linéaire dans une Pipeline, référence moyenne, RMSE vectorisée, joblib et JSON ; API pour Cindy | Entraînement 800/test 200 ; RMSE NumPy et sklearn identiques (188,348946), référence 255,746440 ; 17 tests réussis dont rechargement et séparation ; 200 situations compatibles avec les métadonnées | Implémenté et vérifié par Codex ; Davy doit relire et pouvoir expliquer le code |
| 2026-11-14 | Codex | Lancer les tests des données et créer un graphique avec du code simple reprenant le cours | Module exploration.py : histogramme des totaux, moyenne et médiane ; commandes et explications dans le README | Exécution des 10 tests : tous réussis ; génération de l'image sur les 1 000 transactions ; contrôle visuel du titre, des axes et de la légende ; consultation de la documentation Matplotlib | Implémenté et vérifié par Codex ; à relire et expliquer par Davy avant remise |

