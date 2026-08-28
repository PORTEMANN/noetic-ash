# PROTOCOLE C18 — campagne exp016 (couches n=7 et n=8, boîte RMAX=12000)

Date : 2026-08-28. Attente : EXP-016 (bridge/expectations.json v0.8.0, commit
712c1c4 — figée AVANT mesure).

## Chaîne

1. Fond monopole ρ=1 : solveur L-BFGS-B (même code que C14–C17), témoin
   C(1) = 1,3033212195 (±1e-9), indépendant de la boîte.
2. Spectres radiaux : eigh_tridiagonal, Coulomb tronqué R_core=3,04,
   α=1/137,036, m=1, **boîte RMAX=NR=12000, dr=1** (addendum de boîte :
   4000 → 8000 → 12000 ; dr inchangé, donc grille ASH identique). Couches
   complètes n=1…8 (36 orbitales) — n≤6 re-mesurées : la clause (b) porte sur
   les séries à l fixe n=l+1…8 dans cette boîte.
3. Témoin d'intégrité : 4f boîte 12000 (même chaîne que C16, boîte étendue) —
   E = −1,664105e-6 (Balmer-exact).
4. Contrôle de spécificité : bruit blanc graine 43 (octet-identique à exp013,
   sha256 a3909a6b…).
5. Instrument figé : ASH v1.0.0 (run/ash_core.py,
   sha256 338dbda7b499fdc8…), f0=2⁻¹¹, fs=1, fenêtre 1024, nperseg=1024,
   5 octaves, RMS=1, agrégation médiane. Aucun post-traitement.

## État de liaison à 12000 (constaté avant déclaration)

n=7 complète liée (ratios Balmer 0,82–0,99) ; n=8 complète mais 8s/8p/8d
faiblement liés (0,18–0,31) — observation secondaire déclarée dans l'attente
(le diagnostic boîte prédit leurs ratios 8/7 sous 1,45).

## Falsifiabilité

Clauses (a) ordre nodal ±5 % sur n=7 et n=8, (b) ratios ∈ [1,45 ; 1,75] et
moyenne géométrique ≈ δ⁸=1,5874 ±5 % sur les séries n=l+1…8, (c) toutes
Cosmologique — évaluées par run/c18_analyse.py, consignées dans
run/evaluation_clauses.json. Les défauts de formulation de l'attente,
découverts en cours de calibration élargie, sont assumés dans le README.
