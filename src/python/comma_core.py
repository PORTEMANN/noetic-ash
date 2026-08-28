#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comma_core.py — Le comma noétique : extension temporelle de l'instrument ASH.

noetic-ash, couche extension de l'écosystème Noetic Physics.
Auteur : Patrice Portemann
Licence : MIT
Version : 1.0.0 (figée)

Le comma noétique est l'analogue continu du comma pythagoricien — le défaut de
fermeture d'un cycle (Theorie_Residus §2.3, éq. 4) :

    Rdyn := inf_{T>0} ‖u(t+T) − u_mod(t+T)‖_{L²}

L'ASH (v1.0.0, figé) mesure le contenu spectral (raies) sur la grille tempérée
2^(1/12) ; son Rdyn propre est bloqué au fallback 1.0 sur les signaux
mono-bosse (campagne C15) — il est aveugle au *timing* des événements. Le
comma_core comble cette lacune : il mesure la récurrence temporelle — le
*calendrier* des événements — et la cohérence de phase.

Méthode figée (validée par les campagnes exp017–exp021, voir campagnes/) :
  1. détrending Savitzky–Golay (résidu r) ;
  2. auto-comma C(T) = ‖r(t+T) − r(t)‖₂ / ‖r‖₂ ;
  3. surrogates à phases randomisées (spectre préservé, timing détruit) —
     modèle nul : le comma d'UN MÊME surrogate décalé (verrouillé après la
     correction de l'addendum A1 : jamais deux surrogates indépendants) ;
  4. Z(T) = (C − μ_surr) / σ_surr : une bande Z < −3 signe une récurrence qui
     n'est PAS dans le spectre de puissance mais dans l'ordonnancement ;
  5. comma au lag T₀ : récurrence à une période caractéristique connue —
     observable expérimentale NON validée au null corrigé (voir ci-dessous).

INTÉGRITÉ : les campagnes au lag caractéristique (exp022/023/024) utilisaient
un modèle nul buggé (double surrogate) qui exagérait la significativité ; elles
ont été corrigées (addenda A1) et leurs conclusions CWRU ne tiennent pas au
null corrigé. Ce qui est validé (null correct dès l'origine) : le détecteur de
résurgence sur dynamique à événements (E44, exp017–021) et le comma contre
dynamique idéale (Rdyn, stable sur 13 graines). Le détecteur de cohérence de
phase sur capteur (CWRU) est conservé comme observable à recalibrer.

Chaque détecteur retourne un verdict xAI structuré : la réponse (oui/non),
le temps de la récurrence, la magnitude, et une justification lisible en trois
lignes. Rien n'est appris ; tout est figé, falsifiable et reproductible.

Dépendances : numpy, scipy (comme ash_core).
"""

from typing import Dict, Optional

import numpy as np
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit

__version__ = "1.0.0"

# Paramètres figés par les campagnes (C19–C26) — jamais ajustés sur données
N_SURR = 60                  # surrogates (bande de récurrence)
N_SURR_LAG = 40              # surrogates (comma au lag)
SEED_SURR = 2019             # graine des surrogates
SEUIL_Z = -3.0               # seuil de significativité de la bande
LARGEUR_BANDE_MIN = 10.0     # largeur minimale d'une bande (unités de temps)
SEUIL_MAGNITUDE = -3.0       # seuil de magnitude (spécificité, EXP-024)
ZONE_MORTE_AC = 0.05         # zone morte du signe d'autocorrélation


# --------------------------------------------------------------------------- #
# Primitives figées                                                            #
# --------------------------------------------------------------------------- #

def detrend_sg(u: np.ndarray, win: int, order: int = 3) -> np.ndarray:
    """Résidu r = u − Savitzky–Golay(u, win, order). Fenêtre figée par domaine."""
    return u - savgol_filter(u, win, order)


def comma_profil(r: np.ndarray, taus: np.ndarray) -> np.ndarray:
    """Auto-comma : C(T) = ‖r(t+T) − r(t)‖₂ / ‖r‖₂ pour chaque lag T ∈ taus."""
    n = len(r)
    out = np.empty(len(taus))
    ru2 = np.mean(r**2)
    for i, k in enumerate(taus):
        k = int(k)
        if k <= 0 or k >= n:
            out[i] = np.nan
            continue
        d = r[:n - k] - r[k:]
        out[i] = np.sqrt(np.mean(d**2) / ru2) if ru2 > 0 else 0.0
    return out


def surrogate(r: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Surrogate à phases randomisées : spectre de puissance préservé, timing
    détruit. C'est le modèle nul — une bande significative contre lui signe une
    récurrence du *calendrier*, pas du spectre."""
    F = np.fft.rfft(r)
    ph = rng.uniform(0, 2 * np.pi, len(F))
    F2 = np.abs(F) * np.exp(1j * ph)
    F2[0] = F[0].real
    return np.fft.irfft(F2, len(r))


def z_scores(C: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Z = (C − μ_surr) / σ_surr, colonne par colonne (S : n_surr × n_tau)."""
    mu, sd = S.mean(0), S.std(0)
    return (C - mu) / np.maximum(sd, 1e-12)


def comma_z_profil(r: np.ndarray, taus: np.ndarray,
                   n_surr: int = N_SURR, seed: int = SEED_SURR) -> Dict:
    """Profil d'auto-comma + Z-score contre surrogates. Retourne C, Z, taus."""
    C = comma_profil(r, taus)
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    S = np.array([comma_profil(surrogate(r, rng), taus) for _ in range(n_surr)])
    z = z_scores(C, S)
    return {"C": C, "Z": z, "taus": taus}


def bande_recurrence(z: np.ndarray, dt: float,
                     largeur_min: float = LARGEUR_BANDE_MIN,
                     seuil: float = SEUIL_Z) -> Dict:
    """Bandes contiguës de largeur ≥ largeur_min où Z < seuil.

    Une bande signe une récurrence du calendrier des événements (pas du
    spectre) : la série a une mémoire temporelle.
    """
    idx = np.where(z < seuil)[0]
    i_min = int(np.argmin(z))
    # taus = arange(1, n//2) dans comma_z_profil : T à l'indice i = (i+1)·dt
    T_zmin = float((i_min + 1) * dt)
    if len(idx) == 0:
        return {"presente": False, "bandes": [], "z_min": float(z.min()),
                "T_zmin": T_zmin}
    bandes = []
    debut = idx[0]
    prev = idx[0]
    for i in idx[1:]:
        if i != prev + 1:
            if (prev - debut + 1) * dt >= largeur_min:
                bandes.append((float((debut + 1) * dt), float((prev + 1) * dt)))
            debut = i
        prev = i
    if (prev - debut + 1) * dt >= largeur_min:
        bandes.append((float((debut + 1) * dt), float((prev + 1) * dt)))
    return {"presente": len(bandes) > 0, "bandes": bandes,
            "z_min": float(z.min()), "T_zmin": T_zmin}


def comma_au_lag(r: np.ndarray, T_ms: float, fs: float,
                 n_surr: int = N_SURR_LAG, seed: int = SEED_SURR) -> Dict:
    """Comma à un lag caractéristique T₀ (capteur identifié), modèle nul
    CORRIGÉ : le comma d'un même surrogate décalé (un seul surrogate par
    tirage ; la norme du surrogate égale ‖r‖ par Parseval).

    NOTE D'INTÉGRITÉ (addendum A1 des campagnes exp022/023/024) : la chaîne
    publiée initialement appelait surrogate() deux fois par tirage (différence
    de deux surrogates indépendants), ce qui gonflait le modèle nul et
    exagérait |Z|. Au null corrigé — celui-ci —, le détecteur au lag
    caractéristique n'a PAS été validé sur le corpus CWRU : la séparation et
    la spécificité revendiquées ne tiennent pas (voir les addenda A1). Cette
    fonction est conservée comme observable, sans prétention validée."""
    k = max(1, int(T_ms / 1000.0 * fs))
    C_obs = np.sqrt(np.mean((r[:-k] - r[k:])**2) / np.mean(r**2))
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    Cs = np.empty(n_surr)
    for i in range(n_surr):
        s = surrogate(r, rng)
        Cs[i] = np.sqrt(np.mean((s[:-k] - s[k:])**2) / np.mean(s**2))
    return {"Z": float((C_obs - Cs.mean()) / max(Cs.std(), 1e-12))}


def coherence_phase(r: np.ndarray, T_ms: float, fs: float) -> float:
    """Autocorrélation du résidu au lag T₀ : > 0 = train phase-cohérent
    (la forme de l'impulsion se répète) ; < 0 = non cohérent / alterné."""
    k = max(1, int(T_ms / 1000.0 * fs))
    return float(np.corrcoef(r[:-k], r[k:])[0, 1])


# --------------------------------------------------------------------------- #
# Détecteurs validés (sortie xAI structurée)                                   #
# --------------------------------------------------------------------------- #

def detecteur_resurgence(u: np.ndarray, dt: float, win_sg: int,
                         u_zone: Optional[np.ndarray] = None,
                         dt_zone: Optional[float] = None,
                         taus: Optional[np.ndarray] = None) -> Dict:
    """Détecteur de résurgence (dynamique à événements, ex. E44).

    Chaîne figée validée par EXP-019 (biconditionnelle bande ⟺ résurgence,
    2/2 aveugles) et EXP-021 (micro-rythme : la résurgence est le redémarrage
    du même processus) — modèle nul correct dès l'origine (un seul surrogate
    par tirage). Une bande de récurrence dans le résidu signe un « second
    acte » — un silence prolongé suivi d'une reprise de l'activité.

    Chaîne fidèle aux campagnes : la zone active t ∈ [5 ; t_eff] est figée par
    la série de comptage `u_zone` (t_eff = premier u_zone ≤ 1 soutenu sur
    10 pas ; dans E44, u_zone = Nv, le comptage de plaquettes) puis appliquée
    à la série analysée `u` (dans E44, Lt, la longueur des boucles). Si u_zone
    est None, la zone est calculée sur `u` elle-même. Détrending
    SG(win_sg, 3), auto-comma, 60 surrogates graine 2019, bande Z < −3
    contiguë ≥ 10 temps.

    Retourne un verdict xAI : presente (bool), bandes, T de récurrence, et une
    justification lisible.
    """
    # zone active figée par la série de comptage (comme les campagnes)
    zref = u_zone if u_zone is not None else u
    dtz = dt_zone if dt_zone is not None else dt
    i0z = int(5.0 / dtz)
    soutenu = np.where(np.convolve((zref <= 1).astype(int),
                                   np.ones(10, dtype=int), 'valid') == 10)[0]
    i1z = min(soutenu[0] + 1, len(zref)) if len(soutenu) else len(zref)
    t_eff = (i1z) * dtz
    # applique la fenêtre temporelle [5 ; t_eff] à la série analysée
    i0 = int(np.searchsorted(np.arange(len(u)) * dt, 5.0))
    i1 = min(int(np.searchsorted(np.arange(len(u)) * dt, t_eff)), len(u))
    uz = u[i0:i1].astype(float)
    if len(uz) < win_sg:
        return {"detecteur": "resurgence", "presente": False, "bandes": [],
                "z_min": None, "T_recurrence": None,
                "justification": ("Zone active trop courte pour le détrending "
                                  "figé — pas assez de données pour conclure.")}
    r = detrend_sg(uz, win_sg, 3)
    if taus is None:
        taus = np.arange(1, len(r) // 2)
    prof = comma_z_profil(r, taus)
    b = bande_recurrence(prof["Z"], dt)
    if b["presente"]:
        just = (f"Résurgence détectée : bande de récurrence Z < −3 sur "
                f"{b['bandes']} (Z_min = {b['z_min']:.2f}). La série a un "
                f"second acte : un silence prolongé suivi d'une reprise — le "
                f"calendrier des événements récurre, pas leur spectre.")
    else:
        just = (f"Pas de résurgence : aucune bande de récurrence significative "
                f"(Z_min = {b['z_min']:.2f}). La série n'a pas de second acte.")
    return {"detecteur": "resurgence", "presente": b["presente"],
            "bandes": b["bandes"], "z_min": b["z_min"], "T_recurrence": b["T_zmin"],
            "justification": just}


def detecteur_coherence_defaut(u: np.ndarray, fs: float, T_lag_ms: float,
                               win_sg: int = 501,
                               seuil_magnitude: float = SEUIL_MAGNITUDE,
                               zone_morte: float = ZONE_MORTE_AC) -> Dict:
    """Détecteur de cohérence de phase à une période caractéristique
    (capteur identifié, ex. défaut de roulement au BPFI/BPFO/BSF).

    STATUT HONNÊTE (après correction du modèle nul, addenda A1 des campagnes
    exp022/023/024) : ce détecteur N'EST PAS VALIDÉ. La chaîne publiée
    initialement utilisait un modèle nul buggé (double surrogate) qui
    exagérait la significativité ; au null corrigé, ni la séparation
    défaut/sain, ni la spécificité, ni la loi de cohérence de phase ne
    tiennent sur le corpus CWRU. Ce détecteur est conservé comme observable
    expérimentale, à recalibrer proprement avant tout usage.

    Ce qui EST validé (modèle nul correct dès l'origine) : le détecteur de
    résurgence sur dynamique à événements (detecteur_resurgence, campagnes
    exp017–021) et le comma contre dynamique idéale (comma_vs_ideal, Rdyn
    stable sur 13 graines)."""
    r = detrend_sg(u, win_sg, 3)
    z = comma_au_lag(r, T_lag_ms, fs)["Z"]
    ac = coherence_phase(r, T_lag_ms, fs)
    declenche = z <= seuil_magnitude
    if abs(ac) < zone_morte:
        coh = None
    else:
        coh = ac > 0
    if declenche:
        just = (f"Récurrence significative à T₀ = {T_lag_ms} ms (Z = {z:.2f} ≤ "
                f"{seuil_magnitude}). AC = {ac:+.3f}. ATTENTION : observable "
                f"non validée au modèle nul corrigé (voir addenda A1).")
    else:
        just = (f"Pas de récurrence significative à T₀ = {T_lag_ms} ms "
                f"(Z = {z:.2f} > {seuil_magnitude}). AC = {ac:+.3f}. ATTENTION : "
                f"observable non validée au modèle nul corrigé (addenda A1).")
    return {"detecteur": "coherence_defaut", "valide": False,
            "declenche": declenche, "coherent": coh, "Z": z, "AC": ac,
            "T_lag_ms": T_lag_ms, "justification": just}


def comma_vs_ideal(u: np.ndarray, t: np.ndarray) -> Dict:
    """Comma noétique contre dynamique idéale (Theorie_Residus §2.3 éq. 4) :
    Rdyn = inf_T ‖u(t) − u_mod(t+T)‖ / ‖u‖, u_mod = meilleure bi-exponentielle.

    Validé comme l'observable la plus stable de la série (13 graines E44 :
    Rdyn ∈ [0,16 ; 0,23] — borné, non nul, indépendant de la durée du plateau).
    Critère CTFT : 0 < Rdyn < Rcrit signe un processus réel à événements.
    """
    tt = t - t[0]

    def biexpo(x, a1, t1, a2, t2, c):
        return a1 * np.exp(-x / t1) + a2 * np.exp(-x / t2) + c

    p, _ = curve_fit(biexpo, tt, u, p0=[1500, 8, 400, 100, 50], maxfev=50000)
    umod = biexpo(tt, *p)
    n = len(u)
    ru2 = np.mean(u**2)
    taus = np.arange(1, n // 2)
    out = np.empty(len(taus))
    for i, k in enumerate(taus):
        out[i] = np.sqrt(np.mean((u[:n - k] - umod[k:])**2) / ru2)
    ib = int(np.argmin(out))
    return {"Rdyn": float(out[ib]), "T_star": float(taus[ib] * (t[1] - t[0])),
            "params_biexpo": [float(x) for x in p]}


# --------------------------------------------------------------------------- #
# Ligne de commande                                                            #
# --------------------------------------------------------------------------- #

def main() -> None:
    import sys
    if len(sys.argv) < 2:
        print("Usage: python comma_core.py fichier.csv [T_lag_ms]")
        print("  Analyse le comma noétique d'un signal (t,signal).")
        sys.exit(1)
    vals = []
    with open(sys.argv[1]) as f:
        next(f)
        for ln in f:
            vals.append(float(ln.split(",")[1]))
    u = np.array(vals)
    r = detecteur_resurgence(u, dt=0.1, win_sg=51)
    print(f"Résurgence : {r['presente']} — {r['justification']}")
    if len(sys.argv) > 2:
        T = float(sys.argv[2])
        c = detecteur_coherence_defaut(u, fs=1.0, T_lag_ms=T)
        print(f"Cohérence à {T} ms : {c['declenche']} — {c['justification']}")


if __name__ == "__main__":
    main()
