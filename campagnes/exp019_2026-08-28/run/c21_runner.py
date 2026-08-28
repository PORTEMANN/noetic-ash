#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C21 — campagne exp019 : le comma noétique de Lt comme détecteur de
résurgence, graines aveugles 2031+2032 (attente EXP-019, figée AVANT mesure,
bridge/expectations.json v1.1.0, commit 3f97c14).

Régénère les graines 2031 et 2032 (reprise exacte du volet a de
c14_runner.py : e44_core.py, SeedSequence(2031/2032), N=48, A=1, gamma=0.2,
dt=0.1, 2048 pas). Témoins d'intégrité : les graines 2028 et 2029 doivent
être octet-identiques aux campagnes exp017/exp018.

Produit (octets déterministes, fins de ligne LF) :
  signaux/e44_nv_t_g2031.csv, signaux/e44_lt_t_g2031.csv
  signaux/e44_nv_t_g2032.csv, signaux/e44_lt_t_g2032.csv
  run/manifest_signaux.json

Usage : python3 run/c21_runner.py   (depuis la racine de la campagne)
"""

import hashlib
import json
import os
import sys

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RUN)
import e44_core as e44

SIG = os.path.join(BASE, "signaux")
os.makedirs(SIG, exist_ok=True)

N, A, GAM, DT, STEPS = 48, 1.0, 0.2, 0.1, 2048

def wcsv(path, xs, ys, head):
    with open(path, "w", newline="") as f:
        f.write(head + "\n")
        for a, b in zip(xs, ys):
            f.write(f"{a:.10e},{b:.10e}\n")

def genere(graine):
    rng = np.random.default_rng(np.random.SeedSequence(graine))
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
    return Nv, Lt

# témoins d'intégrité : graines 2028 et 2029 (attestées exp017 / exp018)
TEMOINS = {
    2028: "86361e02918493a5d7921884dba9e8ee021660f803209ad32ec333a72db1474c",
    2029: "64dc589d9808f81f94a35111f07fae5378a2cb8a573c313bf9922f50a6943767",
}
for g, attendu in TEMOINS.items():
    Nv_t, Lt_t = genere(g)
    h = hashlib.sha256(Nv_t.tobytes() + Lt_t.tobytes()).hexdigest()
    print(f"[C21] témoin graine {g} : {h[:16]}… "
          + ("CONFORME" if h == attendu else "EN ECART — chaîne invalide, ne pas analyser"))

# graines aveugles 2031 et 2032
for g in (2031, 2032):
    Nv, Lt = genere(g)
    ta = np.arange(1, STEPS + 1) * DT
    tb = np.arange(4, STEPS + 1, 4) * DT
    wcsv(os.path.join(SIG, f"e44_nv_t_g{g}.csv"), ta, Nv, "t,signal")
    wcsv(os.path.join(SIG, f"e44_lt_t_g{g}.csv"), tb, Lt, "t,signal")
    print(f"[C21] graine {g} : sha256 tableaux nus = "
          f"{hashlib.sha256(Nv.tobytes() + Lt.tobytes()).hexdigest()}")

man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(RUN, "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C21] manifest_signaux.json : {len(man)} empreintes")
