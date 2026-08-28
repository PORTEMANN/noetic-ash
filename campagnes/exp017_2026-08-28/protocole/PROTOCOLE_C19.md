# PROTOCOLE C19 — campagne exp017 (comma noétique sur dynamique E44, graine aveugle 2028)

Date : 2026-08-28. Attente : EXP-017 figée AVANT mesure (bridge/expectations.json
v0.9.0, commit 65b192b). Graine 2028 générée en aveugle le 2026-08-28T12:21:43Z,
sha256 a3fc0e61c5eab17e2a646bb0c7ea17d736ea2fcc8af9f9dc0bead7b47c4a9b3c
épinglé avant toute mesure (run/attestation_graine2028.json).

## Objet

Première campagne portant sur une observable que l'instrument ASH ne possède
pas : le **comma noétique** Rdyn (Theorie_Residus §2.3 éq. 4) — défaut de
fermeture temporelle entre dynamique effective et dynamique idéale :

    Rdyn := inf_{T>0} ‖u(t+T) − u_mod(t+T)‖_{L²}

appliqué à la relaxation de vortex E44 (GP amorti 3D, protocole C14 volet a
figé : N=48, A=1, γ=0,2, dt=0,1, 2048 pas, quench bruit blanc complexe).

## Discipline temporelle (pilier 1)

| Date (2026-08-28, UTC) | Événement |
|---|---|
| matin | Calibration : exploration du comma sur la graine 2026 (données C14 publiées) — consignée dans `run/exploration_comma_noetique_E44_LOCAL.md` |
| midi | Génération graine 2027 + inspection d'intégrité grossière (consignée : 4 phases, 970 sauts, effondrement t≈199 — aucune analyse de récurrence) |
| 12:21:43 | **Génération AVEUGLE graine 2028** — sha256 a3fc0e61… épinglé |
| 13:0x | EXP-017 figée (registre v0.9.0, commit 65b192b) |
| ensuite | Exécution C19 sur la graine 2028 |

La mesure porte sur la graine 2028 (aveugle). La graine 2027 sert de témoin
d'intégrité du runner (régénération octet-identique vérifiée en scratch).

## Chaîne figée

1. **Runner** (`run/c19_runner.py`) : régénère la graine 2028 par reprise
   exacte du volet a de c14_runner.py (e44_core.py blob 2baf8d8d…,
   SeedSequence(2028)) ; vérifie le sha256 contre l'attestation AVANT toute
   analyse ; régénère aussi la graine 2027 (témoin d'intégrité, doit être
   octet-identique à la génération du midi) ; produit
   `signaux/e44_nv_t_g2028.csv`, `signaux/e44_lt_t_g2028.csv` (format CSV
   canonique C14).
2. **Zone active** (règle figée, adaptative mais déterministe) : t ∈ [5 ; t_eff]
   où t_eff = premier instant où Nv(t) ≤ 1 de façon soutenue (10 pas
   consécutifs). Valeur sur 2028 inconnue à la déclaration.
3. **Détrending figé** : Savitzky-Golay fenêtre 51, ordre 3 (robustesse de
   calibration : bandes identiques pour fenêtres 31/51/71).
4. **Pipeline comma figé** (`run/c19_comma.py`) :
   - résidu r(t) = Nv − SG(Nv) ; r_L(t) = Lt − SG(Lt, fenêtre 13, ordre 3) ;
   - auto-comma C(T) = ‖r(t+T) − r(t)‖₂/‖r‖₂, T = 0,1 … L/2 (pas 0,1) ;
   - surrogates à phases randomisées : 60 tirages, SeedSequence(2019) figée ;
   - Z(T) = (C − μ_surr)/σ_surr ;
   - comma vs dynamique idéale : u_mod = bi-exponentielle ajustée (curve_fit,
     p0 = [1500, 8, 400, 100, 50], maxfev=50000 — figé), Rdyn =
     inf_T ‖Nv(t) − u_mod(t+T)‖/‖Nv‖.
5. **Contrôles (statut H, HORS-CONTRAT)** : bruit blanc de variance égale
   (graine 43), exponentielle pure bruitée à 10 %, sinus de période 12
   (validation positive du protocole : minima francs aux multiples),
   permutation des sauts (graine 11).

## Clauses du falsifieur (texte faisant foi : attente EXP-017)

(a) bande de récurrence du résidu Nv : intervalle contigu ≥ 10 temps où
Z(T) < −3, minimum dans [20 ; 35] ; (b) le résidu Lt n'en présente pas ;
(c) Rdyn ∈ [0,10 ; 0,30]. Une seule clause suffit à falsifier.

## Reproduction

`run/c19_runner.py` puis `run/c19_comma.py` — chaîne auto-vérifiable,
manifeste SHA-256, régénération testée en dépôt vierge avant publication.
