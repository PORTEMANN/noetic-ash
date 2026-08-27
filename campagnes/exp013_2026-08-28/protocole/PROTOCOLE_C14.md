# PROTOCOLE C14 — campagne exp013 (EXP-013a / EXP-013b)

**Statut : figé avant mesure, le 2026-08-28. Campagne LOCALE — la publication GitHub est décidée après coup, artefact par artefact.**

Référence de l'attente : `protocole/attente_EXP-013.json` (sha256 préfixe `8edd18e87821902c`).
Discipline : C12.1 (protocole figé), B3-FAIL (résultats publiés quel que soit le verdict), append-only.

## Volet a — relaxation de vortex E44 (GP amorti)

Moteur : `src/core/e44_core.py` du dépôt noetic-machine (GP amorti 3D, vorticité plaquette, traceur de filaments), téléchargé tel quel (sha256 Git blob `2baf8d8dc6bc4d3a397f8d4e0ea6494950efc02a`).

Paramètres figés :
- Grille : N = 48 (périodique, 48³), dx = 1 (unité réseau, convention e44_core : k = 2π·fftfreq(N)).
- Propagateur : splitting de Strang de e44_core (`gp_linear`, `gp_step`), A = 1,0, γ = 0,2, dt = 0,1.
- Condition initiale : ψ = exp(iθ), θ champ de phase aléatoire gaussien filtré (graine numpy SeedSequence 2026 ; filtre spectral gaussien exp(−k²ξc²/2), ξc = 2 mailles), amplitude uniforme 1.
- Durée : 2048 pas (t ∈ [0, 204,8]).
- Séries enregistrées :
  - `N_v(t)` = nombre de plaquettes de vorticité non nulles (`nfaces` de e44_core.analyse… non : somme directe des wx,wy,wz ≠ 0), **à chaque pas** → 2048 échantillons, fs = 10 pas⁻¹.
  - `L(t)` = longueur totale des boucles fermées (somme des `len` des filaments fermés, trace_filaments), **tous les 4 pas** → 512 échantillons, fs = 2,5 pas⁻¹.
- Contrôles statut H (mêmes longueurs) : bruit blanc gaussien graine 43 (2048 pts) ; décroissance exponentielle pure exp(−t/τ), τ = 40 (2048 pts).

Analyse ASH (ash_core.py v1.0.0, sha256 `338dbda7b499fdc8…`) :
- `N_v(t)` : fs=10, f0=0,125 Hz, 5 octaves, fenêtre 512 pts (51,2 s), overlap 0,5, nperseg=256, agrégation médiane.
- `L(t)` : fs=2,5, f0=0,03125 Hz, 5 octaves, fenêtre 512 pts (204,8 s — couvre toute la série, 1 fenêtre), nperseg=256, overlap 0,5.
- Normalisation RMS = 1 obligatoire avant analyse (B3-FAIL #1), déclarée dans chaque signature.
- Contrôles : fs=10, f0=0,125, 5 octaves, fenêtre 512 pts, nperseg=256.

## Volet b — orbitales radiales P1

Fond monopole : ρ = 1 régénéré par l'artefact P0 (p0_monopole_su2.py, sha256 `52929bda0603…`, grille C13.1 : 4096 pts, ξmax = 30, L-BFGS-B, même code que la campagne monopole_ash).

Hamiltonien P1 (p1_etats_lies.py, sha256 Git blob `cfc05c221818965ee1413dd89726975a2f479af5a`… paramètres figés) :
- NR = 4000, RMAX = 40, dr = 0,01 ; M_E = 1 ; ALPHA = 1/137,036 ; R_CORE = 3,04.
- Potentiel : Coulomb tronqué V = −α/max(r, R_CORE).
- Diagonalisation : scipy eigh_tridiagonal, l = 0..3.
- Signaux retenus : u_{n,l}(r) pour (n,l) ∈ {1s, 2s, 2p, 3s, 3p, 3d, 4s, 4p, 4d, 4f} — 10 orbitales, 4000 pts chacune, axe r (pas ξ).

Analyse ASH : fs = 100 (pts par unité r), f0 = 0,125 cycle/unité r, 5 octaves, fenêtre 1024 pts (10,24 unités r), overlap 0,5, nperseg = 1024, agrégation médiane. RMS = 1 obligatoire.

## Formats et empreintes

- CSV canoniques `t,signal` (volet a) et `r,signal` (volet b), format `%.10e`, fins de ligne LF, en-tête inclus. Les CSV sont commitables localement ; leur sha256 est consigné.
- Signatures `ash-signature/0.1` (JSON indent=2, sort_keys, sans newline finale) ; verdicts via noetic_bridge v0.1.0 contre les attentes EXP-013a/b (fichier d'attentes local, NON publié sur GitHub à ce stade) ; horodatage figé `2026-08-28T00:00:00+00:00`.
- Verdicts attendus : volet a → EXP-013a (étiquette `gp_vortex_relax`) ; volet b → EXP-013b (étiquette `p1_orbitale_radiale`) ; contrôles → HORS-CONTRAT.

## Ce que cette campagne ne fait pas

- Elle ne touche pas au corpus publié (expectations.json GitHub reste à v0.4.0 — 12 attentes).
- Elle ne conclut rien sur P16 (hors champ : sortie classificatoire, pas de signal).
- Elle ne publie rien sans décision explicite.
