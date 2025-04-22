# =====================================================================================================
#                       ENREGISTREMENT MULTIPLE DANS UN DOSSIER DE SPECTRES DE MASSE
#                                       Auteur   : Riwan Ghobril
#                                        Date     : Avril 2025
# =====================================================================================================
#
# Objectif :
# Ce script explore récursivement un dossier principal contenant des sous-dossiers de mesures
# (avec des fichiers CSV plasma ON, OFF, et potentiellement isolés), puis :
#   - Applique le traitement `main_()` défini dans `supperposition_A2.py`
#   - Génère automatiquement les graphiques pour plusieurs modes d’analyse
#   - Supprime les fichiers inutiles (conserve uniquement les images `.PNG`)
#
# Fonctionnalités :
#   - Analyse tous les sous-dossiers de `folder_path`
#   - Gère les erreurs individuellement pour chaque fichier / dossier
#   - Exécute les 6 modes de traitement définis dans `main_()` (normé, relevé, etc.)
# =====================================================================================================

import os
import supperposition_A2 as sA2

# Mots-clés pour identifier les fichiers CSV
off_variations = ["off", "Off", "OFf", "OFF", "oFf", "oFF", "ofF", "OfF"]
on_variations = ["on", "On", "ON", "oN"]

# Variables pour stocker les DataFrames
df_off = None
df_on = None
df_iso = None

# Dossier racine contenant les sous-dossiers à traiter
folder_path = os.getcwd()+"/DATA"

# Parcours récursif du dossier principal
for i in os.listdir(folder_path):
    if os.path.isdir(folder_path+"/"+i):
        Sous_dos = os.listdir(folder_path+"/"+i)
        for j in Sous_dos:
            if os.path.isdir(folder_path+"/"+i+"/"+j):
                name = i
                sous_dos_path = (folder_path+"/"+i+"/"+j)
                name =sous_dos_path+"/"+name # nom utilisé pour les figures
                k = 0
                try:
                    # Vérification rapide de présence de CSV
                    csv_files = [f for f in os.listdir(sous_dos_path) if f.endswith(".csv")]
                    if not csv_files:
                        print("Aucun fichier CSV trouvé, on saute.")
                        continue
                    
                    # Exécution des 6 modes d’analyse (main_ est robuste face aux erreurs internes)
                    for k in range(6):
                        try:
                            sA2.main_ (k+1,name,sous_dos_path)
                        except Exception as e:
                            print(f"Erreur pendant main_({k+1}) : {e}")
                            continue
                    
                    # Suppression de tous les fichiers sauf les images PNG
                    for filename in os.listdir(sous_dos_path) :
                        if not filename.lower().endswith(".png"):
                            try:
                                os.remove(sous_dos_path + "/" + filename)
                            except Exception as e:
                                print(f"Erreur suppression {filename} : {e}")

                except Exception as e:
                    print(f"Erreur inattendue dans le dossier {sous_dos_path} : {e}")
                    continue
