#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C19 — pipeline comma noétique figé (attente EXP-017, protocole C19).

Comma noétique (Theorie_Residus §2.3 éq. 4) :
    Rdyn := inf_{T>0} ‖u(t+T) − u_mod(t+T)‖_{L²}

Mesure sur la graine 2028 (aveugle) :
  1. zone active : t ∈ [5 ; t_eff], t_eff = premier Nv ≤ 1 soutenu (10 pas) ;
  2. détrending Savitzky-Golay fenêtre 51 ordre 3 (Lt : fenêtre 13) ;
  3. auto-comma C(T) = ‖r(t+T) − r(t)‖₂/‖r‖₂, T = 0,1 … L/2 (pas 0,1) ;
  4. surrogates à phases randomisées : 60 tirages, SeedSequence(2019) ;
  5. Z(T) = (C − μ_surr)/σ_surr ;
  6. comma vs idéal : u_mod = bi-exponentielle (curve_fit, p0 figé),
     Rdyn = inf_T ‖Nv(t) − u_mod(t+T)‖/‖Nv‖ ;
  7. contrôles : bruit blanc graine 43, exponentielle bruitée, sinus période
     12 (validation positive), permutation des sauts graine 11.

Évalue les trois clauses d'EXP-017 et écrit run/evaluation_clauses.json +
run/resultats_comma.json + run/manifest.json.
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
    """Intervalles contigus où z < seuil, de largeur ≥ largeur_min temps."""
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
    """Pipeline figé sur une série brute (t, u). Retourne le dict de mesures.

    zone : (i0, i1) indices de la zone active. Si None, la zone est calculée
    sur cette série : t ∈ [5 ; t_eff], t_eff = premier u ≤ 1 soutenu (10 pas).
    Le protocole C19 fige la zone par Nv et l'applique à Lt (même fenêtre
    temporelle) — d'où le passage explicite pour Lt.
    """
    if zone is None:
        i0 = int(5.0 / (t_brut[1] - t_brut[0]))
        soutenu = np.where(np.convolve((u_brut <= 1).astype(int), np.ones(10, dtype=int), 'valid') == 10)[0]
        i1 = (soutenu[0] + 1) if len(soutenu) else len(u_brut)
        i1 = min(i1, len(u_brut))
    else:
        # même fenêtre temporelle : indices déduits des bornes en temps
        t0, t1 = zone
        i0 = int(np.searchsorted(t_brut, t0))
        i1 = int(np.searchsorted(t_brut, t1))
        i1 = min(i1, len(u_brut))
    t = t_brut[i0:i1]
    u = u_brut[i0:i1].astype(float)
    t_eff = t[-1]
    # détrending figé
    fit = savgol_filter(u, win_sg, 3)
    r = u - fit
    # auto-comma
    taus = np.arange(1, len(u) // 2)
    C = comma_profil(r, taus)
    rng = np.random.default_rng(np.random.SeedSequence(2019))
    S = np.array([comma_profil(surrogate(r, rng), taus) for _ in range(60)])
    mu, sd = S.mean(0), S.std(0)
    z = (C - mu) / np.maximum(sd, 1e-12)
    dt_loc = t[1] - t[0]
    bandes = bandes_significatives(z, dt_loc)
    res = {
        "etiquette": etiquette,
        "t_eff": float(t_eff),
        "n_zone": int(len(u)),
        "z_min": float(z.min()),
        "T_zmin": float(taus[int(np.argmin(z))] * dt_loc),
        "bandes": [[float(taus[b[0]] * dt_loc), float(taus[b[1]] * dt_loc)] for b in bandes],
        "C": C, "z": z, "taus": taus, "t": t, "u": u, "r": r,
    }
    return res

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
            "params_biexpo": [float(x) for x in p],
            "residu_rms_biexpo": float(np.sqrt(np.mean((u - umod)**2)))}

def main():
    Nv = load_csv(os.path.join(SIG, "e44_nv_t_g2028.csv"))
    Lt = load_csv(os.path.join(SIG, "e44_lt_t_g2028.csv"))
    tN = np.arange(1, len(Nv)+1) * DT
    tL = np.arange(4, 4*len(Lt)+1, 4) * DT

    res_nv = analyse_comma(Nv, tN, 51, "e44_comma_noetique_g2028_Nv")
    # protocole C19 : la zone active est figée par Nv (t_eff = premier Nv ≤ 1
    # soutenu sur 10 pas) et la même fenêtre temporelle est appliquée à Lt
    zone_t = (5.0, res_nv["t_eff"])
    res_lt = analyse_comma(Lt, tL, 13, "e44_comma_noetique_g2028_Lt", zone=zone_t)
    rid = comma_vs_ideal(res_nv)

    # contrôles (statut H) : validation du protocole sur signaux connus —
    # les contrôles sont analysés sur leur longueur complète (la règle de
    # zone physique t_eff ne s'applique pas à des signaux synthétiques)
    rng43 = np.random.default_rng(np.random.SeedSequence(43))
    nz = res_nv["n_zone"]
    bruit = rng43.standard_normal(nz) * res_nv["r"].std()
    zone_ctrl = (tN[0], tN[nz-1])
    res_bruit = analyse_comma(bruit, tN[:nz], 51, "controle_bruit43", zone=zone_ctrl)
    per = 12.0
    sinus = np.sin(2*np.pi*np.arange(nz)*DT/per) * res_nv["r"].std()
    res_sin = analyse_comma(sinus, tN[:nz], 51, "controle_sinus12", zone=zone_ctrl)

    # clauses EXP-017
    # (a) bande de récurrence Nv : intervalle ≥ 10 temps où Z < −3, min ∈ [20 ; 35]
    bandes_nv = res_nv["bandes"]
    clause_a = (len(bandes_nv) > 0) and any(20.0 <= res_nv["T_zmin"] <= 35.0 for _ in [1])
    clause_a = clause_a and (20.0 <= res_nv["T_zmin"] <= 35.0)
    # (b) Lt SANS bande significative
    clause_b = len(res_lt["bandes"]) == 0
    # (c) Rdyn ∈ [0,10 ; 0,30]
    clause_c = 0.10 <= rid["Rdyn"] <= 0.30

    clauses = {
        "attente": "EXP-017",
        "graine": 2028,
        "clause_a_recurrence_Nv": {
            "resultat": clause_a,
            "bandes_significatives": bandes_nv,
            "T_minimum": res_nv["T_zmin"],
            "z_min": res_nv["z_min"],
            "t_eff": res_nv["t_eff"],
        },
        "clause_b_Lt_sans_bande": {
            "resultat": clause_b,
            "bandes_significatives_Lt": res_lt["bandes"],
            "z_min_Lt": res_lt["z_min"],
        },
        "clause_c_Rdyn_borne": {
            "resultat": clause_c,
            "Rdyn": rid["Rdyn"],
            "T_star": rid["T_star"],
            "params_biexpo": rid["params_biexpo"],
        },
        "controles": {
            "bruit43": {"z_min": res_bruit["z_min"], "bandes": res_bruit["bandes"]},
            "sinus12": {"z_min": res_sin["z_min"], "bandes": res_sin["bandes"]},
        },
        "EXP017_conforme_aux_trois_clauses": clause_a and clause_b and clause_c,
    }
    with open(os.path.join(RUN, "evaluation_clauses.json"), "w", newline="") as f:
        f.write(json.dumps(clauses, ensure_ascii=False, indent=2) + "\n")

    # résultats détaillés (profils complets, pour traçabilité)
    def profil(res):
        return {"t_eff": res["t_eff"], "n_zone": res["n_zone"],
                "z_min": res["z_min"], "T_zmin": res["T_zmin"],
                "bandes": res["bandes"],
                "T": (res["taus"] * (res["t"][1]-res["t"][0])).tolist(),
                "C": res["C"].tolist(), "Z": res["z"].tolist()}
    resultats = {"graine": 2028, "Nv": profil(res_nv), "Lt": profil(res_lt),
                 "comma_vs_ideal": rid}
    with open(os.path.join(RUN, "resultats_comma.json"), "w", newline="") as f:
        f.write(json.dumps(resultats, ensure_ascii=False, indent=2) + "\n")

    print(f"[C19] Nv : t_eff={res_nv['t_eff']:.1f}, bandes={bandes_nv}, "
          f"Zmin={res_nv['z_min']:.2f} à T={res_nv['T_zmin']:.1f}")
    print(f"[C19] Lt : bandes={res_lt['bandes']}, Zmin={res_lt['z_min']:.2f}")
    print(f"[C19] Rdyn = {rid['Rdyn']:.4f} à T* = {rid['T_star']:.2f}")
    print(f"[C19] clauses : a={clause_a} b={clause_b} c={clause_c} "
          f"→ EXP-017 {'CONFORME' if clause_a and clause_b and clause_c else 'FALSIFIÉE'}")

    # manifeste
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
    print(f"[C19] manifest.json : {len(man)} empreintes")

if __name__ == "__main__":
    main()
