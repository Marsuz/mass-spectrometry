# ======================================================================================================
#                                ANALYSE COMPARATIVE SPECTRES ON / OFF
#                                Traitement des données QMS (plasma)
#                                Auteur : Riwan Ghobril – Avril 2025
# ======================================================================================================
#
# Ce script assure l’analyse des spectres de masse obtenus avec et sans plasma :
#   - Chargement automatique des fichiers `ON` et `OFF` depuis un dossier
#   - Sélection possible des 5 derniers cycles pour des mesures stabilisées
#   - Calcul des intensités moyennes, écarts-types et différences
#   - Option de normalisation :
#       • par une masse molaire (ex. He à 4 amu)
#       • par la somme totale des intensités (mode 101)
#   - Possibilité de filtrer les valeurs peu significatives (utilisabilité)
#   - Génération et sauvegarde de graphiques en `.PNG` :
#       • Comparaison des intensités ON / OFF
#       • Spectre des différences ON - OFF
#
# Ce fichier dépend du module `cycle_seul.py` pour le traitement bas niveau.
# Il est conçu pour fonctionner avec un appel automatique ou une interface Tkinter.
# ======================================================================================================

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import cycle_seul

# vameur à modifier pour pour selectionné la masse molaire a normern souhaiter 
# si 101 selectionner on nomre en fonction de la somme de tout les SEM c/s
constant_norme = 101 

def path(sous_dos_path):
    """
    Charge les fichiers CSV 'ON' et 'OFF' présents dans un dossier donné.

    Le dossier doit contenir deux fichiers CSV :
    - un avec un nom contenant 'on' ou ses variantes et un avec 'off' ou ses variantes

    La fonction lit ces fichiers en sautant les 41 premières lignes (en-tête),
    et retourne :
    - df_off/df_on: DataFrame des mesures sans plasma
    - file_name : nom du fichier chargé (le dernier parcouru)
    """
    folder_path = sous_dos_path + "/"
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")] # recupère les fichier CSV dans le dossier

    #on selectionne les CSV contenat les mots On et OFF
    off_variations = ["off", "Off", "OFf", "OFF", "oFf", "oFF", "ofF", "OfF"]
    on_variations = ["on", "On", "ON", "oN"]

    df_off = None # On initialise ici
    df_on = None
    file_name = None  

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path, skiprows=41, header=0, sep=";")
            if any(keyword in file for keyword in off_variations):
                df_off = df
                file_name = file  # associer un nom au fichier
            elif any(keyword in file for keyword in on_variations):
                df_on = df
                file_name = file
            print(f"Fichier {file} chargé avec succès.")
        except Exception as e:
            print(f"Erreur avec {file} : {e}")

    if df_off is not None:
        print("df_off chargé avec succès")
    else:
        print("Aucun fichier avec 'off' trouvé.")

    if df_on is not None:
        print("df_on chargé avec succès")
    else:
        print("Aucun fichier avec 'On' trouvé.")

    print(df_off.head(5))  # Pour voir si les colonnes sont bien décalées
    return df_off, df_on, file_name  # file_name peut rester None si rien n’a été lu

def path_end(sous_dos_path): 
    """
    Identique à `path()`, mais ne conserve que les 5 derniers cycles du fichier CSV.

    Utile pour focaliser l’analyse sur la fin de l’expérience, souvent plus stable.

    Retourne les mêmes objets : df_off, df_on, file_name
    """
    folder_path = sous_dos_path + "/"
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    off_variations = ["off", "Off", "OFf", "OFF", "oFf", "oFF", "ofF", "OfF"]
    on_variations = ["on", "On", "ON", "oN"]

    df_off = None
    df_on = None
    file_name = None  # On initialise ici

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path, skiprows=41, header=0, sep=";")
            if "Cycle" not in df.columns:
                raise ValueError(f"Colonne 'Cycle' manquante dans le fichier {file}")

            # Garder uniquement les 5 derniers cycles
            max_cycle = df["Cycle"].max()
            df_filtered = df[df["Cycle"] > max_cycle - 5]

            if any(keyword in file for keyword in off_variations):
                df_off = df_filtered
                file_name = file  # associer un nom au fichier
            elif any(keyword in file for keyword in on_variations):
                df_on = df_filtered
                file_name = file
            print(f"Fichier {file} chargé avec succès.")
        except Exception as e:
            print(f"Erreur avec {file} : {e}")

    if df_off is not None:
        print("df_off chargé avec succès")
    else:
        print("Aucun fichier avec 'off' trouvé.")

    if df_on is not None:
        print("df_on chargé avec succès")
    else:
        print("Aucun fichier avec 'On' trouvé.")

    print(df_off.head(5))  # Pour voir si les colonnes sont bien décalées
    return df_off, df_on, file_name  # file_name peut rester None si rien n’a été lu

def val_non_norme(df_off,df_on):
    """
    Calcule les valeurs moyennes et les incertitudes sans normalisation.

    Cette fonction retourne :
    - Moyenne ON et OFF
    - Incertitude ON et OFF (2 * écart-type)
    - Différence moyenne ON - OFF

    Utilise des fonctions de `cycle_seul` pour le traitement.
    """
    mean_off = cycle_seul.MS_moyen(df_off)
    mean_on = cycle_seul.MS_moyen(df_on)
    insValues_off=[]
    insValues_on=[]
    for i in range(len(mean_off)): insValues_off.append(2*cycle_seul.ecart_type(df_off)[i])
    for i in range(len(mean_on)): insValues_on.append(2*cycle_seul.ecart_type(df_on)[i])
    mean_diff = [mean_on_elt - mean_off_elt  for mean_on_elt, mean_off_elt  in zip(mean_on, mean_off)]
    return mean_off,mean_on,insValues_off,insValues_on,mean_diff

def val_norme(df_off,df_on): 
    """
    Identique à `val_non_norme`, mais avec une normalisation des intensités.

    La normalisation peut être :
    - par rapport à une masse atomique spécifique (`constant_norme`)
    - ou à la somme totale des SEM si `constant_norme == 101`

    Cela permet de comparer des spectres sur une base relative.
    """
    mean_off= cycle_seul.MS_moyen_norme(df_off,constant_norme)
    mean_on= cycle_seul.MS_moyen_norme(df_on,constant_norme)
    insValues_off=[]
    insValues_on=[]
    for i in range(len(mean_off)): insValues_off.append(2*cycle_seul.ecart_type_norme(df_off,4)[i])
    for i in range(len(mean_on)): insValues_on.append(2*cycle_seul.ecart_type_norme(df_on,4)[i])
    mean_diff = [mean_on_elt - mean_off_elt  for mean_on_elt, mean_off_elt  in zip(mean_on, mean_off)]
    return mean_off,mean_on,insValues_off,insValues_on,mean_diff

def val_norme_releve(df_off,df_on): # cette focntion retounr les valeur moyenne nomré relevé On et OFF ainsi que les ecrats types a partir des df
    """
    Identique à `val_norme`, mais avec une normalisation relevé des intensités.
    la valezur normalisé est alors mutliplier par 100 pour etre plus lisible
    """
    mean_off= cycle_seul.MS_moyen_norme_releve(df_off,constant_norme)
    mean_on= cycle_seul.MS_moyen_norme_releve(df_on,constant_norme)
    insValues_off=[]
    insValues_on=[]
    for i in range(len(mean_off)): insValues_off.append(2*cycle_seul.ecart_type_norme_releve(df_off,constant_norme)[i])
    for i in range(len(mean_on)): insValues_on.append(2*cycle_seul.ecart_type_norme_releve(df_on,constant_norme)[i])
    mean_diff = [mean_on_elt - mean_off_elt  for mean_on_elt, mean_off_elt  in zip(mean_on, mean_off)]
    return mean_off,mean_on,insValues_off,insValues_on,mean_diff

def utilisable(insValues, mean):
    """
    Cette fonction compare deux listes de valeurs et génère une liste binaire indiquant
    si chaque élément de la première liste est inférieur ou égal à l'élément correspondant
    dans la deuxième liste.
    
    Si la valeur de insValues est supérieure à mean, on ajoute 0 (non utilisable),
    sinon on ajoute 1 (utilisable).
    
    Ensuite, on applique cette liste binaire aux listes insValues et mean pour filtrer les valeurs.
    """
    unsable = []
    if len(insValues) == len(mean):
        for i in range(len(insValues)):
            if insValues[i] > mean[i]:
                unsable.append(0)
            else:
                unsable.append(1)
    else:
        print("ERROR: vos listes ne sont pas de la même taille")
        return None
    
    # Application du masque binaire aux listes d'entrée
    insValues = np.multiply(unsable, insValues)
    mean = np.multiply(unsable, mean)
    
    return insValues, mean

def main_ (choix, name, sous_dos_path):
    """
    Fonction principale pour l'analyse et la génération des graphiques.

    - `choix` : détermine le mode d’analyse (normalisé, relevé, utilisabilité, etc.)
    - `name` : nom du dossier ou configuration analysée (sert à nommer les fichiers PNG)
    - `sous_dos_path` : chemin vers le dossier contenant les fichiers CSV

    - récupère les données (5 derniers cycles)
    - calcule les moyennes, incertitudes et différences
    - applique le filtrage par utilisabilité si demandé
    - génère et sauvegarde deux graphiques (ON/OFF + différence)
    """
    df_off,df_on,file = path_end(sous_dos_path)
    amu_cycle_on = cycle_seul.cycle(df_on,1)[0]
    bar_width = 0.3
    x = np.array(amu_cycle_on)
    name_choice = ""
    if choix == 1:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme_releve(df_off,df_on)
        insValues_on, mean_on = utilisable(insValues_on, mean_on)
        insValues_off, mean_off = utilisable(insValues_off, mean_off)
        name_choice = "-val_norme_releve_use"
    if choix == 2:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme(df_off,df_on)
        insValues_on, mean_on = utilisable(insValues_on, mean_on)
        insValues_off, mean_off = utilisable(insValues_off, mean_off)
        name_choice = "-val_norme_use"
    if choix == 3:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_non_norme(df_off,df_on)
        insValues_on, mean_on = utilisable(insValues_on, mean_on)
        insValues_off, mean_off = utilisable(insValues_off, mean_off)
        name_choice = "-val_non_norme_use"
    if choix == 4:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme_releve(df_off,df_on)
        name_choice = "-val_norme_releve"
    if choix == 5:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme(df_off,df_on)
        name_choice = "-val_norme"
    if choix == 6:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_non_norme(df_off,df_on)
        name_choice = "-val_non_norme"

    plt.figure(1, figsize=(18.5, 10.5))
    plt.bar(x - bar_width/2, mean_on, bar_width, color='red', label = "plasma ON")
    plt.bar(x + bar_width/2, mean_off, bar_width, color='blue', label = "plasma OFF")
    plt.errorbar(x + bar_width/2, mean_off, yerr=insValues_off, fmt='none', capsize=4, ecolor='skyblue', label="plasma OFF", elinewidth=1, capthick=4)
    plt.errorbar(x - bar_width/2, mean_on, yerr=insValues_on, fmt='none', capsize =4, ecolor = 'pink', label = "plasma ON", elinewidth = 1, capthick = 4)
    plt.xticks(np.arange(int(min(x)), int(max(x)) + 1, 2))  # ticks de 2 en 2
    plt.yscale("symlog")
    plt.xlabel('mass amu')
    plt.ylabel('SEM c/s')
    plt.legend()
    plt.title('Mean mass spectrometry')
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))  # forcer l'affichage sans décimale
    plt.savefig(name+name_choice+file+".PNG", dpi = 300)
    plt.figure(1, figsize=(18.5, 10.5)).clear()
    plt.close(plt.figure(1, figsize=(18.5, 10.5)))

    plt.figure(2, figsize=(18.5, 10.5))
    plt.bar(amu_cycle_on, mean_diff, color=["blue" if v >= 0 else "red" for v in mean_diff], label = "difference")
    plt.axhline(0, color='black', linewidth=1)
    plt.yscale("symlog")
    plt.xlabel('mass amu')
    plt.ylabel('SEM c/s')
    plt.title('Mean mass spectrometry')
    plt.savefig(name+name_choice+file+"diff.PNG", dpi = 300)
    plt.figure(2, figsize=(18.5, 10.5)).clear()
    plt.close(plt.figure(2, figsize=(18.5, 10.5)))


#print(len(path("Riwan/14.03.25")[0])) 
""" exemple d'utilisation du code """
