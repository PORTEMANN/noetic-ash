# Exploration locale — le « seuil abrupt » Nv/Lt n'existe pas : c'est une structure de résurgence (2026-08-28)

**Statut : exploration locale (H), non publiée.** Suite de la falsification
d'EXP-018 clause (b). Question posée : le seuil de la distinction Nv/Lt entre
t_eff = 199,2 (2027, sans bande) et 201,3 (2029, avec bande) est-il réel ?

## Correction d'une erreur de calibration (assumée)

L'attente EXP-018 affirmait dans ses notes que la clause (b) — distinction
Nv/Lt — était « tenue sur 2026, 2027 et 2028 ». **C'était inexact pour 2027** :
la série Lt de la graine 2027 (témoin d'intégrité) n'avait jamais été passée
au pipeline comma avant cette exploration. Mesurée ici : **2027 présente une
bande Lt** (Z_min = −9,49, bande [26,4 ; 66,8]). La distinction Nv/Lt était
donc déjà rompue sur 2027 — non mesurée à la déclaration. Même classe
d'erreur que la clause (c) d'EXP-015 (clause déclarée sans vérification
complète de la calibration). Consigné.

## Tableau complet (pipeline C19 figé, 5 graines)

| graine | t_eff | bande Nv | bande Lt | trou max entre épisodes | épisodes après le trou |
|---|---|---|---|---|---|
| 2026 | 153,3 | oui | non (Z=−2,3) | 44,8 | 9 |
| 2027 | 199,2 | oui | **oui (Z=−9,5)** | **108,8** | 10 |
| 2028 | 133,8 | oui (fragmentée) | non (Z=−0,5) | 17,6 | 6 |
| 2029 | 201,3 | oui | **oui (Z=−16,6)** | **79,2** | 7 |
| 2030 | 204,8 | oui | non (Z=−0,5) | 29,6 | 9 |

Le « seuil abrupt entre 199,2 et 201,3 » **n'existe pas** : 2030 a le plateau
le plus long (204,8) et aucune bande Lt ; 2027 (199,2) en a une. Ni t_eff,
ni le nombre d'épisodes, ni la couverture ne discriminent.

## Discriminant trouvé : la résurgence

**La bande Lt apparaît si et seulement si la série présente une résurgence** :
un long silence entre épisodes de boucles (≥ 60 temps) **suivi d'une reprise**
(≥ 3 épisodes). Accord discriminant ↔ bande : **5/5 graines**.

- 2027 : silence de 108,8 temps puis 10 épisodes → bande ;
- 2029 : silence de 79,2 temps puis 7 épisodes → bande ;
- 2030 : pas de long trou inter-épisodes (29,6) → pas de bande ;
- 2026/2028 : activité continue (trous < 45) → pas de bande.

**Le timing suffit** : la série binaire d'activité (épisode = 0/1, sans les
amplitudes) reproduit les bandes de 2027 (Z = −12,0 vs −11,8 complet) et 2029
(Z = −12,4 vs −14,9 complet). Le comma lit la **structure temporelle des
événements**, pas leurs amplitudes. Un test synthétique à deux gaussiennes
lisses ne reproduit PAS la bande — il faut la structure fine multi-épisodes
(l'intermittence), pas deux bosses lisses.

## Interprétation physique (candidate, à valider)

Le plateau d'annihilation connaît parfois une **seconde vague de formation de
boucles fermées** après un silence prolongé — une résurgence de l'enchevêtrement
de vortex alors que le comptage de plaquettes (Nv) poursuit sa décroissance
modulée. Le comma noétique de Lt détecte cette structure à deux actes ; Nv la
porte toujours (modulation collective continue), Lt ne la porte que lorsqu'il
y a résurgence. La « distinction Nv/Lt » d'EXP-017/018 était donc un cas
particulier : l'absence de résurgence dans les graines regardées.

## Vers une EXP-019 (à déclarer AVANT mesure, graines neuves aveugles)

Formulation possible : « sur deux graines E44 neuves aveugles, la bande de
récurrence du résidu Lt (pipeline C19 figé) existe si et seulement si la
série présente une résurgence (trou inter-épisodes ≥ 60 temps ET ≥ 3 épisodes
après le trou) » — biconditionnelle, testée sur graines non vues.
ATTENTION : les 5 graines regardées (2026–2030) ont servi à la calibration —
2030 a été générée et analysée dans cette exploration ; toute attente porte
sur des graines ultérieures (2031+).

## Fichiers

Exploration en session IPython. Graine 2030 : /tmp/e44_g2030.npz (éphémère,
régénérable par la chaîne C19 avec SeedSequence(2030)). Grainne 2027 analysée
au comma pour la première fois ici (données : campagne exp013, C14 —
témoin d'intégrité des campagnes exp017/exp018).
