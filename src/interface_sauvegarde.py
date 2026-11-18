
import tkinter as tk
from tkinter import ttk, messagebox

from src.jeu import Partie
from src.exceptions import DonneeInvalideError

from src.variables import VariableNumerique
from src.exceptions import DonneeInvalideError

from datetime import datetime
from uuid import uuid4
from src.historique import Historique



class InterfaceJeu:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Devine le prix en trois essais")
        self.fenetre.geometry("850x800")

        self.partie = Partie()
        self.historique = Historique("historique_parties.csv")
        self.id_manche = None
        self.enregistrement = None
        self.champs = {}

        caracteristiques = [
            ("prix_unitaire", "Prix unitaire"),
            ("categorie", "Catégorie du produit"),
            ("type_client", "Type de client"),
            ("succursale", "Succursale"),
            ("paiement", "Moyen de paiement"),
            ("heure", "Heure d'achat"),
            ("jour_semaine", "Jour de la semaine")
        ]

        cadre = ttk.LabelFrame(
            fenetre,
            text="Caractéristiques de la transaction",
            padding=10
        )
        cadre.pack(pady=10)

        
        # Options temporaires, en attendant les métadonnées de Davy
        categories = {
            "categorie": [
                "Electronic accessories",
                "Fashion accessories",
                "Food and beverages",
                "Health and beauty",
                "Home and lifestyle",
                "Sports and travel"
            ],
            "type_client": ["Member", "Normal"],
            "succursale": ["A", "B", "C"],
            "paiement": ["Cash", "Credit card", "Ewallet"],
            "jour_semaine": [
                "Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"
            ]
        }

        for nom, libelle in caracteristiques:
            ligne = ttk.Frame(cadre)
            ligne.pack(fill="x", pady=3)

            ttk.Label(
                ligne,
                text=libelle,
                width=22
            ).pack(side="left")

            if nom in categories:
                champ = ttk.Combobox(
                    ligne,
                    values=categories[nom],
                    state="readonly",
                    width=23
                )
            else:
                champ = ttk.Entry(ligne, width=25)

            champ.pack(side="left")
            self.champs[nom] = champ


        titre = ttk.Label(
            fenetre,
            text="Devine le prix en trois essais",
            font=("Arial", 20)
        )
        titre.pack(pady=25)

        self.bouton_commencer = ttk.Button(
            fenetre,
            text="Commencer une partie",
            command=self.commencer
        )
        self.bouton_commencer.pack(pady=15)

        ttk.Label(
            fenetre,
            text="Entre ta proposition :"
        ).pack(pady=10)

        self.champ_prix = ttk.Entry(fenetre)
        self.champ_prix.pack(pady=10)

        self.bouton_proposer = ttk.Button(
            fenetre,
            text="Proposer",
            command=self.proposer,
            state="disabled"
        )
        self.bouton_proposer.pack(pady=15)

        self.message = ttk.Label(
            fenetre,
            text="Clique sur Commencer une partie.",
            font=("Arial", 13)
        )
        self.message.pack(pady=20)

        self.bouton_historique = ttk.Button(
            fenetre,
            text="Voir l'historique",
            command=self.afficher_historique
        )
        self.bouton_historique.pack(pady=15)


    
    def commencer(self):
        #  Récupérer les sept valeurs saisies
        entrees = {}

        for nom, champ in self.champs.items():
            valeur = champ.get().strip()

            if not valeur:
                messagebox.showerror(
                    "Erreur",
                    f"Le champ '{nom}' ne peut pas être vide."
                )
                return

            entrees[nom] = valeur

        # Vérifier les deux valeurs numériques
    
        try:
            variable_prix = VariableNumerique(
                "prix_unitaire",
                "Prix unitaire",
                10.08,
                99.96
            )

            variable_heure = VariableNumerique(
                "heure",
                "Heure d'achat",
                0,
                23,
                entier=True
            )

            prix = variable_prix.valider(
                entrees["prix_unitaire"]
            )

            heure = variable_heure.valider(
                entrees["heure"]
            )

            entrees["prix_unitaire"] = prix
            entrees["heure"] = heure

        except DonneeInvalideError as erreur:
            messagebox.showerror(
                "Erreur",
                str(erreur)
            )
            return


        # Afficher les données pour vérifier leur récupération
        print("Caractéristiques saisies :", entrees)

        # Prix temporaire, en attendant le modèle de Davy
        self.partie.demarrer(120)

        # Créer l'enregistrement de la nouvelle manche
        self.id_manche = str(uuid4())

        self.enregistrement = {
            "id_manche": self.id_manche,
            "horodatage": datetime.now().isoformat(
                timespec="seconds"
            ),
            "mode": "Jeu",
            "entrees": entrees.copy(),
            "prediction_brute": 120.0,
            "cible": 120.0,
            "tolerance": 6.0,
            "propositions": [],
            "indices": [],
            "essais_utilises": 0,
            "etat": "EN_COURS"
        }

        self.historique.ajouter(self.enregistrement)


        self.champ_prix.delete(0, tk.END)
        self.bouton_proposer.config(state="normal")

        self.message.config(
            text="Partie commencée ! Tu as 3 essais."
        )

        


    def proposer(self):
        montant = self.champ_prix.get()

        try:
            # 1. Vérifier la proposition avec le jeu
            resultat = self.partie.proposer(montant)

        except DonneeInvalideError as erreur:
            messagebox.showerror("Erreur", str(erreur))
            return

        # 2. Enregistrer uniquement une proposition valide
        self.enregistrement["propositions"].append(montant)

        self.enregistrement["indices"].append(
            resultat["indice"]
        )

        self.enregistrement["essais_utilises"] += 1
        self.enregistrement["etat"] = resultat["etat"]

        # 3. Mettre à jour le fichier CSV
        try:
            self.historique.ajouter(self.enregistrement)
        except (OSError, ValueError) as erreur:
            messagebox.showerror(
                "Erreur d'historique",
                f"Impossible de sauvegarder la partie : {erreur}"
            )

        # 4. Afficher le résultat dans la fenêtre
        texte = (
            f"{resultat['indice']}\n"
            f"Essais restants : {resultat['essais_restants']}"
        )

        if resultat["etat"] != "EN_COURS":
            texte += (
                f"\nPrix à trouver : {resultat['cible']:.2f} $"
            )
            self.bouton_proposer.config(state="disabled")

        self.message.config(text=texte)
        self.champ_prix.delete(0, tk.END)

    
    def afficher_historique(self):
        """Affiche les parties enregistrées dans une fenêtre."""

        try:
            parties = self.historique.lire()
        except (OSError, ValueError) as erreur:
            messagebox.showerror(
                "Erreur",
                f"Impossible de lire l'historique : {erreur}"
            )
            return

        fenetre_historique = tk.Toplevel(self.fenetre)
        fenetre_historique.title("Historique des parties")
        fenetre_historique.geometry("800x400")

        colonnes = ("date", "mode", "essais", "etat", "cible")

        tableau = ttk.Treeview(
            fenetre_historique,
            columns=colonnes,
            show="headings"
        )

        titres = {
            "date": "Date",
            "mode": "Mode",
            "essais": "Essais",
            "etat": "Résultat",
            "cible": "Prix à trouver"
        }

        for colonne in colonnes:
            tableau.heading(
                colonne,
                text=titres[colonne]
            )
            tableau.column(colonne, width=140)

        tableau.pack(fill="both", expand=True, padx=10, pady=10)

        for partie in parties:
            # Ne pas révéler le prix d'une partie en cours
            cible = (
                "Secret"
                if partie["etat"] == "EN_COURS"
                else partie["cible"]
            )

            tableau.insert(
                "",
                "end",
                values=(
                    partie["horodatage"],
                    partie["mode"],
                    partie["essais_utilises"],
                    partie["etat"],
                    cible
                )
            )
  


if __name__ == "__main__":
    fenetre = tk.Tk()
    application = InterfaceJeu(fenetre)
    fenetre.mainloop()

