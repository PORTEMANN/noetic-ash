#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C20 — pipeline comma noétique figé (attente EXP-018, protocole C20).
Identique à C19 (c19_comma.py) ; seules les clauses évaluées changent
(texte faisant foi : attente EXP-018, registre v1.0.0).

Comma noétique (Theorie_Residus §2.3 éq. 4) :
    Rdyn := inf_{T>0} ‖u(t+T) − u_mod(t+T)‖_{L²}

Clauses EXP-018 :
  (a1) existence : si t_eff ≥ 140, une bande contiguë ≥ 10 temps avec
       Z < −3 doit exister (sinon falsifiée ; si t_eff < 140 : HORS DOMAINE) ;
  (a2) échelle : si une bande significative existe (≥ 1 point Z < −3), son
       bord supérieur T_sup ∈ [0,32 ; 0,44]·t_eff ;
  (b) Lt sans bande significative ;
  (c) Rdyn ∈ [0,10 ; 0,30] (comma vs bi-exponentielle idéale, p0 figé).

Contrôles (statut H) : bruit blanc graine 43, sinus période 12 (validation
positive), permutation des sauts graine 11.
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

    zone : (t0, t1) bornes en temps de la zone active. Si None, la zone est
    calculée sur cette série : t ∈ [5 ; t_eff], t_eff = premier u ≤ 1 soutenu
    (10 pas). Le protocole C20 fige la zone par Nv et l'applique à Lt (même
    fenêtre temporelle) — d'où le passage explicite pour Lt.
    """
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
    # bord supérieur : dernier T avec Z < −3 (indépendant de la contiguïté)
    sous = np.where(z < -3.0)[0]
    T_sup = float(taus[sous[-1]] * dt_loc) if len(sous) else None
    res = {
        "etiquette": etiquette,
        "t_eff": float(t_eff),
        "n_zone": int(len(u)),
        "z_min": float(z.min()),
        "T_zmin": float(taus[int(np.argmin(z))] * dt_loc),
        "T_sup": T_sup,
        "n_significatifs": int(len(sous)),
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
    Nv = load_csv(os.path.join(SIG, "e44_nv_t_g2029.csv"))
    Lt = load_csv(os.path.join(SIG, "e44_lt_t_g2029.csv"))
    tN = np.arange(1, len(Nv)+1) * DT
    tL = np.arange(4, 4*len(Lt)+1, 4) * DT

    res_nv = analyse_comma(Nv, tN, 51, "e44_comma_noetique_g2029_Nv")
    # protocole C20 : la zone active est figée par Nv et appliquée à Lt
    zone_t = (5.0, res_nv["t_eff"])
    res_lt = analyse_comma(Lt, tL, 13, "e44_comma_noetique_g2029_Lt", zone=zone_t)
    rid = comma_vs_ideal(res_nv)

    # contrôles (statut H) : longueur complète (signaux synthétiques)
    rng43 = np.random.default_rng(np.random.SeedSequence(43))
    nz = res_nv["n_zone"]
    bruit = rng43.standard_normal(nz) * res_nv["r"].std()
    zone_ctrl = (tN[0], tN[nz-1])
    res_bruit = analyse_comma(bruit, tN[:nz], 51, "controle_bruit43", zone=zone_ctrl)
    per = 12.0
    sinus = np.sin(2*np.pi*np.arange(nz)*DT/per) * res_nv["r"].std()
    res_sin = analyse_comma(sinus, tN[:nz], 51, "controle_sinus12", zone=zone_ctrl)

    # clauses EXP-018 (texte faisant foi : attente, registre v1.0.0)
    t_eff = res_nv["t_eff"]
    # (a1) existence : si t_eff ≥ 140, une bande contiguë ≥ 10 doit exister
    if t_eff >= 140.0:
        clause_a1 = len(res_nv["bandes"]) > 0
        domaine_a1 = "applicable"
    else:
        clause_a1 = None
        domaine_a1 = "HORS-DOMAINE (t_eff < 140) — graine consignée"
    # (a2) échelle : si une bande significative existe, T_sup ∈ [0,32 ; 0,44]·t_eff
    if res_nv["T_sup"] is not None:
        ratio_sup = res_nv["T_sup"] / t_eff
        clause_a2 = 0.32 <= ratio_sup <= 0.44
    else:
        ratio_sup = None
        clause_a2 = None   # pas de bande du tout : (a2) sans objet, (a1) tranche
    # (b) Lt SANS bande significative
    clause_b = len(res_lt["bandes"]) == 0
    # (c) Rdyn ∈ [0,10 ; 0,30]
    clause_c = 0.10 <= rid["Rdyn"] <= 0.30

    clauses_applicables = [c for c in (clause_a1, clause_a2, clause_b, clause_c)
                           if c is not None]
    conforme = all(clauses_applicables)

    clauses = {
        "attente": "EXP-018",
        "graine": 2029,
        "t_eff": t_eff,
        "clause_a1_existence": {
            "domaine": domaine_a1,
            "resultat": clause_a1,
            "bandes_significatives": res_nv["bandes"],
            "z_min": res_nv["z_min"],
            "T_zmin": res_nv["T_zmin"],
        },
        "clause_a2_echelle": {
            "resultat": clause_a2,
            "T_sup": res_nv["T_sup"],
            "ratio_T_sup_sur_t_eff": ratio_sup,
            "bornes_ratio": [0.32, 0.44],
            "n_points_significatifs": res_nv["n_significatifs"],
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
        "EXP018_conforme_aux_clauses_applicables": conforme,
    }
    with open(os.path.join(RUN, "evaluation_clauses.json"), "w", newline="") as f:
        f.write(json.dumps(clauses, ensure_ascii=False, indent=2) + "\n")

    def profil(res):
        return {"t_eff": res["t_eff"], "n_zone": res["n_zone"],
                "z_min": res["z_min"], "T_zmin": res["T_zmin"],
                "T_sup": res["T_sup"], "n_significatifs": res["n_significatifs"],
                "bandes": res["bandes"],
                "T": (res["taus"] * (res["t"][1]-res["t"][0])).tolist(),
                "C": res["C"].tolist(), "Z": res["z"].tolist()}
    resultats = {"graine": 2029, "Nv": profil(res_nv), "Lt": profil(res_lt),
                 "comma_vs_ideal": rid}
    with open(os.path.join(RUN, "resultats_comma.json"), "w", newline="") as f:
        f.write(json.dumps(resultats, ensure_ascii=False, indent=2) + "\n")

    print(f"[C20] Nv : t_eff={t_eff:.1f}, bandes={res_nv['bandes']}, "
          f"Zmin={res_nv['z_min']:.2f} à T={res_nv['T_zmin']:.1f}, "
          f"T_sup={res_nv['T_sup']}, ratio={ratio_sup}")
    print(f"[C20] Lt : bandes={res_lt['bandes']}, Zmin={res_lt['z_min']:.2f}")
    print(f"[C20] Rdyn = {rid['Rdyn']:.4f} à T* = {rid['T_star']:.2f}")
    print(f"[C20] clauses : a1={clause_a1} ({domaine_a1}), a2={clause_a2}, "
          f"b={clause_b}, c={clause_c} "
          f"→ EXP-018 {'CONFORME' if conforme else 'FALSIFIÉE'}")

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
    print(f"[C20] manifest.json : {len(man)} empreintes")

if __name__ == "__main__":
    main()
