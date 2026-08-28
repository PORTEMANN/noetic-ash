#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C17 — campagne exp015 : fond monopole rho=2 (attente EXP-015, figée AVANT
mesure dans bridge/expectations.json v0.7.0, commit f7d4dea ; registre v0.8.0
figé commit 712c1c4 pour l'analyse).

Produit les signaux du protocole C17 (octets déterministes, fins de ligne LF) :
  signaux/p1_orb_{2s..6h}_rho2.csv  — 21 orbitales des couches n=2..6 sur fond rho=2
  signaux/temoin_4f_rho1.csv        — témoin d'intégrité (fond rho=1, R_core=3,04,
                                      même boîte RMAX=8000)
  signaux/controle_bruit43.csv      — contrôle de spécificité (doit être
      octet-identique à exp013 signaux/controle_bruit43.csv, sha256 a3909a6b…)

Couplage fond -> hamiltonien orbital (déclaré) : dans P1, le seul point de
couplage est la taille du cœur — R_CORE(rho) = 3,04/sqrt(rho) (longueur de
cohérence de Higgs ∝ 1/sqrt(rho) dans le fonctionnel C(rho)). Le reste de la
chaîne est identique à C14+A2/C15/C16 : L-BFGS-B pour le fond, eigh_tridiagonal
pour les spectres, Coulomb tronqué, alpha=1/137,036, dr=1.

Témoins d'intégrité : C(rho=1) = 1,3033212195 (indépendant de la boîte) ;
table P1 n<=4 Balmer-exacte à RMAX=8000 ; comptages de nœuds.
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
print(f"[C17] témoin fond rho=1 : C = {C1:.10f}, niter {res1.nit}")
print("[C17] témoin C(1) CONFORME" if abs(C1 - 1.3033212195) < 1e-9
      else "[C17] TEMOIN C(1) EN ECART — chaîne invalide, ne pas analyser")
res2 = solve_mono(2.0)
print(f"[C17] fond rho=2 : C = {float(res2.fun):.10f}, niter {res2.nit}")

# ---------------------------------------------------------------- spectres P1
NR, RMAX = 8000, 8000.0
ALPHA, M_E = 1 / 137.036, 1.0
R_CORE1 = 3.04
R_CORE2 = 3.04 / np.sqrt(2.0)   # couplage déclaré : cœur Higgs ∝ 1/sqrt(rho)
r = np.linspace(RMAX / NR, RMAX, NR)
dr = r[1] - r[0]

def spectrum(l, R_CORE):
    V = np.where(r >= R_CORE, -ALPHA / r, -ALPHA / R_CORE)
    diag = 1.0 / (M_E * dr**2) + l * (l + 1) / (2 * M_E * r**2) + V
    off = -1.0 / (2 * M_E * dr**2) * np.ones(NR - 1)
    return eigh_tridiagonal(diag, off, select='i', select_range=(0, 8))

# couches n=2..6 complètes : (nom, l, idx=n-l-1, noeuds)
LETTRES = "spdfgh"
ETATS = [(f"{n}{LETTRES[l]}", l, n - l - 1, n - l - 1)
         for n in range(2, 7) for l in range(n)]
specs2 = {l: spectrum(l, R_CORE2) for l in range(6)}
energies = {}
for nom, l, idx, nd in ETATS:
    wcsv(os.path.join(SIG, f"p1_orb_{nom}_rho2.csv"), r, specs2[l][1][:, idx], "r,signal")
    E = specs2[l][0][idx]
    energies[nom] = E
    bal = -ALPHA**2 * M_E / (2 * (idx + 1 + l)**2)
    print(f"[C17] {nom}_rho2 ({nd} noeuds) : E={E:.6e} (ratio Balmer {E/bal:.4f})")

# témoin d'intégrité : 4f sur fond rho=1 (même boîte)
specs1 = {3: spectrum(3, R_CORE1)}
wcsv(os.path.join(SIG, "temoin_4f_rho1.csv"), r, specs1[3][1][:, 0], "r,signal")
print(f"[C17] temoin_4f_rho1 : E={specs1[3][0][0]:.6e}")

# contrôle de spécificité : bruit blanc graine 43 (identique à C14/C16)
STEPS = 2048
ta = (np.arange(STEPS) + 1) / 10.0
bruit = np.random.default_rng(np.random.SeedSequence(43)).standard_normal(STEPS)
wcsv(os.path.join(SIG, "controle_bruit43.csv"), ta, bruit, "t,signal")
hbr = hashlib.sha256(open(os.path.join(SIG, "controle_bruit43.csv"), "rb").read()).hexdigest()
print(f"[C17] controle_bruit43 sha256 = {hbr}")
print("[C17] controle CONFORME (octet-identique a exp013)" if hbr ==
      "a3909a6b7611313e91cbcdbef0db4690401d6d43a6b7be420f7794319f528a87"
      else "[C17] CONTROLE EN ECART")

# manifeste des signaux (+ énergies consignées)
man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(BASE, "run", "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
with open(os.path.join(BASE, "run", "energies_c17.json"), "w", newline="") as f:
    f.write(json.dumps({"C_rho1": C1, "C_rho2": float(res2.fun),
                        "R_CORE_rho2": R_CORE2, "energies_rho2": energies,
                        "E_temoin_4f_rho1": float(specs1[3][0][0])},
                       ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C17] manifest_signaux.json : {len(man)} empreintes")
