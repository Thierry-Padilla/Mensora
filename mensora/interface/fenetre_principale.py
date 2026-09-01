"""Construction de la première fenêtre mensuelle de Mensora."""

import tkinter as tk
from datetime import date
from tkinter import ttk


NOMS_MOIS = (
    "",
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
)


def formater_mois(date_affichee):
    """Retourner le mois et l'année dans un format français lisible."""
    return f"{NOMS_MOIS[date_affichee.month]} {date_affichee.year}"


def creer_fenetre_principale(date_affichee=None):
    """Créer la fenêtre mensuelle sans encore charger de données."""
    date_affichee = date_affichee or date.today()

    fenetre = tk.Tk()
    fenetre.title("Mensora")
    fenetre.geometry("960x680")
    fenetre.minsize(780, 580)
    fenetre.configure(background="#F4F1EA")

    style = ttk.Style(fenetre)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure("Fond.TFrame", background="#F4F1EA")
    style.configure(
        "Titre.TLabel",
        background="#F4F1EA",
        foreground="#203A43",
        font=("Segoe UI", 28, "bold"),
    )
    style.configure(
        "Mois.TLabel",
        background="#F4F1EA",
        foreground="#52636B",
        font=("Segoe UI", 18),
    )
    style.configure(
        "Action.TButton",
        font=("Segoe UI", 14, "bold"),
        padding=(20, 16),
    )
    style.configure(
        "Section.TLabel",
        background="#F4F1EA",
        foreground="#203A43",
        font=("Segoe UI", 16, "bold"),
    )
    style.configure("Treeview", font=("Segoe UI", 12), rowheight=34)
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

    contenu = ttk.Frame(fenetre, style="Fond.TFrame", padding=28)
    contenu.pack(fill="both", expand=True)
    contenu.columnconfigure(0, weight=1)
    contenu.rowconfigure(3, weight=1)

    entete = ttk.Frame(contenu, style="Fond.TFrame")
    entete.grid(row=0, column=0, sticky="ew")
    entete.columnconfigure(0, weight=1)

    ttk.Label(entete, text="Mensora", style="Titre.TLabel").grid(
        row=0,
        column=0,
        sticky="w",
    )
    ttk.Label(
        entete,
        text=formater_mois(date_affichee),
        style="Mois.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(2, 0))

    actions = ttk.Frame(contenu, style="Fond.TFrame")
    actions.grid(row=1, column=0, sticky="ew", pady=(26, 26))
    actions.columnconfigure((0, 1), weight=1)

    # Les actions deviennent fonctionnelles avec les formulaires des prochains lots.
    ttk.Button(
        actions,
        text="AJOUTER UNE DÉPENSE",
        style="Action.TButton",
    ).grid(row=0, column=0, sticky="ew", padx=(0, 10))
    ttk.Button(
        actions,
        text="AJOUTER UN REVENU",
        style="Action.TButton",
    ).grid(row=0, column=1, sticky="ew", padx=(10, 0))

    ttk.Label(
        contenu,
        text="Tableau des opérations",
        style="Section.TLabel",
    ).grid(row=2, column=0, sticky="w", pady=(0, 10))

    zone_tableau = ttk.Frame(contenu)
    zone_tableau.grid(row=3, column=0, sticky="nsew")
    zone_tableau.columnconfigure(0, weight=1)
    zone_tableau.rowconfigure(0, weight=1)

    colonnes = ("date", "type", "categorie", "montant")
    tableau = ttk.Treeview(
        zone_tableau,
        columns=colonnes,
        show="headings",
        height=8,
    )
    tableau.heading("date", text="Date")
    tableau.heading("type", text="Type")
    tableau.heading("categorie", text="Catégorie")
    tableau.heading("montant", text="Montant")
    tableau.column("date", width=170, anchor="center")
    tableau.column("type", width=150, anchor="center")
    tableau.column("categorie", width=260, anchor="w")
    tableau.column("montant", width=160, anchor="e")
    tableau.grid(row=0, column=0, sticky="nsew")

    defilement = ttk.Scrollbar(
        zone_tableau,
        orient="vertical",
        command=tableau.yview,
    )
    defilement.grid(row=0, column=1, sticky="ns")
    tableau.configure(yscrollcommand=defilement.set)

    totaux = ttk.Frame(contenu, style="Fond.TFrame")
    totaux.grid(row=4, column=0, sticky="ew", pady=(24, 0))
    totaux.columnconfigure((0, 1, 2), weight=1)

    cartes = (
        ("Revenus", "0,00 €", "#DCEFE2", "#235B37"),
        ("Dépenses", "0,00 €", "#F6DEDC", "#7A2E2A"),
        ("Reste", "0,00 €", "#DDE8F2", "#274C69"),
    )
    for colonne, (libelle, valeur, fond, texte) in enumerate(cartes):
        carte = tk.Frame(totaux, background=fond, padx=18, pady=14)
        carte.grid(
            row=0,
            column=colonne,
            sticky="ew",
            padx=(0 if colonne == 0 else 8, 0 if colonne == 2 else 8),
        )
        tk.Label(
            carte,
            text=libelle,
            background=fond,
            foreground=texte,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")
        tk.Label(
            carte,
            text=valeur,
            background=fond,
            foreground=texte,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", pady=(4, 0))

    return fenetre
