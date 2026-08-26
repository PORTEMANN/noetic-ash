#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mtr_mapper.py - Correspondance universelle ASH ↔ MTR (1..80)
Auteur : Patrice Portemann
Date : 2026-06-07

⚠ AVERTISSEMENT (v1.0.0) : les correspondances ci-dessous sont HEURISTIQUES
(arbres de décision à seuils construits sur l'atlas MTR-80). Elles n'ont pas
de validation expérimentale indépendante — module contrib, hors garantie C12.1.

Utilisation :
    from mtr_mapper import assign_mtr, map_dataframe
    mtr = assign_mtr(Rc, Rtop, Rdyn, ReN, bands)
    df_with_mtr = map_dataframe(df_ash_results)
"""

import numpy as np
import pandas as pd

# ------------------------------------------------------------
# Seuils généraux pour les familles MTR (d'après l'atlas)
# ------------------------------------------------------------
def get_family(ReN, Rtop, Rdyn, bands):
    """
    Détermine la famille MTR (1 à 5) à partir des indicateurs ASH.
    Retourne un numéro de famille (1..5) et un score de confiance.
    """
    # Famille 1 : Simples (ReN très faible, Rtop petit, Rdyn=1)
    if ReN < 0.1 and Rtop <= 2 and (Rdyn > 0.9 or Rdyn == 1.0):
        return 1
    # Famille 2 : Transition (ReN faible à modéré, Rtop 2-3)
    if 0.1 <= ReN < 1.0 and 2 <= Rtop <= 3 and 0.2 <= Rdyn <= 0.5:
        return 2
    # Famille 3 : Cycliques (ReN modéré, Rtop 3-5, Rdyn bas)
    if 1.0 <= ReN < 10.0 and 3 <= Rtop <= 5 and Rdyn < 0.4:
        return 3
    # Famille 4 : Chaotiques (ReN élevé, Rtop >=5, Rdyn modéré à élevé)
    if 10.0 <= ReN < 100.0 and Rtop >= 5 and Rdyn > 0.4:
        return 4
    # Famille 5 : Singuliers (ReN très élevé ou infini, Rdyn critique, bandes hautes)
    if ReN >= 100.0 or (Rtop >= 6 and Rdyn > 0.8) or (bands[5] + bands[6] > 0.5):
        return 5
    # Par défaut, on essaye de se rapprocher
    if ReN < 1:
        return 1
    elif ReN < 10:
        return 3
    elif ReN < 100:
        return 4
    else:
        return 5

# ------------------------------------------------------------
# Affinement intra-famille (sous-index 1..16 selon la famille)
# ------------------------------------------------------------
def subindex_family1(Rc, Rtop, Rdyn, bands):
    """Famille 1 : MTR 1 à 10. Basé sur la bande dominante et Rc."""
    dominant_band = np.argmax(bands)
    if dominant_band == 0:
        return 1   # MTR 1 : vide résonnant
    elif dominant_band == 1:
        return 2   # MTR 2 : fluctuation linéaire
    elif dominant_band == 2:
        return 3   # MTR 3 : inertie basse
    else:
        # selon Rc
        if Rc < 0.8:
            return 4
        elif Rc < 1.2:
            return 5
        else:
            return 6

def subindex_family2(Rc, Rtop, Rdyn, bands):
    """Famille 2 : MTR 11 à 25. Basé sur Rdyn et la bande B3."""
    if Rdyn < 0.3:
        return 11   # MTR 11
    elif Rdyn < 0.4:
        return 14
    else:
        if bands[2] > bands[3]:
            return 18
        else:
            return 22

def subindex_family3(Rc, Rtop, Rdyn, bands):
    """Famille 3 : MTR 26 à 45. Basé sur Rtop et ReN."""
    if Rtop <= 3:
        if ReN < 5:
            return 26
        else:
            return 30
    elif Rtop <= 4:
        if Rdyn < 0.2:
            return 34
        else:
            return 38
    else:
        return 42

def subindex_family4(Rc, Rtop, Rdyn, bands):
    """Famille 4 : MTR 46 à 65. Basé sur Rdyn et la bande B5."""
    if Rdyn < 0.6:
        if bands[4] > 0.3:
            return 46
        else:
            return 50
    elif Rdyn < 0.7:
        return 54
    else:
        if bands[5] > 0.2:
            return 60
        else:
            return 64

def subindex_family5(Rc, Rtop, Rdyn, bands):
    """Famille 5 : MTR 66 à 80. Basé sur la bande B6/B7."""
    if bands[6] > 0.1:
        return 76
    elif bands[5] > 0.3:
        return 70
    else:
        if Rdyn > 0.9:
            return 66
        else:
            return 68

# ------------------------------------------------------------
# Fonction principale d'attribution MTR
# ------------------------------------------------------------
def assign_mtr(Rc, Rtop, Rdyn, ReN, bands):
    """
    Retourne un entier MTR entre 1 et 80 (ou None si indéfini).
    Paramètres :
        Rc, Rtop, Rdyn, ReN : flottants (Rdyn = 1.0 par défaut si <2 pics)
        bands : liste ou array de 7 flottants (normalisés ou non)
    """
    # Normalisation des bandes si nécessaire
    bands = np.asarray(bands)
    if np.sum(bands) > 0:
        bands = bands / np.sum(bands)

    # Gérer le cas où ReN est NaN ou infini
    if np.isnan(ReN) or np.isinf(ReN):
        return 80   # singularité ultime

    family = get_family(ReN, Rtop, Rdyn, bands)

    if family == 1:
        idx = subindex_family1(Rc, Rtop, Rdyn, bands)
        # MTR de 1 à 10
        mtr = idx
    elif family == 2:
        idx = subindex_family2(Rc, Rtop, Rdyn, bands)
        mtr = 10 + idx
    elif family == 3:
        idx = subindex_family3(Rc, Rtop, Rdyn, bands)
        mtr = 25 + idx
    elif family == 4:
        idx = subindex_family4(Rc, Rtop, Rdyn, bands)
        mtr = 45 + idx
    else:  # family 5
        idx = subindex_family5(Rc, Rtop, Rdyn, bands)
        mtr = 65 + idx

    # Clamping
    return max(1, min(80, mtr))

# ------------------------------------------------------------
# Utilitaire pour mapper un DataFrame de résultats ASH
# ------------------------------------------------------------
def map_dataframe(df_ash):
    """
    Ajoute une colonne 'MTR' au DataFrame contenant les résultats ASH.
    Le DataFrame doit avoir les colonnes : 'Rc', 'Rtop', 'Rdyn', 'ReN', 'bands'
    où 'bands' est une liste ou un array de 7 valeurs.
    """
    df = df_ash.copy()
    mtr_list = []
    for _, row in df.iterrows():
        # Extraire bands (peut être une chaîne)
        bands = row['bands']
        if isinstance(bands, str):
            # Convertir la chaîne "[0.1 0.2 ...]" en liste
            import ast
            bands = ast.literal_eval(bands)
        mtr = assign_mtr(row['Rc'], row['Rtop'], row['Rdyn'], row['ReN'], bands)
        mtr_list.append(mtr)
    df['MTR'] = mtr_list
    return df

# ------------------------------------------------------------
# Exemple d'utilisation (si exécuté directement)
# ------------------------------------------------------------
if __name__ == "__main__":
    # Test avec les valeurs typiques
    test_cases = [
        # (Rc, Rtop, Rdyn, ReN, bands)
        (1.107, 2, 0.0, 0.00015, [0.6, 0.3, 0.1, 0.0, 0.0, 0.0, 0.0]),  # moteur sain
        (1.030, 3.67, 0.302, 74.3, [0.1, 0.1, 0.2, 0.4, 0.2, 0.0, 0.0]),   # moteur défaut
        (1.661, 1.22, 0.778, 40.4, [0.1, 0.15, 0.18, 0.97, 0.0, 0.0, 0.0]),  # EEG intention
        (1.233, 2.0, 0.411, 1.55, [0.6, 0.6, 0.45, 0.27, 0.0, 0.0, 0.0]),    # ECG normal
    ]
    for i, (Rc, Rtop, Rdyn, ReN, bands) in enumerate(test_cases):
        mtr = assign_mtr(Rc, Rtop, Rdyn, ReN, bands)
        print(f"Test {i+1}: MTR = {mtr}")
