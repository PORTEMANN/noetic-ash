# PROTOCOLE C23 — campagne exp021 (micro-rythme de la résurgence, 6 graines aveugles 2035–2040)

Date : 2026-08-28. Attente : EXP-021 figée AVANT mesure
(bridge/expectations.json v1.3.0). Graines 2035–2040 générées en aveugle
(sha256 épinglés dans run/attestation_graines2035_2040.json avant toute
mesure).

## Objet

Tester la clause restée hors domaine dans EXP-020 : la résurgence est-elle le
redémarrage du MÊME processus ? — distinguabilité des distributions
d'espacements inter-épisodes des actes 1 et 2 (test de permutation bilatéral
sur l'écart des médianes, 10 000 tirages, graine 7 figée, seuil p < 0,05).
Six graines (résurgence sur ~40 % en calibration : ~2 attendues).

## Définitions figées (avant mesure, reprises d'EXP-019/020)

- **Épisode** : segment contigu de Lt > 0 (échantillonnage 0,4 temps).
- **Trou inter-épisodes** : durée Lt = 0 soutenue entre deux épisodes.
- **Résurgence** : trou max ≥ 60 temps ET ≥ 3 épisodes après ce trou.
- **Acte 2** : épisodes après le trou maximal ; acte 1 : les précédents.
- **Seuil de puissance** : clause (a) évaluée seulement si acte 2 a ≥ 5
  épisodes (sinon hors domaine, consignée).
- **Bande** : intervalle contigu ≥ 10 temps où Z(T) < −3 (auto-comma du
  résidu, 60 surrogates graine 2019).
- **Zone active** : t ∈ [5 ; t_eff], t_eff = premier Nv ≤ 1 soutenu sur
  10 pas.

## Chaîne figée (= C22 à l'identique)

1. **Runner** (`run/c23_runner.py`) : régénère les six graines 2035–2040 ;
   témoins d'intégrité : graines 2028 et 2029 (octet-identiques aux npz
   attestés d'exp017/exp018) ; produit `signaux/e44_{nv,lt}_t_g{2035..2040}.csv`.
2. **Pipeline** (`run/c23_comma.py`) : pipeline comma C19 figé + analyse de
   résurgence + test de permutation acte 1 / acte 2.
3. **Contrôles (statut H)** : bruit blanc graine 43, sinus période 12.

## Clauses du falsifieur (texte faisant foi : attente EXP-021)

(a) micro-rythme : sur une graine à résurgence avec ≥ 5 épisodes en acte 2,
distinguabilité p < 0,05 falsifie ; (b) robustesse Nv : sur une graine avec
t_eff ≥ 130 (clause de domaine apprise d'EXP-020), le résidu Nv doit
présenter ≥ 1 point Z < −3 ; (c) Rdyn ∈ [0,10 ; 0,30] sur chaque graine.
Domaine : (a) non évaluée si aucune graine applicable (consignée) ; (b) hors
domaine si t_eff < 130 ; (c) toujours évaluée.

## Reproduction

`run/c23_runner.py` puis `run/c23_comma.py` — chaîne auto-vérifiable,
manifeste SHA-256, régénération testée en dépôt vierge avant publication.

## Statut

Protocole figé à la publication. Mesure exécutée après figement de
l'attente (registre v1.3.0) sur les six graines aveugles attestées.
