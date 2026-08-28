#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C25 — pipeline : le comma au lag caractéristique est un détecteur de
cohérence de phase (attente EXP-023, protocole C25). Chaîne figée :

  signal brut, fenêtre 2 s (échantillons 24000:48000), détrending
  Savitzky-Golay (fenêtre 501, ordre 3) ; autocorrélation du brut détrendu au
  lag T ; comma C(T) = ‖r(t+T)−r(t)‖/‖r‖, 40 surrogates graine 2019,
  Z = (C − μ)/σ.

Lags caractéristiques (documentés, 6205-2RS, ~1797 tr/min) : BPFI = 6,17 ms
(interne), BPFO = 9,31 ms (externe), BSF = 7,08 ms (bille).

Clauses EXP-023 : (a) mécanisme — sur un défaut, violation du signe (Z<0 avec
AC<0, ou Z≥0 avec AC>0) falsifie ; zone morte |AC|<0,05 → hors domaine ;
(b) spécificité — le sain (100) lit Z < 0 à un des trois lags falsifie.
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
DEFAUT = {169: "BPFI", 170: "BPFI", 185: "BSF", 186: "BSF", 197: "BPFO", 198: "BPFO"}
SAIN = [100]
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
    resultats = {}
    for n in SAIN + sorted(DEFAUT):
        r = detrend(load_csv(os.path.join(SIG, f"cwru_{n}.csv"))[WIN])
        zs = {lag: comma_au_lag(r, ms) for lag, ms in LAGS.items()}
        lag_def = DEFAUT.get(n)
        ac_def = ac_au_lag(r, LAGS[lag_def]) if lag_def else None
        resultats[str(n)] = {"Z": zs, "lag_defaut": lag_def,
                             "AC_au_lag_defaut": ac_def}
        role = "sain" if n in SAIN else f"défaut {lag_def}"
        print(f"[C25] cwru_{n} ({role:15s}) : Z BPFI={zs['BPFI']:+.2f} "
              f"BPFO={zs['BPFO']:+.2f} BSF={zs['BSF']:+.2f}"
              + (f"  AC@{lag_def}={ac_def:+.3f}" if ac_def is not None else ""), flush=True)

    # clause (a) : mécanisme — signe du déclenchement suit la cohérence
    detail_a = {}
    violations = []
    for n, lag in DEFAUT.items():
        ac = resultats[str(n)]["AC_au_lag_defaut"]
        z = resultats[str(n)]["Z"][lag]
        if abs(ac) < ZONE_MORTE:
            detail_a[str(n)] = {"AC": ac, "Z": z, "statut": "HORS-DOMAINE (|AC|<0,05)"}
        else:
            ok = (z < 0) == (ac > 0)
            detail_a[str(n)] = {"AC": ac, "Z": z, "statut": "tenu" if ok else "VIOLATION"}
            if not ok:
                violations.append(n)
    clause_a = len(violations) == 0
    # clause (b) : spécificité — le sain lit Z ≥ 0 aux trois lags
    detail_b = {str(n): all(resultats[str(n)]["Z"][lag] >= 0 for lag in LAGS) for n in SAIN}
    clause_b = all(detail_b.values())

    evaluation = {
        "attente": "EXP-023",
        "fichiers": SAIN + sorted(DEFAUT),
        "fenêtre_echantillons": [24000, 48000],
        "lags_ms": LAGS,
        "zone_morte_AC": ZONE_MORTE,
        "resultats": resultats,
        "clause_a_mecanisme": {"resultat": clause_a, "detail": detail_a,
                               "violations": violations,
                               "regle": "déclenchement (Z<0) ⟺ cohérence (AC>0) au lag du défaut"},
        "clause_b_specificite": {"resultat": clause_b, "detail": detail_b,
                                 "regle": "sain lit Z ≥ 0 aux trois lags"},
        "EXP023_conforme": clause_a and clause_b,
    }
    with open(os.path.join(RUN, "evaluation_clauses.json"), "w", newline="") as f:
        f.write(json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n")
    print(f"[C25] (a) mécanisme = {clause_a} (violations : {violations}) ; "
          f"(b) spécificité = {clause_b} → EXP-023 {'CONFORME' if clause_a and clause_b else 'FALSIFIÉE'}")

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
    print(f"[C25] manifest.json : {len(man)} empreintes")

if __name__ == "__main__":
    main()
