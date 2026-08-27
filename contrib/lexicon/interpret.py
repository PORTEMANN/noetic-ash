"""
interpret.py — Pipeline ASH → invariants → lecture multi-niveaux du lexique.

Usage :
    python interpret.py signal.csv [type_signal] [--niveaux M,E,I,X,PHI]

Niveaux : M (mathématique), E (étalonnage — mesuré sur corpus figés),
I (industriel/embarqué), X (xAI — explicabilité de la décision),
PHI (philosophique — documentaire).
Statuts : T (théorème/protocole figé) > C (calibré) > E (empirique) > H (hypothèse).

Protocole C12.1 : les niveaux ne sont jamais fusionnés, chaque interprétation
est affichée avec son statut, et PHI reste toujours H (documentaire).

Note : le niveau N (machine noétique) a été supprimé en lexique v0.3.0 —
l'ASH (industrie embarquée, xAI) est antérieur à la machine ; ce sont des
approches distinctes. Les ponts éventuels sont documentés dans les notes
des entrées, jamais comme niveau.
"""

import argparse
import json
import os
import sys

# --- Import du noyau canonique -----------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "src", "python"))
from ash_core import ASH  # noqa: E402

import numpy as np  # noqa: E402

ORDRE_STATUTS = {"T": 0, "C": 1, "E": 2, "H": 3}  # du plus fort au plus faible
NIVEAUX = ["M", "E", "I", "X", "PHI"]
NOMS_NIVEAUX = {
    "M": "Mathématique",
    "E": "Étalonnage (corpus figés C12.1)",
    "I": "Industriel / embarqué",
    "X": "xAI — explicabilité",
    "PHI": "Philosophique (documentaire)",
}


# --- Agrégation des invariants sur tout le signal ----------------------------
def aggreger(df):
    """Agrège le DataFrame ASH (time, Rc, Rtop, Rdyn, bands, ReN, regime)
    en un vecteur d'invariants global.

    Médianes pour ReN, Rtop, Rdyn (robustes aux transitoires), moyennes pour
    Rc et les bandes. Le régime global est recalculé depuis le ReN médian
    pour rester cohérent avec les seuils figés (1 et 10).
    """
    if len(df) == 0:
        raise ValueError("Aucune fenêtre ASH produite.")
    ren_med = float(np.median(df["ReN"].to_numpy(dtype=float)))
    bandes = np.mean(np.stack(df["bands"].to_numpy()), axis=0)
    if ren_med > 10.0:
        regime = "Quantique"
    elif ren_med < 1.0:
        regime = "Cosmologique"
    else:
        regime = "Méso"
    return {
        "ReN": ren_med,
        "Rtop": float(np.median(df["Rtop"].to_numpy(dtype=float))),
        "Rdyn": float(np.median(df["Rdyn"].to_numpy(dtype=float))),
        "Rc": float(np.mean(df["Rc"].to_numpy(dtype=float))),
        "bands": bandes,
        "regime": regime,
        "bande_dominante": f"E{int(np.argmax(bandes)) + 1}",
    }


# --- Correspondance signature ↔ invariants -----------------------------------
def correspond(signature, inv):
    """Vrai si toutes les conditions de la signature sont satisfaites."""
    if not signature:
        return False  # entrée conceptuelle : jamais déclenchée automatiquement
    if "regime" in signature and inv["regime"] != signature["regime"]:
        return False
    if "bande_dominante" in signature and inv["bande_dominante"] != signature["bande_dominante"]:
        return False
    if "rtop_min" in signature and inv["Rtop"] < signature["rtop_min"]:
        return False
    if "rtop_max" in signature and inv["Rtop"] > signature["rtop_max"]:
        return False
    if "rdyn_min" in signature and inv["Rdyn"] < signature["rdyn_min"]:
        return False
    if "rdyn_max" in signature and inv["Rdyn"] > signature["rdyn_max"]:
        return False
    if "ren_min" in signature and inv["ReN"] < signature["ren_min"]:
        return False
    if "ren_max" in signature and inv["ReN"] > signature["ren_max"]:
        return False
    return True


def charger_lexique(chemin=None):
    chemin = chemin or os.path.join(_ROOT, "lexicon", "lexicon.json")
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def interpreter(inv, lexique, niveaux=None):
    """Retourne les entrées dont la signature correspond, triées par statut."""
    niveaux = niveaux or NIVEAUX
    matches = [
        e for e in lexique["entrees"]
        if correspond(e["signature"], inv)
        and any(n in e["niveaux"] and n in niveaux for n in NIVEAUX)
    ]
    matches.sort(key=lambda e: ORDRE_STATUTS.get(e["statut_global"], 9))
    return matches


# --- Affichage ----------------------------------------------------------------
def formater_lecture(inv, matches, niveaux=None):
    niveaux = niveaux or NIVEAUX
    lignes = []
    lignes.append("=" * 72)
    lignes.append("LECTURE ASH MULTI-NIVEAUX (instrument — couche acquisition/mesure)")
    lignes.append("=" * 72)
    lignes.append(
        f"Invariants : ReN={inv['ReN']:.4g}  Rtop={inv['Rtop']:.4g}  "
        f"Rdyn={inv['Rdyn']:.4g}  Rc={inv['Rc']:.4g}"
    )
    lignes.append(f"Régime : {inv['regime']}   Bande dominante : {inv['bande_dominante']}")
    lignes.append("")
    if not matches:
        lignes.append("Aucune entrée du lexique ne correspond à cette signature.")
        lignes.append("→ Candidat P35+ : documenter ce signal pour une nouvelle entrée.")
        return "\n".join(lignes)
    for e in matches:
        lignes.append(f"--- {e['id']} — {e['titre']}  [statut global : {e['statut_global']}]")
        for n in NIVEAUX:
            if n not in niveaux or n not in e["niveaux"]:
                continue
            nv = e["niveaux"][n]
            lignes.append(f"  [{n} | {nv['statut']}] {NOMS_NIVEAUX[n]}")
            lignes.append(f"       {nv['texte']}")
        if e.get("falsifieur"):
            lignes.append(f"  Falsifieur : {e['falsifieur']}")
        lignes.append("")
    lignes.append("Rappel C12.1 : [T] théorème/protocole figé · [C] calibré/vérifié ·")
    lignes.append("[E] empirique/étude de cas · [H] hypothèse. PHI est toujours H.")
    return "\n".join(lignes)


# --- Entrées pratiques ---------------------------------------------------------
def analyser_signal(chemin_csv, type_signal="generic", niveaux=None, chemin_lexique=None):
    """Pipeline complet : CSV → ASH → invariants agrégés → lecture du lexique."""
    ash, signal = ASH.from_csv(chemin_csv, signal_type=type_signal)
    df = ash.process_signal(signal)
    inv = aggreger(df)
    lexique = charger_lexique(chemin_lexique)
    matches = interpreter(inv, lexique, niveaux)
    return inv, matches


def main():
    ap = argparse.ArgumentParser(description="Lecture multi-niveaux d'un signal via le lexique ASH.")
    ap.add_argument("csv", nargs="?", help="Fichier CSV du signal (colonnes time,signal ou une colonne)")
    ap.add_argument("type_signal", nargs="?", default="generic",
                    choices=["eeg", "ecg", "vibration", "generic"])
    ap.add_argument("--niveaux", default=None,
                    help="Niveaux à afficher, ex. M,E (défaut : tous, PHI inclus)")
    args = ap.parse_args()
    if not args.csv:
        ap.print_help()
        sys.exit(1)
    niveaux = args.niveaux.split(",") if args.niveaux else None
    inv, matches = analyser_signal(args.csv, args.type_signal, niveaux)
    print(formater_lecture(inv, matches, niveaux))


if __name__ == "__main__":
    main()
