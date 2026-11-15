
import tkinter as tk
from tkinter import ttk, messagebox

from src.jeu import Partie
from src.exceptions import DonneeInvalideError

from src.variables import VariableNumerique
from src.exceptions import DonneeInvalideError

from datetime import datetime
from uuid import uuid4
from src.historique import Historique

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class InterfaceJeu:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Devine le prix en trois essais")
        self.fenetre.geometry("850x800")

        # Créer les trois onglets
        self.onglets = ttk.Notebook(fenetre)
        self.onglets.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.onglet_jeu = ttk.Frame(self.onglets)
        self.onglet_simulation = ttk.Frame(self.onglets)
        self.onglet_historique = ttk.Frame(self.onglets)

        self.onglets.add(
            self.onglet_jeu,
            text="Jeu"
        )
        self.onglets.add(
            self.onglet_simulation,
            text="Simulation"
        )
        self.onglets.add(
            self.onglet_historique,
            text="Historique"
        )

        self.onglets.bind(
            "<<NotebookTabChanged>>",
            self.changement_onglet
        )

        
        # Titre de l'onglet Simulation
        ttk.Label(
            self.onglet_simulation,
            text="Simulation des prix",
            font=("Arial", 20)
        ).pack(pady=20)

        # Créer un graphique Matplotlib
        self.figure_simulation = Figure(figsize=(8, 4), dpi=100)
        self.graphique_simulation = self.figure_simulation.add_subplot(111)

        # Données provisoires pour tester l'affichage
        essais = [1, 2, 3]
        prix = [80, 150, 118]

        

        self.graphique_simulation.set_title("Évolution des propositions")
        self.graphique_simulation.set_xlabel("Numéro de l'essai")
        self.graphique_simulation.set_ylabel("Prix ($)")
        self.graphique_simulation.set_xticks(essais)
        self.graphique_simulation.legend()
        self.graphique_simulation.grid(True)

        # Intégrer le graphique dans Tkinter
        self.canvas_simulation = FigureCanvasTkAgg(
            self.figure_simulation,
            master=self.onglet_simulation
        )

        self.canvas_simulation.draw()

        self.canvas_simulation.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        
        # Tableau de l'onglet Historique
        colonnes = (
            "date", "mode", "essais", "etat", "cible"
        )

        self.tableau_historique = ttk.Treeview(
            self.onglet_historique,
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
            self.tableau_historique.heading(
                colonne,
                text=titres[colonne]
            )
            self.tableau_historique.column(
                colonne,
                width=140
            )

        self.tableau_historique.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        ttk.Button(
            self.onglet_historique,
            text="Actualiser l'historique",
            command=self.actualiser_historique
        ).pack(pady=10)

        self.bouton_commencer = ttk.Button(
            self.onglet_jeu,
            text="Commencer une partie",
            command=self.commencer
        )

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
            self.onglet_jeu,
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
            self.onglet_jeu,
            text="Devine le prix en trois essais",
            font=("Arial", 20)
        )
        titre.pack(pady=25)

        self.bouton_commencer = ttk.Button(
            self.onglet_jeu,
            text="Commencer une partie",
            command=self.commencer
        )
        self.bouton_commencer.pack(pady=15)

        ttk.Label(
            self.onglet_jeu,
            text="Entre ta proposition :"
        ).pack(pady=10)

        self.champ_prix = ttk.Entry(self.onglet_jeu)
        self.champ_prix.pack(pady=10)

        self.bouton_proposer = ttk.Button(
            self.onglet_jeu,
            text="Proposer",
            command=self.proposer,
            state="disabled"
        )
        self.bouton_proposer.pack(pady=15)

        self.message = ttk.Label(
            self.onglet_jeu,
            text="Clique sur Commencer une partie.",
            font=("Arial", 13)
        )
        self.message.pack(pady=20)

        self.bouton_historique = ttk.Button(
            self.onglet_jeu,
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
        self.mettre_a_jour_simulation([])

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
        

    
    def changement_onglet(self, evenement):
        """Actualise les données quand on ouvre l'onglet Historique."""
        if self.onglets.select() == str(self.onglet_historique):
            self.actualiser_historique()
    


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

        # Actualiser le graphique après chaque proposition valide
        self.mettre_a_jour_simulation(
            self.enregistrement["propositions"],
            cible=(
                resultat["cible"]
                if resultat["etat"] != "EN_COURS"
                else None
            )
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
        """Affiche l'onglet Historique et actualise les données."""
        self.actualiser_historique()
        self.onglets.select(self.onglet_historique)


    def actualiser_historique(self):
        """Actualise le tableau des parties enregistrées."""

        # Effacer les anciennes lignes
        for ligne in self.tableau_historique.get_children():
            self.tableau_historique.delete(ligne)

        try:
            parties = self.historique.lire()

        except (OSError, ValueError) as erreur:
            messagebox.showerror(
                "Erreur",
                f"Impossible de lire l'historique : {erreur}"
            )
            return

        for partie in parties:
            # Ne pas révéler le prix d'une partie en cours
            cible = (
                "Secret"
                if partie["etat"] == "EN_COURS"
                else partie["cible"]
            )

            self.tableau_historique.insert(
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

    def mettre_a_jour_simulation(self, propositions, cible=None):
        """Actualise le graphique à partir des propositions."""

        graphique = self.graphique_simulation
        graphique.clear()

        essais = list(range(1, len(propositions) + 1))

        if propositions:
            graphique.plot(
                essais,
                [float(prix) for prix in propositions],
                marker="o",
                label="Prix proposés"
            )

        # La cible n'est affichée que si elle est autorisée
        if cible is not None:
            graphique.axhline(
                y=float(cible),
                linestyle="--",
                label="Prix cible"
            )

        graphique.set_title("Évolution des propositions")
        graphique.set_xlabel("Numéro de l'essai")
        graphique.set_ylabel("Prix ($)")
        graphique.set_xticks(essais)
        graphique.grid(True)

        if propositions or cible is not None:
            graphique.legend()

        self.canvas_simulation.draw()


if __name__ == "__main__":
    fenetre = tk.Tk()
    application = InterfaceJeu(fenetre)
    fenetre.mainloop()

