#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_examples.py — régénère les signatures et verdicts d'exemple du pont.

Reproductibilité (pilier 2, C12.1) : tous les signaux sont seedés ou
déterministes ; les CSV canoniques (time,signal en %.10e) sont écrits dans
``csv/`` (non commités) et leurs empreintes SHA-256 consignées dans les
signatures JSON. Une ré-exécution à versions figées (ash_core 1.0.0,
noetic_bridge 0.1.0) reproduit les fichiers à l'identique, à l'horodatage
près — exclu de l'empreinte des verdicts.

Usage (depuis la racine du dépôt) :
    python bridge/examples/generate_examples.py
"""

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "src", "python"))
sys.path.insert(0, os.path.join(_ROOT, "bridge"))
from ash_core import ASH            # noqa: E402
import noetic_bridge as nb          # noqa: E402

SEED = 42                    # convention C12.1 (v1.0.0)
HORODATAGE = "2026-08-27T12:00:00Z"   # figé : exemples reproductibles
CSV_DIR = os.path.join(_HERE, "csv")
os.makedirs(CSV_DIR, exist_ok=True)


def canon_csv(t, sig, nom):
    """Écrit le CSV canonique et retourne (sha256, n_points, duree_s)."""
    df = pd.DataFrame({"time": t, "signal": sig})
    path = os.path.join(CSV_DIR, nom + ".csv")
    df.to_csv(path, index=False, float_format="%.10e")
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    return sha, len(df), float(df["time"].iloc[-1] - df["time"].iloc[0]) + 1.0


def mesurer(sig, signal_type):
    """Analyse ASH complète + agrégation médiane (convention interpret.py)."""
    ash = ASH(signal_type=signal_type)
    res = ash.process_signal(np.asarray(sig, dtype=float))
    bandes = np.median(np.stack(res["bands"].to_numpy()), axis=0)
    p = bandes / bandes.sum()
    H = float(-np.sum(p * np.log(p + 1e-12)))
    sb = np.sort(bandes)[::-1]
    return ash, {
        "Rc": round(float(res["Rc"].median()), 6),
        "Rtop": int(res["Rtop"].median()),
        "Rdyn": round(float(res["Rdyn"].median()), 6),
        "bandes": [round(float(b), 6) for b in bandes],
        "H": round(H, 6),
        "D": round(float(sb[0] - sb[1]), 6),
        "ReN": round(float(res["ReN"].median()), 6),
    }, res["regime"].mode()[0].split(" ")[0], f"E{int(np.argmax(bandes)) + 1}", len(res)


# ---------------------------------------------------------------------- #
# Signaux (générateurs seedés / déterministes)                            #
# ---------------------------------------------------------------------- #

def sig_eeg_intention():
    """P32+ : alpha 10 Hz + bêta 20 Hz modulé 4–7 s (intention), bruits."""
    np.random.seed(SEED)
    fs, t = 250, np.arange(0, 10.0, 1 / 250)
    intention = np.zeros_like(t); intention[(t >= 4) & (t <= 7)] = 1.0
    b, a = butter(2, 30, fs=fs, btype="low")
    sig = (0.5 * np.sin(2 * np.pi * 10 * t)
           + intention * 0.8 * np.sin(2 * np.pi * 20 * t)
           + filtfilt(b, a, np.random.randn(len(t))) * 0.15
           + 0.1 * np.random.randn(len(t)))
    return t, sig, "eeg"


def sig_ecg_normal():
    """P33+ : ECG synthétique 72 bpm (QRS + ondes P/T), bruit, dérive."""
    np.random.seed(SEED)
    fs, t = 360, np.arange(0, 10.0, 1 / 360)
    period = 60.0 / 72
    phase = 2 * np.pi * (t % period) / period
    sig = (1.2 * np.exp(-((phase - 0.3) * 20) ** 2)
           + 0.25 * np.exp(-((phase - 0.0) * 30) ** 2)
           + 0.35 * np.exp(-((phase - 0.6) * 15) ** 2)
           + 0.05 * np.random.randn(len(t))
           + 0.02 * np.sin(2 * np.pi * 0.5 * t))
    return t, sig, "ecg"


def sig_vibration_roulement():
    """P34+ : rotation 30 Hz + défaut BPFO ~129 Hz émergeant à t = 5 s."""
    np.random.seed(SEED)
    fs, t = 1000, np.arange(0, 10.0, 1 / 1000)
    fr, fd = 30, 4.3 * 30
    sain = (0.5 * np.sin(2 * np.pi * fr * t)
            + 0.3 * np.sin(2 * np.pi * 2 * fr * t)
            + 0.1 * np.sin(2 * np.pi * 3 * fr * t))
    env = np.exp(-((t - 5) / 1.5) ** 2)
    sig = (sain + env * (0.4 * np.sin(2 * np.pi * fd * t)
           * (1 + 0.3 * np.sin(2 * np.pi * fr * t)))
           + 0.02 * np.random.randn(len(t)))
    return t, sig, "vibration"


def sig_ton_pur():
    """Étalon LEX-013 : sinus pur 4 Hz (méso par construction)."""
    fs, t = 250, np.arange(0, 10.0, 1 / 250)
    return t, np.sin(2 * np.pi * 4 * t), "generic"


def sig_logistique_p3():
    """LEX-012 / P35+ famille A : logistique r = 3.84, protocole figé."""
    FS, DUREE, SPI, TRANS, X0 = 250.0, 20.0, 32, 1000, 0.3
    x = X0
    for _ in range(TRANS):
        x = 3.84 * x * (1.0 - x)
    n_iter = int(FS * DUREE / SPI)
    orb = np.empty(n_iter)
    for i in range(n_iter):
        x = 3.84 * x * (1.0 - x); orb[i] = x
    sig = np.repeat(orb, SPI)
    return np.arange(len(sig)) / FS, sig, "generic"


def sig_bruit_blanc():
    """LEX-005 : bruit blanc gaussien stationnaire, seed 42."""
    np.random.seed(SEED)
    sig = np.random.randn(2500)
    return np.arange(2500) / 250.0, sig, "generic"


def sig_finance_gbm():
    """EXP-007 (H) : marche aléatoire géométrique SYNTHÉTIQUE, seed 42.

    Échantillon exploratoire — pas une donnée de marché réelle. L'ASH
    analyse toute série (temps, valeur) ; l'interprétation n'advient que
    si une distribution non triviale émerge sur échantillon réel.
    """
    np.random.seed(SEED)
    n = 2500
    prix = 100 * np.exp(np.cumsum(0.0005 + 0.012 * np.random.randn(n)))
    return np.arange(n) / 250.0, prix, "generic"


# ---------------------------------------------------------------------- #
# Fabrication des signatures et verdicts                                  #
# ---------------------------------------------------------------------- #

EXEMPLES = [
    # (nom, générateur, source, domaine, etiquette, description, statut, falsifieur, sources)
    ("eeg_intention_p32plus", sig_eeg_intention,
     "examples/eeg_motor_intention/eeg_intention.py (seed 42, dataset régénérable)",
     "eeg", "eeg_intention_motrice",
     "EEG synthétique 10 s : alpha 10 Hz en fond, bêta 20 Hz modulé entre 4 et 7 s (intention motrice), bruits rose et blanc.",
     "E",
     "La régénération du dataset seedé ne reproduisant pas ReN > 10 pendant la fenêtre d'intention.",
     ["https://github.com/PORTEMANN/noetic-ash/tree/main/examples/eeg_motor_intention"]),
    ("ecg_normal_p33plus", sig_ecg_normal,
     "examples/ecg_mitbih/ecg_normal.py (seed 42, dataset régénérable)",
     "ecg", "ecg_normal",
     "ECG synthétique 72 bpm, 10 s : QRS + ondes P/T, bruit 5 %, dérive lente 0,5 Hz.",
     "E",
     "Des ECG normaux (MIT-BIH NSRDB) classés majoritairement quantiques par le pipeline figé.",
     ["https://github.com/PORTEMANN/noetic-ash/tree/main/examples/ecg_mitbih"]),
    ("vibration_roulement_p34plus", sig_vibration_roulement,
     "examples/vibration_bearing/generate_bearing_signal.py (seed 42, dataset régénérable)",
     "vibration", "vibration_roulement_defaut",
     "Vibration de roulement 1 kHz, 10 s : rotation 30 Hz + harmoniques ; défaut BPFO ~129 Hz émergeant à t = 5 s.",
     "E",
     "Sur un dataset public (ex. CWRU), défectueux classés cosmologiques ou sains classés quantiques de façon systématique.",
     ["https://github.com/PORTEMANN/noetic-ash/tree/main/examples/vibration_bearing"]),
    ("ton_pur_4hz", sig_ton_pur,
     "Sinus pur 4 Hz, fs = 250 Hz, 10 s (déterministe, sans RNG)",
     "acoustique", "ton_pur",
     "Sinusoïde pure 4 Hz — étalon du fallback Rdyn (Rtop = 1 → méso par construction).",
     "C",
     "Un sinus pur classé hors méso en configuration generic figée.",
     ["https://github.com/PORTEMANN/noetic-ash/tree/main/benchmarks/p35_meso"]),
    ("logistique_p3_r384", sig_logistique_p3,
     "benchmarks/p35_meso/sweep_meso.py famille A (r = 3.84, x0 = 0.3, zero-order 32 éch./it, déterministe)",
     "chaos", "logistique_periode3",
     "Map logistique r = 3.84 (fenêtre de période 3, dynamique ordonnée), protocole P35+ figé.",
     "C",
     "Ré-exécution de sweep_meso.py ne reproduisant pas 100 % quantique sur r ∈ [3.83, 3.85].",
     ["https://github.com/PORTEMANN/noetic-ash/tree/main/benchmarks/p35_meso"]),
    ("bruit_blanc_seed42", sig_bruit_blanc,
     "Bruit blanc gaussien, seed 42, fs = 250 Hz, 10 s",
     "etalonnage", "bruit_blanc_stationnaire",
     "Bruit blanc stationnaire — sonde de spécificité (pas de fausse alarme quantique).",
     "C",
     "Plus de 5 % de fenêtres quantiques sur le protocole figé 100 graines (seed 42).",
     ["https://github.com/PORTEMANN/noetic-ash/blob/main/CHANGELOG.md"]),
    ("finance_gbm_synth_h", sig_finance_gbm,
     "Marche aléatoire géométrique synthétique (rendements gaussiens, seed 42) — échantillon exploratoire, PAS une donnée de marché réelle",
     "finance", "finance_echantillon",
     "Échantillon exploratoire finance (statut H strict) : série (temps, valeur) analysable comme toute autre ; aucune prédiction, la banque consigne.",
     "H",
     "Sur N séries financières réelles à protocole figé, une distribution des régimes indiscernable de surrogates aléatoires tue la piste d'une structure spectrale spécifique.",
     ["https://github.com/PORTEMANN/noetic-ash/tree/main/contrib"]),
]


def main():
    with open(os.path.join(_ROOT, "bridge", "expectations.json"), encoding="utf-8") as f:
        attentes = json.load(f)["attentes"]
    for nom, gen, source, domaine, etiquette, descr, statut, falsifieur, sources in EXEMPLES:
        t, sig, stype = gen()
        sha, npts, _ = canon_csv(t, sig, nom)
        fs = float(1.0 / np.mean(np.diff(t)))
        ash, inv, regime, bande_dom, nfen = mesurer(sig, stype)
        signature = {
            "format": "ash-signature/0.1",
            "ash_version": ash.__version__ if hasattr(ash, "__version__") else "1.0.0",
            "signal": {"sha256": sha, "n_points": int(npts),
                       "duree_s": round(float(t[-1] - t[0]) + 1.0 / fs, 6),
                       "source": source,
                       "generateur": "bridge/examples/generate_examples.py"},
            "grille": {"fs": ash.fs, "f0": ash.f0, "n_octaves": ash.n_octaves,
                       "fenetre_s": ash.window_duration, "overlap": ash.overlap,
                       "nperseg": ash.nperseg},
            "normalisation": "aucune",
            "agregation": {"n_fenetres": int(nfen), "methode": "mediane"},
            "invariants": inv,
            "regime": regime,
            "bande_dominante": bande_dom,
            "contexte": {"domaine": domaine, "etiquette": etiquette,
                         "description": descr, "date_mesure": "2026-08-27"},
            "statut": statut,
            "falsifieur": falsifieur,
            "sources": sources,
        }
        verdict = nb.evaluer(signature, attentes, horodatage=HORODATAGE)
        base = os.path.join(_HERE, nom)
        with open(base + ".signature.json", "w", encoding="utf-8") as f:
            json.dump(signature, f, ensure_ascii=False, indent=1)
        with open(base + ".verdict.json", "w", encoding="utf-8") as f:
            json.dump(verdict, f, ensure_ascii=False, indent=1)
        print(f"{verdict['verdict']:<12} {nom:<32} "
              f"régime={verdict['mesure']['regime']:<13} sha={verdict['sha256'][:10]}")


if __name__ == "__main__":
    main()
