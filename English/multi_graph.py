# =====================================================================================================
#                       MULTIPLE REGISTRATION IN A FOLDER OF MASS SPECTRA
#                                       Author   : Riwan Ghobril
#                                        Date     : April 2025
# =====================================================================================================
#
# Objective :
# This script recursively explores a main folder containing subfolders of measurements
# (with CSV files for plasma ON, OFF, and potentially isolated), then:
#   - Applies the processing `main_()` defined in `supperposition_A2.py`
#   - Automatically generates graphs for multiple analysis modes
#   - Deletes unnecessary files (only keeps `.PNG` images)
#
# Features:
#   - Analyzes all subfolders of `folder_path`
#   - Handles errors individually for each file / folder
#   - Runs the 6 processing modes defined in `main_()` (normalized, recorded, etc.)
# =====================================================================================================

import os
import supperposition_A2 as sA2

# Keywords to identify the CSV files
off_variations = ["off", "Off", "OFf", "OFF", "oFf", "oFF", "ofF", "OfF"]
on_variations = ["on", "On", "ON", "oN"]

# Variables to store the DataFrames
df_off = None
df_on = None
df_iso = None

print(os.getcwd())
# Root folder containing the subfolders to be processed
folder_path =  os.getcwd()+"/DATA"

"""
# Recursive traversal of the main folder
for i in os.listdir(folder_path):
    if os.path.isdir(folder_path+"/"+i):
        Sub_folder = os.listdir(folder_path+"/"+i)
        for j in Sub_folder:
            if os.path.isdir(folder_path+"/"+i+"/"+j):
                name = i
                sub_folder_path = (folder_path+"/"+i+"/"+j)
                name = sub_folder_path+"/"+name # name used for the figures
                k = 0
                try:
                    # Quick check for the presence of CSV files
                    csv_files = [f for f in os.listdir(sub_folder_path) if f.endswith(".csv")]
                    if not csv_files:
                        print("No CSV files found, skipping.")
                        continue
                    
                    # Execute the 6 analysis modes (main_ is robust to internal errors)
                    for k in range(6):
                        try:
                            sA2.main_ (k+1,name,sub_folder_path)
                        except Exception as e:
                            print(f"Error during main_({k+1}) : {e}")
                            continue
                    
                    # Delete all files except PNG images
                    for filename in os.listdir(sub_folder_path) :
                        if not filename.lower().endswith(".png"):
                            try:
                                os.remove(sub_folder_path + "/" + filename)
                            except Exception as e:
                                print(f"Error deleting {filename} : {e}")

                except Exception as e:
                    print(f"Unexpected error in folder {sub_folder_path} : {e}")
                    continue
"""