# ======================================================================================================
#                                UNITARY MASS SPECTRA PROCESSING
#                           Plasma ON / Plasma OFF Analysis (Mass Spectrometry)
#                             Author: Riwan Ghobril – April 2025
# ======================================================================================================
#
# This module contains the core functions to:
#    - Read and structure mass spectrometry data (CSV files from QMS)
#    - Automatically identify measurement cycles
#    - Compute averages and standard deviations for each atomic mass unit (AMU)
#    - Normalize intensities:
#         • either by a reference mass (e.g. He at 4 amu)
#         • or by the total SEM intensity sum (id = 101)
#    - Format results for further visualization (via matplotlib)
#
# This code is used in conjunction with:
#    - `supperposition_A2.py` for ON / OFF comparisons
#    - A Tkinter interface for graphical folder-based processing
#
# ======================================================================================================
import numpy as np
import pandas as pd

def detect_num_saisi_SEM(df):
    """
    Automatically detects the number of points in a measurement cycle 
    by identifying the first repeated mass (in the 'mass amu' column).
    returns the size of a cycle
    """
    masses = df.iloc[:, 3]
    first_mass = masses.iloc[0]
    for i in range(1, len(masses)):
        if masses.iloc[i] == first_mass:
            return i
    raise ValueError("Unable to detect the start of the second cycle.")

def ind_norme(df, id):
    """
    Returns the row index corresponding to the selected mass for normalization.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    if id == 101:  # special identifier: normalize by total sum
        i = 101
        return i 
    for i in range(num_saisi_SEM):
        mass = int(str(df.iloc[i, 3]).replace(" ", "").replace(",00", "")) 
        if mass == id:
            return i
    raise ValueError(f"Mass {id} not found in the cycle.")

def somme_sem(df):
    """
    Computes the total sum of the 'SEM c/s' column values.
    
    This sum is used in global normalization functions
    when identifier 101 is provided.
    """
    if df is None or df.empty:
        raise ValueError("DataFrame is empty or invalid.")
    
    if "SEM c/s" not in df.columns:
        raise ValueError("'SEM c/s' column not found in DataFrame.")
    
    # Convert to float if not already
    sem_values = pd.to_numeric(df["SEM c/s"], errors="coerce")  # summing all values in 'SEM c/s' column
    
    # Ignore potential NaNs and calculate the sum
    total = sem_values.sum(skipna=True)
    
    return total

def cycle(df, num): 
    """
    Extracts a specific cycle (defined by its number "num") as two lists:
    the masses (AMU) and the corresponding values (SEM).
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    amu_cycle = [float(str(df.iloc[i + num * num_saisi_SEM, 3]).replace(" ", "").replace(",00", "")) for i in range(num_saisi_SEM)]
    SEM_cycle = [float(df.iloc[i + num * num_saisi_SEM, 4]) for i in range(num_saisi_SEM)]
    return amu_cycle, SEM_cycle

def MS_moyen(df):
    """
    Computes vertical means (per mass) of all combined cycles.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    return [float(np.mean(row)) for row in cycles]

def MS_moyen_norme(df, mass_id): 
    """
    Computes normalized means for each mass either:
    - by the given mass `mass_id`,
    - or by the total SEM intensity sum if `mass_id` = 101.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index == 101:
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df))))
    else:
        normed = cycles / cycles[norm_index]
    return [round(float(np.mean(row)), 4) for row in normed]

def MS_moyen_norme_releve(df, mass_id): 
    """
    Variant of `MS_moyen_norme` with a scaling factor of 100 to
    improve result readability (expressed as %).
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index == 101:  # normalize using total SEM sum
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df)))) * 100
    else:
        normed = (cycles / cycles[norm_index]) * 100
    return [round(float(np.mean(row)), 4) for row in normed]

def ecart_type(df): 
    """
    Computes the standard deviation for each mass across all cycles.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    return [round(float(np.nanstd(row)), 2) for row in cycles]

def ecart_type_norme(df, mass_id): 
    """
    Computes the standard deviation of normalized values either by:
    - the given mass `mass_id`,
    - or by the total SEM sum if `mass_id` = 101.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index == 101:  # normalize using total SEM sum
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df))))
    else:
        normed = cycles / cycles[norm_index]
    return [round(float(np.nanstd(row)), 4) for row in normed]

def ecart_type_norme_releve(df, mass_id): 
    """
    Like `ecart_type_norme` but with a ×100 scaling factor
    for better graphical visualization.
    """
    num_saisi_SEM = detect_num_saisi_SEM(df)
    norm_index = ind_norme(df, mass_id)
    cycles = np.array(df.iloc[:, 4]).reshape(-1, num_saisi_SEM).T
    if norm_index == 101:
        normed = (cycles / (somme_sem(df)/(df.index[-1]/detect_num_saisi_SEM(df)))) * 100
    else:
        normed = (cycles / cycles[norm_index]) * 100
    return [round(float(np.nanstd(row)), 4) for row in normed]
