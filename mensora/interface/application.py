"""Démarrage de l'interface graphique de Mensora."""

from mensora.interface.fenetre_principale import creer_fenetre_principale


def lancer_application():
    """Créer la fenêtre principale puis démarrer la boucle graphique."""
    fenetre = creer_fenetre_principale()
    fenetre.mainloop()
