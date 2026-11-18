"""Vérifications de la métrique, des sauvegardes et du partage des données."""

import json
import os

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import root_mean_squared_error

from src.donnees import RACINE
from src.entrainer import creer_metadonnees
from src.modele import ModeleTicket, rmse_numpy


def test_rmse_connue_et_sklearn():
    """Les erreurs 0 et 4 donnent sqrt(8), indépendamment de l'implémentation."""
    reels = [10, 20]
    predictions = [10, 16]
    assert rmse_numpy(reels, predictions) == pytest.approx(np.sqrt(8))
    assert rmse_numpy(reels, predictions) == pytest.approx(root_mean_squared_error(reels, predictions))


@pytest.mark.parametrize("reels,predictions", [([], []), ([1], [1, 2]), ([1], [float("nan")])])
def test_rmse_invalide(reels, predictions):
    with pytest.raises(ValueError):
        rmse_numpy(reels, predictions)


def test_sauvegarde_et_validation(tmp_path):
    """Une relation artificielle simple vérifie chargement et contrat d'entrée."""
    x = pd.DataFrame({
        "prix_unitaire": [10., 20., 30., 40.], "heure": [12] * 4,
        "categorie": ["Food and beverages"] * 4, "type_client": ["Member"] * 4,
        "succursale": ["A"] * 4, "paiement": ["Cash"] * 4,
        "jour_semaine": ["lundi"] * 4,
    })
    y = pd.Series([21., 42., 63., 84.])
    modele = ModeleTicket()
    modele.entrainer(x, y)
    metadata = creer_metadonnees(x, {})
    fichier = str(tmp_path / "modele.joblib")
    json_path = str(tmp_path / "metadata.json")
    modele.sauvegarder(fichier, json_path, metadata)
    charge = ModeleTicket()
    charge.charger(fichier, json_path)
    exemple = x.iloc[1].to_dict()
    assert charge.predire(exemple) == pytest.approx(42.)
    assert charge.predire(exemple) == pytest.approx(modele.predire(exemple))
    with pytest.raises(ValueError):
        charge.predire({**exemple, "heure": 12.5})
    with pytest.raises(ValueError):
        charge.predire({**exemple, "categorie": "inconnue"})
    with pytest.raises(ValueError):
        charge.predire({**exemple, "prix_unitaire": 99})


def test_modele_non_charge():
    with pytest.raises(ValueError):
        ModeleTicket().predire_lot(pd.DataFrame())


def test_separation_sauvegardee():
    """Contrôle les identifiants du partage réel sans charger le CSV sous licence."""
    with open(os.path.join(RACINE, "modeles", "separation.json"), encoding="utf-8") as fichier:
        separation = json.load(fichier)
    train = set(separation["entrainement"])
    test = set(separation["test"])
    assert len(train) == 800
    assert len(test) == 200
    assert train.isdisjoint(test)
    assert train | test == set(range(1000))
