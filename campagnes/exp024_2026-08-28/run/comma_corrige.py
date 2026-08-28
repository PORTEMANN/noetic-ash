#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comma au lag caractéristique — modèle nul CORRIGÉ (addendum A1 des
campagnes exp022/023/024).

Correction du bug de la chaîne publiée (c24/c25/c26) : la version d'origine
appelait `surrogate()` DEUX fois par tirage —

    surrogate(r, rng)[:-k] - surrogate(r, rng)[k:]

soit la différence de DEUX surrogates indépendants, au lieu du comma d'UN
même surrogate décalé (`s[:-k] - s[k:]`). Le modèle nul était donc gonflé
(la différence de deux surrogates indépendants est ≈ √2 plus grande), et le
Z-score était exagéré en magnitude. La version corrigée ci-dessous mesure le
comma du surrogate décalé — le modèle nul correct (« spectre préservé,
timing détruit », même observable que le signal observé).

Les campagnes E44 (exp017–021) ne sont PAS affectées : leur pipeline
appelait surrogate() une seule fois par tirage.

Chaîne figée (identique à l'originale sauf le modèle nul) :
  signal brut, fenêtre 2 s (24000:48000), détrending SG(501, 3),
  comma C(T) = ‖r(t+T)−r(t)‖/‖r‖ au lag, 40 surrogates graine 2019,
  Z = (C − μ_surr)/σ_surr.
"""

import numpy as np
from scipy.signal import savgol_filter

FS = 12000
WIN = slice(24000, 48000)

def detrend(u):
    return u - savgol_filter(u, 501, 3)

def surrogate(u, rng):
    F = np.fft.rfft(u)
    ph = rng.uniform(0, 2*np.pi, len(F))
    F2 = np.abs(F) * np.exp(1j*ph)
    F2[0] = F[0].real
    return np.fft.irfft(F2, len(u))

def comma_au_lag(r, T_ms, fs=FS):
    """Modèle nul CORRIGÉ : le comma du surrogate décalé (un seul surrogate
    par tirage). Les surrogates préservent la puissance (Parseval), donc
    ‖s‖ = ‖r‖ — la normalisation est identique."""
    k = max(1, int(T_ms/1000.0*fs))
    C_obs = np.sqrt(np.mean((r[:-k]-r[k:])**2)/np.mean(r**2))
    rng = np.random.default_rng(np.random.SeedSequence(2019))
    Cs = np.empty(40)
    for i in range(40):
        s = surrogate(r, rng)
        Cs[i] = np.sqrt(np.mean((s[:-k]-s[k:])**2)/np.mean(s**2))
    return float((C_obs - Cs.mean())/max(Cs.std(), 1e-12))

def ac_au_lag(r, T_ms, fs=FS):
    k = max(1, int(T_ms/1000.0*fs))
    return float(np.corrcoef(r[:-k], r[k:])[0, 1])
