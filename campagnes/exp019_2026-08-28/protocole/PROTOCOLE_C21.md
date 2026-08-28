# PROTOCOLE C21 — campagne exp019 (comma de Lt = détecteur de résurgence, graines aveugles 2031+2032)

Date : 2026-08-28. Attente : EXP-019 figée AVANT mesure
(bridge/expectations.json v1.1.0, commit 3f97c14). Graines 2031 et 2032
générées en aveugle (sha256 57c590a6a96f8c45… et 431e68fc823b74fe…, épinglés
dans run/attestation_graines2031_2032.json avant toute mesure).

## Objet

Tester la biconditionnelle découverte en exploration post-EXP-018 :
le comma noétique du résidu Lt est un **détecteur de résurgence** —

    BANDE (intervalle contigu ≥ 10 temps où Z(T) < −3)
      ⟺
    RÉSURGENCE (trou inter-épisodes ≥ 60 temps ET ≥ 3 épisodes après)

sur deux graines neuves aveugles (2031, 2032) de la relaxation E44
(protocole C14 volet a figé : N=48, A=1, γ=0,2, dt=0,1, 2048 pas).

## Définitions figées (avant mesure)

- **Épisode** : segment contigu de Lt > 0 (échantillonnage 0,4 temps).
- **Trou inter-épisodes** : durée Lt = 0 soutenue entre la fin d'un épisode
  et le début du suivant.
- **Résurgence** : max des trous ≥ 60 temps ET nombre d'épisodes après ce
  trou ≥ 3. (Calibration : trous 17,6–44,8 sans bande vs 79,2–108,8 avec ;
  reprises 6–10 dans les deux cas — le critère trou porte la marge.)
- **Bande** : intervalle contigu ≥ 10 temps où Z(T) < −3 (auto-comma du
  résidu SG-13, 60 surrogates graine 2019) — identique à C19/C20.

## Discipline temporelle (pilier 1)

| Date (2026-08-28, UTC) | Événement |
|---|---|
| matin–midi | Calibration comma : 2026, 2027, 2028, 2029 mesurées et publiées |
| 13:5x | Exploration du « seuil » Nv/Lt : seuil en t_eff réfuté (2030), discriminant résurgence trouvé (5/5) — consigné dans run/exploration_seuil_NvLt_resurgence_LOCAL.md |
| 15:04:45 | **Graine 2031 générée en AVEUGLE** — sha256 57c590a6a96f8c45… |
| 15:06:39 | **Graine 2032 générée en AVEUGLE** — sha256 431e68fc823b74fe… |
| 15:1x | EXP-019 figée (registre v1.1.0, commit 3f97c14) PUIS exécution C21 |

## Chaîne figée (= C19/C20 à l'identique)

1. **Runner** (`run/c21_runner.py`) : régénère les graines 2031 et 2032
   (SeedSequence(2031/2032)) ; témoins d'intégrité : régénération des graines
   2028 et 2029 (doivent être octet-identiques aux npz attestés d'exp017 et
   exp018) ; produit `signaux/e44_{nv,lt}_t_g{2031,2032}.csv`.
2. **Pipeline** (`run/c21_comma.py` = c20_comma.py à l'identique, clauses
   remplacées par le texte d'EXP-019) : zone par Nv ; résidus SG-51 (Nv) et
   SG-13 (Lt) ; auto-comma ; surrogates graine 2019 ; Rdyn vs bi-exponentielle
   (p0 figé) ; analyse de résurgence (définitions ci-dessus) sur Lt.
3. **Contrôles (statut H)** : bruit blanc graine 43, sinus période 12,
   série binaire d'activité de chaque graine (le timing seul doit suffire —
   calibration : bandes reproduites à ΔZ < 3).

## Clauses du falsifieur

Texte faisant foi : attente EXP-019. (a) biconditionnelle bande ⟺ résurgence
sur chaque graine ; (b) Nv significatif sur chaque graine ; (c) Rdyn ∈
[0,10 ; 0,30] sur chaque graine. Une seule clause suffit.

## Reproduction

`run/c21_runner.py` puis `run/c21_comma.py` — chaîne auto-vérifiable,
manifeste SHA-256, régénération testée en dépôt vierge avant publication.

## Statut

Protocole figé à la publication. Mesure exécutée après figement de l'attente
(registre v1.1.0, commit 3f97c14) sur les graines aveugles attestées.
