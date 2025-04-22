# Analyse de Spectres de Masse Plasma (QMS)

## 🇫🇷 Présentation du Projet

Ce dépôt regroupe un ensemble de scripts Python pour le **traitement, l’analyse et la visualisation de spectres de masse** obtenus par **spectrométrie QMS HIDEN** dans différents contextes d’expérience plasma :

- Spectres mesurés **avec plasma ON, OFF et en condition isolée**
- Normalisation par masse atomique ou par intensité totale
- Génération automatique de **graphes avec barres d’erreur**
- Création d'une **interface graphique (Tkinter)** pour faciliter les comparaisons

L’objectif est d’offrir un outil **souple et automatisable** pour l’analyse de fichiers expérimentaux issus de campagnes QMS.

---

##  Structure du Dépôt

| Script                  | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `cycle_seul.py`        | **TRAITEMENT UNITAIRE DE SPECTRES DE MASSE** : fonctions de base (moyenne, normalisation, écart-type) |
| `supperposition_A2.py` | **ANALYSE COMPARATIVE SPECTRES ON / OFF** : traitement de fichiers et production automatique de figures |
| `supperposition_A3.py` | **TRAITEMENT INDIVIDUEL DES SPECTRES DE MASSE** : inclut les spectres en condition isolée |
| `multi_graph.py`       | **ENREGISTREMENT MULTIPLE DANS UN DOSSIER** : traitement par lot de tous les sous-dossiers contenant des spectres |
| `Supperposition2.py`   | **APPLICATION INTERACTIVE** (Tkinter) : interface utilisateur pour choisir un dossier et lancer l’analyse avec options |

---

## Prérequis

- Python ≥ 3.8
- `numpy`
- `pandas`
- `matplotlib`
- `tkinter` (inclus dans les distributions Python standard)

```bash
pip install numpy pandas matplotlib
