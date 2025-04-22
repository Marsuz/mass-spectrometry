# ======================================================================================================
#                                COMPARATIVE ANALYSIS OF ON / OFF SPECTRA
#                                QMS Data Processing (plasma)
#                                Author: Riwan Ghobril – April 2025
# ======================================================================================================
#
# This script analyzes mass spectra obtained with and without plasma:
#   - Automatic loading of `ON` and `OFF` files from a folder
#   - Optional selection of the last 5 cycles for stabilized measurements
#   - Computation of mean intensities, standard deviations, and differences
#   - Normalization option:
#       • by a molar mass (e.g., He at 4 amu)
#       • by the total sum of intensities (mode 101)
#   - Possibility to filter out insignificant values (usability)
#   - Generation and saving of `.PNG` plots:
#       • Comparison of ON / OFF intensities
#       • Spectrum of ON - OFF differences
#
# This file depends on the module `cycle_seul.py` for low-level processing.
# It is designed to work via automatic call or a Tkinter interface.
# ======================================================================================================

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import cycle_seul

# value to change to select the desired molar mass for normalization 
# if 101 is selected, normalization is done based on the sum of all SEM c/s
constant_norme = 101 

def path(sous_dos_path):
    """
    Loads 'ON' and 'OFF' CSV files from a given folder.

    The folder must contain two CSV files:
    - one with a name containing 'on' or variants, and one with 'off' or variants

    The function reads these files skipping the first 41 lines (header),
    and returns:
    - df_off/df_on: DataFrame of measurements without plasma
    - file_name : name of the loaded file (last one read)
    """
    folder_path = sous_dos_path + "/"
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]  # get CSV files in folder

    # select CSVs containing On and OFF
    off_variations = ["off", "Off", "OFf", "OFF", "oFf", "oFF", "ofF", "OfF"]
    on_variations = ["on", "On", "ON", "oN"]

    df_off = None
    df_on = None
    file_name = None  

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path, skiprows=41, header=0, sep=";")
            if any(keyword in file for keyword in off_variations):
                df_off = df
                file_name = file  # associate file name
            elif any(keyword in file for keyword in on_variations):
                df_on = df
                file_name = file
            print(f"File {file} loaded successfully.")
        except Exception as e:
            print(f"Error with {file} : {e}")

    if df_off is not None:
        print("df_off loaded successfully")
    else:
        print("No file with 'off' found.")

    if df_on is not None:
        print("df_on loaded successfully")
    else:
        print("No file with 'On' found.")

    print(df_off.head(5))  # Check if columns are correctly shifted
    return df_off, df_on, file_name  # file_name may remain None if nothing was read

def path_end(sous_dos_path): 
    """
    Same as `path()`, but only keeps the last 5 cycles from the CSV file.

    Useful to focus the analysis on the end of the experiment, usually more stable.

    Returns the same objects: df_off, df_on, file_name
    """
    folder_path = sous_dos_path + "/"
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    off_variations = ["off", "Off", "OFf", "OFF", "oFf", "oFF", "ofF", "OfF"]
    on_variations = ["on", "On", "ON", "oN"]

    df_off = None
    df_on = None
    file_name = None

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path, skiprows=41, header=0, sep=";")
            if "Cycle" not in df.columns:
                raise ValueError(f"Missing 'Cycle' column in file {file}")

            # Keep only the last 5 cycles
            max_cycle = df["Cycle"].max()
            df_filtered = df[df["Cycle"] > max_cycle - 5]

            if any(keyword in file for keyword in off_variations):
                df_off = df_filtered
                file_name = file
            elif any(keyword in file for keyword in on_variations):
                df_on = df_filtered
                file_name = file
            print(f"File {file} loaded successfully.")
        except Exception as e:
            print(f"Error with {file} : {e}")

    if df_off is not None:
        print("df_off loaded successfully")
    else:
        print("No file with 'off' found.")

    if df_on is not None:
        print("df_on loaded successfully")
    else:
        print("No file with 'On' found.")

    print(df_off.head(5))  # Check if columns are correctly shifted
    return df_off, df_on, file_name

def val_non_norme(df_off,df_on):
    """
    Calculates mean values and uncertainties without normalization.

    This function returns:
    - ON and OFF means
    - ON and OFF uncertainty (2 * standard deviation)
    - Mean difference ON - OFF

    Uses functions from `cycle_seul` for processing.
    """
    mean_off = cycle_seul.MS_moyen(df_off)
    mean_on = cycle_seul.MS_moyen(df_on)
    insValues_off = []
    insValues_on = []
    for i in range(len(mean_off)): insValues_off.append(2 * cycle_seul.ecart_type(df_off)[i])
    for i in range(len(mean_on)): insValues_on.append(2 * cycle_seul.ecart_type(df_on)[i])
    mean_diff = [mean_on_elt - mean_off_elt for mean_on_elt, mean_off_elt in zip(mean_on, mean_off)]
    return mean_off, mean_on, insValues_off, insValues_on, mean_diff

def val_norme(df_off,df_on): 
    """
    Same as `val_non_norme`, but with intensity normalization.

    Normalization can be:
    - relative to a specific atomic mass (`constant_norme`)
    - or to the total SEM sum if `constant_norme == 101`

    This allows comparison of spectra on a relative basis.
    """
    mean_off = cycle_seul.MS_moyen_norme(df_off, constant_norme)
    mean_on = cycle_seul.MS_moyen_norme(df_on, constant_norme)
    insValues_off = []
    insValues_on = []
    for i in range(len(mean_off)): insValues_off.append(2 * cycle_seul.ecart_type_norme(df_off, 4)[i])
    for i in range(len(mean_on)): insValues_on.append(2 * cycle_seul.ecart_type_norme(df_on, 4)[i])
    mean_diff = [mean_on_elt - mean_off_elt for mean_on_elt, mean_off_elt in zip(mean_on, mean_off)]
    return mean_off, mean_on, insValues_off, insValues_on, mean_diff

def val_norme_releve(df_off,df_on):  # this function returns normalized mean values for ON and OFF + standard deviations
    """
    Same as `val_norme`, but with normalized readings of intensities.
    The normalized value is multiplied by 100 for readability.
    """
    mean_off = cycle_seul.MS_moyen_norme_releve(df_off, constant_norme)
    mean_on = cycle_seul.MS_moyen_norme_releve(df_on, constant_norme)
    insValues_off = []
    insValues_on = []
    for i in range(len(mean_off)): insValues_off.append(2 * cycle_seul.ecart_type_norme_releve(df_off, constant_norme)[i])
    for i in range(len(mean_on)): insValues_on.append(2 * cycle_seul.ecart_type_norme_releve(df_on, constant_norme)[i])
    mean_diff = [mean_on_elt - mean_off_elt for mean_on_elt, mean_off_elt in zip(mean_on, mean_off)]
    return mean_off, mean_on, insValues_off, insValues_on, mean_diff

def utilisable(insValues, mean):
    """
    This function compares two lists of values and generates a binary list indicating
    if each element in the first list is less than or equal to the corresponding element
    in the second list.

    If insValues > mean, append 0 (not usable),
    otherwise append 1 (usable).

    Then apply this binary list as a mask to filter the original lists.
    """
    unsable = []
    if len(insValues) == len(mean):
        for i in range(len(insValues)):
            if insValues[i] > mean[i]:
                unsable.append(0)
            else:
                unsable.append(1)
    else:
        print("ERROR: your lists are not the same length")
        return None
    
    # Apply binary mask to input lists
    insValues = np.multiply(unsable, insValues)
    mean = np.multiply(unsable, mean)
    
    return insValues, mean

def main_(choix, name, sous_dos_path):
    """
    Main function for analysis and graph generation.

    - `choix`: determines analysis mode (normalized, raw, usability, etc.)
    - `name`: name of folder or configuration analyzed (used to name PNG files)
    - `sous_dos_path`: path to folder containing CSV files

    - retrieves data (last 5 cycles)
    - calculates means, uncertainties and differences
    - applies usability filtering if requested
    - generates and saves two plots (ON/OFF + difference)
    """
    df_off, df_on, file = path_end(sous_dos_path)
    amu_cycle_on = cycle_seul.cycle(df_on, 1)[0]
    bar_width = 0.3
    x = np.array(amu_cycle_on)
    name_choice = ""
    if choix == 1:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme_releve(df_off, df_on)
        insValues_on, mean_on = utilisable(insValues_on, mean_on)
        insValues_off, mean_off = utilisable(insValues_off, mean_off)
        name_choice = "-val_norme_releve_use"
    if choix == 2:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme(df_off, df_on)
        insValues_on, mean_on = utilisable(insValues_on, mean_on)
        insValues_off, mean_off = utilisable(insValues_off, mean_off)
        name_choice = "-val_norme_use"
    if choix == 3:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_non_norme(df_off, df_on)
        insValues_on, mean_on = utilisable(insValues_on, mean_on)
        insValues_off, mean_off = utilisable(insValues_off, mean_off)
        name_choice = "-val_non_norme_use"
    if choix == 4:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme_releve(df_off, df_on)
        name_choice = "-val_norme_releve"
    if choix == 5:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_norme(df_off, df_on)
        name_choice = "-val_norme"
    if choix == 6:
        mean_off, mean_on, insValues_off, insValues_on, mean_diff = val_non_norme(df_off, df_on)
        name_choice = "-val_non_norme"

    plt.figure(1, figsize=(18.5, 10.5))
    plt.bar(x - bar_width/2, mean_on, bar_width, color='red', label="plasma ON")
    plt.bar(x + bar_width/2, mean_off, bar_width, color='blue', label="plasma OFF")
    plt.errorbar(x + bar_width/2, mean_off, yerr=insValues_off, fmt='none', capsize=4, ecolor='skyblue', label="plasma OFF", elinewidth=1, capthick=4)
    plt.errorbar(x - bar_width/2, mean_on, yerr=insValues_on, fmt='none', capsize=4, ecolor='pink', label="plasma ON", elinewidth=1, capthick=4)
    plt.xticks(np.arange(int(min(x)), int(max(x)) + 1, 2))
    plt.yscale("symlog")
    plt.xlabel('mass amu')
    plt.ylabel('SEM c/s')
    plt.legend()
    plt.title('Mean mass spectrometry')
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))
    plt.savefig(name + name_choice + file + ".PNG", dpi=300)
    plt.figure(1, figsize=(18.5, 10.5)).clear()
    plt.close(plt.figure(1, figsize=(18.5, 10.5)))

    plt.figure(2, figsize=(18.5, 10.5))
    plt.bar(amu_cycle_on, mean_diff, color=["blue" if v >= 0 else "red" for v in mean_diff], label="difference")
    plt.axhline(0, color='black', linewidth=1)
    plt.yscale("symlog")
    plt.xlabel('mass amu')
    plt.ylabel('SEM c/s')
    plt.title('Mean mass spectrometry')
    plt.savefig(name + name_choice + file + "diff.PNG", dpi=300)
    plt.figure(2, figsize=(18.5, 10.5)).clear()
    plt.close(plt.figure(2, figsize=(18.5, 10.5)))

# print(len(path("Riwan/14.03.25")[0])) 
""" example of code usage """
