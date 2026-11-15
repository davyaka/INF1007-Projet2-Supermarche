
import csv
import json
import os
from pathlib import Path


class Historique:
    """Gère la sauvegarde des parties dans un fichier CSV."""

    def __init__(self, chemin: str):
        self._chemin = Path(chemin)

    def ajouter(self, enregistrement: dict) -> None:
        """Ajoute une partie ou actualise une partie existante."""
        donnees = self.lire()

        identifiant = enregistrement["id_manche"]

        for i, partie in enumerate(donnees):
            if partie["id_manche"] == identifiant:
                donnees[i] = enregistrement.copy()
                break
        else:
            donnees.append(enregistrement.copy())

        self._sauvegarder(donnees)

    def lire(self) -> list[dict]:
        """Retourne les parties enregistrées."""
        if not self._chemin.exists():
            return []

        with open(
            self._chemin, "r", encoding="utf-8", newline=""
        ) as fichier:
            lecteur = csv.DictReader(fichier)
            resultat = []

            for ligne in lecteur:
                for champ in ("entrees", "propositions", "indices"):
                    if ligne.get(champ):
                        ligne[champ] = json.loads(ligne[champ])

                resultat.append(ligne)

            return resultat

    def _sauvegarder(self, donnees: list[dict]) -> None:
        """Enregistre les parties avec un en-tête unique."""
        self._chemin.parent.mkdir(
            parents=True, exist_ok=True
        )

        colonnes = [
            "id_manche", "horodatage", "mode",
            "entrees", "prediction_brute",
            "cible", "tolerance",
            "propositions", "indices",
            "essais_utilises", "etat"
        ]

        with open(
            self._chemin, "w", encoding="utf-8", newline=""
        ) as fichier:
            ecrivain = csv.DictWriter(
                fichier, fieldnames=colonnes
            )
            ecrivain.writeheader()

            for partie in donnees:
                ligne = partie.copy()

                for champ in ("entrees", "propositions", "indices"):
                    ligne[champ] = json.dumps(
                        ligne.get(champ, []),
                        ensure_ascii=False
                    )

                ecrivain.writerow(ligne)


