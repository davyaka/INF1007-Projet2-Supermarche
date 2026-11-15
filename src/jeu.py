
import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .exceptions import DonneeInvalideError


class Partie:
    """Gère une manche de trois essais."""

    def __init__(self):
        self._cible = None
        self._essais = []
        self._etat = "NON_COMMENCE"
        self._tolerance = None

    def demarrer(self, prediction: float):
        """Démarre une nouvelle manche avec une cible secrète."""
        if not math.isfinite(prediction) or prediction <= 0:
            raise DonneeInvalideError("Prédiction invalide.")

        self._cible = Decimal(str(prediction)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        self._tolerance = max(
            Decimal("0.01"),
            (self._cible * Decimal("0.05")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )

        self._essais = []
        self._etat = "EN_COURS"

    def essais_restants(self) -> int:
        """Retourne le nombre de tentatives restantes."""
        return 3 - len(self._essais)

    def proposer(self, montant: str) -> dict:
        """Vérifie une proposition et retourne le résultat."""
        if self._etat != "EN_COURS":
            raise DonneeInvalideError("Aucune partie active.")

        try:
            proposition = Decimal(montant.strip())
        except (InvalidOperation, AttributeError):
            raise DonneeInvalideError(
                "Veuillez entrer un montant valide."
            ) from None

        if not proposition.is_finite() or proposition < 0:
            raise DonneeInvalideError(
                "Le montant doit être positif ou nul et fini."
            )

        proposition = proposition.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        self._essais.append(proposition)

        difference = abs(proposition - self._cible)

        if difference <= self._tolerance:
            self._etat = "GAGNE"
            indice = "Bravo ! Vous avez gagné !"
        elif proposition < self._cible:
            indice = "Le prix à trouver est plus élevé."
        else:
            indice = "Le prix à trouver est plus bas."

        if self._etat == "EN_COURS" and self.essais_restants() == 0:
            self._etat = "PERDU"

        resultat = {
            "etat": self._etat,
            "indice": indice,
            "essais_restants": self.essais_restants()
        }

        if self._etat != "EN_COURS":
            resultat["cible"] = float(self._cible)

        return resultat

    
