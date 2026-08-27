#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""c14_runner.py — campagne exp013 : régénère bit-à-bit les 14 CSV de signaux/.

Protocole C14 figé + addenda A1 (condition initiale : quench bruit blanc
complexe graine 2026) et A2 (boîte P1 : RMAX = NR = 4000, dr = 1).

Volet a : GP amorti 3D (e44_core.py copié ici, blob GitHub 2baf8d8d…),
graine SeedSequence(2026), N=48, A=1, gamma=0.2, dt=0.1, 2048 pas.
  - e44_nv_t.csv  : plaquettes de vorticité à chaque pas (2048 pts)
  - e44_lt_t.csv  : longueur totale des boucles fermées tous les 4 pas (512 pts)
  - controle_bruit43.csv, controle_expo.csv (2048 pts, statut H)

Volet b : fond monopole rho=1 (artefact P0, grille C13.1 : 4096 pts, dx=30/4096,
L-BFGS-B), hamiltonien radial P1 (Coulomb tronqué R_core=3.04, alpha=1/137.036),
orbitales u_{n,l}(r) pour 1s,2s,2p,3s,3p,3d,4s,4p,4d,4f (4000 pts).

CSV canoniques : en-tête + lignes "%.10e,%.10e", fins de ligne LF.

Usage : python3 run/c14_runner.py   (depuis la racine de la campagne ou du dépôt)
"""
import hashlib, json, os
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import eigh_tridiagonal

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, RUN)
import e44_core as e44

SIG = os.path.join(BASE, "signaux")
os.makedirs(SIG, exist_ok=True)

def wcsv(path, xs, ys, head):
    with open(path, "w") as f:
        f.write(head + "\n")
        for a, b in zip(xs, ys):
            f.write(f"{a:.10e},{b:.10e}\n")

# ---------------------------------------------------------------- volet a
N, A, GAM, DT, STEPS = 48, 1.0, 0.2, 0.1, 2048
rng = np.random.default_rng(np.random.SeedSequence(2026))
psi = rng.standard_normal((N, N, N)) + 1j * rng.standard_normal((N, N, N))
lin = e44.gp_linear(N, A, GAM, DT)
Nv = np.empty(STEPS)
Lt = np.empty(STEPS // 4)
for it in range(STEPS):
    psi = e44.gp_step(psi, lin, GAM, DT)
    wx, wy, wz = e44.vorticity(psi)
    Nv[it] = int(np.sum(wx != 0) + np.sum(wy != 0) + np.sum(wz != 0))
    if it % 4 == 3:
        fils, _, _ = e44.trace_filaments(wx, wy, wz)
        Lt[it // 4] = sum(f['len'] for f in fils
                          if f['closed'] and not np.any(f['disp']))

ta = np.arange(1, STEPS + 1) * DT
tb = np.arange(4, STEPS + 1, 4) * DT
rng43 = np.random.default_rng(np.random.SeedSequence(43))
bruit = rng43.standard_normal(STEPS)
expo = np.exp(-ta / 40.0)
wcsv(os.path.join(SIG, "e44_nv_t.csv"), ta, Nv, "t,signal")
wcsv(os.path.join(SIG, "e44_lt_t.csv"), tb, Lt, "t,signal")
wcsv(os.path.join(SIG, "controle_bruit43.csv"), ta, bruit, "t,signal")
wcsv(os.path.join(SIG, "controle_expo.csv"), ta, expo, "t,signal")

# ---------------------------------------------------------------- volet b
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
    res = minimize(fg, y0, jac=True, method='L-BFGS-B',
                   options={'maxiter': 20000, 'ftol': 1e-14, 'gtol': 1e-10})
    return res

res1 = solve_mono(1.0)
print(f"[C14-b] fond monopole rho=1 : C = {float(res1.fun):.10f}, niter {res1.nit}")

NR, RMAX = 4000, 4000.0          # addendum A2 : boîte corrigée (table P1 reproduite)
ALPHA, M_E, R_CORE = 1 / 137.036, 1.0, 3.04
r = np.linspace(RMAX / NR, RMAX, NR)
dr = r[1] - r[0]
V_eff = np.where(r >= R_CORE, -ALPHA / r, -ALPHA / R_CORE)

def spectrum(l):
    diag = 1.0 / (M_E * dr**2) + l * (l + 1) / (2 * M_E * r**2) + V_eff
    off = -1.0 / (2 * M_E * dr**2) * np.ones(NR - 1)
    return eigh_tridiagonal(diag, off, select='i', select_range=(0, 8))

ETATS = [("1s", 0, 0), ("2s", 0, 1), ("2p", 1, 0), ("3s", 0, 2), ("3p", 1, 1),
         ("3d", 2, 0), ("4s", 0, 3), ("4p", 1, 2), ("4d", 2, 1), ("4f", 3, 0)]
specs = {l: spectrum(l) for l in range(4)}
for nom, l, idx in ETATS:
    wcsv(os.path.join(SIG, f"p1_orb_{nom}.csv"), r, specs[l][1][:, idx], "r,signal")
    E = specs[l][0][idx]; n = idx + 1 + l
    print(f"[C14-b] {nom} : E={E:.6e} (Balmer {-ALPHA**2 * M_E / (2 * n**2):.6e})")

# ---------------------------------------------------------------- empreintes
man = {}
for fn in sorted(os.listdir(SIG)):
    if fn.endswith(".csv"):
        man[f"signaux/{fn}"] = hashlib.sha256(
            open(os.path.join(SIG, fn), "rb").read()).hexdigest()
print(json.dumps(man, indent=1))
