# Plasma Mass Spectrum Analysis (QMS)

## Project presentation

This repository gathers a set of Python scripts for the **processing, analysis and visualization of mass spectra** obtained by **QMS spectrometry** in different plasma experiment contexts:

- Measured spectra **with plasma ON, OFF and in isolated condition**.
- Normalization by atomic mass or total intensity
- Automatic generation of **graphs with error bars**.
- Creation of a **graphical interface (Tkinter)** to facilitate comparisons

The aim is to offer a **flexible and automatable** tool for the analysis of experimental files from QMS campaigns.

---

## Repository Structure

| Script | Description |
|------------------------|-----------------------------------------------------------------------------|
| `cycle_seul.py` | **UNITARY PROCESSING OF MASS SPECTRUM**: basic functions (mean, normalization, standard deviation) |
| `supperposition_A2.py` | **COMPARATIVE SPECTRUM ANALYSIS ON / OFF**: file processing and automatic figure production |
| `supperposition_A3.py` | **INDIVIDUAL MASS SPECTRUM PROCESSING**: includes spectra in isolated conditions |
| `multi_graph.py` | **MULTIPLE RECORDING IN A FOLDER**: batch processing of all subfolders containing spectra |
| `Supperposition2.py` | **INTERACTIVE APPLICATION** (Tkinter): user interface for choosing a folder and starting analysis with options |

---


## Prerequisites

- Python ≥ 3.8
- `numpy`
- `pandas`
- `matplotlib`
- `tkinter` (included in standard Python distributions)

```bash
pip install numpy pandas matplotlib
