"""Vérifie le contrat des données sur de petites transactions indépendantes."""

import pandas as pd
import pytest

from src.donnees import ENTREES, JeuDeDonnees


@pytest.fixture
def transaction() -> dict:
    """Renvoie une transaction avec une date ambiguë et des colonnes à exclure."""
    return {
        "Unit price": 20.0, "Product line": "Food and beverages",
        "Customer type": "Member", "Branch": "A", "Payment": "Cash",
        "Time": "13:08", "Date": "1/5/2019", "Total": 63.0,
        "Quantity": 3, "Tax 5%": 3.0, "cogs": 60.0,
    }


def charger_exemple(tmp_path, transaction: dict) -> JeuDeDonnees:
    """Écrit puis charge la transaction reçue dans un CSV temporaire."""
    chemin = tmp_path / "exemple.csv"
    pd.DataFrame([transaction]).to_csv(chemin, index=False)
    jeu = JeuDeDonnees(str(chemin))
    jeu.charger()
    return jeu


def test_date_americaine_et_contrat(tmp_path, transaction):
    jeu = charger_exemple(tmp_path, transaction)
    preparees = jeu.preparer()
    x, y = jeu.separer_entrees_cible()
    assert preparees.loc[0, "jour_semaine"] == "samedi"  # 5 janvier 2019
    assert preparees.loc[0, "heure"] == 13
    assert list(x.columns) == ENTREES
    assert x.shape == (1, 7)
    assert "Quantity" not in x and "total" not in x
    assert y.iloc[0] == pytest.approx(63.0)


def test_fichier_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        JeuDeDonnees(str(tmp_path / "absent.csv")).charger()


def test_colonne_absente(tmp_path, transaction):
    del transaction["Total"]
    with pytest.raises(ValueError, match="Total"):
        charger_exemple(tmp_path, transaction)


@pytest.mark.parametrize("valeur", [0, -1, float("inf"), float("nan"), "texte"])
def test_prix_invalide(tmp_path, transaction, valeur):
    transaction["Unit price"] = valeur
    jeu = charger_exemple(tmp_path, transaction)
    with pytest.raises(ValueError):
        jeu.preparer()


def test_ordre_appels():
    jeu = JeuDeDonnees("non_utilise.csv")
    with pytest.raises(ValueError):
        jeu.preparer()
    with pytest.raises(ValueError):
        jeu.separer_entrees_cible()


def test_resultats_ne_modifient_pas_etat(tmp_path, transaction):
    jeu = charger_exemple(tmp_path, transaction)
    copie = jeu.preparer()
    copie.loc[0, "total"] = 999
    _, y = jeu.separer_entrees_cible()
    assert y.iloc[0] == pytest.approx(63.0)
    assert jeu.bilan() == {"lignes": 1, "colonnes": 11, "valeurs_manquantes": 0, "doublons": 0}
