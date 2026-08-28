#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C26 — pipeline : spécificité du comma à seuil de magnitude + réplication
du mécanisme de cohérence de phase (attente EXP-024, protocole C26).
Chaîne figée :

  signal brut, fenêtre 2 s (échantillons 24000:48000), détrending
  Savitzky-Golay (fenêtre 501, ordre 3) ; comma C(T) = ‖r(t+T)−r(t)‖/‖r‖,
  40 surrogates graine 2019, Z = (C − μ)/σ ; autocorrélation du brut au lag
  du défaut (pour la clause b).

Lags documentés (6205-2RS, ~1797 tr/min) : BPFI = 6,17 ms, BPFO = 9,31 ms,
BSF = 7,08 ms.

Clauses EXP-024 : (a) spécificité à magnitude — un canal FE sain lit Z ≤ −3
à un des trois lags falsifie ; (b) réplication du mécanisme — sur un fichier
21 mil, violation du signe (Z<0 avec AC<0, ou Z≥0 avec AC>0) falsifie,
zone morte |AC|<0,05 hors domaine.
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
SAINS_FE = [97, 98, 99, 100]
DEFAUTS_21 = {209: "BPFI", 210: "BPFI", 222: "BSF", 223: "BSF",
              234: "BPFO", 235: "BPFO"}
SEUIL_MAGNITUDE = -3.0
ZONE_MORTE = 0.05

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

def detrend(u):
    return u - savgol_filter(u, 501, 3)

def comma_au_lag(r, T_ms):
    k = max(1, int(T_ms/1000*FS))
    C_obs = np.sqrt(np.mean((r[:-k]-r[k:])**2)/np.mean(r**2))
    rng = np.random.default_rng(np.random.SeedSequence(2019))
    Cs = np.array([np.sqrt(np.mean((surrogate(r, rng)[:-k]-surrogate(r, rng)[k:])**2)/np.mean(r**2))
                   for _ in range(40)])
    return float((C_obs - Cs.mean())/max(Cs.std(), 1e-12))

def ac_au_lag(r, T_ms):
    k = max(1, int(T_ms/1000*FS))
    return float(np.corrcoef(r[:-k], r[k:])[0, 1])

def main():
    # (a) spécificité à magnitude : sains FE
    detail_a = {}
    fausse_alarme = []
    for n in SAINS_FE:
        r = detrend(load_csv(os.path.join(SIG, f"cwru_{n}_FE.csv"))[WIN])
        zs = {lag: comma_au_lag(r, ms) for lag, ms in LAGS.items()}
        detail_a[str(n)] = zs
        alarme = any(zs[lag] <= SEUIL_MAGNITUDE for lag in LAGS)
        if alarme:
            fausse_alarme.append(n)
        print(f"[C26] cwru_{n}_FE (sain) : BPFI={zs['BPFI']:+.2f} "
              f"BPFO={zs['BPFO']:+.2f} BSF={zs['BSF']:+.2f} "
              f"{'← FAUSSE ALARME' if alarme else ''}", flush=True)
    clause_a = len(fausse_alarme) == 0

    # (b) réplication du mécanisme : famille 21 mil
    detail_b = {}
    violations = []
    for n, lag in DEFAUTS_21.items():
        r = detrend(load_csv(os.path.join(SIG, f"cwru_{n}_DE.csv"))[WIN])
        z = comma_au_lag(r, LAGS[lag])
        ac = ac_au_lag(r, LAGS[lag])
        if abs(ac) < ZONE_MORTE:
            detail_b[str(n)] = {"AC": ac, "Z": z, "statut": "HORS-DOMAINE (|AC|<0,05)"}
        else:
            ok = (z < 0) == (ac > 0)
            detail_b[str(n)] = {"AC": ac, "Z": z, "statut": "tenu" if ok else "VIOLATION"}
            if not ok:
                violations.append(n)
        print(f"[C26] cwru_{n}_DE (défaut {lag}) : AC={ac:+.3f} Z={z:+.2f} "
              f"{detail_b[str(n)]['statut']}", flush=True)
    clause_b = len(violations) == 0

    evaluation = {
        "attente": "EXP-024",
        "fenêtre_echantillons": [24000, 48000],
        "lags_ms": LAGS,
        "seuil_magnitude": SEUIL_MAGNITUDE,
        "zone_morte_AC": ZONE_MORTE,
        "clause_a_specificite_magnitude": {
            "resultat": clause_a, "detail": detail_a,
            "fausses_alarmes": fausse_alarme,
            "regle": "sain FE ne lit jamais Z ≤ −3 à un lag"},
        "clause_b_replication_mecanisme": {
            "resultat": clause_b, "detail": detail_b, "violations": violations,
            "regle": "21 mil : déclenchement (Z<0) ⟺ cohérence (AC>0) au lag du défaut"},
        "EXP024_conforme": clause_a and clause_b,
    }
    with open(os.path.join(RUN, "evaluation_clauses.json"), "w", newline="") as f:
        f.write(json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n")
    print(f"[C26] (a) spécificité magnitude = {clause_a} (fausses alarmes : {fausse_alarme}) ; "
          f"(b) réplication mécanisme = {clause_b} (violations : {violations}) → "
          f"EXP-024 {'CONFORME' if clause_a and clause_b else 'FALSIFIÉE'}")

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
    print(f"[C26] manifest.json : {len(man)} empreintes")

if __name__ == "__main__":
    main()
