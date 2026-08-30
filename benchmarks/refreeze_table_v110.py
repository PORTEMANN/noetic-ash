#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refreeze_table_v110.py — Re-figeage de la table des benchmarks (F18)
====================================================================
Conséquence 4 du chantier P45 (corpus noetic-machine-complete,
data/p45_bench_renormalise_verdict.json) : la table de juin 2026 n'était
reproductible par aucun pipeline publié. Ce script EST le pipeline
déclaré, figé :

  noyau    : src/python/ash_core.py v1.1.0 (grille EEG 5 octaves)
  fenêtrage: process_signal du noyau (fenêtre domaine, recouvrement 0,5)
  données  : les 5 CSV régénérés bit-à-bit par les générateurs seedés
             (np.random.seed(42)) de examples/ — empreintes vérifiées
             contre benchmarks/SHASUMS.txt avant calcul
  sortie   : benchmarks/results/table_bench_v110.csv (+ sha256 affiché)

Changements de fond (F16) : la colonne « régime ReN » est retirée de la
classification officielle (ReN ∝ 1/amplitude — non portable) ; ReN reste
publié comme indicateur relatif à gain fixe déclaré. La classification
officielle repose sur les invariants normalisés (Rtop, Rdyn, E1..E7),
invariants d'amplitude mesurés à 1e-9 (P45-C2) et séparant 10/10 paires
(P45-C3).

Reproductibilité : deux exécutions doivent donner le même SHA-256 de la
table (contrôle C0).
"""

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "python"))
from ash_core import ASH  # v1.1.0

RACINE = Path(__file__).resolve().parent.parent
RESULTS = RACINE / "benchmarks" / "results"
RESULTS.mkdir(exist_ok=True)

# (fichier, domaine, générateur seedé de référence, empreinte SHASUMS)
SIGNAUX = [
    ("signal_sinusoidal.csv", "generic", "examples/synthetic/signal_sinusoidal.py",
     None),  # pas d'empreinte figée historique — déclaré
    ("vibration_moteur_sain.csv", "vibration",
     "examples/vibration_bearing/vibration_moteur_sain.py",
     "bb20c04d7d0de99ba37ed323b14ea97bcda58adca066bf35fb7e417ea27924e6"),
    ("vibration_bearing.csv", "vibration",
     "examples/vibration_bearing/generate_bearing_signal.py",
     "375d649ee279e38cf673a0cb271299f07a8ae99b243a57ab41411d9f09c9b634"),
    ("ecg_normal.csv", "ecg", "examples/ecg_mitbih/ecg_normal.py",
     "d25d65f9297bf94c1b37300ad5065dc105e432b23eaf70782ae905b9f3b161ed"),
    ("eeg_intention.csv", "eeg", "examples/eeg_motor_intention/eeg_intention.py",
     "228c615550a60eed84d7b9bf02b4e4f9555bc56f9d533ec9096e8afdf2883d1f"),
]

NOMS = {
    "signal_sinusoidal.csv": "sinusoide_10Hz",
    "vibration_moteur_sain.csv": "moteur_sain",
    "vibration_bearing.csv": "moteur_defaillant",
    "ecg_normal.csv": "ecg_normal",
    "eeg_intention.csv": "eeg_intention",
}


def main():
    lignes = []
    for csv, domaine, generateur, sha_ref in SIGNAUX:
        path = RACINE / csv
        if not path.exists():  # les générateurs écrivent dans le cwd
            path = Path(csv)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha_ref:
            assert sha == sha_ref, f"empreinte non conforme pour {csv}"
        sig = pd.read_csv(path)["signal"].to_numpy(dtype=float)
        ash = ASH(signal_type=domaine)
        df = ash.process_signal(sig)
        bands = np.array(df["bands"].tolist())
        lig = {
            "signal": NOMS[csv],
            "domaine": domaine,
            "n_fenetres": len(df),
            "Rc_moy": round(float(df["Rc"].mean()), 4),
            "Rtop_moy": round(float(df["Rtop"].mean()), 4),
            "Rdyn_moy": round(float(df["Rdyn"].mean()), 4),
            **{f"E{i}_moy": round(float(bands[:, i - 1].mean()), 4)
               for i in range(1, 8)},
            "ReN_moy_indicatif_gain_fixe": round(float(df["ReN"].mean()), 4),
            "sha256_dataset": sha,
        }
        lignes.append(lig)
        print(f"{NOMS[csv]:<20} Rc={lig['Rc_moy']:<8} Rtop={lig['Rtop_moy']:<6} "
              f"Rdyn={lig['Rdyn_moy']:<8} ReN*={lig['ReN_moy_indicatif_gain_fixe']}")

    table = pd.DataFrame(lignes)
    out = RESULTS / "table_bench_v110.csv"
    table.to_csv(out, index=False)
    sha_table = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"\ntable figée : {out}  sha256 {sha_table}")
    print("(relancer : le SHA doit être identique — contrôle C0)")


if __name__ == "__main__":
    main()
