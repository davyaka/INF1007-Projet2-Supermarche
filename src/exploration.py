"""Graphique exploratoire : répartition des montants des transactions."""

import os

import matplotlib.pyplot as plt
import pandas as pd

from src.donnees import RACINE, JeuDeDonnees, chemin_csv


def creer_histogramme(totaux: pd.Series, chemin_image: str) -> None:
    """Enregistre l'histogramme des totaux préparés dans chemin_image.

    Ne renvoie rien. Les totaux doivent être numériques, finis et non vides,
    comme ceux validés par JeuDeDonnees. Une erreur d'écriture lève OSError.
    """
    # Un histogramme regroupe les montants dans des intervalles.
    figure, axes = plt.subplots(figsize=(9, 5))
    axes.hist(totaux, bins=20, color="steelblue", edgecolor="white")

    # Ces deux lignes aident à comparer moyenne et médiane.
    moyenne = totaux.mean()
    mediane = totaux.median()
    axes.axvline(moyenne, color="darkorange", linestyle="--",
                 label=f"Moyenne : {moyenne:.2f}")
    axes.axvline(mediane, color="darkgreen", linestyle=":",
                 label=f"Médiane : {mediane:.2f}")

    axes.set_title(f"Répartition des montants au supermarché ({len(totaux)} transactions)")
    axes.set_xlabel("Montant total (unités monétaires)")
    axes.set_ylabel("Nombre de transactions")
    axes.legend()
    axes.grid(axis="y", alpha=0.2)
    axes.set_axisbelow(True)
    figure.tight_layout()

    # Sauvegarder l'image pour le rapport et la présentation orale.
    try:
        figure.savefig(chemin_image, dpi=150)
    finally:
        plt.close(figure)


def main() -> None:
    """Charge le CSV et crée le graphique ; propage les erreurs de données/fichier."""
    jeu = JeuDeDonnees(chemin_csv())
    jeu.charger()
    donnees = jeu.preparer()

    dossier = os.path.join(RACINE, "graphiques")
    os.makedirs(dossier, exist_ok=True)
    chemin_image = os.path.join(dossier, "exploration_total.png")
    creer_histogramme(donnees["total"], chemin_image)
    print(f"Graphique enregistré : {chemin_image}")


if __name__ == "__main__":
    main()
