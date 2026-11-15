
from src.jeu import Partie


def test_tolerance_prix():
    partie = Partie()
    partie.demarrer(100)

    resultat = partie.proposer("104")

    assert resultat["etat"] == "GAGNE"
    assert resultat["essais_restants"] == 2
    assert resultat["cible"] == 100.0

def test_trois_essais_maximum():
    partie = Partie()
    partie.demarrer(100)

    resultat1 = partie.proposer("50")
    resultat2 = partie.proposer("60")
    resultat3 = partie.proposer("70")

    assert resultat1["essais_restants"] == 2
    assert resultat2["essais_restants"] == 1
    assert resultat3["essais_restants"] == 0
    assert resultat3["etat"] == "PERDU"


def test_quatrieme_proposition_refusee():
    partie = Partie()
    partie.demarrer(100)

    partie.proposer("50")
    partie.proposer("60")
    partie.proposer("70")

    try:
        resultat = partie.proposer("100")
    except Exception:
        return

    assert resultat["etat"] != "GAGNE"


def test_saisie_invalide_sans_perdre_essai():
    from src.exceptions import DonneeInvalideError

    partie = Partie()
    partie.demarrer(100)

    try:
        partie.proposer("bonjour")
        assert False, "Une erreur devait être déclenchée"
    except DonneeInvalideError:
        pass

    resultat = partie.proposer("50")

    assert resultat["essais_restants"] == 2
