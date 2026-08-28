#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
noetic_bridge.py — Pont mesure ↔ interprétation (ASH ↔ écosystème noétique).

Consomme une signature ASH (format ``ash-signature/0.1``, voir
``bridge/schema/signature.schema.json``), la confronte au registre
d'attentes (``bridge/expectations.json``) et émet un verdict JSON
(``ash-verdict/0.1``, voir ``bridge/schema/verdict.schema.json``).

Position épistémologique (lexique v0.3.0) : le pont n'est PAS un niveau
d'interprétation. L'ASH est antérieur à la machine noétique — ce module
consigne des confrontations datées et falsifiables, sans projeter la
phénoménologie de la machine sur l'instrument. Toute série (temps, valeur)
est analysable ; c'est le contexte déclaré (``contexte.etiquette``) qui relie
la mesure aux attentes et consolide la sémantique des régimes.

Dépendances : bibliothèque standard uniquement (auditable, embarquable).

Usage :
    python noetic_bridge.py signature.json \
        [--attentes expectations.json] [-o verdict.json] [--horodatage ISO]
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

PONT_VERSION = "0.1.0"
FORMAT_SIGNATURE = "ash-signature/0.1"
FORMAT_VERDICT = "ash-verdict/0.1"

REGIMES = ("Cosmologique", "Méso", "Quantique", "indéfini")
STATUTS = ("T", "C", "E", "H")

# Verdicts possibles
CONFORME = "CONFORME"          # régime mesuré ∈ régime(s) attendu(s)
DIVERGENT = "DIVERGENT"        # écart — consigné avec la même rigueur (B3-FAIL)
EXPLORATION = "EXPLORATION"    # attente sans prédiction (statut H) : la banque consigne
HORS_CONTRAT = "HORS-CONTRAT"  # aucune attente pour ce contexte


# ---------------------------------------------------------------------- #
# Canonisation et empreintes                                              #
# ---------------------------------------------------------------------- #

def canonique(obj) -> str:
    """JSON canonique : clés triées, séparateurs compacts, UTF-8.

    Deux exécutions du même calcul produisent la même chaîne — condition
    de la reproductibilité SHA-256 (pilier 2, C12.1).
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def empreinte(obj) -> str:
    """SHA-256 hexadécimal du JSON canonique de ``obj``."""
    return hashlib.sha256(canonique(obj).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------- #
# Validation légère de la signature                                       #
# ---------------------------------------------------------------------- #

def valider_signature(sig: dict) -> list:
    """Validation structurelle (sans dépendance externe).

    La référence normative reste ``schema/signature.schema.json`` ; cette
    fonction vérifie les points critiques pour un usage embarqué sans
    jsonschema. Retourne la liste des erreurs (vide si conforme).
    """
    erreurs = []
    requis = ["format", "ash_version", "signal", "grille", "normalisation",
              "agregation", "invariants", "regime", "bande_dominante",
              "contexte", "statut", "falsifieur"]
    for cle in requis:
        if cle not in sig:
            erreurs.append(f"champ requis absent : {cle}")
    if erreurs:
        return erreurs

    if sig["format"] != FORMAT_SIGNATURE:
        erreurs.append(f"format inattendu : {sig['format']!r} (attendu {FORMAT_SIGNATURE!r})")

    sha = sig["signal"].get("sha256", "")
    if not (isinstance(sha, str) and len(sha) == 64
            and all(c in "0123456789abcdef" for c in sha)):
        erreurs.append("signal.sha256 : empreinte hexadécimale de 64 caractères attendue")

    if sig["regime"] not in REGIMES:
        erreurs.append(f"regime inconnu : {sig['regime']!r}")
    if sig["statut"] not in STATUTS:
        erreurs.append(f"statut inconnu : {sig['statut']!r}")
    if sig["statut"] in ("C", "E") and not sig.get("falsifieur"):
        erreurs.append("falsifieur obligatoire pour les statuts C et E")

    bandes = sig["invariants"].get("bandes", [])
    if not (isinstance(bandes, list) and len(bandes) == 7
            and all(isinstance(b, (int, float)) for b in bandes)):
        erreurs.append("invariants.bandes : 7 nombres attendus (plans E1..E7)")

    bd = sig.get("bande_dominante", "")
    if not (isinstance(bd, str) and len(bd) == 2 and bd[0] == "E" and bd[1] in "1234567"):
        erreurs.append(f"bande_dominante invalide : {bd!r}")

    if not sig["contexte"].get("etiquette"):
        erreurs.append("contexte.etiquette vide : la signature n'est pas reliée au registre")

    return erreurs


# ---------------------------------------------------------------------- #
# Confrontation                                                           #
# ---------------------------------------------------------------------- #

def trouver_attente(sig: dict, attentes: list):
    """Première attente dont l'étiquette de contexte correspond."""
    etiquette = sig["contexte"]["etiquette"]
    for att in attentes:
        if att.get("contexte_etiquette") == etiquette:
            return att
    return None


def _mises_en_garde(sig: dict) -> list:
    """Mises en garde d'étalonnage applicables (lexique, niveau X)."""
    notes = []
    inv = sig["invariants"]
    if inv["Rtop"] < 2:
        notes.append(
            "Rtop < 2 : Rdyn = 1.0 par convention (fallback mono-pic) — "
            "un ton pur se classe méso par construction, cf. LEX-013 ; "
            "Rdyn est aveugle au désaccord sub-demi-ton, cf. LEX-014.")
    if sig.get("normalisation") in (None, "", "aucune"):
        notes.append(
            "ReN ∝ 1/amplitude (B3-FAIL #1) : ne comparer ce ReN à d'autres "
            "signatures qu'à normalisation d'amplitude commune déclarée.")
    return notes


def evaluer(sig: dict, attentes: list, horodatage: str = None) -> dict:
    """Confronte une signature au registre d'attentes et émet un verdict.

    Args:
        sig: signature conforme à ``ash-signature/0.1``.
        attentes: liste d'attentes (``expectations.json`` → clé ``attentes``).
        horodatage: ISO 8601 ; par défaut, l'heure UTC courante. Exclu du
            sha256 du verdict (reproductibilité).

    Returns:
        Verdict conforme à ``ash-verdict/0.1``.
    """
    erreurs = valider_signature(sig)
    if erreurs:
        raise ValueError("Signature non conforme : " + "; ".join(erreurs))

    inv = sig["invariants"]
    mesure = {
        "regime": sig["regime"],
        "ReN": inv["ReN"],
        "Rtop": inv["Rtop"],
        "Rdyn": inv["Rdyn"],
        "bande_dominante": sig["bande_dominante"],
    }
    attente = trouver_attente(sig, attentes)
    gardes = _mises_en_garde(sig)

    base = (f"ReN = {inv['ReN']:.4g} (agrégation {sig['agregation']['methode']} "
            f"de {sig['agregation']['n_fenetres']} fenêtres) → régime {sig['regime']} ; "
            f"Rtop = {inv['Rtop']}, Rdyn = {inv['Rdyn']:.4g}, "
            f"bande dominante {sig['bande_dominante']}.")

    if attente is None:
        verdict = HORS_CONTRAT
        bloc_attente = None
        explication = (base + " Aucune attente enregistrée pour le contexte "
                       f"« {sig['contexte']['etiquette']} » : la mesure est "
                       "consignée sans confrontation.")
    else:
        bloc_attente = {
            "id": attente["id"],
            "statut": attente["statut"],
            "regime_attendu": attente.get("regime_attendu"),
            "source": attente.get("source", ""),
            "falsifieur": attente.get("falsifieur"),
        }
        attendu = attente.get("regime_attendu")
        ref = (f"attente {attente['id']} (statut {attente['statut']}, "
               f"source : {attente.get('source', '—')})")
        if attendu is None:
            verdict = EXPLORATION
            explication = (base + f" L'{ref} ne porte aucune prédiction "
                           "(exploration, statut H) : la banque consigne la "
                           "signature, rien n'est conclu.")
        else:
            attendus = attendu if isinstance(attendu, list) else [attendu]
            if sig["regime"] in attendus:
                verdict = CONFORME
                explication = (base + f" L'{ref} prévoit "
                               f"{' ou '.join(attendus)} pour le contexte "
                               f"« {sig['contexte']['etiquette']} » : régime mesuré "
                               "dans l'attente.")
            else:
                verdict = DIVERGENT
                explication = (base + f" DIVERGENCE : l'{ref} prévoit "
                               f"{' ou '.join(attendus)}, le régime mesuré est "
                               f"{sig['regime']}. Consignée avec la même rigueur "
                               "qu'une conformité (B3-FAIL) — falsifieur de "
                               f"l'attente : {attente.get('falsifieur', '—')}")

    if gardes:
        explication += " Mises en garde : " + " ".join(gardes)

    v = {
        "format": FORMAT_VERDICT,
        "pont_version": PONT_VERSION,
        "signature_sha256": empreinte(sig),
        "contexte": {"domaine": sig["contexte"]["domaine"],
                     "etiquette": sig["contexte"]["etiquette"]},
        "attente": bloc_attente,
        "mesure": mesure,
        "verdict": verdict,
        "explication": explication,
        "horodatage": horodatage or datetime.now(timezone.utc).isoformat(),
    }
    # L'empreinte exclut horodatage et sha256 : un même couple
    # signature+attentes redonne le même verdict (reproductibilité).
    corps = {k: val for k, val in v.items() if k not in ("horodatage", "sha256")}
    v["sha256"] = empreinte(corps)
    return v


# ---------------------------------------------------------------------- #
# Ligne de commande                                                       #
# ---------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Pont mesure ↔ interprétation : confronte une signature ASH "
                    "au registre d'attentes et émet un verdict JSON.")
    ap.add_argument("signature", help="Fichier signature (ash-signature/0.1)")
    ap.add_argument("--attentes", default="expectations.json",
                    help="Registre d'attentes (défaut : expectations.json)")
    ap.add_argument("-o", "--sortie", help="Fichier verdict de sortie (défaut : stdout)")
    ap.add_argument("--horodatage", help="Horodatage ISO 8601 du verdict "
                    "(figé pour la reproductibilité des exemples)")
    args = ap.parse_args()

    with open(args.signature, encoding="utf-8") as f:
        sig = json.load(f)
    with open(args.attentes, encoding="utf-8") as f:
        attentes = json.load(f)["attentes"]

    v = evaluer(sig, attentes, horodatage=args.horodatage)
    texte = json.dumps(v, ensure_ascii=False, indent=1)
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8") as f:
            f.write(texte + "\n")
        print(f"{v['verdict']} — {args.sortie} (sha256 {v['sha256'][:12]}…)")
    else:
        print(texte)


if __name__ == "__main__":
    main()
