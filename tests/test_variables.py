
import pytest
from src.variables import VariableNumerique


def test_variable_numerique():
    variable = VariableNumerique(
        "prix_unitaire",
        "Prix unitaire",
        minimum=0,
        maximum=100
    )

    assert variable.valider("50") == 50


from src.exceptions import DonneeInvalideError


@pytest.mark.parametrize("valeur", [
    "",
    "bonjour",
    "-5",
    "150",
    "nan",
    "inf"
])
def test_variable_numerique_invalide(valeur):
    variable = VariableNumerique(
        "prix_unitaire",
        "Prix unitaire",
        minimum=0,
        maximum=100
    )

    with pytest.raises(DonneeInvalideError):
        variable.valider(valeur)


from src.variables import VariableCategorielle


def test_categorie_valide():
    variable = VariableCategorielle(
        "type_client",
        "Type de client",
        ["Member", "Normal"]
    )

    assert variable.valider("Member") == "Member"


def test_categorie_invalide():
    variable = VariableCategorielle(
        "type_client",
        "Type de client",
        ["Member", "Normal"]
    )

    with pytest.raises(DonneeInvalideError):
        variable.valider("VIP")
