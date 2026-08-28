#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C21 — pipeline comma noétique figé (attente EXP-019, protocole C21).
Identique à C19/C20 ; clauses remplacées par le texte d'EXP-019
(registre v1.1.0). Définitions figées (protocole C21) :

  ÉPISODE    : segment contigu de Lt > 0 (échantillonnage 0,4 temps)
  TROU       : durée Lt = 0 soutenue entre deux épisodes
  RÉSURGENCE : max des trous ≥ 60 temps ET ≥ 3 épisodes après ce trou
  BANDE      : intervalle contigu ≥ 10 temps où Z(T) < −3 (auto-comma du
               résidu SG-13, 60 surrogates graine 2019)

Clauses EXP-019 (par graine, les deux graines doivent passer) :
  (a) biconditionnelle : BANDE résidu Lt ⟺ RÉSURGENCE de Lt ;
  (b) robustesse : le résidu de Nv présente au moins un point Z < −3 ;
  (c) Rdyn (comma vs bi-exponentielle idéale, p0 figé) ∈ [0,10 ; 0,30].

Contrôle (statut H) : la série binaire d'activité (timing seul) doit
reproduire la bande Lt à |ΔZ_min| < 3 (le timing suffit — calibration).
"""

import hashlib
import json
import os

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.dirname(os.path.abspath(__file__))
SIG = os.path.join(BASE, "signaux")

DT = 0.1
DTL = 0.4

def load_csv(p):
    vals = []
    with open(p) as f:
        next(f)
        for ln in f:
            vals.append(float(ln.split(",")[1]))
    return np.array(vals)

def comma_profil(u, taus):
    n = len(u)
    out = np.empty(len(taus))
    ru2 = np.mean(u**2)
    for i, k in enumerate(taus):
        d = u[:n-k] - u[k:]
        out[i] = np.sqrt(np.mean(d**2) / ru2) if ru2 > 0 else 0.0
    return out

def surrogate(u, rng):
    F = np.fft.rfft(u)
    ph = rng.uniform(0, 2*np.pi, len(F))
    F2 = np.abs(F) * np.exp(1j*ph)
    F2[0] = F[0].real
    return np.fft.irfft(F2, len(u))

def bandes_significatives(z, dt, largeur_min=10.0, seuil=-3.0):
    idx = np.where(z < seuil)[0]
    if len(idx) == 0:
        return []
    bandes = []
    debut = idx[0]
    prev = idx[0]
    for i in idx[1:]:
        if i != prev + 1:
            if (prev - debut + 1) * dt >= largeur_min:
                bandes.append((debut, prev))
            debut = i
        prev = i
    if (prev - debut + 1) * dt >= largeur_min:
        bandes.append((debut, prev))
    return bandes

def analyse_comma(u_brut, t_brut, win_sg, etiquette, zone=None):
    if zone is None:
        i0 = int(5.0 / (t_brut[1] - t_brut[0]))
        soutenu = np.where(np.convolve((u_brut <= 1).astype(int), np.ones(10, dtype=int), 'valid') == 10)[0]
        i1 = (soutenu[0] + 1) if len(soutenu) else len(u_brut)
        i1 = min(i1, len(u_brut))
    else:
        t0, t1 = zone
        i0 = int(np.searchsorted(t_brut, t0))
        i1 = min(int(np.searchsorted(t_brut, t1)), len(u_brut))
    t = t_brut[i0:i1]
    u = u_brut[i0:i1].astype(float)
    t_eff = t[-1]
    fit = savgol_filter(u, win_sg, 3)
    r = u - fit
    taus = np.arange(1, len(u) // 2)
    C = comma_profil(r, taus)
    rng = np.random.default_rng(np.random.SeedSequence(2019))
    S = np.array([comma_profil(surrogate(r, rng), taus) for _ in range(60)])
    mu, sd = S.mean(0), S.std(0)
    z = (C - mu) / np.maximum(sd, 1e-12)
    dt_loc = t[1] - t[0]
    bandes = bandes_significatives(z, dt_loc)
    sous = np.where(z < -3.0)[0]
    res = {
        "etiquette": etiquette,
        "t_eff": float(t_eff),
        "n_zone": int(len(u)),
        "z_min": float(z.min()),
        "T_zmin": float(taus[int(np.argmin(z))] * dt_loc),
        "n_significatifs": int(len(sous)),
        "bandes": [[float(taus[b[0]] * dt_loc), float(taus[b[1]] * dt_loc)] for b in bandes],
        "C": C, "z": z, "taus": taus, "t": t, "u": u, "r": r,
    }
    return res

def resurgence(Lt, te, dt=DTL, trou_seuil=60.0, rep_seuil=3):
    """Définition figée : trou inter-épisodes ≥ 60 temps ET ≥ 3 épisodes après."""
    i0, i1 = int(5.0 / dt), int(te / dt)
    u = Lt[i0:i1].astype(float)
    act = u > 0
    seg = np.diff(np.concatenate([[0], act.astype(int), [0]]))
    starts = np.where(seg == 1)[0]
    ends = np.where(seg == -1)[0]
    if len(starts) < 2:
        return {"resurgence": False, "trou_max": 0.0, "reprise": 0,
                "n_episodes": int(len(starts))}
    trous = (starts[1:] - ends[:-1]) * dt
    i_max = int(np.argmax(trous))
    trou_max = float(trous[i_max])
    reprise = int(len(starts) - (i_max + 1))
    return {"resurgence": bool(trou_max >= trou_seuil and reprise >= rep_seuil),
            "trou_max": trou_max, "reprise": reprise,
            "n_episodes": int(len(starts))}

def biexpo(t, a1, t1, a2, t2, c):
    return a1*np.exp(-t/t1) + a2*np.exp(-t/t2) + c

def comma_vs_ideal(res):
    t, u = res["t"], res["u"]
    tt = t - t[0]
    p, _ = curve_fit(biexpo, tt, u, p0=[1500, 8, 400, 100, 50], maxfev=50000)
    umod = biexpo(tt, *p)
    taus = np.arange(1, len(u) // 2)
    n = len(u)
    out = np.empty(len(taus))
    ru2 = np.mean(u**2)
    for i, k in enumerate(taus):
        out[i] = np.sqrt(np.mean((u[:n-k] - umod[k:])**2) / ru2)
    ib = int(np.argmin(out))
    return {"Rdyn": float(out[ib]), "T_star": float(taus[ib] * (t[1]-t[0])),
            "params_biexpo": [float(x) for x in p]}

def main():
    toutes = {}
    for g in (2031, 2032):
        Nv = load_csv(os.path.join(SIG, f"e44_nv_t_g{g}.csv"))
        Lt = load_csv(os.path.join(SIG, f"e44_lt_t_g{g}.csv"))
        tN = np.arange(1, len(Nv)+1) * DT
        tL = np.arange(4, 4*len(Lt)+1, 4) * DT

        res_nv = analyse_comma(Nv, tN, 51, f"e44_comma_resurgence_g{g}_Nv")
        zone_t = (5.0, res_nv["t_eff"])
        res_lt = analyse_comma(Lt, tL, 13, f"e44_comma_resurgence_g{g}_Lt", zone=zone_t)
        rid = comma_vs_ideal(res_nv)
        resu = resurgence(Lt, res_nv["t_eff"])

        # contrôle : la série binaire (timing seul) reproduit la bande Lt
        i0, i1 = int(5.0/DTL), int(res_nv["t_eff"]/DTL)
        binaire = (Lt[i0:i1] > 0).astype(float)
        res_bin = analyse_comma(binaire, tL[:len(binaire)], 13,
                                f"controle_binaire_g{g}",
                                zone=(5.0, res_nv["t_eff"]))
        dZ = abs(res_bin["z_min"] - res_lt["z_min"])
        ctrl_bin = dZ < 3.0 if res_lt["bandes"] else True

        # clauses EXP-019
        bande_lt = len(res_lt["bandes"]) > 0
        clause_a = bande_lt == resu["resurgence"]           # biconditionnelle
        clause_b = res_nv["n_significatifs"] > 0            # Nv significatif
        clause_c = 0.10 <= rid["Rdyn"] <= 0.30              # Rdyn borné

        toutes[str(g)] = {
            "t_eff": res_nv["t_eff"],
            "resurgence": resu,
            "bande_Lt": bande_lt,
            "bandes_Lt": res_lt["bandes"],
            "z_min_Lt": res_lt["z_min"],
            "z_min_Nv": res_nv["z_min"],
            "n_significatifs_Nv": res_nv["n_significatifs"],
            "Rdyn": rid["Rdyn"],
            "controle_binaire": {"z_min": res_bin["z_min"], "delta_Z": dZ,
                                 "reproduit": ctrl_bin},
            "clause_a_biconditionnelle": clause_a,
            "clause_b_Nv_significatif": clause_b,
            "clause_c_Rdyn_borne": clause_c,
        }
        print(f"[C21] graine {g} : t_eff={res_nv['t_eff']:.1f}, "
              f"résurgence={resu['resurgence']} (trou={resu['trou_max']:.1f}, "
              f"reprise={resu['reprise']}), bande Lt={bande_lt} "
              f"(Z={res_lt['z_min']:.2f}), Nv Zmin={res_nv['z_min']:.2f}, "
              f"Rdyn={rid['Rdyn']:.4f}, binaire ΔZ={dZ:.2f}")
        print(f"[C21]   clauses : a={clause_a} b={clause_b} c={clause_c}")

    conforme = all(toutes[g]["clause_a_biconditionnelle"]
                   and toutes[g]["clause_b_Nv_significatif"]
                   and toutes[g]["clause_c_Rdyn_borne"] for g in toutes)
    evaluation = {
        "attente": "EXP-019",
        "graines": [2031, 2032],
        "par_graine": toutes,
        "EXP019_conforme_sur_les_deux_graines": conforme,
    }
    with open(os.path.join(RUN, "evaluation_clauses.json"), "w", newline="") as f:
        f.write(json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n")
    print(f"[C20] EXP-019 {'CONFORME sur les deux graines' if conforme else 'FALSIFIÉE'}")

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
    print(f"[C21] manifest.json : {len(man)} empreintes")

if __name__ == "__main__":
    main()
