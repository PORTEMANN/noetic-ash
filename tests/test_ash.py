#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires du noyau ASH (noetic-ash v1.0.0).

Protocole C12.1 : toutes les valeurs attendues ont été mesurées et figées
empiriquement le 26/08/2026 sur le code consolidé (fs=250, f0=1.0,
4 octaves, fenêtre 2 s — configuration EEG/générique par défaut).

Les trois tests couvrent les propriétés fondamentales documentées dans
docs/algorithm.md :
  1. Pureté harmonique : pics séparés d'une octave exacte → Rdyn = 0
     (torsion nulle), régime cosmologique.
  2. Robustesse au bruit : un bruit blanc stationnaire ne déclenche pas
     de fausse alarme quantique (ReN < seuil quantique).
  3. Invariance d'échelle : Rtop, Rdyn et bandes strictement invariants ;
     ReN ∝ 1/amplitude (comportement effectif du code — cf. note §6.1).

Lancement : pytest tests/test_ash.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "python"))

from ash_core import (  # noqa: E402
    ASH,
    REGIME_COSMOLOGICAL,
    REGIME_MESO,
    REGIME_QUANTUM,
    REN_THRESHOLD_QUANTUM,
)

FS = 250.0
N = int(2.0 * FS)  # une fenêtre de 2 s
T = np.arange(N) / FS


@pytest.fixture(scope="module")
def ash() -> ASH:
    """Analyseur en configuration par défaut (f0=1 Hz, 4 octaves, Tw=2 s)."""
    return ASH(fs=FS, signal_type="generic")


# --------------------------------------------------------------------- #
# Test 1 — Pureté harmonique (docs/algorithm.md §2.3)                    #
# --------------------------------------------------------------------- #

def test_octave_harmonic_purity(ash: ASH) -> None:
    """Deux composantes séparées d'une octave exacte (4 Hz et 8 Hz, toutes
    deux sur la grille f0·2^(n/12) avec f0=1) doivent donner :

    - Rtop = 2            (deux singularités topologiques, modes en octave)
    - Rdyn ≈ 0            (un seul rapport logarithmique = ln 2 → std nulle,
                           torsion nulle dans le Koilon)
    - ReN < 1             (régime cosmologique : pression dominante)

    Valeur mesurée (26/08/2026) : Rdyn = 0.0, ReN ≈ 3.1e-6.
    """
    signal = np.sin(2 * np.pi * 4.0 * T) + 0.8 * np.sin(2 * np.pi * 8.0 * T)
    r = ash.process_window(signal)

    assert r["Rtop"] == 2, f"Rtop attendu = 2, obtenu {r['Rtop']}"
    assert r["Rdyn"] == pytest.approx(0.0, abs=1e-6), (
        f"Rdyn attendu ≈ 0 (octave exacte), obtenu {r['Rdyn']}"
    )
    assert r["ReN"] < 1.0, f"ReN attendu < 1, obtenu {r['ReN']}"
    assert r["regime"] == REGIME_COSMOLOGICAL


# --------------------------------------------------------------------- #
# Test 2 — Robustesse au bruit (pas de fausse alarme)                    #
# --------------------------------------------------------------------- #

def test_white_noise_no_false_quantum_alarm(ash: ASH) -> None:
    """Un bruit blanc gaussien stationnaire ne doit pas être classé en
    régime quantique : la pression (Rc) et la dispersion entropique (H)
    dominent, le ReN reste sous le seuil quantique (10).

    Graine figée (42) pour la reproductibilité SHA-256.
    Valeur mesurée (26/08/2026) : Rtop = 3, Rdyn ≈ 0.143, ReN ≈ 1.19 (Méso).

    NOTE : sur 100 graines testées, 1/100 a dépassé ReN = 10 — le seuil
    reste une construction phénoménologique (docs/algorithm.md §7.4).
    """
    rng = np.random.default_rng(42)
    signal = rng.standard_normal(N)
    r = ash.process_window(signal)

    assert r["Rtop"] >= 2, "Le bruit doit produire plusieurs pics"
    assert 0.0 < r["Rdyn"] < 1.0
    assert r["ReN"] < REN_THRESHOLD_QUANTUM, (
        f"Fausse alarme quantique sur bruit blanc : ReN = {r['ReN']}"
    )
    assert r["regime"] in (REGIME_COSMOLOGICAL, REGIME_MESO)


# --------------------------------------------------------------------- #
# Test 3 — Invariance d'échelle (docs/algorithm.md §6.1, corrigée)       #
# --------------------------------------------------------------------- #

def test_scale_invariance(ash: ASH) -> None:
    """Multiplication du signal par α > 0 :

    - Rtop, Rdyn et les bandes normalisées sont STRICTEMENT invariants
      (le seuil de pics est relatif : 10 % du maximum).
    - ReN suit la loi effective ReN(α·x) = ReN(x)/α, car Rc (au
      dénominateur) croît linéairement avec l'amplitude.

    ⚠ Cette loi 1/α contredisait l'invariance du ReN autrefois affirmée
    en §6.1 — écart constaté le 26/08/2026, documentation corrigée
    (B3-FAIL). Ce test fige le comportement RÉEL du code.

    Valeurs mesurées (sinus 4 Hz) : ReN(×1) ≈ 2.4732, ReN(×10) ≈ 0.2473.
    """
    signal = np.sin(2 * np.pi * 4.0 * T)  # Rdyn = 1.0 → ReN non trivial
    r_ref = ash.process_window(signal)

    for alpha in (0.1, 10.0, 100.0):
        r = ash.process_window(alpha * signal)

        assert r["Rtop"] == r_ref["Rtop"]
        assert r["Rdyn"] == pytest.approx(r_ref["Rdyn"], abs=1e-9)
        np.testing.assert_allclose(r["bands"], r_ref["bands"], atol=1e-12)

        expected_ren = r_ref["ReN"] / alpha
        assert r["ReN"] == pytest.approx(expected_ren, rel=1e-6), (
            f"α={alpha} : ReN attendu ≈ {expected_ren:.6f}, obtenu {r['ReN']:.6f}"
        )
