# PROTOCOLE C20 — campagne exp018 (loi d'échelle temporelle du comma, graine aveugle 2029)

Date : 2026-08-28. Attente : EXP-018 figée AVANT mesure
(bridge/expectations.json v1.0.0, commit 0a4ffef). Graine 2029 générée en
aveugle le 2026-08-28T13:31:00Z, sha256
e247a223cd62e8ccbbcf2a409e4e95e5c81905473308e5f210c04b808daff0d7 épinglé
avant toute mesure (run/attestation_graine2029.json).

## Objet

Test de la loi d'échelle temporelle du comma noétique découverte en
exploration post-EXP-017 : la largeur contiguë maximale de la bande de
récurrence (Z < −3) du résidu Nv suit la durée du plateau d'annihilation :

    Wmax ≈ 0,61·t_eff − 70,8   (temps)

Mesure sur la graine 2029 (aveugle) de la relaxation de vortex E44
(protocole C14 volet a figé : N=48, A=1, γ=0,2, dt=0,1, 2048 pas).

## Discipline temporelle (pilier 1)

| Date (2026-08-28, UTC) | Événement |
|---|---|
| matin | Calibration comma sur graine 2026 (publiée C14) |
| midi | Graine 2027 générée, inspection d'intégrité grossière consignée |
| 12:21:43 | Graine 2028 générée en aveugle (sha256 a3fc0e61…) |
| 13:0x | EXP-017 figée (v0.9.0, commit 65b192b), puis mesurée : FALSIFIÉE clause (a) |
| 13:2x | Exploration post-falsification : relation Wmax ↔ t_eff découverte sur les 3 graines mesurées (consignée dans run/exploration_fragmentation_vs_teff_LOCAL.md) |
| 13:31:00 | **Graine 2029 générée en AVEUGLE** — sha256 e247a223cd62e8cc… épinglé dans run/attestation_graine2029.json, AUCUNE valeur lue |
| 13:4x | EXP-018 figée (registre v1.0.0, commit 0a4ffef) PUIS exécution C20 |

## Chaîne figée (= C19 à l'identique)

1. **Runner** (`run/c20_runner.py` = c19_runner.py avec SeedSequence(2029)) :
   régénère la graine 2028 en témoin (doit être octet-identique au npz attesté
   d'exp017) et la graine 2029 ; produit `signaux/e44_nv_t_g2029.csv` et
   `signaux/e44_lt_t_g2029.csv`.
2. **Pipeline** (`run/c20_comma.py` = c19_comma.py à l'identique) : zone
   t ∈ [5 ; t_eff] (t_eff = premier Nv ≤ 1 soutenu sur 10 pas) ; détrending
   SG-51 ordre 3 (Lt : SG-13) ; auto-comma C(T) = ‖r(t+T)−r(t)‖/‖r‖,
   T = 0,1 … L/2 ; 60 surrogates à phases randomisées graine 2019 ;
   Z(T) = (C − μ)/σ ; comma vs idéal (bi-exponentielle, p0 figé).
3. **Contrôles (statut H)** : bruit blanc graine 43, sinus période 12
   (validation positive), permutation des sauts graine 11.

## Clauses du falsifieur

Texte faisant foi : attente EXP-018 (version resserrée après revue des bornes).
(a1) existence : si t_eff ≥ 140, une bande contiguë ≥ 10 temps avec Z < −3
doit exister ; (a2) échelle : si une bande significative existe, son bord
supérieur T_sup ∈ [0,32 ; 0,44]·t_eff ; clause de domaine : si t_eff < 140,
(a1) est HORS DOMAINE (graine consignée, non falsifiée), (a2) reste évaluée ;
(b) Lt sans bande significative ; (c) Rdyn ∈ [0,10 ; 0,30].

Justification des bornes (revue du 2026-08-28, avant figement) : la droite
Wmax = 0,61·t_eff − 70,8 ajustée sur 3 points a des bornes quasi-vacueuses
aux petits t_eff ; le ratio T_sup/t_eff est trois fois plus serré
(dispersion ±11 % autour de 0,381, bornes ±15 % avec marge) et mesurable
même sur bande fragmentée. Seuil de domaine 140 : milieu conservateur entre
t_eff = 133,8 (bande fragmentée, 2028) et 153,3 (bande contiguë, 2026).

## Reproduction

`run/c20_runner.py` puis `run/c20_comma.py` — chaîne auto-vérifiable,
manifeste SHA-256, régénération testée en dépôt vierge avant publication.

## Statut

Protocole figé à la publication. Mesure exécutée après figement de l'attente
(registre v1.0.0, commit 0a4ffef) sur la graine 2029 aveugle attestée.
