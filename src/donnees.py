"""Chargement et préparation des transactions pour le modèle de prix total."""

import os

import numpy as np
import pandas as pd


RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREES = [
    "prix_unitaire", "categorie", "type_client", "succursale",
    "paiement", "heure", "jour_semaine",
]
COLONNES_REQUISES = [
    "Unit price", "Product line", "Customer type", "Branch",
    "Payment", "Time", "Date", "Total",
]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def chemin_csv() -> str:
    """Renvoie le chemin du CSV ; lève FileNotFoundError si aucun fichier n'existe."""
    candidats = [
        os.path.join(RACINE, "donnees", "supermarket_sales.csv"),
        os.path.join(RACINE, "supermarket_sales - Sheet1.csv"),
    ]
    for chemin in candidats:
        if os.path.isfile(chemin):
            return chemin
    raise FileNotFoundError("CSV introuvable : placer supermarket_sales.csv dans donnees/.")


class JeuDeDonnees:
    """Conserve les transactions brutes et prépare les variables du modèle."""

    def __init__(self, chemin: str) -> None:
        """Mémorise le chemin reçu sans ouvrir le fichier ; ne renvoie rien."""
        self._chemin = chemin
        self._brutes: pd.DataFrame | None = None
        self._preparees: pd.DataFrame | None = None

    def charger(self) -> pd.DataFrame:
        """Charge le CSV et renvoie une copie ; lève FileNotFoundError ou ValueError."""
        if not os.path.isfile(self._chemin):
            raise FileNotFoundError(f"Fichier introuvable : {self._chemin}")
        with open(self._chemin, encoding="utf-8-sig", newline="") as fichier:
            donnees = pd.read_csv(fichier)
        manquantes = sorted(set(COLONNES_REQUISES) - set(donnees.columns))
        if manquantes:
            raise ValueError(f"Colonnes absentes : {', '.join(manquantes)}")
        if donnees.empty:
            raise ValueError("Le fichier ne contient aucune transaction.")
        self._brutes = donnees
        self._preparees = None
        return donnees.copy()

    def bilan(self) -> dict:
        """Renvoie dimensions, valeurs manquantes et doublons ; échoue avant charger()."""
        if self._brutes is None:
            raise ValueError("Charger les données avant de demander leur bilan.")
        return {
            "lignes": len(self._brutes),
            "colonnes": len(self._brutes.columns),
            "valeurs_manquantes": int(self._brutes.isna().sum().sum()),
            "doublons": int(self._brutes.duplicated().sum()),
        }

    def preparer(self) -> pd.DataFrame:
        """Renvoie sept entrées et total ; lève ValueError si les données sont invalides.

        Les dates sont au format mois/jour/année. Aucun encodage appris ni aucune
        normalisation n'est ajusté ici : cela appartiendra au modèle entraîné.
        """
        if self._brutes is None:
            raise ValueError("Charger les données avant de les préparer.")
        d = self._brutes.copy()
        if d[COLONNES_REQUISES].isna().any().any():
            raise ValueError("Une valeur obligatoire est manquante.")
        for colonne in ["Unit price", "Total"]:
            d[colonne] = pd.to_numeric(d[colonne], errors="raise")
            if not np.isfinite(d[colonne].to_numpy(dtype=float)).all():
                raise ValueError(f"Valeur non finie dans {colonne}.")
            if (d[colonne] <= 0).any():
                raise ValueError(f"Les valeurs de {colonne} doivent être positives.")
        categories = ["Product line", "Customer type", "Branch", "Payment"]
        for colonne in categories:
            if not d[colonne].map(lambda valeur: isinstance(valeur, str)).all():
                raise ValueError(f"La colonne {colonne} doit contenir du texte.")
            d[colonne] = d[colonne].str.strip()
            if d[colonne].eq("").any():
                raise ValueError(f"Catégorie vide dans {colonne}.")
        dates = pd.to_datetime(d["Date"], format="%m/%d/%Y", errors="raise")
        heures = pd.to_datetime(d["Time"], format="%H:%M", errors="raise")
        self._preparees = pd.DataFrame({
            "prix_unitaire": d["Unit price"],
            "categorie": d["Product line"],
            "type_client": d["Customer type"],
            "succursale": d["Branch"],
            "paiement": d["Payment"],
            "heure": heures.dt.hour,
            "jour_semaine": dates.dt.day_of_week.map(dict(enumerate(JOURS))),
            "total": d["Total"],
        })
        return self._preparees.copy()

    def separer_entrees_cible(self) -> tuple[pd.DataFrame, pd.Series]:
        """Renvoie X et y copiés ; lève ValueError avant preparer().

        Cette séparation des colonnes n'est pas le partage entraînement/test.
        """
        if self._preparees is None:
            raise ValueError("Préparer les données avant de séparer X et y.")
        return self._preparees[ENTREES].copy(), self._preparees["total"].copy()

    def __str__(self) -> str:
        """Renvoie un résumé du jeu et de son état de chargement."""
        taille = "non chargé" if self._brutes is None else f"{len(self._brutes)} transactions"
        return f"JeuDeDonnees({taille})"


if __name__ == "__main__":
    jeu = JeuDeDonnees(chemin_csv())
    jeu.charger()
    print(jeu)
    print(jeu.bilan())
    print(jeu.preparer().head().to_string(index=False))
