#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""c13_1_analyse.py — campagne monopole_ash : analyse ASH + signatures + verdicts.

Reproduit bit-à-bit signatures/ et verdicts/ depuis les CSV de signaux/
(régénérés par c13_1_runner.py), le noyau ASH et le pont du dépôt.

Usage (depuis la racine du dépôt noetic-ash) :
    python3 campagnes/monopole_ash_2026-08-27/run/c13_1_analyse.py

Protocole C13.1 figé : RMS=1, grille f0=0.125 cycle/ξ, 5 octaves,
fenêtre 1024 pts, overlap 0.5, nperseg 1024, agrégation médiane (7 fenêtres).
"""
import hashlib, json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # campagnes/monopole_ash_2026-08-27
REPO = os.path.dirname(os.path.dirname(BASE))                        # racine du dépôt
sys.path.insert(0, os.path.join(REPO, "src", "python"))
sys.path.insert(0, os.path.join(REPO, "bridge"))
from ash_core import ASH
import noetic_bridge as nb
import numpy as np

HORODATAGE = "2026-08-27T16:45:00+00:00"   # figé (reproductibilité des verdicts)

meta = json.load(open(os.path.join(BASE, "run", "runs_c13_1.json")))
N = meta["grille"]["N"]; XMAX = meta["grille"]["xmax"]
FS = meta["grille"]["fs"]; WIN = 1024
RHOS = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
tag = lambda r: str(r).replace(".", "p")

exp = json.load(open(os.path.join(REPO, "bridge", "expectations.json")))
FALS_EXP012 = next(a["falsifieur"] for a in exp["attentes"] if a["id"] == "EXP-012")

ash = ASH(fs=FS, signal_type="generic", f0=0.125, n_octaves=5,
          window_duration=WIN/FS, overlap=0.5, nperseg=1024)

def analyse(sig):
    s = sig / np.sqrt(np.mean(sig**2))            # RMS = 1 (B3-FAIL #1)
    df = ash.process_signal(s)
    med = {"Rc": float(df["Rc"].median()), "Rtop": float(df["Rtop"].median()),
           "Rdyn": float(df["Rdyn"].median()), "ReN": float(df["ReN"].median()),
           "bands": np.median(np.stack(df["bands"]), axis=0)}
    p = med["bands"] / med["bands"].sum()
    med["H"] = float(-np.sum(p*np.log(p + 1e-12)))
    sb = np.sort(med["bands"])[::-1]
    med["D"] = float(sb[0]-sb[1])
    med["bande_dominante"] = f"E{int(np.argmax(med['bands']))+1}"
    med["regime"] = "Quantique" if med["ReN"] > 10 else ("Cosmologique" if med["ReN"] < 1 else "Méso")
    return med

def signature(rho, med, sha, statut, etiquette, desc, falsifieur):
    return {
        "format": "ash-signature/0.1",
        "ash_version": "1.0.0",
        "signal": {
            "sha256": sha,
            "source": f"Campagne monopole_ash C13.1 — {desc} ; artefact p0_monopole_su2.py sha256=52929bda0603…, minimisation L-BFGS-B grille 4096 pts [30/4096, 30], continuation depuis ρ=0.5",
            "n_points": N,
            "duree_s": XMAX,
        },
        "grille": {"f0": 0.125, "n_octaves": 5, "fs": FS,
                   "fenetre_s": WIN/FS, "overlap": 0.5, "nperseg": 1024},
        "normalisation": "rms1",
        "agregation": {"methode": "mediane", "n_fenetres": 7},
        "invariants": {"Rc": round(med["Rc"], 6), "Rtop": med["Rtop"], "Rdyn": round(med["Rdyn"], 6),
                       "ReN": round(med["ReN"], 6), "D": round(med["D"], 6), "H": round(med["H"], 6),
                       "bandes": [round(float(b), 6) for b in med["bands"]]},
        "regime": med["regime"],
        "bande_dominante": med["bande_dominante"],
        "contexte": {"domaine": "soliton_radial", "etiquette": etiquette,
                     "date_mesure": "2026-08-27", "description": desc},
        "statut": statut,
        "falsifieur": falsifieur,
        "sources": ["noetic-machine P0 (artefact 52929bda0603)", "protocole C13.1 figé"],
    }

def load_csv(p):
    vals = []
    with open(p) as f:
        next(f)
        for ligne in f:
            vals.append(float(ligne.split(",")[1]))
    return np.array(vals)

os.makedirs(os.path.join(BASE, "signatures"), exist_ok=True)
os.makedirs(os.path.join(BASE, "verdicts"), exist_ok=True)
n = 0
for rho in RHOS:
    t = tag(rho)
    C = meta["runs"][str(rho)]["C"]
    specs = [("eps", "E", "monopole_su2_radial",
              f"Densité d'énergie radiale ε(ξ) du monopole SU(2), ρ={rho} (C={C:.5f})", FALS_EXP012)]
    for nom in ("h", "k"):
        specs.append((nom, "H", f"monopole_su2_{nom}_controle",
                      f"Contrôle {nom.upper()}(ξ) du monopole SU(2), ρ={rho} — consigné sans attente (statut H)", None))
    for nom, statut, etiquette, desc, fals in specs:
        p_csv = os.path.join(BASE, "signaux", f"{nom}_r{t}.csv")
        sha = hashlib.sha256(open(p_csv, "rb").read()).hexdigest()
        assert sha == meta["sha256_csv"][f"{nom}_r{t}"], f"empreinte CSV divergente : {nom}_r{t}"
        med = analyse(load_csv(p_csv))
        s = signature(rho, med, sha, statut, etiquette, desc, fals)
        with open(os.path.join(BASE, "signatures", f"monopole_{nom}_r{t}.signature.json"), "w") as f:
            f.write(json.dumps(s, ensure_ascii=False, indent=2, sort_keys=True))
        v = nb.evaluer(s, exp["attentes"], horodatage=HORODATAGE)
        with open(os.path.join(BASE, "verdicts", f"monopole_{nom}_r{t}.verdict.json"), "w") as f:
            f.write(json.dumps(v, ensure_ascii=False, indent=1) + "\n")
        n += 2
        print(f"{nom}_r{t} : ReN={med['ReN']:.3f} {med['regime']} → {v['verdict']}")
print(f"{n} fichiers écrits (signatures + verdicts)")
