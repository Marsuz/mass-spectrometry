# =====================================================================================================
#             TRAITEMENT INDIVIDUEL DES SPECTRES DE MASSE (PLASMA OFF / ON / ISOLÉ)
#                                   Auteur   : Riwan Ghobril
#                                    Date     : Avril 2025
# =====================================================================================================
#
# Objectif :
# Ce script permet de comparer les spectres de masse mesurés par un quadrupôle pour trois
# conditions expérimentales :
#   - Plasma OFF
#   - Plasma ON
#   - État isolé (de référence, ou bruit instrumental)
#
# Fonctionnalités :
#   - Chargement automatique des fichiers CSV selon leur nom
#   - Extraction des valeurs moyennes pour chaque masse AMU
#   - Affichage graphique avec barres d’erreurs (2×écart-type)
#   - Calcul de la différence ON - OFF
#   - Insertion du plasma isolé pour comparaison
# =====================================================================================================


import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import cycle_seul

def path(sous_dos_path):
    """
    Parcourt un dossier pour détecter les fichiers contenant les spectres ON, OFF, et isolé.
    Charge chaque fichier dans un DataFrame selon les mots-clés trouvés dans le nom du fichier.
    Retourne : df_off, df_on, df_iso, et le nom du fichier utilisé (utile pour nommer les figures).
    """
    folder_path = sous_dos_path + "/"
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    off_variations = ["off", "Off", "OFf", "OFF", "oFf", "oFF", "ofF", "OfF"]
    on_variations = ["on", "On", "ON", "oN"]
    isole_variations = ["isolé", "Isolé", "ISolé", "ISOLé", "Isole", "isoLe", "isoLE", "IsoLe", "isole"]

    df_off = None
    df_on = None
    df_iso = None
    file_name = None  # On initialise ici

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
            elif any(keyword in file for keyword in isole_variations):
                df_iso = df
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
    
    if df_iso is not None:
        print("df_iso chargé avec succès")
    else:
        print("Aucun fichier avec 'isolé' trouvé.")

    #print(df_off.head(5))  # Pour voir si les colonnes sont bien décalées
    return df_off, df_on, df_iso,file_name  # file_name peut rester None si rien n’a été lu

def val_non_norme(df_off,df_on):
    """
    Calcule les moyennes et les incertitudes (2*écart type) sans normalisation.
    Retourne :
        - Moyennes ON / OFF
        - Incertitudes ON / OFF
        - Différences ON - OFF pour chaque masse AMU.
    """
    mean_off = cycle_seul.MS_moyen(df_off)
    mean_on  = cycle_seul.MS_moyen(df_on)
    insValues_off = [2 * (cycle_seul.ecart_type(df_off)[i]) for i in range(len(mean_off))]
    insValues_on  = [2 * (cycle_seul.ecart_type(df_on)[i]) for i in range(len(mean_on))]
    mean_diff = [mean_on_elt - mean_off_elt  for mean_on_elt, mean_off_elt  in zip(mean_on, mean_off)]
    return mean_off,mean_on,insValues_off,insValues_on,mean_diff

def production_sinificatif(insValues_off,insValues_on,mean_off,mean_on):
    """
    Vérifie si une variation est significative pour chaque masse AMU.
    Critère : (ON - ins_ON) > (OFF + ins_OFF)
    Retourne une liste binaire [1 si significatif, 0 sinon].
    """
    usable=[]
    if len(insValues_off)==len(insValues_on) and len(mean_off)==len(mean_on) and len(insValues_on)==len(mean_on):
        for i in range(len(insValues_off)):
            val = (mean_on[i]-insValues_on[i])-(mean_off[i]+insValues_off[i])
            print(val)
            if val>0:
                usable.append(1)
            else:
                usable.append(0)
    else:
        print("ERROR: vos listes ne sont pas de la meme taille")
    
    return usable

def insValues_nul(insValues):
    """
    Force à 0 les incertitudes négatives ou nulles (problèmes numériques).
    Évite que des erreurs visuelles apparaissent sur les graphiques.
    """
    for i in range(len(insValues)): 
        if insValues[i]<=0:
            insValues[i] =0
    return insValues

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
        Fonction principale du script (mode sans interface).

    Étapes :
      - Chargement des données (ON, OFF, isolé)
      - Calcul des moyennes et des écarts-types
      - (Optionnel) application du filtre "utilisable"
      - Génération et sauvegarde des graphiques :
          1. Valeurs absolues ON/OFF + isolé
          2. Différences ON - OFF

    Paramètres :
      - choix : 1 = avec filtrage (utilisable), 2 = sans filtrage
      - name  : nom du fichier de sortie (préfixe)
      - sous_dos_path : chemin du dossier contenant les fichiers CSV
    """
    df_off,df_on,df_iso,file = path(sous_dos_path)
    amu_cycle_on = cycle_seul.cycle(df_on,1)[0]
    bar_width = 0.3
    x = np.array(amu_cycle_on)
    name_choice = ""
    if choix == 1:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_non_norme(df_off,df_on)
        insValues_on, mean_on = utilisable(insValues_on, mean_on)
        insValues_off, mean_off = utilisable(insValues_off, mean_off)
        name_choice = "-val_non_norme_use"
    if choix == 2:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_non_norme(df_off,df_on)
        name_choice = "-val_non_norme"

    insValues_off = insValues_nul((insValues_off))
    insValues_off = insValues_nul((insValues_on))
    plt.figure(1, figsize=(18.5, 10.5))
    plt.bar(x - bar_width/2, mean_on, bar_width, color='red', label = "plasma ON")
    plt.bar(x + bar_width/2, mean_off, bar_width, color='blue', label = "plasma OFF")
    plt.bar(x , cycle_seul.MS_moyen(df_iso), bar_width*2, color='orange', label = "plasma isolé/error")
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

main_ (2, "teste_2", "Riwan/14.03.25")
