# Campagne exp015 — fond monopole ρ=2 (EXP-015) — DIVERGENT documenté (B3-FAIL)

Date : 2026-08-28. Attente EXP-015 figée AVANT mesure (bridge/expectations.json
v0.7.0, commit f7d4dea ; analyse sur v0.8.0, commit 712c1c4). Protocole C17
(protocole/PROTOCOLE_C17.md). Verdict global : **DIVERGENT** — clause (a)
tenue, clauses (b) et (c) falsifiées.

## Résultats

| Clause | Résultat | Détail |
|---|---|---|
| (a) ordre nodal par couche, tolérance 5 % | **TENUE** | aucune inversion > 5 % sur les 5 couches n=2…6 (21 orbitales) ; une quasi-dégénérescence consignée : 4d/4p −1,9 % (même jointure fragile qu'à ρ=1) |
| (b) ratios ∈ [1,45 ; 1,75], moy. géom. ≈ δ⁸ ±5 % | **FALSIFIÉE** | 5 ratios sur 14 hors bornes : 3s/2s = 56,28 ; 3p/2p = 73,79 ; 4d/3d = 2,84 ; 6d/5d = 1,437 ; 5f/4f = 1,216 ; moyenne géométrique 2,766 (écart δ⁸ : +74 %) |
| (c) toutes Cosmologique | **FALSIFIÉE** | 2s lit Méso (ReN = 1,53 ; Rc = 0,75 quasi-nul gonfle ReN ∝ 1/Rc) |

Faits positifs consignés : insensibilité au cœur — les Rc à ρ=2 égalent ceux à
ρ=1 à mieux que 0,03 % (le couplage R_CORE=3,04/√ρ est sans effet mesurable
sur les états liés) ; l'ordre nodal Rc par couche survit au changement de fond
et de boîte ; C(ρ=2) = 1,6676062896 (premier fond ρ=2 convergé et publié).

## Défauts de formulation assumés (précédent EXP-013b « ill-founded »)

La divergence est en grande partie due à des défauts de déclaration que nous
assumons publiquement, pas à une surprise de la nature :

1. **Domaine des séries** : la clause (b) incluait les joints profonds
   (3s/2s, 3p/2p), dont la calibration savait qu'ils sont hors échelle
   (~56–74, Rc des états n=2 quasi-nul à cette boîte).
2. **Bornes mal calibrées** : [1,45 ; 1,75] exclut des valeurs présentes dans
   la calibration elle-même (5f/4f = 1,216 et 6d/5d = 1,437 étaient mesurés à
   ρ=1 avant la déclaration).
3. **Clause (c) non vérifiée sur la calibration** : 2s lisait déjà Méso à
   boîte 8000 (ρ=1) avant la déclaration.

## Leçon pour la suite

- Toute attente d'échelle sur Rc doit être **normalisée par la position de la
  bosse spectrale** (moiré bosse/grille) ou déclarée boîte par boîte ;
- les domaines de séries doivent **exclure les joints profonds** (Rc quasi-nul,
  plancher de grille) au moment de la calibration ;
- la clause de régime doit être **vérifiée sur l'intégralité des données de
  calibration**, pas sur un échantillon.

La campagne sœur exp016 (boîte 12000) montre que la « loi δ⁸ » ne survit pas
au changement de boîte : elle est réfutée comme loi universelle.

## Reproduction

run/c17_runner.py régénère les 22 signaux octet-identiques (vérifié en
scratch, run/manifest_signaux.json) ; run/c17_analyse.py régénère signatures,
verdicts, évaluation des clauses et run/manifest.json (75 empreintes).
Instrument figé : ASH v1.0.0 (run/ash_core.py, sha256 338dbda7b499fdc8…).
