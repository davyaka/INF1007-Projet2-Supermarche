"""Entraînement explicite : python -m src.entrainer. Jamais lancé par l'interface."""

import json
import os
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyRegressor
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import train_test_split

from src.donnees import RACINE, ENTREES, JeuDeDonnees, chemin_csv
from src.modele import ModeleTicket, NUMERIQUES, rmse_numpy


def creer_metadonnees(x_train: pd.DataFrame, resultats: dict) -> dict:
    """Renvoie le contrat JSON issu de l'entraînement, avec métriques et versions."""
    variables = []
    for nom in ENTREES:
        variable = {"nom": nom, "libelle": nom.replace("_", " ").capitalize()}
        if nom in NUMERIQUES:
            variable.update({
                "type": "entier" if nom == "heure" else "numerique",
                "minimum": float(x_train[nom].min()),
                "maximum": float(x_train[nom].max()),
            })
        else:
            variable.update({"type": "categorielle", "categories": sorted(x_train[nom].unique().tolist())})
        variables.append(variable)
    return {
        "version_schema": 1, "cible": "total", "unite": "unités monétaires",
        "colonnes": ENTREES, "variables": variables,
        "modele": "LinearRegression", "graine": 42, "fraction_test": 0.2,
        "metrique": "RMSE", "resultats": resultats,
        "versions": {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                     "numpy": np.__version__, "pandas": pd.__version__, "joblib": joblib.__version__},
        "jeu": {"essais_maximum": 3, "tolerance_relative_proposee": 0.05,
                "cible_du_jeu": "prédiction du modèle arrondie au centime"},
    }


def main() -> None:
    """Entraîne, évalue et sauvegarde ; propage les erreurs de données ou de fichiers."""
    jeu = JeuDeDonnees(chemin_csv())
    jeu.charger()
    jeu.preparer()
    x, y = jeu.separer_entrees_cible()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    modele = ModeleTicket()
    modele.entrainer(x_train, y_train)
    predictions = modele.predire_lot(x_test)

    reference = DummyRegressor(strategy="mean")
    reference.fit(x_train, y_train)
    predictions_reference = reference.predict(x_test)
    rmse = rmse_numpy(y_test, predictions)
    rmse_sklearn = float(root_mean_squared_error(y_test, predictions))
    if not np.isclose(rmse, rmse_sklearn):
        raise ValueError("Les deux calculs de RMSE ne concordent pas.")
    resultats = {
        "lignes_entrainement": len(x_train), "lignes_test": len(x_test),
        "rmse_modele": rmse, "rmse_sklearn": rmse_sklearn,
        "rmse_reference": rmse_numpy(y_test, predictions_reference),
        "moyenne_entrainement": float(y_train.mean()),
        "predictions_test_non_positives": int((predictions <= 0).sum()),
    }

    dossier = os.path.join(RACINE, "modeles")
    os.makedirs(dossier, exist_ok=True)
    metadata = creer_metadonnees(x_train, resultats)
    modele.sauvegarder(os.path.join(dossier, "ticket.joblib"),
                       os.path.join(dossier, "metadonnees.json"), metadata)

    # Identifiants de lignes pour vérifier que les manches ne viennent pas du train.
    with open(os.path.join(dossier, "separation.json"), "w", encoding="utf-8") as fichier:
        json.dump({"entrainement": x_train.index.tolist(), "test": x_test.index.tolist()}, fichier, indent=2)
    manches = x_test.copy()
    manches["total_reel"] = y_test
    manches["prediction_modele"] = predictions
    with open(os.path.join(dossier, "manches_test.csv"), "w", encoding="utf-8", newline="") as fichier:
        manches.to_csv(fichier, index_label="ligne_source")
    print(json.dumps(resultats, indent=2, ensure_ascii=False))
    print("Modèle et métadonnées sauvegardés dans modeles/.")


if __name__ == "__main__":
    main()
