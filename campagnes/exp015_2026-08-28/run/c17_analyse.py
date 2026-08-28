#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C17 — analyse de la campagne exp015 (attente EXP-015, expectations v0.8.0
figée AVANT mesure, commit 712c1c4).

Régénère signatures + verdicts (octets déterministes) depuis signaux/ :
  signatures/*.signature.json  — ash-signature/0.1 (json trié, indent 2, sans LF final)
  verdicts/*.verdict.json      — ash-verdict/0.1 (indent 1, LF final)
  run/evaluation_clauses.json  — évaluation clause par clause du falsifieur EXP-015
  run/manifest.json            — empreintes SHA-256 complètes

Agrégation médiane identique à c14_analyse.py / c16_analyse.py. Aucun
post-traitement.
"""

import hashlib
import json
import math
import os
import sys

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RUN)
from ash_core import ASH
import noetic_bridge as nb

SIG = os.path.join(BASE, "signaux")
OUT_S = os.path.join(BASE, "signatures")
OUT_V = os.path.join(BASE, "verdicts")
os.makedirs(OUT_S, exist_ok=True)
os.makedirs(OUT_V, exist_ok=True)

exp = json.load(open(os.path.join(RUN, "expectations_v080.json")))
F15 = next(a["falsifieur"] for a in exp["attentes"] if a["id"] == "EXP-015")
F_CTRL = ("Contrôle statut H : consigné sans attente (HORS-CONTRAT), "
          "aucune conclusion.")
HORODATAGE = "2026-08-28T00:00:00+00:00"

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

LETTRES = "spdfgh"
ETATS = [(f"{n}{LETTRES[l]}", n - l - 1) for n in range(2, 7) for l in range(n)]
PLUR = {0: "0 nœud", 1: "1 nœud"}
SN = ("Campagne exp015 C17 — orbitale radiale u_{{{}}}(r) sur fond monopole ρ=2 "
      "(C=1,6676 ; couplage déclaré R_core=3,04/√2), boîte RMAX=8000, NR=8000, dr=1")

TRAVAUX = [(f"p1_orb_{nom}_rho2", 8000, 1.0, 2.0**-11, 1024, 1024, "E",
            "p1_orbitale_radiale_rho2_boite8000", "spectre_lie",
            SN.format(nom) + f" ({PLUR.get(nd, str(nd) + ' nœuds')})", F15,
            ["noetic-machine-complete P1", "protocole C17 figé"])
           for nom, nd in ETATS]
TRAVAUX += [
    ("temoin_4f_rho1", 8000, 1.0, 2.0**-11, 1024, 1024, "H", "temoin_integrite",
     "spectre_lie", "Campagne exp015 C17 — témoin d'intégrité 4f sur fond ρ=1 "
     "(R_core=3,04, même boîte 8000 ; E=−1,664092e-6 Balmer-exact)", F_CTRL,
     ["protocole C17 figé"]),
    ("controle_bruit43", 2048, 10.0, 2.0**-11, 512, 256, "H", "controle_bruit",
     "etalonnage", "Campagne exp015 C17 — bruit blanc gaussien graine 43 "
     "(CSV octet-identique à exp013, sha256 a3909a6b…)", F_CTRL,
     ["protocole C17 figé"]),
]

resultats = {}
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
    resultats[nom] = {"Rc": med["Rc"], "ReN": s["invariants"]["ReN"],
                      "regime": s["regime"], "verdict": v["verdict"]}
    print(f"[C17] {nom:18s} Rc={s['invariants']['Rc']:12.6f} "
          f"ReN={s['invariants']['ReN']:10.6f} {s['regime']:13s} → {v['verdict']}")

# ---------------------------------------------------------------- clauses EXP-015
Rc = {f"{n}{LETTRES[l]}": resultats[f"p1_orb_{n}{LETTRES[l]}_rho2"]["Rc"]
      for n in range(2, 7) for l in range(n)}
# (a) ordre nodal par couche, tolérance 5 %
clA = True
quasi = []
detail_a = {}
for n in range(2, 7):
    seq = sorted([(f"{n}{LETTRES[l]}", n - l - 1) for l in range(n)],
                 key=lambda x: x[1])
    rcs = [Rc[nm] for nm, _ in seq]
    inv = []
    for i in range(len(rcs) - 1):
        if rcs[i + 1] < rcs[i]:
            ecart = rcs[i + 1] / rcs[i] - 1
            inv.append({"jointure": f"{seq[i][0]}/{seq[i+1][0]}",
                        "ecart_relatif": ecart})
            if abs(ecart) > 0.05:
                clA = False
            else:
                quasi.append({"couche": n, "jointure": f"{seq[i][0]}/{seq[i+1][0]}",
                              "ecart_relatif": ecart})
    detail_a[str(n)] = {"ordre": [nm for nm, _ in seq], "Rc": rcs,
                        "inversions": inv}
# (b) ratios inter-couches à l fixe (séries n=l+1..6 d'états liés)
rats = {}
for l in range(5):
    for n in range(max(2, l + 1), 6):
        rats[f"{n+1}{LETTRES[l]}/{n}{LETTRES[l]}"] = \
            Rc[f"{n+1}{LETTRES[l]}"] / Rc[f"{n}{LETTRES[l]}"]
hors = {k: v for k, v in rats.items() if not (1.45 <= v <= 1.75)}
mg = math.exp(sum(math.log(v) for v in rats.values()) / len(rats))
clB = (not hors) and abs(mg / 1.5874 - 1) <= 0.05
# (c) tous Cosmologique
clC = all(resultats[f"p1_orb_{n}{LETTRES[l]}_rho2"]["regime"] == "Cosmologique"
          for n in range(2, 7) for l in range(n))

clauses = {
    "attente": "EXP-015", "Rc": Rc,
    "clause_a_ordre": {"resultat": clA, "detail": detail_a,
                       "quasi_degenerescences_consignees": quasi},
    "clause_b_echelle": {"resultat": clB, "ratios": rats,
                         "ratios_hors_1.45_1.75": hors,
                         "moyenne_geometrique": mg,
                         "delta8": 2.0 ** (2 / 3),
                         "ecart_relatif_delta8": mg / 2.0 ** (2 / 3) - 1},
    "clause_c_regime": {"resultat": clC,
                        "non_cosmologiques": {
                            nom: resultats[nom]["regime"]
                            for nom in resultats
                            if nom.startswith("p1_orb_")
                            and resultats[nom]["regime"] != "Cosmologique"}},
    "EXP015_conforme_aux_trois_clauses": clA and clB and clC,
}
with open(os.path.join(RUN, "evaluation_clauses.json"), "w", newline="") as f:
    f.write(json.dumps(clauses, ensure_ascii=False, indent=2) + "\n")
print("[C17] clauses : a =", clA, " b =", clB, " c =", clC)

# ---------------------------------------------------------------- manifeste
man = {}
for sub in ("protocole", "signaux", "signatures", "verdicts"):
    d = os.path.join(BASE, sub)
    for f in sorted(os.listdir(d)):
        man[f"{sub}/{f}"] = hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest()
for f in ("c17_runner.py", "c17_analyse.py", "ash_core.py", "noetic_bridge.py",
          "expectations_v080.json", "evaluation_clauses.json", "energies_c17.json"):
    man[f"run/{f}"] = hashlib.sha256(open(os.path.join(RUN, f), "rb").read()).hexdigest()
with open(os.path.join(RUN, "manifest.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C17] manifest.json : {len(man)} empreintes")
