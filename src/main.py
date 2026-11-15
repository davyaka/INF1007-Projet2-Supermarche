
import tkinter as tk
from .interface import InterfaceJeu


def main():
    """Lance le jeu Devine le prix en trois essais."""
    fenetre = tk.Tk()
    application = InterfaceJeu(fenetre)
    fenetre.mainloop()


if __name__ == "__main__":
    main()

