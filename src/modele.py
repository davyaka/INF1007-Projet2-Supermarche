"""Modèle de total : préparation, évaluation et chargement pour l'interface."""

import json
import os
from functools import wraps
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.donnees import ENTREES

NUMERIQUES = ["prix_unitaire", "heure"]
CATEGORIELLES = [nom for nom in ENTREES if nom not in NUMERIQUES]


def chronometrer(fonction):
    """Décore une fonction en affichant sa durée ; conserve résultat et exceptions."""
    @wraps(fonction)
    def enveloppe(*args, **kwargs):
        """Transmet les arguments, renvoie le résultat et affiche le temps écoulé."""
        debut = perf_counter()
        resultat = fonction(*args, **kwargs)
        print(f"Durée de {fonction.__name__} : {perf_counter() - debut:.3f} s")
        return resultat
    return enveloppe


def rmse_numpy(reels, predictions) -> float:
    """Renvoie la RMSE vectorisée ; lève ValueError sur tableaux invalides."""
    reels = np.asarray(reels, dtype=float)
    predictions = np.asarray(predictions, dtype=float)
    if reels.ndim != 1 or reels.shape != predictions.shape or reels.size == 0:
        raise ValueError("Deux listes non vides de même taille sont nécessaires.")
    if not np.isfinite(reels).all() or not np.isfinite(predictions).all():
        raise ValueError("Les montants doivent être finis.")
    return float(np.sqrt(np.mean((reels - predictions) ** 2)))


def creer_pipeline() -> Pipeline:
    """Renvoie un prétraitement et une régression non entraînés."""
    preparation = ColumnTransformer([
        ("categories", OneHotEncoder(handle_unknown="ignore", drop="first"), CATEGORIELLES),
        ("nombres", "passthrough", NUMERIQUES),
    ])
    return Pipeline([("preparation", preparation), ("regression", LinearRegression())])


class ModeleTicket:
    """Conserve la Pipeline et les métadonnées utilisées par l'interface."""

    def __init__(self) -> None:
        """Initialise un modèle vide, sans entraînement ni ouverture de fichier."""
        self._pipeline: Pipeline | None = None
        self._metadonnees: dict = {}

    @chronometrer
    def entrainer(self, entrees: pd.DataFrame, cible: pd.Series) -> None:
        """Ajuste la Pipeline sur l'entraînement reçu ; propage les erreurs sklearn."""
        pipeline = creer_pipeline()
        pipeline.fit(entrees[ENTREES], cible)
        self._pipeline = pipeline
        self._metadonnees = {}

    def sauvegarder(self, chemin_modele: str, chemin_json: str, metadonnees: dict) -> None:
        """Écrit le modèle et son JSON ; lève ValueError si non entraîné, OSError sinon."""
        if self._pipeline is None:
            raise ValueError("Le modèle n'est pas entraîné.")
        with open(chemin_modele, "wb") as fichier:
            joblib.dump(self._pipeline, fichier)
        with open(chemin_json, "w", encoding="utf-8") as fichier:
            json.dump(metadonnees, fichier, ensure_ascii=False, indent=2, allow_nan=False)
        self._metadonnees = metadonnees

    def charger(self, chemin_modele: str, chemin_json: str) -> None:
        """Charge les fichiers du projet ; lève FileNotFoundError s'ils manquent.

        Charger uniquement des modèles de confiance, avec les versions documentées.
        """
        for chemin in [chemin_modele, chemin_json]:
            if not os.path.isfile(chemin):
                raise FileNotFoundError(f"Fichier du modèle absent : {chemin}")
        with open(chemin_modele, "rb") as fichier:
            pipeline = joblib.load(fichier)
        with open(chemin_json, encoding="utf-8") as fichier:
            metadonnees = json.load(fichier)
        self._pipeline = pipeline
        self._metadonnees = metadonnees

    def predire(self, entrees: dict) -> float:
        """Renvoie le total brut d'une situation ; lève ValueError si saisie invalide.

        La validation suit les métadonnées. Sans métadonnées, cette méthode échoue :
        pendant l'évaluation, utiliser predire_lot sur les lignes de test.
        """
        if not self._metadonnees:
            raise ValueError("Charger ou sauvegarder les métadonnées avant de jouer.")
        valeurs = {}
        for variable in self._metadonnees["variables"]:
            nom = variable["nom"]
            valeur = entrees.get(nom)
            if variable["type"] == "categorielle":
                if valeur not in variable["categories"]:
                    raise ValueError(f"Catégorie invalide pour {nom}.")
            else:
                try:
                    valeur = float(valeur)
                except (ValueError, TypeError) as erreur:
                    raise ValueError(f"Nombre requis pour {nom}.") from erreur
                if not np.isfinite(valeur) or not variable["minimum"] <= valeur <= variable["maximum"]:
                    raise ValueError(f"Valeur hors intervalle pour {nom}.")
                if variable["type"] == "entier":
                    if not valeur.is_integer():
                        raise ValueError(f"Un entier est requis pour {nom}.")
                    valeur = int(valeur)
            valeurs[nom] = valeur
        resultat = float(self.predire_lot(pd.DataFrame([valeurs]))[0])
        if not np.isfinite(resultat) or resultat <= 0:
            raise ValueError("Estimation non positive : choisir une autre situation.")
        return resultat

    def predire_lot(self, entrees: pd.DataFrame) -> np.ndarray:
        """Renvoie les estimations brutes ; lève ValueError avant entraînement/chargement."""
        if self._pipeline is None:
            raise ValueError("Charger ou entraîner le modèle avant de prédire.")
        return self._pipeline.predict(entrees[ENTREES])

    def __str__(self) -> str:
        """Renvoie le type du modèle et son état."""
        return f"ModeleTicket(régression linéaire, prêt={self._pipeline is not None})"
