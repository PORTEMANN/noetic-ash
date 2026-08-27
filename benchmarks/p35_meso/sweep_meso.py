#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programme P35+ — Le régime Méso comme objet mesuré.

Objectif : tester la conjecture LEX-004 (« méso = frontière entre ordre et chaos »,
 analogue du point auto-dual ρ*≈0.75 du diagramme de phases de la machine noétique).

Trois familles de signaux DÉTERMINISTES (aucun RNG) :

  A. Balayage de la logistique x_{n+1} = r·x_n(1-x_n) pour r ∈ [3.40, 4.00]
     (61 valeurs), en traversant r∞ = 3.56995 (Feigenbaum) et la fenêtre de
     période 3 (~3.83–3.86). Orbite tenue par zero-order hold (32 éch./itér.).
  B. Mélange harmonique + chaos : signal = (1-λ)·harmonique + λ·chaos normalisé,
     λ ∈ [0, 1] (51 valeurs). L'harmonique est un méso parfait (ton pur 100 Hz),
     le chaos est la logistique à r=4.
  C. Octave désaccordée : deux tons à f et 4f·2^(δ/12), δ ∈ [0, 6] (13 valeurs).
     Teste la sensibilité de Rdyn au désaccord sub-demi-ton.

Protocole C12.1 : aucun paramètre ajusté, corpus régénérable à l'identique,
hash SHA-256 des résultats gelé dans benchmarks/SHASUMS.txt.

Usage :  python3 sweep_meso.py
Sortie : results_p35_meso.csv (125 points de mesure)
"""

import os
import sys

import numpy as np
import pandas as pd

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "src", "python"))
from ash_core import ASHConfig, process_signal  # noqa: E402

# --- Constantes du corpus (gelées) -----------------------------------------
FS = 250.0              # fréquence d'échantillonnage (Hz)
DUREE_ANALYSE = 20.0    # fenêtre analysée (s) après suppression du transitoire
SAMPLES_PAR_ITER = 32   # tenue d'ordre zéro : échantillons par itéré logistique
TRANSIENT_ITER = 1000   # itérés logistiques jetés avant enregistrement
X0 = 0.3                # condition initiale — PAS 0.5 : à r=4, l'orbite
                        # 0.5 → 1 → 0 est dégénérée (point fixe trivial)
R_INFINITY = 3.56995    # accumulation de Feigenbaum (naissance du chaos)


# --- Générateurs -----------------------------------------------------------
def orbite_logistique(r, n_iter, x0=X0):
    """Orbite de la logistique après suppression du transitoire."""
    x = x0
    for _ in range(TRANSIENT_ITER):
        x = r * x * (1.0 - x)
    out = np.empty(n_iter)
    for i in range(n_iter):
        x = r * x * (1.0 - x)
        out[i] = x
    return out


def signal_logistique(r):
    """Famille A : orbite logistique tenue (zero-order hold) à FS Hz."""
    n_iter = int(DUREE_ANALYSE * FS / SAMPLES_PAR_ITER)
    return np.repeat(orbite_logistique(r, n_iter), SAMPLES_PAR_ITER)


def signal_melange(lam):
    """Famille B : (1-λ)·ton pur 100 Hz + λ·chaos logistique (r=4) normalisé."""
    chaos = signal_logistique(4.0)
    n = len(chaos)
    t = np.arange(n) / FS
    harm = np.sin(2.0 * np.pi * 100.0 * t)
    c = (chaos - chaos.mean()) / (chaos.std() + 1e-12)
    return (1.0 - lam) * harm + lam * c


def signal_octave_desaccordee(delta):
    """Famille C : tons à 100 Hz et 400·2^(δ/12) Hz (octave + δ demi-tons)."""
    n = int(DUREE_ANALYSE * FS)
    t = np.arange(n) / FS
    f2 = 400.0 * 2.0 ** (delta / 12.0)
    return np.sin(2.0 * np.pi * 100.0 * t) + np.sin(2.0 * np.pi * f2 * t)


# --- Mesure ----------------------------------------------------------------
def mesurer(signal, ash):
    """Agrège les invariants ASH sur toutes les fenêtres du signal."""
    df = process_signal(signal, FS, ash)
    ren = df["ReN"].to_numpy(dtype=float)
    return dict(
        ReN_med=float(np.median(ren)),
        ReN_mean=float(ren.mean()),
        Rtop_med=float(df["Rtop"].median()),
        Rdyn_med=float(df["Rdyn"].median()),
        Rc_mean=float(df["Rc"].mean()),
        pct_cosmo=float(100.0 * (ren < 1.0).mean()),
        pct_meso=float(100.0 * ((ren >= 1.0) & (ren <= 10.0)).mean()),
        pct_quant=float(100.0 * (ren > 10.0).mean()),
        n_fenetres=int(len(df)),
    )


def main():
    ash = ASHConfig()
    lignes = []

    # Famille A — balayage du paramètre de la logistique
    for r in np.arange(3.40, 4.001, 0.01):
        m = mesurer(signal_logistique(float(r)), ash)
        lignes.append(dict(famille="A_logistique", parametre=round(float(r), 4), **m))
        print(f"A r={r:.2f}  ReN_med={m['ReN_med']:.3f}  méso={m['pct_meso']:.0f}%")

    # Famille B — mélange harmonique / chaos
    for lam in np.arange(0.0, 1.001, 0.02):
        m = mesurer(signal_melange(float(lam)), ash)
        lignes.append(dict(famille="B_melange", parametre=round(float(lam), 4), **m))
        print(f"B λ={lam:.2f}  ReN_med={m['ReN_med']:.3f}  méso={m['pct_meso']:.0f}%")

    # Famille C — octave désaccordée
    for delta in np.arange(0.0, 6.001, 0.5):
        m = mesurer(signal_octave_desaccordee(float(delta)), ash)
        lignes.append(dict(famille="C_octave_desaccordee",
                           parametre=round(float(delta), 4), **m))
        print(f"C δ={delta:.1f}  ReN_med={m['ReN_med']:.3f}  Rdyn={m['Rdyn_med']:.3f}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "results_p35_meso.csv")
    pd.DataFrame(lignes).to_csv(out, index=False)
    print(f"\n{len(lignes)} points de mesure → {out}")
    print("Penser à geler le SHA-256 dans benchmarks/SHASUMS.txt (C12.1).")


if __name__ == "__main__":
    main()
