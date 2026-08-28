#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C24 — campagne exp022 : comma au lag caractéristique sur roulements réels
CWRU, 7 fichiers aveugles (attente EXP-022, figée AVANT mesure,
bridge/expectations.json v1.4.0).

Télécharge les 7 fichiers aveugles depuis engineering.case.edu (corpus
public), extrait le canal DE (capteur 12 kHz), écrit signaux/cwru_{N}.csv
(format canonique, décimales figées), manifeste SHA-256.

Fichiers : 98, 99 (sains), 106 (défaut interne), 118, 119 (bille),
130, 131 (externe). Jamais lus par cette chaîne avant la mesure.

Usage : python3 run/c24_runner.py   (depuis la racine de la campagne)
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
FICHIERS = [98, 99, 106, 118, 119, 130, 131]

def wcsv(path, xs, ys, head):
    with open(path, "w", newline="") as f:
        f.write(head + "\n")
        for a, b in zip(xs, ys):
            f.write(f"{a:.10e},{b:.10e}\n")

def telecharge(n):
    path = os.path.join(RUN, f"cwru_{n}.mat")
    if not os.path.exists(path):
        print(f"[C24] téléchargement {n}.mat …", flush=True)
        urllib.request.urlretrieve(URL.format(n), path)
    d = sio.loadmat(path)
    # Canal EXACT X{N}_DE_time : le fichier 99.mat embarque AUSSI les canaux
    # X098 (artefact documenté de la campagne vibration_hf) — prendre le canal
    # du fichier, pas le premier canal DE_time du dictionnaire.
    cible = f"X{n:03d}_DE_time"
    if cible in d:
        return d[cible].ravel()
    cles = [k for k in d if k.endswith("DE_time") and not k.startswith("__")]
    print(f"[C24] {n}.mat : canal cible {cible} absent, canaux présents {cles}")
    return d[cles[0]].ravel()

FS = 12000
for n in FICHIERS:
    x = telecharge(n)
    t = np.arange(1, len(x) + 1) / FS
    wcsv(os.path.join(SIG, f"cwru_{n}.csv"), t, x, "t,signal")
    print(f"[C22] cwru_{n}.csv : {len(x)} points", flush=True)

man = {}
for f in sorted(os.listdir(SIG)):
    man[f"signaux/{f}"] = hashlib.sha256(open(os.path.join(SIG, f), "rb").read()).hexdigest()
with open(os.path.join(RUN, "manifest_signaux.json"), "w", newline="") as f:
    f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(f"[C24] manifest_signaux.json : {len(man)} empreintes")
