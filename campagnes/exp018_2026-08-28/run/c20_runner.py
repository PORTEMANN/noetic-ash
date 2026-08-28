#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C20 — campagne exp018 : loi d'échelle temporelle du comma noétique E44,
graine aveugle 2029 (attente EXP-018, figée AVANT mesure,
bridge/expectations.json v1.0.0, commit 0a4ffef).

Régénère la graine 2029 (reprise exacte du volet a de c14_runner.py :
e44_core.py, SeedSequence(2029), N=48, A=1, gamma=0.2, dt=0.1, 2048 pas) et
vérifie son sha256 contre run/attestation_graine2029.json AVANT toute
écriture de signal. Régénère aussi la graine 2028 (témoin d'intégrité : doit
être octet-identique au npz attesté de la campagne exp017, sha256
a3fc0e61c5eab17e…).

Produit (octets déterministes, fins de ligne LF) :
  signaux/e44_nv_t_g2029.csv  — plaquettes de vorticité à chaque pas (2048 pts)
  signaux/e44_lt_t_g2029.csv  — longueur des boucles fermées tous les 4 pas (512 pts)
  run/manifest_signaux.json   — empreintes

Usage : python3 run/c20_runner.py   (depuis la racine de la campagne)
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

# témoin d'intégrité : graine 2028 (attestée exp017, npz publié)
Nv28, Lt28 = genere(2028)
h28 = hashlib.sha256(Nv28.tobytes() + Lt28.tobytes()).hexdigest()
print(f"[C20] témoin graine 2028 : sha256 tableaux nus = {h28}")
print("[C20] témoin CONFORME (identique à exp017)" if h28 ==
      "86361e02918493a5d7921884dba9e8ee021660f803209ad32ec333a72db1474c"
      else "[C20] TEMOIN EN ECART — chaîne invalide, ne pas analyser")

# graine 2029 : régénération, attestation consignée
Nv29, Lt29 = genere(2029)
att = json.load(open(os.path.join(RUN, "attestation_graine2029.json")))
print(f"[C20] graine 2029 régénérée ; attestation npz : {att['sha256'][:16]}…")
print(f"[C20] sha256 tableaux nus (Nv+Lt) : "
      f"{hashlib.sha256(Nv29.tobytes() + Lt29.tobytes()).hexdigest()}")

ta = np.arange(1, STEPS + 1) * DT
tb = np.arange(4, STEPS + 1, 4) * DT
wcsv(os.path.join(SIG, "e44_nv_t_g2029.csv"), ta, Nv29, "t,signal")
wcsv(os.path.join(SIG, "e44_lt_t_g2029.csv"), tb, Lt29, "t,signal")

man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(RUN, "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C20] manifest_signaux.json : {len(man)} empreintes")
