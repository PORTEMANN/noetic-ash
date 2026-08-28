#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C16 — analyse de la campagne exp014_mesure (attente EXP-014, expectations
v0.6.0 figée AVANT mesure, commit 9bce034).

Régénère signatures + verdicts (octets déterministes) depuis signaux/ :
  signatures/*.signature.json  — ash-signature/0.1 (json trié, indent 2, sans LF final)
  verdicts/*.verdict.json      — ash-verdict/0.1 (indent 1, LF final)
  run/manifest.json            — empreintes SHA-256 (signaux + signatures + verdicts
                                 + protocole + scripts)

Agrégation médiane identique à c14_analyse.py. Aucun post-traitement.
"""

import hashlib
import json
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

exp = json.load(open(os.path.join(RUN, "expectations_v060.json")))
F14 = next(a["falsifieur"] for a in exp["attentes"] if a["id"] == "EXP-014")
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

SN5 = ("Campagne exp014_mesure C16 — orbitale radiale u_{{{}}}(r), couche n=5 "
       "du hamiltonien P1 sur fond monopole ρ=1 (C=1,3033), boîte RMAX=4000, "
       "NR=4000, dr=1")
TRAVAUX = [
    ("p1_orb_5g", 4000, 1.0, 2.0**-11, 1024, 1024, "E", "p1_orbitale_radiale_n5",
     "spectre_lie", SN5.format("5g") + " (0 nœud)", F14,
     ["noetic-machine-complete P1", "protocole C16 figé"]),
    ("p1_orb_5f", 4000, 1.0, 2.0**-11, 1024, 1024, "E", "p1_orbitale_radiale_n5",
     "spectre_lie", SN5.format("5f") + " (1 nœud)", F14,
     ["noetic-machine-complete P1", "protocole C16 figé"]),
    ("p1_orb_5d", 4000, 1.0, 2.0**-11, 1024, 1024, "E", "p1_orbitale_radiale_n5",
     "spectre_lie", SN5.format("5d") + " (2 nœuds)", F14,
     ["noetic-machine-complete P1", "protocole C16 figé"]),
    ("p1_orb_5p", 4000, 1.0, 2.0**-11, 1024, 1024, "E", "p1_orbitale_radiale_n5",
     "spectre_lie", SN5.format("5p") + " (3 nœuds)", F14,
     ["noetic-machine-complete P1", "protocole C16 figé"]),
    ("p1_orb_5s", 4000, 1.0, 2.0**-11, 1024, 1024, "E", "p1_orbitale_radiale_n5",
     "spectre_lie", SN5.format("5s") + " (4 nœuds)", F14,
     ["noetic-machine-complete P1", "protocole C16 figé"]),
    ("temoin_4f", 4000, 1.0, 2.0**-11, 1024, 1024, "H", "temoin_integrite",
     "spectre_lie", "Campagne exp014_mesure C16 — témoin d'intégrité 4f "
     "(CSV octet-identique à exp013 p1_orb_4f.csv, sha256 423604b8…)", F_CTRL,
     ["protocole C16 figé"]),
    ("controle_bruit43", 2048, 10.0, 2.0**-11, 512, 256, "H", "controle_bruit",
     "etalonnage", "Campagne exp014_mesure C16 — bruit blanc gaussien graine 43 "
     "(CSV octet-identique à exp013, sha256 a3909a6b…)", F_CTRL,
     ["protocole C16 figé"]),
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
    resultats[nom] = {"Rc": s["invariants"]["Rc"], "ReN": s["invariants"]["ReN"],
                      "regime": s["regime"], "verdict": v["verdict"]}
    print(f"[C16] {nom:18s} Rc={s['invariants']['Rc']:12.6f} "
          f"ReN={s['invariants']['ReN']:10.6f} {s['regime']:13s} → {v['verdict']}")

# évaluation des clauses du falsifieur EXP-014 (hors pont : le pont ne
# confronte que le régime ; clauses (a) et (b) évaluées ici, consignées)
Rc = {o: resultats[f"p1_orb_{o}"]["Rc"] for o in ["5g", "5f", "5d", "5p", "5s"]}
echelle = ["5g", "5f", "5d", "5p", "5s"]
r1 = Rc["5f"] / Rc["5g"]
r2 = Rc["5d"] / Rc["5f"]
r3 = Rc["5p"] / Rc["5d"]
r4 = Rc["5s"] / Rc["5p"]
clause_a = all(Rc[echelle[i]] < Rc[echelle[i + 1]] for i in range(3)) \
    and Rc["5s"] >= 0.99 * Rc["5p"]
clause_b = 1.7 <= r1 <= 2.2 and 1.3 <= r2 <= 1.6
clause_c = all(resultats[f"p1_orb_{o}"]["regime"] == "Cosmologique"
               for o in echelle)
clauses = {"Rc": Rc, "r1_5f_sur_5g": r1, "r2_5d_sur_5f": r2,
           "r3_5p_sur_5d": r3, "r4_5s_sur_5p": r4,
           "clause_a_ordre": clause_a, "clause_b_echelle": clause_b,
           "clause_c_regime": clause_c,
           "EXP014_conforme_aux_trois_clauses": clause_a and clause_b and clause_c}
with open(os.path.join(BASE, "run", "evaluation_clauses.json"), "w", newline="") as f:
    f.write(json.dumps(clauses, ensure_ascii=False, indent=2) + "\n")
print("[C16] clauses :", json.dumps({k: v for k, v in clauses.items()
                                     if k != "Rc"}, ensure_ascii=False))

# manifeste complet
man = {}
for sub in ("protocole", "signaux", "signatures", "verdicts"):
    d = os.path.join(BASE, sub)
    for f in sorted(os.listdir(d)):
        rel = f"{sub}/{f}"
        man[rel] = hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest()
for f in ("c16_runner.py", "c16_analyse.py", "ash_core.py", "noetic_bridge.py",
          "expectations_v060.json", "evaluation_clauses.json"):
    man[f"run/{f}"] = hashlib.sha256(open(os.path.join(RUN, f), "rb").read()).hexdigest()
with open(os.path.join(RUN, "manifest.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C16] manifest.json : {len(man)} empreintes")
