# Campagne exp020 — micro-rythme de la résurgence E44, graines aveugles 2033+2034 (EXP-020) — FALSIFIÉE par (b), clause (a) hors domaine (B3-FAIL)

Date : 2026-08-28. Attente EXP-020 figée AVANT mesure (bridge/expectations.json
v1.2.0, commit 3d9efe8). Graines 2033 et 2034 générées en aveugle le
2026-08-28 (sha256 f898992532eb90e2… à 17:21:47Z et 16ac7e22ffad9247… à
17:22:38Z, épinglés dans run/attestation_graines2033_2034.json avant toute
mesure). Témoins d'intégrité : graines 2028 et 2029 octet-identiques aux
campagnes exp017 et exp018. Protocole C22 (protocole/PROTOCOLE_C22.md).

Verdict global : **EXP-020 FALSIFIÉE par la clause (b)** sur la graine 2034 —
la clause centrale (a) est hors domaine sur les deux graines (aucune
résurgence), la clause (c) tient sur les deux.

## Résultats (graines 2033 et 2034, jamais inspectées avant la mesure)

| Graine | t_eff | Résurgence | Bande Lt | Nv Z_min | Rdyn | (a) | (b) | (c) |
|---|---|---|---|---|---|---|---|---|
| 2033 | 135,5 | non (trou 39,2, reprise 6) | non | −6,55 | 0,176 | hors domaine | ✓ | ✓ |
| 2034 | **83,0** | non (trou 9,2, reprise 9) | non | **−2,81** | 0,184 | hors domaine | **✗** | ✓ |

## Lecture honnête

1. **La clause centrale (a) n'a pas été testée** : aucune des deux graines ne
   présente de résurgence (trous 39,2 et 9,2, sous le seuil déclaré de 60) —
   la clause est hors domaine par sa propre règle déclarée, consignée, non
   falsifiée. La question du micro-rythme reste ouverte ; elle exigera des
   graines à résurgence (en calibration : 2 sur 5 — la probabilité d'un
   double tirage hors domaine était réelle et assumée dans les notes de
   l'attente).
2. **La falsification vient de la clause auxiliaire (b)**, et c'est un
   résultat physique, pas un défaut de la chaîne : sur la graine 2034, le
   plateau est le plus court jamais mesuré (t_eff = 83,0 ; calibration :
   133,8 à 204,8), et le résidu Nv n'y atteint pas la significativité
   (Z_min = −2,81 ≥ −3). **La modulation collective du plateau a besoin
   d'une durée minimale pour émerger** — cohérent avec la loi d'échelle
   d'EXP-018 (la bande couvre ~38 % du plateau ; sous t_eff ≈ 85, la zone
   d'analyse est trop courte pour qu'une bande significative s'établisse).
   La calibration de la clause (b) (« Nv significatif sur les 5 graines »)
   portait sur des plateaux ≥ 133,8 — elle ne couvrait pas ce régime.
   Conséquence consignée : toute clause de significativité Nv sur graine
   neuve doit désormais porter une clause de domaine en t_eff (la règle de
   la maison, apprise une fois de plus par falsification).
3. **Rdyn tient** : 0,176 (2033) et 0,184 (2034) — série sur sept graines :
   0,177 / 0,197 / 0,198 / 0,224 / 0,160 / 0,176 / 0,184. Le défaut de
   fermeture du cycle temporel reste borné et stable, y compris sur le
   plateau le plus court — il ne dépend pas de la durée du plateau, contrairement
   à la bande de récurrence.
4. La chaîne est saine : témoins 2028/2029 octet-identiques, régénération
   scratch 7/7 octet-identiques (signaux + évaluation + manifeste).

## Correction de formulation assumée (avant figement)

La clause initialement envisagée pour (a) — ratio des médianes à ±30 % — a
été retirée après calibration (bootstrap : IC90 % [0,42 ; 3,63] sur 2029 —
une loterie, pas un test) et remplacée par le test de permutation. La
falsification par (b) n'est pas liée à cette correction.

## Discipline temporelle

Graines 2033/2034 aveugles attestées (17:21:47Z / 17:22:38Z) AVANT le
figement de l'attente (commit 3d9efe8), mesure après figement. Aucune valeur
lue avant l'exécution de run/c22_comma.py.

## Reproduction

```
python3 run/c22_runner.py   # régénère les 4 signaux + témoins 2028/2029
python3 run/c22_comma.py    # régénère evaluation_clauses.json
```

Empreintes : run/manifest.json. Données sources : campagne exp013
(campagnes/exp013_2026-08-28, protocole C14).

## Corpus

Aucune signature ASH versée : le comma noétique n'est pas une observable de
l'instrument figé (le pont ne s'applique pas, regime_attendu = null).
Registre corpus inchangé (v0.7.0). Le verdict est porté par
run/evaluation_clauses.json.

## Suite

La question centrale (micro-rythme de la résurgence) reste ouverte par hors
domaine. La suite naturelle : EXP-021 sur graines neuves, avec clause de
domaine en t_eff pour (b) (apprise ici) et — pour augmenter la probabilité
de tester (a) — plus de graines (la résurgence apparaît sur ~40 % des
graines en calibration).
