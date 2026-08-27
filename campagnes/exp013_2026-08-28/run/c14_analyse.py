#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""c14_analyse.py — campagne exp013 : régénère bit-à-bit signatures/ et verdicts/
depuis les CSV de signaux/ (eux-mêmes régénérés par c14_runner.py).

Protocole C14 + addenda A1/A2. RMS = 1 obligatoire (B3-FAIL #1).
  - volet a : N_v(t) fs=10 f0=0,125 ; L(t) fs=2,5 f0=0,03125 ; fenêtre 512 pts,
    nperseg=256, overlap 0,5, 5 octaves, agrégation médiane.
  - contrôles : mêmes paramètres que N_v(t).
  - volet b : fs=1, f0=0,00390625 (2^-8), fenêtre 1024 pts, nperseg=1024.

Attentes : bridge/expectations.json du dépôt (EXP-013a / EXP-013b, v0.5.0).
Horodatage figé : 2026-08-28T00:00:00+00:00.

Usage (depuis la racine du dépôt noetic-ash) :
    python3 campagnes/exp013_2026-08-28/run/c14_analyse.py
"""
import hashlib, json, os, sys
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # campagnes/exp013_2026-08-28
REPO = os.path.dirname(os.path.dirname(BASE))                        # racine du dépôt
sys.path.insert(0, os.path.join(REPO, "src", "python"))
sys.path.insert(0, os.path.join(REPO, "bridge"))
from ash_core import ASH
import noetic_bridge as nb

HORODATAGE = "2026-08-28T00:00:00+00:00"
SIG = os.path.join(BASE, "signaux")
OUT_S = os.path.join(BASE, "signatures")
OUT_V = os.path.join(BASE, "verdicts")
os.makedirs(OUT_S, exist_ok=True); os.makedirs(OUT_V, exist_ok=True)

exp = json.load(open(os.path.join(REPO, "bridge", "expectations.json")))
F13A = next(a["falsifieur"] for a in exp["attentes"] if a["id"] == "EXP-013a")
F13B = next(a["falsifieur"] for a in exp["attentes"] if a["id"] == "EXP-013b")
F_CTRL = ("Contrôle statut H : consigné sans attente (HORS-CONTRAT), "
          "aucune conclusion.")

def load_csv(p):
    vals = []
    with open(p) as f:
        next(f)
        for ln in f:
            vals.append(float(ln.split(",")[1]))
    return np.array(vals)

def analyse(sig, fs, f0, win_pts, nperseg):
    s = sig / np.sqrt(np.mean(sig**2))                 # RMS = 1
    ash = ASH(fs=fs, signal_type="generic", f0=f0, n_octaves=5,
              window_duration=win_pts / fs, overlap=0.5, nperseg=nperseg)
    df = ash.process_signal(s)
    med = {"Rc": float(df["Rc"].median()), "Rtop": float(df["Rtop"].median()),
           "Rdyn": float(df["Rdyn"].median()), "ReN": float(df["ReN"].median()),
           "bands": np.median(np.stack(df["bands"]), axis=0),
           "n_fenetres": len(df)}
    p = med["bands"] / med["bands"].sum()
    med["H"] = float(-np.sum(p * np.log(p + 1e-12)))
    sb = np.sort(med["bands"])[::-1]
    med["D"] = float(sb[0] - sb[1])
    med["bande"] = f"E{int(np.argmax(med['bands'])) + 1}"
    med["regime"] = ("Quantique" if med["ReN"] > 10
                     else ("Cosmologique" if med["ReN"] < 1 else "Méso"))
    return med

def signature(csv, npts, med, fs, f0, win, nps, statut, etiquette,
              domaine, desc, falsif, sources):
    return {
        "format": "ash-signature/0.1", "ash_version": "1.0.0",
        "signal": {"sha256": hashlib.sha256(open(csv, "rb").read()).hexdigest(),
                   "source": desc, "n_points": npts},
        "grille": {"f0": f0, "n_octaves": 5, "fs": fs,
                   "fenetre_s": win / fs, "overlap": 0.5, "nperseg": nps},
        "normalisation": "rms1",
        "agregation": {"methode": "mediane", "n_fenetres": med["n_fenetres"]},
        "invariants": {"Rc": round(med["Rc"], 6), "Rtop": med["Rtop"],
                       "Rdyn": round(med["Rdyn"], 6), "ReN": round(med["ReN"], 6),
                       "D": round(med["D"], 6), "H": round(med["H"], 6),
                       "bandes": [round(float(b), 6) for b in med["bands"]]},
        "regime": med["regime"], "bande_dominante": med["bande"],
        "contexte": {"domaine": domaine, "etiquette": etiquette,
                     "date_mesure": "2026-08-28", "description": desc},
        "statut": statut, "falsifieur": falsif, "sources": sources,
    }

SA = ("Campagne exp013 C14+A1 — GP amorti 3D (e44_core.py blob 2baf8d8d…), "
      "quench bruit blanc graine 2026, N=48, γ=0,2, dt=0,1, 2048 pas")
SB = ("Campagne exp013 C14+A2 — orbitale radiale u_{{{}}}(r), hamiltonien P1 sur "
      "fond monopole ρ=1 (C=1,3033), boîte RMAX=4000, NR=4000, dr=1 (table P1 "
      "publiée reproduite : 1s ratio 0,9994)")

TRAVAUX = [
    ("e44_nv_t", 2048, 10.0, 0.125, 512, 256, "E", "gp_vortex_relax",
     "dynamique_vortex", SA + " ; N_v(t) = plaquettes de vorticité, chaque pas",
     F13A, ["noetic-machine e44_core", "protocole C14+A1 figé"]),
    ("e44_lt_t", 512, 2.5, 0.03125, 512, 256, "E", "gp_vortex_relax",
     "dynamique_vortex", SA + " ; L(t) = longueur totale des boucles fermées, tous les 4 pas",
     F13A, ["noetic-machine e44_core", "protocole C14+A1 figé"]),
    ("controle_bruit43", 2048, 10.0, 0.125, 512, 256, "H", "controle_bruit",
     "etalonnage", "Campagne exp013 C14 — bruit blanc gaussien graine 43 (contrôle)",
     F_CTRL, ["protocole C14 figé"]),
    ("controle_expo", 2048, 10.0, 0.125, 512, 256, "H", "controle_expo",
     "etalonnage", "Campagne exp013 C14 — décroissance exp(−t/40) pure (contrôle)",
     F_CTRL, ["protocole C14 figé"]),
]
ETATS = ["1s", "2s", "2p", "3s", "3p", "3d", "4s", "4p", "4d", "4f"]
for nom in ETATS:
    TRAVAUX.append(
        (f"p1_orb_{nom}", 4000, 1.0, 0.00390625, 1024, 1024, "E",
         "p1_orbitale_radiale", "spectre_lie", SB.format(nom),
         F13B, ["noetic-machine-complete P1", "protocole C14+A2 figé"]))

for nom, npts, fs, f0, win, nps, statut, etiq, dom, desc, falsif, srcs in TRAVAUX:
    csv = os.path.join(SIG, f"{nom}.csv")
    med = analyse(load_csv(csv), fs, f0, win, nps)
    s = signature(csv, npts, med, fs, f0, win, nps, statut, etiq, dom, desc,
                  falsif, srcs)
    with open(os.path.join(OUT_S, f"{nom}.signature.json"), "w") as f:
        f.write(json.dumps(s, ensure_ascii=False, indent=2, sort_keys=True))
    v = nb.evaluer(s, exp["attentes"], HORODATAGE)
    with open(os.path.join(OUT_V, f"{nom}.verdict.json"), "w") as f:
        f.write(json.dumps(v, indent=1) + "\n")
    print(f"{nom:18s} {v['verdict']:14s} {med['regime']:12s} "
          f"ReN={round(med['ReN'], 6)}")
