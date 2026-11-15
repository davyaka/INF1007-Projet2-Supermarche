
from abc import ABC, abstractmethod
import math

from .exceptions import DonneeInvalideError


class Variable(ABC):
    """Classe abstraite représentant une variable."""

    def __init__(self, nom: str, libelle: str):
        self._nom = nom
        self._libelle = libelle

    @abstractmethod
    def valider(self, valeur: str):
        """Valide une valeur saisie."""
        pass

    def __str__(self):
        return self._libelle


class VariableNumerique(Variable):
    """Variable numérique avec limites autorisées."""

    def __init__(
        self,
        nom: str,
        libelle: str,
        minimum: float,
        maximum: float,
        entier: bool = False
    ):
        super().__init__(nom, libelle)
        self._minimum = minimum
        self._maximum = maximum
        self._entier = entier

    def valider(self, valeur: str) -> float | int:
        if not isinstance(valeur, str):
            raise DonneeInvalideError(
                "La valeur doit être une chaîne de caractères."
            )

        if not valeur.strip():
            raise DonneeInvalideError(
                "Le champ ne peut pas être vide."
            )

        try:
            nombre = float(valeur)
        except ValueError:
            raise DonneeInvalideError(
                "Veuillez entrer un nombre valide."
            ) from None

        if not math.isfinite(nombre):
            raise DonneeInvalideError(
                "Le nombre doit être fini."
            )

        if not self._minimum <= nombre <= self._maximum:
            raise DonneeInvalideError(
                f"Le nombre doit être entre "
                f"{self._minimum} et {self._maximum}."
            )

        if self._entier:
            if not nombre.is_integer():
                raise DonneeInvalideError(
                    "Veuillez entrer un nombre entier."
                )
            return int(nombre)

        return nombre


class VariableCategorielle(Variable):
    """Variable contenant des catégories autorisées."""

    def __init__(
        self,
        nom: str,
        libelle: str,
        categories: list[str]
    ):
        super().__init__(nom, libelle)
        self._categories = tuple(categories)

    def valider(self, valeur: str) -> str:
        if not isinstance(valeur, str):
            raise DonneeInvalideError(
                "Veuillez entrer du texte."
            )

        if not valeur.strip():
            raise DonneeInvalideError(
                "Le champ ne peut pas être vide."
            )

        if valeur not in self._categories:
            raise DonneeInvalideError(
                f"Catégorie inconnue : {valeur}"
            )

        return valeur
