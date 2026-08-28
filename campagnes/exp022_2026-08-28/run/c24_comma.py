#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C24 — pipeline comma au lag caractéristique (attente EXP-022, protocole
C24). Chaîne figée :

  signal brut, fenêtre 2 s (échantillons 24000:48000), détrending
  Savitzky-Golay (fenêtre 501, ordre 3), comma C(T) = ‖r(t+T)−r(t)‖/‖r‖ au
  lag caractéristique, 40 surrogates à phases randomisées graine 2019,
  Z = (C − μ_surr)/σ_surr.

Lags caractéristiques (documentés, roulement 6205-2RS JEM SKF, ~1797 tr/min) :
  BPFI = 6,17 ms (162 Hz, interne), BPFO = 9,31 ms (107 Hz, externe),
  BSF = 7,08 ms (141 Hz, bille).

Clauses EXP-022 : (a) séparation — un défectueux lit Z ≥ 0 au lag de son
défaut (106→BPFI, 118/119→BSF, 130/131→BPFO) falsifie ; (b) spécificité —
un sain (98, 99) lit Z < 0 à un des trois lags falsifie.
"""

import hashlib
import json
import os

import numpy as np
from scipy.signal import savgol_filter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.dirname(os.path.abspath(__file__))
SIG = os.path.join(BASE, "signaux")

FS = 12000
WIN = slice(24000, 48000)  # 2 s
LAGS = {"BPFI": 6.17, "BPFO": 9.31, "BSF": 7.08}  # ms
DEFAUT = {106: "BPFI", 118: "BSF", 119: "BSF", 130: "BPFO", 131: "BPFO"}
SAIN = [98, 99]

def load_csv(p):
    vals = []
    with open(p) as f:
        next(f)
        for ln in f:
            vals.append(float(ln.split(",")[1]))
    return np.array(vals)

def surrogate(u, rng):
    F = np.fft.rfft(u)
    ph = rng.uniform(0, 2*np.pi, len(F))
    F2 = np.abs(F) * np.exp(1j*ph)
    F2[0] = F[0].real
    return np.fft.irfft(F2, len(u))

def comma_au_lag(u, T_ms):
    r = u - savgol_filter(u, 501, 3)
    k = max(1, int(T_ms/1000*FS))
    C_obs = np.sqrt(np.mean((r[:-k]-r[k:])**2)/np.mean(r**2))
    rng = np.random.default_rng(np.random.SeedSequence(2019))
    Cs = np.array([np.sqrt(np.mean((surrogate(r, rng)[:-k]-surrogate(r, rng)[k:])**2)/np.mean(r**2))
                   for _ in range(40)])
    return float((C_obs - Cs.mean())/max(Cs.std(), 1e-12))

def main():
    resultats = {}
    for n in SAIN + sorted(DEFAUT):
        x = load_csv(os.path.join(SIG, f"cwru_{n}.csv"))[WIN]
        zs = {lag: comma_au_lag(x, ms) for lag, ms in LAGS.items()}
        resultats[str(n)] = zs
        role = "sain" if n in SAIN else f"défaut {DEFAUT[n]}"
        print(f"[C24] cwru_{n} ({role:18s}) : BPFI={zs['BPFI']:+.2f} "
              f"BPFO={zs['BPFO']:+.2f} BSF={zs['BSF']:+.2f}", flush=True)

    # clauses EXP-022
    # (a) séparation : chaque défaut doit lire Z < 0 à SON lag
    sep = {}
    for n, lag in DEFAUT.items():
        sep[str(n)] = resultats[str(n)][lag] < 0
    clause_a = all(sep.values())
    # (b) spécificité : chaque sain doit lire Z ≥ 0 aux trois lags
    spec = {}
    for n in SAIN:
        spec[str(n)] = all(resultats[str(n)][lag] >= 0 for lag in LAGS)
    clause_b = all(spec.values())

    evaluation = {
        "attente": "EXP-022",
        "fichiers": SAIN + sorted(DEFAUT),
        "fenêtre_echantillons": [24000, 48000],
        "lags_ms": LAGS,
        "resultats_Z": resultats,
        "clause_a_separation": {"resultat": clause_a, "detail": sep,
                                "regle": "défaut lit Z < 0 au lag de son défaut"},
        "clause_b_specificite": {"resultat": clause_b, "detail": spec,
                                 "regle": "sain lit Z ≥ 0 aux trois lags"},
        "EXP022_conforme": clause_a and clause_b,
    }
    with open(os.path.join(RUN, "evaluation_clauses.json"), "w", newline="") as f:
        f.write(json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n")
    print(f"[C24] (a) séparation = {clause_a} ; (b) spécificité = {clause_b} "
          f"→ EXP-022 {'CONFORME' if clause_a and clause_b else 'FALSIFIÉE'}")

    man = {}
    for sub in ("protocole", "signaux"):
        d = os.path.join(BASE, sub)
        for f in sorted(os.listdir(d)):
            man[f"{sub}/{f}"] = hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest()
    for f in sorted(os.listdir(RUN)):
        if f.endswith((".py", ".json", ".md")) and f != "manifest.json":
            man[f"run/{f}"] = hashlib.sha256(open(os.path.join(RUN, f), "rb").read()).hexdigest()
    with open(os.path.join(RUN, "manifest.json"), "w", newline="") as f:
        f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(f"[C24] manifest.json : {len(man)} empreintes")

if __name__ == "__main__":
    main()
