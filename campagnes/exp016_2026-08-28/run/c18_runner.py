#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C18 — campagne exp016 : couches n=7 et n=8 de P1 (attente EXP-016, figée
AVANT mesure dans bridge/expectations.json v0.8.0, commit 712c1c4).

Produit les signaux du protocole C18 (octets déterministes, fins de ligne LF) :
  signaux/p1_orb_{1s..8k}.csv  — 36 orbitales des couches n=1..8 sur fond rho=1,
                                 boîte RMAX=NR=12000, dr=1 (les couches n<=6 sont
                                 re-mesurées : la clause (b) porte sur les séries
                                 à l fixe n=l+1..8 dans CETTE boîte)
  signaux/temoin_4f.csv        — témoin d'intégrité 4f (même chaîne, boîte 12000)
  signaux/controle_bruit43.csv — contrôle de spécificité (doit être
      octet-identique à exp013 signaux/controle_bruit43.csv, sha256 a3909a6b…)

Chaîne identique à C14+A2/C15/C16/C17 : L-BFGS-B pour le fond monopole rho=1,
eigh_tridiagonal, Coulomb tronqué R_core=3,04, alpha=1/137,036, dr=1. Seule la
boîte change (12000 au lieu de 4000/8000) — addendum de boîte déclaré dans
PROTOCOLE_C18.md ; les témoins garantissent la continuité.

Témoins d'intégrité : C(rho=1) = 1,3033212195 (indépendant de la boîte) ;
table P1 n<=4 Balmer-exacte à RMAX=12000 ; comptages de nœuds.
"""

import hashlib
import json
import os

import numpy as np
from scipy.optimize import minimize
from scipy.linalg import eigh_tridiagonal

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIG = os.path.join(BASE, "signaux")
os.makedirs(SIG, exist_ok=True)

def wcsv(path, xs, ys, head):
    with open(path, "w", newline="") as f:
        f.write(head + "\n")
        for a, b in zip(xs, ys):
            f.write(f"{a:.10e},{b:.10e}\n")

# ---------------------------------------------------------------- fond monopole
XMAX30, NPTS = 30.0, 4096
DXC = XMAX30 / NPTS
xic = (np.arange(NPTS) + 1) * DXC

def d1c(u):
    g = np.gradient(u, DXC)
    g[0] = (u[1] - u[0]) / DXC
    g[-1] = (u[-1] - u[-2]) / DXC
    return g

def solve_mono(RHO):
    def energy(H, K):
        Kp = d1c(K); Hp = d1c(H)
        return DXC * (Kp**2 + (K**2 - 1)**2 / (2 * xic**2)
                      + (xic * Hp - H)**2 / (2 * xic**2)
                      + K**2 * H**2 + RHO * (H**2 - 1)**2 / 4).sum()
    def fg(y):
        H = y[:NPTS]; K = y[NPTS:]
        Kp = d1c(K); Hp = d1c(H); Hpp = d1c(Hp)
        E = energy(H, K)
        EK = DXC * (-2 * d1c(Kp) + 2 * K * (K**2 - 1) / xic**2 + 2 * K * H**2)
        EH = DXC * (-Hpp + d1c(H / xic) - Hp / xic + H / xic**2
                    + 2 * K**2 * H + RHO * H * (H**2 - 1))
        EH[0] = 0.0; EK[0] = 0.0
        return E, np.concatenate([EH, EK])
    y0 = np.concatenate([np.tanh(xic), 1 / np.cosh(xic)])
    return minimize(fg, y0, jac=True, method='L-BFGS-B',
                    options={'maxiter': 20000, 'ftol': 1e-14, 'gtol': 1e-10})

res1 = solve_mono(1.0)
C1 = float(res1.fun)
print(f"[C18] témoin fond rho=1 : C = {C1:.10f}, niter {res1.nit}")
print("[C18] témoin C(1) CONFORME" if abs(C1 - 1.3033212195) < 1e-9
      else "[C18] TEMOIN C(1) EN ECART — chaîne invalide, ne pas analyser")

# ---------------------------------------------------------------- spectres P1
NR, RMAX = 12000, 12000.0
ALPHA, M_E, R_CORE = 1 / 137.036, 1.0, 3.04
r = np.linspace(RMAX / NR, RMAX, NR)
dr = r[1] - r[0]
V_eff = np.where(r >= R_CORE, -ALPHA / r, -ALPHA / R_CORE)

def spectrum(l):
    diag = 1.0 / (M_E * dr**2) + l * (l + 1) / (2 * M_E * r**2) + V_eff
    off = -1.0 / (2 * M_E * dr**2) * np.ones(NR - 1)
    return eigh_tridiagonal(diag, off, select='i', select_range=(0, 8))

# couches n=1..8 complètes : (nom, l, idx=n-l-1, noeuds)
LETTRES = "spdfghik"
ETATS = [(f"{n}{LETTRES[l]}", l, n - l - 1, n - l - 1)
         for n in range(1, 9) for l in range(n)]
specs = {l: spectrum(l) for l in range(8)}
energies = {}
for nom, l, idx, nd in ETATS:
    wcsv(os.path.join(SIG, f"p1_orb_{nom}.csv"), r, specs[l][1][:, idx], "r,signal")
    E = specs[l][0][idx]
    energies[nom] = E
    bal = -ALPHA**2 * M_E / (2 * (idx + 1 + l)**2)
    print(f"[C18] {nom} ({nd} noeuds) : E={E:.6e} (ratio Balmer {E/bal:.4f})")

# témoin d'intégrité : 4f (déjà dans ETATS, on consigne son empreinte séparément)
wcsv(os.path.join(SIG, "temoin_4f.csv"), r, specs[3][1][:, 0], "r,signal")
print(f"[C18] temoin_4f : E={specs[3][0][0]:.6e}")

# contrôle de spécificité : bruit blanc graine 43 (identique à C14/C16/C17)
STEPS = 2048
ta = (np.arange(STEPS) + 1) / 10.0
bruit = np.random.default_rng(np.random.SeedSequence(43)).standard_normal(STEPS)
wcsv(os.path.join(SIG, "controle_bruit43.csv"), ta, bruit, "t,signal")
hbr = hashlib.sha256(open(os.path.join(SIG, "controle_bruit43.csv"), "rb").read()).hexdigest()
print(f"[C18] controle_bruit43 sha256 = {hbr}")
print("[C18] controle CONFORME (octet-identique a exp013)" if hbr ==
      "a3909a6b7611313e91cbcdbef0db4690401d6d43a6b7be420f7794319f528a87"
      else "[C18] CONTROLE EN ECART")

# manifeste des signaux (+ énergies consignées)
man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(BASE, "run", "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
with open(os.path.join(BASE, "run", "energies_c18.json"), "w", newline="") as f:
    f.write(json.dumps({"C_rho1": C1, "energies": energies,
                        "E_temoin_4f": float(specs[3][0][0])},
                       ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C18] manifest_signaux.json : {len(man)} empreintes")
