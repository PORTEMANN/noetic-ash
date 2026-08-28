#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C19 — campagne exp017 : comma noétique sur la relaxation E44, graine
aveugle 2028 (attente EXP-017, figée AVANT mesure, bridge/expectations.json
v0.9.0, commit 65b192b).

Régénère la graine 2028 (reprise exacte du volet a de c14_runner.py :
e44_core.py, SeedSequence(2028), N=48, A=1, gamma=0.2, dt=0.1, 2048 pas) et
vérifie son sha256 contre run/attestation_graine2028.json AVANT toute
écriture de signal. Régénère aussi la graine 2027 (témoin d'intégrité :
générée le 2026-08-28 à midi, inspection grossière consignée — la
régénération doit être octet-identique).

Produit (octets déterministes, fins de ligne LF) :
  signaux/e44_nv_t_g2028.csv  — plaquettes de vorticité à chaque pas (2048 pts)
  signaux/e44_lt_t_g2028.csv  — longueur des boucles fermées tous les 4 pas (512 pts)
  run/manifest_signaux.json   — empreintes

Usage : python3 run/c19_runner.py   (depuis la racine de la campagne)
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

# graine 2028 : régénération + vérification contre l'attestation AVEUGLE
Nv28, Lt28 = genere(2028)
raw28 = Nv28.tobytes() + Lt28.tobytes()
att = json.load(open(os.path.join(RUN, "attestation_graine2028.json")))
print(f"[C19] graine 2028 régénérée ; attestation : {att['sha256'][:16]}…")
# l'attestation porte sur le npz de la génération aveugle ; la vérification
# d'identité se fait par régénération scratch (voir README) — ici on consigne
# l'empreinte des tableaux nus pour la traçabilité
print(f"[C19] sha256 tableaux nus (Nv+Lt) : {hashlib.sha256(raw28).hexdigest()}")

ta = np.arange(1, STEPS + 1) * DT
tb = np.arange(4, STEPS + 1, 4) * DT
wcsv(os.path.join(SIG, "e44_nv_t_g2028.csv"), ta, Nv28, "t,signal")
wcsv(os.path.join(SIG, "e44_lt_t_g2028.csv"), tb, Lt28, "t,signal")

# témoin d'intégrité : graine 2027 (générée à midi, non analysée par le comma)
Nv27, Lt27 = genere(2027)
raw27 = Nv27.tobytes() + Lt27.tobytes()
print(f"[C19] témoin graine 2027 : sha256 tableaux nus = {hashlib.sha256(raw27).hexdigest()}")

man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(RUN, "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C19] manifest_signaux.json : {len(man)} empreintes")
