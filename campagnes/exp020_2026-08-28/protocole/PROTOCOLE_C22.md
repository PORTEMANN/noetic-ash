# PROTOCOLE C22 — campagne exp020 (micro-rythme de la résurgence, graines aveugles 2033+2034)

Date : 2026-08-28. Attente : EXP-020 figée AVANT mesure
(bridge/expectations.json v1.2.0, commit 3d9efe8). Graines 2033 et 2034
générées en aveugle (sha256 f898992532eb90e2… et 16ac7e22ffad9247…,
épinglés dans run/attestation_graines2033_2034.json avant toute mesure).

## Objet

Fermer l'interprétation xAI de la résurgence avant industrialisation du
détecteur : la résurgence est-elle le redémarrage du MÊME processus ?
Testé par la distinguabilité des distributions d'espacements inter-épisodes
des actes 1 et 2 (test de permutation bilatéral sur l'écart des médianes,
10 000 tirages, graine 7 figée, seuil p < 0,05).

## Définitions figées (avant mesure, reprises d'EXP-019)

- **Épisode** : segment contigu de Lt > 0 (échantillonnage 0,4 temps).
- **Trou inter-épisodes** : durée Lt = 0 soutenue entre deux épisodes.
- **Résurgence** : trou max ≥ 60 temps ET ≥ 3 épisodes après ce trou.
- **Acte 2** : épisodes après le trou maximal ; acte 1 : les précédents.
- **Seuil de puissance** : la clause (a) n'est évaluée que si l'acte 2 a
  ≥ 5 épisodes (sinon hors domaine, consignée).
- **Bande** : intervalle contigu ≥ 10 temps où Z(T) < −3 (auto-comma du
  résidu, 60 surrogates graine 2019) — identique à C19/C20/C21.

## Chaîne figée (= C21 à l'identique + test de permutation)

1. **Runner** (`run/c22_runner.py`) : régénère les graines 2033 et 2034 ;
   témoins d'intégrité : graines 2028 et 2029 (octet-identiques aux npz
   attestés d'exp017/exp018) ; produit `signaux/e44_{nv,lt}_t_g{2033,2034}.csv`.
2. **Pipeline** (`run/c22_comma.py`) : pipeline comma C19 figé + analyse de
   résurgence (définitions ci-dessus) + test de permutation acte 1 / acte 2.
3. **Contrôles (statut H)** : bruit blanc graine 43, sinus période 12.

## Clauses du falsifieur (texte faisant foi : attente EXP-020)

(a) micro-rythme : sur une graine à résurgence avec ≥ 5 épisodes en acte 2,
distinguabilité p < 0,05 falsifie ; (b) Nv significatif ; (c) Rdyn ∈
[0,10 ; 0,30]. Domaine : sans résurgence ou acte 2 < 5 épisodes, (a) est
HORS DOMAINE (graine consignée, non falsifiante) ; (b) et (c) restent
évaluées dans tous les cas.

## Correction de formulation assumée avant figement

La clause initialement envisagée (ratio des médianes à ±30 %) a été retirée
après calibration : le bootstrap montre des IC90 % trop larges (2029 :
[0,42 ; 3,63]) — une telle clause serait une loterie. Le test de permutation
sur les distributions est la formulation statistiquement honnête. Puissance
faible assumée et consignée dans les notes de l'attente.

## Reproduction

`run/c22_runner.py` puis `run/c22_comma.py` — chaîne auto-vérifiable,
manifeste SHA-256, régénération testée en dépôt vierge avant publication.

## Statut

Protocole figé à la publication. Mesure exécutée après figement de
l'attente (registre v1.2.0, commit 3d9efe8) sur les graines aveugles
attestées.
