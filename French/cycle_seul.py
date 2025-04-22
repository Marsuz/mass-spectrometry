
# ======================================================================================================
#                                TRAITEMENT UNITAIRE DE SPECTRES DE MASSE
#                                 Analyse Plasma ON / Plasma OFF (MS)
#                             Auteur : Riwan Ghobril – Avril 2025
# ======================================================================================================
#
# Ce module contient les fonctions de base permettant :
#    - La lecture et la structuration des données de spectrométrie de masse (fichiers CSV issus d’un QMS)
#    - L’identification automatique des cycles de mesure
#    - Le calcul des moyennes et écarts-types pour chaque masse atomique (AMU)
#    - La normalisation des intensités :
#         • soit par une masse de référence (ex : He à 4 amu)
#         • soit par la somme totale des intensités SEM (id = 101)
#    - Le formatage des résultats pour une visualisation ultérieure (via matplotlib)
#
# Ce code est utilisé conjointement avec :
#    - `supperposition_A2.py` pour les comparaisons ON / OFF
#    - Une interface Tkinter pour le traitement graphique par dossier
#
# ======================================================================================================
import numpy as np
import pandas as pd

def detect_num_saisi_SEM(df):
    """
    Détecte automatiquement le nombre de points dans un cycle en identifiant 
    la première répétition de masse (dans la colonne 'mass amu').
    retourne la taille d'un cycle
    """
    masses = df.iloc[:, 3]
    first_mass = masses.iloc[0]
    for i in range(1, len(masses)):
        if masses.iloc[i] == first_mass:
            return i
    raise ValueError("Impossible de détecter le début du second cycle.")

def ind_norme(df, id):
    """
    Retourne l'indice de ligne correspondant à la masse choisie pour la normalisation.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    if id == 101: #ici si l'indentifiant est de 101 c'est que cette identifiant est particiculier
        i = 101
        return i 
    for i in range(num_saisi_SEM):
        mass = int(str(df.iloc[i, 3]).replace(" ", "").replace(",00", "")) 
        if mass == id:
            return i
    raise ValueError(f"Masse {id} non trouvée dans le cycle.")

def somme_sem(df):
    """
    Calcule la somme totale des valeurs de la colonne 'SEM c/s'.
    
    Cette somme est utilisée dans les fonctions de normalisation globale
    lorsque l’identifiant 101 est fourni.
    """
    if df is None or df.empty:
        raise ValueError("Le DataFrame est vide ou invalide.")
    
    if "SEM c/s" not in df.columns:
        raise ValueError("Colonne 'SEM c/s' introuvable dans le DataFrame.")
    
    # Conversion en float si ce n’est pas déjà le cas
    sem_values = pd.to_numeric(df["SEM c/s"], errors="coerce") # on fait la somme de tout les elements de la colomne SEM c/s
    
    # On ignore les NaN éventuels et on calcule la somme
    total = sem_values.sum(skipna=True)
    
    return total

def cycle(df, num): 
    """
    Extrait un cycle spécifique (défini par son numéro "num") sous forme de deux listes :
    les masses (AMU) et les valeurs correspondantes (SEM).
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    amu_cycle = [float(str(df.iloc[i + num * num_saisi_SEM, 3]).replace(" ", "").replace(",00", "")) for i in range(num_saisi_SEM)]
    SEM_cycle = [float(df.iloc[i + num * num_saisi_SEM, 4]) for i in range(num_saisi_SEM)]
    return amu_cycle, SEM_cycle

def MS_moyen(df):
    """
    Calcule les moyennes verticales (par masse) de tous les cycles combinés.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    return [float(np.mean(row)) for row in cycles]

def MS_moyen_norme(df,mass_id): 
    """
    Calcule les moyennes normalisées de chaque masse soit :
    - par la masse `mass_id` donnée,
    - ou par la somme totale des intensités si `mass_id` = 101.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index ==101:
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df))))
    else:
        normed = cycles / cycles[norm_index]
    return [round(float(np.mean(row)), 4) for row in normed]

def MS_moyen_norme_releve(df,mass_id): 
    """
    Variante de `MS_moyen_norme` avec un facteur d’échelle de 100 pour
    améliorer la lisibilité des résultats (exprimés en %).
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index ==101: #on fait la nomre en fonction de la somme de tout les elements de la colomne SEM c/s
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df)))) *100
    else:
        normed = (cycles / cycles[norm_index]) * 100
    return [round(float(np.mean(row)), 4) for row in normed]

def ecart_type(df): 
    """
    Calcule l’écart-type pour chaque masse sur tous les cycles.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    return [round(float(np.nanstd(row)), 2) for row in cycles]

def ecart_type_norme(df, mass_id): 
    """
    Calcule l’écart-type des valeurs normalisées soit par :
    - la masse `mass_id`,
    - ou par la somme des SEM (si `mass_id` = 101).
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index ==101: #on fait la nomre en fonction de la somme de tout les elements de la colomne SEM c/s
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df))))
    else:
        normed = cycles / cycles[norm_index]
    return [round(float(np.nanstd(row)), 4) for row in normed]

def ecart_type_norme_releve(df, mass_id): 
    """
    Comme `ecart_type_norme` mais avec un facteur d’échelle ×100
    pour une meilleure visibilité graphique.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index ==101:
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df)))) *100
    else:
        normed = (cycles / cycles[norm_index]) * 100
    return [round(float(np.nanstd(row)), 4) for row in normed]