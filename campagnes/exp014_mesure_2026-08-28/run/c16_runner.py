#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C16 — campagne exp014_mesure : couche n=5 de P1 (attente EXP-014, figée
AVANT mesure dans bridge/expectations.json v0.6.0, commit 9bce034).

Produit les signaux du protocole C16 (octets déterministes, fins de ligne LF) :
  signaux/p1_orb_{5g,5f,5d,5p,5s}.csv  — orbitales de la couche n=5
  signaux/temoin_4f.csv                — témoin d'intégrité (doit être
      octet-identique à exp013 signaux/p1_orb_4f.csv, sha256 423604b8…)
  signaux/controle_bruit43.csv         — contrôle de spécificité (doit être
      octet-identique à exp013 signaux/controle_bruit43.csv, sha256 a3909a6b…)

Chaîne identique à C14+A2/C15 : fond monopole rho=1 (L-BFGS-B), spectres P1
(eigh_tridiagonal, boîte RMAX=NR=4000, dr=1, Coulomb tronqué R_core=3,04,
alpha=1/137,036). Aucun paramètre n'a été ajusté sur la couche n=5.
"""

import hashlib
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
print(f"[C16] fond monopole rho=1 : C = {float(res1.fun):.10f}, niter {res1.nit}")

# ---------------------------------------------------------------- spectres P1
NR, RMAX = 4000, 4000.0
ALPHA, M_E, R_CORE = 1 / 137.036, 1.0, 3.04
r = np.linspace(RMAX / NR, RMAX, NR)
dr = r[1] - r[0]
V_eff = np.where(r >= R_CORE, -ALPHA / r, -ALPHA / R_CORE)

def spectrum(l):
    diag = 1.0 / (M_E * dr**2) + l * (l + 1) / (2 * M_E * r**2) + V_eff
    off = -1.0 / (2 * M_E * dr**2) * np.ones(NR - 1)
    return eigh_tridiagonal(diag, off, select='i', select_range=(0, 8))

# couche n=5 : (nom, l, idx=n-l-1, noeuds)
ETATS = [("5g", 4, 0, 0), ("5f", 3, 1, 1), ("5d", 2, 2, 2),
         ("5p", 1, 3, 3), ("5s", 0, 4, 4)]
specs = {l: spectrum(l) for l in range(5)}
for nom, l, idx, nd in ETATS:
    wcsv(os.path.join(SIG, f"p1_orb_{nom}.csv"), r, specs[l][1][:, idx], "r,signal")
    E = specs[l][0][idx]
    print(f"[C16] {nom} ({nd} noeuds) : E={E:.6e} "
          f"(Balmer {-ALPHA**2 * M_E / (2 * 5**2):.6e})")

# témoin d'intégrité : 4f (l=3, idx=0)
wcsv(os.path.join(SIG, "temoin_4f.csv"), r, specs[3][1][:, 0], "r,signal")
h4f = hashlib.sha256(open(os.path.join(SIG, "temoin_4f.csv"), "rb").read()).hexdigest()
print(f"[C16] temoin_4f sha256 = {h4f}")
print("[C16] temoin CONFORME (octet-identique a exp013)" if h4f ==
      "423604b88d31dc88fbd802adfbf68eb5515d7f72b7d25f1f1ddb64244b66f7c4"
      else "[C16] TEMOIN EN ECART — chaine invalide, ne pas analyser")

# contrôle de spécificité : bruit blanc graine 43 (identique à C14)
STEPS = 2048
ta = (np.arange(STEPS) + 1) / 10.0  # axe t de C14 (t_1 = 0,1)
bruit = np.random.default_rng(np.random.SeedSequence(43)).standard_normal(STEPS)
wcsv(os.path.join(SIG, "controle_bruit43.csv"), ta, bruit, "t,signal")
hbr = hashlib.sha256(open(os.path.join(SIG, "controle_bruit43.csv"), "rb").read()).hexdigest()
print(f"[C16] controle_bruit43 sha256 = {hbr}")
print("[C16] controle CONFORME (octet-identique a exp013)" if hbr ==
      "a3909a6b7611313e91cbcdbef0db4690401d6d43a6b7be420f7794319f528a87"
      else "[C16] CONTROLE EN ECART")

# manifeste des signaux
import json
man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(BASE, "run", "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print("[C16] manifest_signaux.json :")
for k, v in sorted(man.items()):
    print(f"  {v}  {k}")
