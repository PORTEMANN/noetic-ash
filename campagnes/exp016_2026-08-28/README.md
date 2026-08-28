# Campagne exp016 — couches n=7 et n=8, boîte 12000 (EXP-016) — DIVERGENT documenté (B3-FAIL)

Date : 2026-08-28. Attente EXP-016 figée AVANT mesure (bridge/expectations.json
v0.8.0, commit 712c1c4). Protocole C18 (protocole/PROTOCOLE_C18.md). Verdict
global : **DIVERGENT** — clause (c) tenue, clauses (a) et (b) falsifiées.

## Résultats

| Clause | Résultat | Détail |
|---|---|---|
| (a) ordre nodal ±5 % sur n=7 et n=8 | **FALSIFIÉE** | n=8 : ordre strict tenu sur 8 états (8k < 8i < 8h < 8g < 8f < 8d < 8p < 8s) ; n=7 : **inversion 7p/7s de −8,6 %** (> 5 %) |
| (b) ratios ∈ [1,45 ; 1,75], moy. géom. ≈ δ⁸ ±5 % | **FALSIFIÉE** | 18 ratios sur 28 hors bornes ou indéfinis (Rc nul au plancher) ; moyenne géométrique 2,77 (écart δ⁸ : +74 %) |
| (c) toutes Cosmologique | **TENUE** | 36/36 orbitales Cosmologique (Rc nul → ReN = 0 pour les états profonds) |

Observation secondaire déclarée (diagnostic boîte sur 8s/8p/8d, ratios 8/7
attendus < 1,45) : 8s/7s = 1,350 et 8p/7p = 1,228 conformes au diagnostic ;
8d/7d = 1,483 marginalement au-dessus (2 %) — diagnostic ni nettement confirmé
ni réfuté, consigné.

## Résultat scientifique central : la « loi δ⁸ » est réfutée comme loi universelle

La loi inter-couches Rc(n+1,l)/Rc(n,l) ≈ δ⁸ = 1,5874, calibrée à boîte 8000
(EXP-015) et proposée par la théorie (gamme tempérée CTFT, Tech_3_Moteurs
§9.1), **ne survit pas au changement de boîte** : à 12000, les ratios se
dispersent de 1,09 à 2,77 (hors joints profonds). Mécanisme : le Rc d'une
orbitale mono-bosse dépend de la position de la bosse relativement à la grille
tempérée (moiré), donc de la longueur du signal. La coïncidence avec δ⁸ à
boîte 8000 était un artefact de la boîte de calibration.

Faits positifs consignés : première couche n=8 complète mesurée — **ordre
nodal strict sur 8 états** ; l'inversion 7p/7s (8,6 %) fixe l'échelle des
jointures fragiles boîte-dépendantes (4p/4s 0,018 % à 4000 ; 4d/4p 1,9 % à
8000 ; 7p/7s 8,6 % à 12000) ; régime Cosmologique universel sur 36 orbitales.

## Défauts de formulation assumés

Comme pour EXP-015 (campagne sœur) : domaine des séries incluant les joints
profonds (2s/1s, 3s/2s… : Rc quasi-nul au plancher), bornes [1,45 ; 1,75]
excluant des valeurs de calibration, et — spécifique ici — tolérance de
jointure de 5 % alors que la calibration ne contenait qu'une inversion de
2 %. Ces défauts sont assumés publiquement (précédent EXP-013b).

## Reproduction

run/c18_runner.py régénère les 38 signaux octet-identiques (vérifié en
scratch, run/manifest_signaux.json) ; run/c18_analyse.py régénère signatures,
verdicts, évaluation des clauses et run/manifest.json (123 empreintes).
Témoins : C(ρ=1) = 1,3033212195 ; table n≤4 Balmer-exacte à 12000 ; contrôle
bruit43 octet-identique à exp013.
