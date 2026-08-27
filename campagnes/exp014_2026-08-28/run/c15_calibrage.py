#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C15 — note de calibration : grille ASH étendue vers le bas sur les
orbitales radiales P1 (fond monopole rho=1).

Contexte : la campagne exp013 (protocole C14+A2, f0 = 2^-8 figé) a lu les 10
orbitales u_{n,l}(r) Cosmologique avec ReN = 0 — artefact de plancher de
grille documenté (pic du 1s a f = 9,77e-4, sous le plancher). Question de la
presente note : peut-on CALIBRER une grille plus basse qui (a) lise le 1s
Quantique (attente EXP-013b d'origine) et (b) rende la structure nodale
visible ?

Ce script N'EST PAS une attente : c'est une étude de calibration consignée
après coup (B3-FAIL). Aucune entrée n'est ajoutée à bridge/expectations.json
(une attente déclarée maintenant serait post-hoc) ni au registre corpus
(pas de verdict : statut exploration).

Chaîne autonome et déterministe :
  1. fond monopole rho=1 (L-BFGS-B, même code que run/c14_runner.py volet b) ;
  2. spectres P1 (eigh_tridiagonal, boîte RMAX=NR=4000, dr=1 — addendum A2) ;
  3. balayage f0 = 2^-11 * 2^(k/12), k = -10..+13, sur les 10 orbitales,
     avec l'instrument figé (run/ash_core.py, ASH v1.0.0,
     sha256 338dbda7b499fdc8…) — agrégation médiane identique à c14_analyse ;
  4. contrôles bruit blanc graine 43 et exp(-t/40) aux grilles k=0 et k=+2
     (paramètres ASH du volet a de C14 : fs=10, fenêtre 512, nperseg 256) ;
  5. diagnostic « masse sous plancher » (fraction de la racine de PSD Welch
     sous f0, première fenêtre) par orbitale et par k.

Sorties (octets déterministes, fins de ligne LF) :
  donnees/balayage_f0.csv   — 24 grilles x 10 orbitales (240 lignes)
  donnees/controles.csv     — 2 contrôles x 2 grilles
  donnees/resume.json       — faits saillants (pic Welch, plateaux, verdict)
  run/manifest.json         — empreintes SHA-256 des sorties
"""

import hashlib
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize
from scipy.linalg import eigh_tridiagonal
from scipy.signal import welch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ash_core import ASH  # copie figée v1.0.0

DON = os.path.join(BASE, "donnees")
os.makedirs(DON, exist_ok=True)

# ---------------------------------------------------------------- spectres P1
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
print(f"[C15] fond monopole rho=1 : C = {C1:.10f}, niter {res1.nit}")

NR, RMAX = 4000, 4000.0
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
U = {}
for nom, l, idx in ETATS:
    U[nom] = specs[l][1][:, idx]
    E = specs[l][0][idx]; n = idx + 1 + l
    print(f"[C15] {nom} : E={E:.6e} (Balmer {-ALPHA**2 * M_E / (2 * n**2):.6e})")

NOEUDS = {nom: idx for nom, l, idx in ETATS}  # nœuds radiaux = n−l−1

# ---------------------------------------------------------------- instrument
def mesure(sig, fs, f0, win_pts, nperseg):
    """Agrégation médiane identique à run/c14_analyse.py (campagne exp013)."""
    s = sig / np.sqrt(np.mean(sig**2))  # RMS = 1
    ash = ASH(fs=fs, signal_type="generic", f0=f0, n_octaves=5,
              window_duration=win_pts / fs, overlap=0.5, nperseg=nperseg)
    df = ash.process_signal(s)
    med = {k: float(df[k].median()) for k in ["Rc", "Rtop", "Rdyn", "ReN"]}
    bands = np.median(np.stack(df["bands"]), axis=0)
    p = bands / bands.sum()
    H = float(-np.sum(p * np.log(p + 1e-12)))
    sb = np.sort(bands)[::-1]
    D = float(sb[0] - sb[1])
    ren = med["ReN"]
    reg = "Quantique" if ren > 10 else ("Cosmologique" if ren < 1 else "Méso")
    return med, H, D, int(np.argmax(bands)) + 1, reg, len(df)

def masse_sous_plancher(sig, f0, fs, nperseg):
    """Fraction de la racine de PSD Welch (première fenêtre) sous f0."""
    s = sig / np.sqrt(np.mean(sig**2))
    fr, psd = welch(s[:nperseg], fs=fs, nperseg=nperseg)
    a = np.sqrt(psd)
    return float(a[fr < f0].sum() / a.sum())

# pic Welch du 1s (paramètres figés C14 volet b : fs=1, nperseg=1024)
fr1, psd1 = welch(U["1s"][:1024] / np.sqrt(np.mean(U["1s"]**2)), fs=1.0, nperseg=1024)
PIC_1S = float(fr1[np.argmax(psd1)])
print(f"[C15] pic Welch 1s : f = {PIC_1S:.10e} (df = {fr1[1]:.10e})")

# ---------------------------------------------------------------- balayage
KMIN, KMAX = -10, 13
lignes = ["k,f0,orbitale,noeuds,Rc,Rtop,Rdyn,ReN,H,D,bande,regime,n_fenetres,masse_sous_plancher"]
synthese = {}
for k in range(KMIN, KMAX + 1):
    f0 = 2.0**-11 * 2.0**(k / 12)
    sser, pser = [], []
    for nom, l, idx in ETATS:
        med, H, D, bande, reg, nfen = mesure(U[nom], 1.0, f0, 1024, 1024)
        msp = masse_sous_plancher(U[nom], f0, 1.0, 1024)
        lignes.append(
            f"{k},{f0:.10e},{nom},{NOEUDS[nom]},{med['Rc']:.10e},{med['Rtop']:.10e},"
            f"{med['Rdyn']:.10e},{med['ReN']:.10e},{H:.10e},{D:.10e},E{bande},{reg},{nfen},{msp:.10e}")
        if l == 0:
            sser.append(med["ReN"])
        if l == 1 and nom != "1s":
            pser.append(med["ReN"])
    mono_s = all(sser[i] > sser[i + 1] for i in range(3))
    mono_p = all(pser[i] > pser[i + 1] for i in range(2))
    synthese[k] = {"f0": f0, "mono_s": mono_s, "mono_p": mono_p}
    print(f"[C15] k={k:+3d} f0={f0:.6e} mono_s={mono_s} mono_p={mono_p}")

csv_bal = "\n".join(lignes) + "\n"
with open(os.path.join(DON, "balayage_f0.csv"), "w", newline="") as f:
    f.write(csv_bal)

# ---------------------------------------------------------------- contrôles
STEPS = 2048
ta = np.arange(STEPS) / 10.0
bruit = np.random.default_rng(np.random.SeedSequence(43)).standard_normal(STEPS)
expo = np.exp(-ta / 40.0)
ligc = ["nom,k,f0,Rc,Rtop,Rdyn,ReN,H,D,bande,regime,n_fenetres"]
ctrl = {}
for k in (0, 2):
    f0 = 2.0**-11 * 2.0**(k / 12)
    for nom, sig in (("controle_bruit43", bruit), ("controle_expo", expo)):
        med, H, D, bande, reg, nfen = mesure(sig, 10.0, f0, 512, 256)
        ligc.append(
            f"{nom},{k},{f0:.10e},{med['Rc']:.10e},{med['Rtop']:.10e},"
            f"{med['Rdyn']:.10e},{med['ReN']:.10e},{H:.10e},{D:.10e},E{bande},{reg},{nfen}")
        ctrl[f"{nom}@k{k}"] = reg
csv_ctl = "\n".join(ligc) + "\n"
with open(os.path.join(DON, "controles.csv"), "w", newline="") as f:
    f.write(csv_ctl)

# ---------------------------------------------------------------- résumé
ren1s = {}
for k in range(KMIN, KMAX + 1):
    f0 = 2.0**-11 * 2.0**(k / 12)
    med, _, _, _, reg, _ = mesure(U["1s"], 1.0, f0, 1024, 1024)
    ren1s[k] = {"ReN": round(med["ReN"], 6), "regime": reg}

resume = {
    "format": "note-calibration/0.1",
    "objet": "Calibration d'une grille ASH basse pour les orbitales P1 — échec documenté (B3-FAIL)",
    "instrument": {"ash_version": "1.0.0",
                   "ash_core_sha256": "338dbda7b499fdc8ea00beb0ddc696270f47eda38253902edc77cba28eedeb0e",
                   "n_octaves": 5, "overlap": 0.5, "normalisation": "rms1",
                   "agregation": "mediane"},
    "grille_balayee": {"forme": "f0 = 2^-11 * 2^(k/12)", "k_min": KMIN, "k_max": KMAX},
    "pic_welch_1s": PIC_1S,
    "ren_1s_par_k": {str(k): v for k, v in ren1s.items()},
    "ordonnancement_nodal": {str(k): v for k, v in synthese.items()},
    "controles": ctrl,
    "verdict_calibration": {
        "clause_a_regime_1s_quantique": "ECHEC — Quantique atteint uniquement dans la rampe de divergence au bord du plancher (ReN 4,31 -> 56,64 -> 0 entre k=0 et k=+12, soit ~6 % de variation de f0) ; aucun plateau stable ; toute grille 'Quantique' serait posée sur l'artefact de bord.",
        "clause_b_structure_nodale": "SUCCES PARTIEL — ordonnancement nodal présent sur deux plateaux (k<=-3 et k=+1..+2), bande d'instabilité moiré entre k=-2 et k=0 ; Rc croît avec le nombre de nœuds sur toutes les grilles (indicateur le plus robuste).",
        "specificite_controles": "aucune fausse alarme Quantique (les deux contrôles lisent Cosmologique, contenu hors bande — test trivial).",
    },
    "fond_monopole": {"rho": 1.0, "C": C1, "niter": int(res1.nit)},
    "energies_P1": {nom: float(specs[l][0][idx]) for nom, l, idx in ETATS},
}
with open(os.path.join(DON, "resume.json"), "w", newline="") as f:
    f.write(json.dumps(resume, ensure_ascii=False, indent=2) + "\n")

# ---------------------------------------------------------------- manifeste
man = {}
for rel in ["donnees/balayage_f0.csv", "donnees/controles.csv", "donnees/resume.json",
            "run/c15_calibrage.py", "run/ash_core.py"]:
    man[rel] = hashlib.sha256(open(os.path.join(BASE, rel), "rb").read()).hexdigest()
with open(os.path.join(BASE, "run", "manifest.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print("[C15] manifeste :")
for rel, h in sorted(man.items()):
    print(f"  {h}  {rel}")
