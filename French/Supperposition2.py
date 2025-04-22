# =====================================================================================================
#                        APPLICATION D'ANALYSE INTERACTIVE DE SPECTRES QMS (PLASMA ON / OFF)
#                                          Auteur : Riwan Ghobril
#                                           Date   : Avril 2025
# =====================================================================================================
#
# Objectif :
# Cette interface Tkinter permet de charger deux fichiers CSV (Plasma ON et OFF), d’analyser les
# données de spectrométrie de masse issues d’un quadrupôle, et d’afficher les résultats sous forme
# de graphiques comparatifs.
#
# Fonctionnalités principales :
#   - Chargement automatique des fichiers ON et OFF (cycle de fin uniquement)
#   - Choix du type de traitement : brut, normalisé, ou normalisé relevé (×100)
#   - Option de filtrage par “utilisabilité” (écart-type comparé à la moyenne)
#   - Choix de la masse pour normalisation (ex : masse 4 = He, ou somme totale = 101)
#   - Affichage des barres d’erreur et différences ON/OFF
# =====================================================================================================

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cycle_seul

# Fonctions scientifiques importées depuis cycle_seul.py
def val_non_norme(df_on, df_off):
    """
    Calcule les moyennes et incertitudes (2*ecart type) sans normalisation.
    Renvoie les valeurs moyennes ON/OFF, les incertitudes associées et la différence ON - OFF.
    """
    mean_off = cycle_seul.MS_moyen(df_off)
    mean_on = cycle_seul.MS_moyen(df_on)
    insValues_off = [2 * val for val in cycle_seul.ecart_type(df_off)]
    insValues_on = [2 * val for val in cycle_seul.ecart_type(df_on)]
    mean_diff = [on - off for on, off in zip(mean_on, mean_off)]
    return mean_off, mean_on, insValues_off, insValues_on, mean_diff

def val_norme(df_on, df_off, mass_id=4):
    """
    Calcule les moyennes et incertitudes après normalisation sur une masse spécifiée.
    La masse `mass_id` est typiquement 4 (He), ou 101 pour une normalisation à la somme totale.
    Renvoie les valeurs moyennes normalisées, incertitudes et différence.
    """
    mean_off = cycle_seul.MS_moyen_norme(df_off, mass_id)
    mean_on = cycle_seul.MS_moyen_norme(df_on, mass_id)
    insValues_off = [2 * val for val in cycle_seul.ecart_type_norme(df_off, mass_id)]
    insValues_on = [2 * val for val in cycle_seul.ecart_type_norme(df_on, mass_id)]
    mean_diff = [on - off for on, off in zip(mean_on, mean_off)]
    return mean_off, mean_on, insValues_off, insValues_on, mean_diff

def val_norme_releve(df_on, df_off, mass_id=4):
    """
    Identique à `val_norme` mais les valeurs sont multipliées par 100 (relevé).
    Permet un affichage plus lisible des petites valeurs.
    """
    mean_off = cycle_seul.MS_moyen_norme_releve(df_off, mass_id)
    mean_on = cycle_seul.MS_moyen_norme_releve(df_on, mass_id)
    insValues_off = [2 * val for val in cycle_seul.ecart_type_norme_releve(df_off, mass_id)]
    insValues_on = [2 * val for val in cycle_seul.ecart_type_norme_releve(df_on, mass_id)]
    mean_diff = [on - off for on, off in zip(mean_on, mean_off)]
    return mean_off, mean_on, insValues_off, insValues_on, mean_diff

def utilisable(insValues, mean):
    """
    Filtre les points non significatifs selon leur écart-type.
    Compare 2*écart-type avec la moyenne : si l’incertitude est plus grande, on marque le point comme inutilisable.
    Applique un masque binaire pour exclure ces points des résultats finaux.
    """
    usable = []
    for i in range(len(insValues)):
        usable.append(0 if insValues[i] > mean[i] else 1)
    return np.multiply(usable, insValues), np.multiply(usable, mean)

def affichage_graphique(x, mean_on, mean_off, insValues_on, insValues_off, mean_diff, usable, with_usable, titre):
    """
    Affiche deux graphiques matplotlib :
        1. Spectre moyen comparant Plasma ON vs OFF avec barres d'erreur
        2. Différences ON - OFF (avec couleurs selon le signe)
    Si l'option “utilisabilité” est activée, on applique un masque sur les données.
    """
    bar_width = 0.3
    plt.bar(x - bar_width/2, mean_on, bar_width, color='red', label = "plasma ON")
    plt.bar(x + bar_width/2, mean_off, bar_width, color='blue', label = "plasma OFF")
    plt.errorbar(x + bar_width/2, mean_off, yerr=insValues_off, fmt='none', capsize=4, ecolor='skyblue', elinewidth=1, capthick=4)
    plt.errorbar(x - bar_width/2, mean_on, yerr=insValues_on, fmt='none', capsize=4, ecolor='pink', elinewidth=1, capthick=4)
    plt.xticks(np.arange(int(min(x)), int(max(x)) + 1, 2))
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))
    plt.yscale("symlog")
    plt.xlabel('mass amu')
    plt.ylabel('SEM c/s')
    plt.title(titre)
    plt.legend()
    plt.tight_layout()
    plt.show()

    if with_usable:
        mean_diff = np.multiply(usable, mean_diff)
    plt.bar(x, mean_diff, color=["blue" if v >= 0 else "red" for v in mean_diff], label = "Diff ON - OFF")
    plt.axhline(0, color='black', linewidth=1)
    plt.yscale("symlog")
    plt.xlabel('mass amu')
    plt.ylabel('SEM c/s')
    plt.title(titre+" différence entre plasmas")
    plt.tight_layout()
    plt.show()

class AnalyseSpectresApp:
    """
    Classe principale de l’application Tkinter.
    Initialise l’interface, gère les entrées utilisateur et lance l’analyse.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Analyse spectres de masse")
        self.root.geometry("600x350")
        self.folder_path = ""

        self.select_button = tk.Button(root, text="Sélectionner un dossier avec CSV ON/OFF", command=self.select_folder)
        self.select_button.pack(pady=10)

        self.mode_var = tk.StringVar()
        self.mode_menu = ttk.Combobox(root, textvariable=self.mode_var, state="readonly")
        self.mode_menu['values'] = ["non normé", "normé", "normé relevé"]
        self.mode_menu.current(0)
        self.mode_menu.pack(pady=10)

        self.norme_mass_label = tk.Label(root, text="Masse pour normalisation (default: 4)")
        self.norme_mass_label.pack()
        self.norme_mass_entry = tk.Entry(root)
        self.norme_mass_entry.insert(0, "4")
        self.norme_mass_entry.pack(pady=5)

        self.utilisable_var = tk.StringVar()
        self.utilisable_menu = ttk.Combobox(root, textvariable=self.utilisable_var, state="readonly")
        self.utilisable_menu['values'] = ["avec utilisabilité", "sans utilisabilité"]
        self.utilisable_menu.current(0)
        self.utilisable_menu.pack(pady=10)

        self.run_button = tk.Button(root, text="Afficher le graphique", command=self.run_analysis)
        self.run_button.pack(pady=20)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder

    def run_analysis(self):
        if not self.folder_path:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier d'abord.")
            return

        files = os.listdir(self.folder_path)
        csv_on = [f for f in files if 'ON' in f.upper() and f.endswith('.csv')]
        csv_off = [f for f in files if 'OFF' in f.upper() and f.endswith('.csv')]

        if not csv_on or not csv_off:
            messagebox.showerror("Erreur", "CSV ON et/ou OFF introuvables dans le dossier.")
            return
        else:
            print(f"Fichier {csv_on} chargé avec succès.")
            print(f"Fichier {csv_off} chargé avec succès.")

        try:
            df_on = pd.read_csv(os.path.join(self.folder_path, csv_on[0]), sep=';', skiprows=41)
            df_off = pd.read_csv(os.path.join(self.folder_path, csv_off[0]), sep=';', skiprows=41)

            max_cycle = df_on["Cycle"].max()
            df_on = df_on[df_on["Cycle"] > max_cycle - 15]
            max_cycle = df_off["Cycle"].max()
            df_off = df_off[df_off["Cycle"] > max_cycle - 15]

        except Exception as e:
            messagebox.showerror("Erreur de lecture", str(e))
            return

        mode = self.mode_var.get()
        with_usable = self.utilisable_var.get() == "avec utilisabilité"
        mass_id = int(self.norme_mass_entry.get()) if self.norme_mass_entry.get().isdigit() else 4

        if mode == "non normé":
            mean_off, mean_on, ins_off, ins_on, diff = val_non_norme(df_on, df_off)
        elif mode == "normé":
            mean_off, mean_on, ins_off, ins_on, diff = val_norme(df_on, df_off, mass_id)
        elif mode == "normé relevé":
            mean_off, mean_on, ins_off, ins_on, diff = val_norme_releve(df_on, df_off, mass_id)
        else:
            messagebox.showerror("Erreur", "Mode d'analyse inconnu.")
            return

        if with_usable:
            ins_on, mean_on = utilisable(ins_on, mean_on)
            ins_off, mean_off = utilisable(ins_off, mean_off)
            usable_mask = [1 if i > 0 else 0 for i in ins_on]
        else:
            usable_mask = [1]*len(mean_on)

        x = np.array(cycle_seul.cycle(df_on, 1)[0])
        titre = os.path.basename(self.folder_path) + " - " + mode
        affichage_graphique(x, mean_on, mean_off, ins_on, ins_off, diff, usable_mask, with_usable, titre)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyseSpectresApp(root)
    root.mainloop()