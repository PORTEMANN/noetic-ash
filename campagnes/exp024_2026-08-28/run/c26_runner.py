#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C26 — campagne exp024 : spécificité du comma à seuil de magnitude (sains
FE aveugles) + réplication du mécanisme de cohérence de phase (famille 21 mil
aveugle). Attente EXP-024 figée AVANT mesure (bridge/expectations.json
v1.6.0).

(a) Extrait les canaux FE exacts X{N}_FE_time des .mat déjà téléchargés
(97–100, corpus exp022/023) ; (b) télécharge la famille 21 mil et extrait
X{N}_DE_time exact. Écrit signaux/cwru_{N}_{DE|FE}.csv, manifeste SHA-256.

Usage : python3 run/c26_runner.py   (depuis la racine de la campagne)
"""

import hashlib
import json
import os
import urllib.request

import numpy as np
import scipy.io as sio

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.dirname(os.path.abspath(__file__))
SIG = os.path.join(BASE, "signaux")
os.makedirs(SIG, exist_ok=True)

URL = "https://engineering.case.edu/sites/default/files/{}.mat"
SAINS_FE = [97, 98, 99, 100]           # canaux FE (fan-end), jamais analysés
DEFAUTS_21 = [209, 210, 222, 223, 234, 235]  # famille 21 mil, jamais lue

def wcsv(path, xs, ys, head):
    with open(path, "w", newline="") as f:
        f.write(head + "\n")
        for a, b in zip(xs, ys):
            f.write(f"{a:.10e},{b:.10e}\n")

def telecharge(n):
    path = os.path.join(RUN, f"cwru_{n}.mat")
    if not os.path.exists(path):
        print(f"[C26] téléchargement {n}.mat …", flush=True)
        urllib.request.urlretrieve(URL.format(n), path)
    return path

FS = 12000

# (a) sains FE : réutilise les .mat déjà présents (téléchargés exp022/023)
for n in SAINS_FE:
    path = os.path.join(RUN, f"cwru_{n}.mat")
    if not os.path.exists(path):
        # cherche dans les campagnes sœurs puis télécharge si absent
        for cand in (f"/mnt/agents/output/campagne_exp023/run/cwru_{n}.mat",
                     f"/mnt/agents/output/campagne_exp022/run/cwru_{n}.mat"):
            if os.path.exists(cand):
                import shutil
                shutil.copy(cand, path)
                break
        else:
            telecharge(n)
    d = sio.loadmat(path)
    cible = f"X{n:03d}_FE_time"
    x = d[cible].ravel()
    t = np.arange(1, len(x) + 1) / FS
    wcsv(os.path.join(SIG, f"cwru_{n}_FE.csv"), t, x, "t,signal")
    print(f"[C26] cwru_{n}_FE.csv : {len(x)} points", flush=True)

# (b) famille 21 mil : télécharge et extrait DE exact
for n in DEFAUTS_21:
    path = telecharge(n)
    d = sio.loadmat(path)
    cible = f"X{n:03d}_DE_time"
    if cible in d:
        x = d[cible].ravel()
    else:
        cles = [k for k in d if k.endswith("DE_time") and not k.startswith("__")]
        print(f"[C26] {n}.mat : canal cible {cible} absent, canaux {cles}")
        x = d[cles[0]].ravel()
    t = np.arange(1, len(x) + 1) / FS
    wcsv(os.path.join(SIG, f"cwru_{n}_DE.csv"), t, x, "t,signal")
    print(f"[C26] cwru_{n}_DE.csv : {len(x)} points", flush=True)

man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(RUN, "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C26] manifest_signaux.json : {len(man)} empreintes")
