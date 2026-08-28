# PROTOCOLE C17 — campagne exp015 (fond monopole ρ=2, boîte RMAX=8000)

Date : 2026-08-28. Attente : EXP-015 (bridge/expectations.json v0.7.0, commit
f7d4dea — figée AVANT mesure ; analyse sur v0.8.0, commit 712c1c4).

## Chaîne

1. Fond monopole ρ=1 (témoin) puis ρ=2 : solveur L-BFGS-B du fonctionnel C(ρ)
   (même code que C14 volet b / C15 / C16), grille ξ ∈ [0,30], 4096 points,
   ftol=1e-14, gtol=1e-10. Témoin : C(1) = 1,3033212195 (±1e-9).
2. Couplage fond → hamiltonien orbital (déclaré) : dans P1, ρ n'entre que par
   la taille du cœur — R_CORE(ρ) = 3,04/√ρ (longueur de cohérence de Higgs
   ∝ 1/√ρ dans le fonctionnel). ρ=2 : R_CORE = 2,149605.
3. Spectres radiaux : eigh_tridiagonal, Coulomb tronqué, α=1/137,036, m=1,
   boîte RMAX=NR=8000, dr=1, 9 premiers états par l. Couches complètes
   n=2…6 sur fond ρ=2 (21 orbitales, 6h incluse).
4. Témoin d'intégrité : 4f sur fond ρ=1 (R_CORE=3,04), même boîte —
   E = −1,664092e-6 (Balmer-exact).
5. Contrôle de spécificité : bruit blanc graine 43 (octet-identique à exp013,
   sha256 a3909a6b…).
6. Instrument figé : ASH v1.0.0 (run/ash_core.py,
   sha256 338dbda7b499fdc8…), f0=2⁻¹¹, fs=1, fenêtre 1024, nperseg=1024,
   5 octaves, RMS=1, agrégation médiane. Aucun post-traitement.

## Clause d'honnêteté (déclarée avec l'attente)

La valeur prédictive de la campagne est limitée par la physique du couplage :
le cœur ne touchant presque pas les orbitales liées (ΔRc ≤ 0,1 % attendu,
mesuré en exploration), la campagne est un **test de robustesse au cœur** et
un test de la loi δ⁸ sur données formellement nouvelles — pas une prédiction
risquée au sens fort. Les défauts de formulation de l'attente, découverts en
cours de calibration élargie, sont assumés dans le README (précédent
« ill-founded at declaration » d'EXP-013b).

## Falsifiabilité

Clauses (a) ordre nodal ±5 % par couche, (b) ratios ∈ [1,45 ; 1,75] et moyenne
géométrique ≈ δ⁸=1,5874 ±5 %, (c) toutes Cosmologique — évaluées par
run/c17_analyse.py, consignées dans run/evaluation_clauses.json.
