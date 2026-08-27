#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""c13_1_runner.py — campagne monopole_ash, protocole C13.1 figé.

Régénère les 18 signaux CSV (octet pour octet) de la campagne du 2026-08-27.

Pipeline :
 1. Minimisation L-BFGS-B du fonctionnel radial du monopole SU(2)
    (artefact P0 p0_monopole_su2.py, sha256=52929bda0603…, équations et
    gradient discret repris à l'identique) sur la grille figée C13.1 :
    4096 points uniformes de [30/4096, 30], dx = 30/4096, différences
    centrées ordre 2, CL dures H(0)=0, K(0)=1.
 2. Calibration : ρ=0.5 depuis le guess tanh/1·cosh (C ≃ 1, borne BPS),
    puis continuation : 0.5 → 0.25 → 0.1 et 0.5 → 1 → 2 → 4
    (warm start sur la branche précédente).
 3. Signal primaire ε(ξ) = intégrand exact de C(ρ) ; contrôles H(ξ), K(ξ).
 4. CSV `xi,signal` en %.10e, fins de ligne LF ; SHA-256 consignés dans
    run/runs_c13_1.json et dans chaque signature.

Analyse ASH (non refaite ici — voir signatures/) : RMS=1, grille
f0=0.125 cycle/ξ, 5 octaves, fenêtre 1024 pts, overlap 0.5, nperseg 1024,
agrégation médiane des 7 fenêtres (ash_core.py 1.0.0, sha256=338dbda7…).
"""
import hashlib
import numpy as np
from scipy.optimize import minimize

N, XMAX = 4096, 30.0
DX = XMAX / N
xi = (np.arange(N) + 1) * DX

def d1(u):
    g = np.gradient(u, DX)
    g[0] = (u[1]-u[0])/DX; g[-1] = (u[-1]-u[-2])/DX
    return g

def make_fg(RHO):
    def energy(H, K):
        Kp = d1(K); Hp = d1(H)
        e = Kp**2 + (K**2-1)**2/(2*xi**2) + (xi*Hp - H)**2/(2*xi**2) \
            + K**2*H**2 + RHO*(H**2-1)**2/4
        return DX*e.sum()
    def fg(y):
        H = y[:N]; K = y[N:]
        Kp = d1(K); Hp = d1(H); Hpp = d1(Hp)
        E = energy(H, K)
        EK = DX*(-2*d1(Kp) + 2*K*(K**2-1)/xi**2 + 2*K*H**2)
        EH = DX*(-Hpp + d1(H/xi) - Hp/xi + H/xi**2 + 2*K**2*H + RHO*H*(H**2-1))
        EH[0] = 0.0; EK[0] = 0.0
        return E, np.concatenate([EH, EK])
    return energy, fg

def minimise(RHO, y0):
    energy, fg = make_fg(RHO)
    res = minimize(fg, y0, jac=True, method='L-BFGS-B',
                   options={'maxiter': 20000, 'ftol': 1e-14, 'gtol': 1e-10})
    H = res.x[:N].copy(); K = res.x[N:].copy()
    H[0] = 0.0; K[0] = 1.0
    return energy, H, K, res

def eps_of(RHO, H, K):
    Kp = d1(K); Hp = d1(H)
    return Kp**2 + (K**2-1)**2/(2*xi**2) + (xi*Hp - H)**2/(2*xi**2) \
           + K**2*H**2 + RHO*(H**2-1)**2/4

def write_csv(path, sig):
    with open(path, "w", newline="") as f:
        f.write("xi,signal\n")
        for a, b in zip(xi, sig):
            f.write(f"{a:.10e},{b:.10e}\n")
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

if __name__ == "__main__":
    import os
    os.makedirs("signaux", exist_ok=True)
    y = np.concatenate([np.tanh(xi), 1.0/np.cosh(xi)])
    branches = [0.5, 0.25, 0.1]         # calibration puis descente vers BPS
    sols = {}
    for rho in branches:
        e, H, K, res = minimise(rho, y)
        sols[rho] = (H, K); y = np.concatenate([H, K])
        print(f"rho={rho}: C={e(H,K):.5f} niter={res.nit}")
    y = np.concatenate([sols[0.5][0], sols[0.5][1]])
    for rho in [1.0, 2.0, 4.0]:          # montée
        e, H, K, res = minimise(rho, y)
        sols[rho] = (H, K); y = np.concatenate([H, K])
        print(f"rho={rho}: C={e(H,K):.5f} niter={res.nit}")
    for rho, (H, K) in sorted(sols.items()):
        t = str(rho).replace(".", "p")
        for nom, sig in (("eps", eps_of(rho, H, K)), ("h", H), ("k", K)):
            h = write_csv(f"signaux/{nom}_r{t}.csv", sig)
            print(f"{nom}_r{t}.csv sha256={h}")
