#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_bridge.py — tests du pont mesure ↔ interprétation.

Vérifie : la validation des signatures d'exemple, les quatre issues de
verdict (CONFORME, DIVERGENT, EXPLORATION, HORS-CONTRAT), la discipline
épistémique (statut H, falsifieurs), et la reproductibilité des empreintes.
"""

import copy
import json
import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "bridge"))
import noetic_bridge as nb  # noqa: E402

EXEMPLES = os.path.join(_ROOT, "bridge", "examples")


def _charge(nom):
    with open(os.path.join(EXEMPLES, nom), encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def attentes():
    with open(os.path.join(_ROOT, "bridge", "expectations.json"), encoding="utf-8") as f:
        return json.load(f)["attentes"]


NOMS_SIGNATURES = [
    "eeg_intention_p32plus", "ecg_normal_p33plus", "vibration_roulement_p34plus",
    "ton_pur_4hz", "logistique_p3_r384", "bruit_blanc_seed42", "finance_gbm_synth_h",
]


# ---------------------------------------------------------------------- #
# Validation                                                              #
# ---------------------------------------------------------------------- #

def test_exemples_valides():
    for nom in NOMS_SIGNATURES:
        erreurs = nb.valider_signature(_charge(nom + ".signature.json"))
        assert erreurs == [], f"{nom} : {erreurs}"


def test_signature_incomplete_rejetee():
    sig = _charge("ecg_normal_p33plus.signature.json")
    del sig["grille"]
    assert any("grille" in e for e in nb.valider_signature(sig))


def test_statut_c_sans_falsifieur_rejete():
    sig = _charge("ton_pur_4hz.signature.json")
    sig["falsifieur"] = None
    assert any("falsifieur" in e for e in nb.valider_signature(sig))


def test_bandes_sept_plans_exiges():
    sig = _charge("ton_pur_4hz.signature.json")
    sig["invariants"]["bandes"] = sig["invariants"]["bandes"][:6]
    assert any("bandes" in e for e in nb.valider_signature(sig))


# ---------------------------------------------------------------------- #
# Verdicts                                                                #
# ---------------------------------------------------------------------- #

def test_conforme_sur_exemplaires(attentes):
    """Les six exemplaires étalonnés (statut C ou E) sont CONFORMES."""
    for nom in NOMS_SIGNATURES:
        if nom == "finance_gbm_synth_h":
            continue
        v = nb.evaluer(_charge(nom + ".signature.json"), attentes,
                       horodatage="2026-08-27T12:00:00Z")
        assert v["verdict"] == nb.CONFORME, f"{nom} → {v['verdict']}"


def test_divergent_consigne(attentes):
    """Un ECG 'normal' mesuré quantique doit produire DIVERGENT — et le
    verdict cite le falsifieur de l'attente (B3-FAIL)."""
    sig = _charge("ecg_normal_p33plus.signature.json")
    sig["invariants"]["ReN"] = 42.0
    sig["regime"] = "Quantique"
    v = nb.evaluer(sig, attentes, horodatage="2026-08-27T12:00:00Z")
    assert v["verdict"] == nb.DIVERGENT
    assert "DIVERGENCE" in v["explication"]
    assert v["attente"]["falsifieur"]


def test_finance_exploration_statut_h(attentes):
    """La finance reste en statut H : verdict EXPLORATION, aucune conclusion."""
    v = nb.evaluer(_charge("finance_gbm_synth_h.signature.json"), attentes,
                   horodatage="2026-08-27T12:00:00Z")
    assert v["verdict"] == nb.EXPLORATION
    assert v["attente"]["statut"] == "H"
    assert v["attente"]["regime_attendu"] is None


def test_contexte_inconnu_hors_contrat(attentes):
    sig = _charge("ton_pur_4hz.signature.json")
    sig["contexte"]["etiquette"] = "contexte_sans_attente"
    v = nb.evaluer(sig, attentes, horodatage="2026-08-27T12:00:00Z")
    assert v["verdict"] == nb.HORS_CONTRAT
    assert v["attente"] is None


def test_mise_en_garde_fallback_mono_pic(attentes):
    """Rtop < 2 → la mise en garde LEX-013/014 doit figurer dans l'explication."""
    v = nb.evaluer(_charge("ton_pur_4hz.signature.json"), attentes,
                   horodatage="2026-08-27T12:00:00Z")
    assert "LEX-013" in v["explication"]


# ---------------------------------------------------------------------- #
# Reproductibilité                                                        #
# ---------------------------------------------------------------------- #

def test_empreinte_verdict_independante_de_l_horodatage(attentes):
    sig = _charge("ecg_normal_p33plus.signature.json")
    v1 = nb.evaluer(sig, attentes, horodatage="2026-08-27T12:00:00Z")
    v2 = nb.evaluer(sig, attentes, horodatage="2030-01-01T00:00:00Z")
    assert v1["sha256"] == v2["sha256"]


def test_verdicts_exemples_figes(attentes):
    """Les verdicts commités correspondent aux signatures commitées."""
    for nom in NOMS_SIGNATURES:
        sig = _charge(nom + ".signature.json")
        fige = _charge(nom + ".verdict.json")
        recalcule = nb.evaluer(sig, attentes, horodatage=fige["horodatage"])
        assert recalcule["sha256"] == fige["sha256"], f"{nom} : verdict non reproduit"
