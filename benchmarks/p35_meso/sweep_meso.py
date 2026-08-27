"""
sweep_meso.py — Programme P35+ : campagne d'étalonnage du régime Méso.

Question : à quoi l'instrument ASH répond-il dans la zone 1 ≤ ReN ≤ 10 ?
Note : une piste d'analogie entre le méso et le point auto-dual ρ* ≈ 0,75 du
diagramme de phases de la machine noétique avait été évoquée (LEX-004) ; elle
n'est pas retenue — l'ASH est antérieur à la machine, approches distinctes.

Stratégie C12.1 : corpus de signaux à paramètre de contrôle dont la
transition de régime est connue (ground truth mathématique), balayage ASH à
protocole figé, mesures publiées quelle que soit l'issue.

Trois familles, toutes DÉTERMINISTES (aucune RNG, x0 figé) :
  A — map logistique x_{n+1} = r·x_n(1-x_n), r ∈ [3.4, 4.0]
      Route au chaos par doublement de période ; transition exacte connue :
      r∞ ≈ 3.56995 (Feigenbaum). Maintien zero-order 32 éch./itération
      (fs=250 Hz → fondamentale période-2 ≈ 3.9 Hz, dans la grille 1-16 Hz).
  B — mélange (1-λ)·sin(4 Hz) + λ·chaos(logistique r=4), λ ∈ [0, 1]
      Interpolation continue entre cohérence pure et chaos pur.
  C — octave désaccordée : sin(4 Hz) + sin(4·2^((12+δ)/12) Hz), δ ∈ [0, 6]
      δ = 0 : octave exacte (Rdyn = 0). Sonde la sémantique de Rdyn.

Sorties : results_p35_meso.csv (non commité, cf. .gitignore ; empreinte
SHA-256 consignée dans benchmarks/SHASUMS.txt) + tableau résumé stdout.

Usage : python sweep_meso.py
"""

import os
import sys

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "src", "python"))
from ash_core import ASH  # noqa: E402

# --- Protocole figé (C12.1) ---------------------------------------------------
FS = 250.0               # Hz
DUREE_ANALYSE = 20.0     # s analysés
SAMPLES_PAR_ITER = 32    # maintien zero-order pour la map logistique
TRANSIENT_ITER = 1000    # itérations jetées
X0 = 0.3                 # condition initiale figée — PAS 0.5 : à r=4,
                         # l'orbite 0.5 → 1 → 0 est dégénérée (signal nul)

R_INFINITY = 3.56995     # point d'accumulation de Feigenbaum (ground truth A)


def orbite_logistique(r, n_iter, x0=X0):
    """Orbite de la map logistique, transitoire écarté. Déterministe."""
    x = x0
    for _ in range(TRANSIENT_ITER):
        x = r * x * (1.0 - x)
    out = np.empty(n_iter)
    for i in range(n_iter):
        x = r * x * (1.0 - x)
        out[i] = x
    return out


def signal_logistique(r):
    """Famille A : orbite tenue (zero-order hold), durée DUREE_ANALYSE."""
    n_iter = int(FS * DUREE_ANALYSE / SAMPLES_PAR_ITER)
    orbite = orbite_logistique(r, n_iter)
    return np.repeat(orbite, SAMPLES_PAR_ITER)


def signal_melange(lam):
    """Famille B : (1-λ)·sinus 4 Hz + λ·chaos normalisé (logistique r=4)."""
    chaos = signal_logistique(4.0)
    chaos = (chaos - chaos.mean()) / chaos.std()
    n = len(chaos)
    t = np.arange(n) / FS
    coherent = np.sin(2 * np.pi * 4.0 * t)
    return (1.0 - lam) * coherent + lam * chaos


def signal_octave_desaccordee(delta):
    """Famille C : octave + δ demi-tons de désaccord (δ=0 → octave exacte)."""
    n = int(FS * DUREE_ANALYSE)
    t = np.arange(n) / FS
    f1 = 4.0
    f2 = 4.0 * 2.0 ** ((12.0 + delta) / 12.0)
    return np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)


def mesurer(signal, ash):
    """Invariants agrégés + occupation des régimes (% de fenêtres)."""
    df = ash.process_signal(np.asarray(signal, dtype=float))
    regimes = df["regime"].astype(str)
    return {
        "ReN_med": float(np.median(df["ReN"])),
        "ReN_mean": float(np.mean(df["ReN"])),
        "Rtop_med": float(np.median(df["Rtop"])),
        "Rdyn_med": float(np.median(df["Rdyn"])),
        "Rc_mean": float(np.mean(df["Rc"])),
        "pct_cosmo": float(100 * regimes.str.startswith("Cosmologique").mean()),
        "pct_meso": float(100 * regimes.str.startswith("Méso").mean()),
        "pct_quant": float(100 * regimes.str.startswith("Quantique").mean()),
        "n_fenetres": int(len(df)),
    }


def main():
    ash = ASH(fs=FS, signal_type="generic")
    lignes = []

    print("=== Famille A — route de Feigenbaum (map logistique) ===")
    print(f"{'r':>7} {'ReN_med':>10} {'Rtop':>5} {'Rdyn':>6} "
          f"{'%cosmo':>7} {'%méso':>6} {'%quant':>7}")
    for r in np.linspace(3.4, 4.0, 61):
        m = mesurer(signal_logistique(r), ash)
        lignes.append({"famille": "A_logistique", "parametre": r, **m})
        print(f"{r:7.4f} {m['ReN_med']:10.3f} {m['Rtop_med']:5.0f} "
              f"{m['Rdyn_med']:6.3f} {m['pct_cosmo']:7.1f} "
              f"{m['pct_meso']:6.1f} {m['pct_quant']:7.1f}")

    print("\n=== Famille B — mélange cohérence/chaos ===")
    print(f"{'λ':>6} {'ReN_med':>10} {'Rtop':>5} {'Rdyn':>6} "
          f"{'%cosmo':>7} {'%méso':>6} {'%quant':>7}")
    for lam in np.linspace(0.0, 1.0, 51):
        m = mesurer(signal_melange(lam), ash)
        lignes.append({"famille": "B_melange", "parametre": lam, **m})
        print(f"{lam:6.2f} {m['ReN_med']:10.3f} {m['Rtop_med']:5.0f} "
              f"{m['Rdyn_med']:6.3f} {m['pct_cosmo']:7.1f} "
              f"{m['pct_meso']:6.1f} {m['pct_quant']:7.1f}")

    print("\n=== Famille C — octave désaccordée ===")
    print(f"{'δ':>5} {'ReN_med':>10} {'Rtop':>5} {'Rdyn':>6} "
          f"{'%cosmo':>7} {'%méso':>6} {'%quant':>7}")
    for delta in np.linspace(0.0, 6.0, 13):
        m = mesurer(signal_octave_desaccordee(delta), ash)
        lignes.append({"famille": "C_desaccord", "parametre": delta, **m})
        print(f"{delta:5.2f} {m['ReN_med']:10.3f} {m['Rtop_med']:5.0f} "
              f"{m['Rdyn_med']:6.3f} {m['pct_cosmo']:7.1f} "
              f"{m['pct_meso']:6.1f} {m['pct_quant']:7.1f}")

    df = pd.DataFrame(lignes)
    out = os.path.join(_HERE, "results_p35_meso.csv")
    df.to_csv(out, index=False)
    print(f"\nRésultats écrits : {out} ({len(df)} points de mesure)")
    print(f"Repère famille A : r∞ = {R_INFINITY} (transition exacte connue).")


if __name__ == "__main__":
    main()
