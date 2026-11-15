from src.historique import Historique


def test_ajouter_et_lire_historique(tmp_path):
    chemin = tmp_path / "historique_test.csv"
    historique = Historique(str(chemin))

    enregistrement = {
        "id_manche": "TEST001",
        "horodatage": "2026-11-15T10:00:00",
        "mode": "jeu",
        "entrees": {"prix_unitaire": 20},
        "prediction_brute": 100,
        "cible": 100,
        "tolerance": 5,
        "propositions": [80, 100],
        "indices": ["Plus haut", "Bravo"],
        "essais_utilises": 2,
        "etat": "GAGNE"
    }

    historique.ajouter(enregistrement)

    parties = historique.lire()

    assert len(parties) == 1
    assert parties[0]["id_manche"] == "TEST001"
    assert parties[0]["etat"] == "GAGNE"
    assert parties[0]["propositions"] == [80, 100]


def test_mise_a_jour_sans_doublon(tmp_path):
    chemin = tmp_path / "historique_test.csv"
    historique = Historique(str(chemin))

    enregistrement = {
        "id_manche": "TEST002",
        "horodatage": "2026-11-15T10:00:00",
        "mode": "jeu",
        "entrees": {"prix_unitaire": 20},
        "prediction_brute": 100,
        "cible": 100,
        "tolerance": 5,
        "propositions": [],
        "indices": [],
        "essais_utilises": 0,
        "etat": "EN_COURS"
    }

    historique.ajouter(enregistrement)

    enregistrement["etat"] = "GAGNE"
    enregistrement["propositions"] = [100]
    enregistrement["essais_utilises"] = 1

    historique.ajouter(enregistrement)

    parties = historique.lire()

    assert len(parties) == 1
    assert parties[0]["id_manche"] == "TEST002"
    assert parties[0]["etat"] == "GAGNE"
    assert parties[0]["propositions"] == [100]
    assert parties[0]["essais_utilises"] == "1"
