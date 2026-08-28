# Campagne exp018 — loi d'échelle temporelle du comma noétique E44, graine aveugle 2029 (EXP-018) — FALSIFIÉE par (b), loi d'échelle tenue (B3-FAIL)

Date : 2026-08-28. Attente EXP-018 figée AVANT mesure (bridge/expectations.json
v1.0.0, commit 0a4ffef). Graine 2029 générée en aveugle le 2026-08-28T13:31:00Z
(sha256 e247a223cd62e8cc… épinglé dans run/attestation_graine2029.json) ;
régénération par run/c20_runner.py vérifiée identique au fichier attesté ;
témoin graine 2028 octet-identique à la campagne exp017. Protocole C20
(protocole/PROTOCOLE_C20.md).

Verdict global : **EXP-018 FALSIFIÉE par la clause (b)** — clauses (a1), (a2)
et (c) tenues. La loi d'échelle temporelle (objet central de l'attente) est
**confirmée sur graine aveugle** ; la distinction Nv/Lt (clause auxiliaire
tenue sur trois graines) est réfutée sur la quatrième.

## Résultats (graine 2029, jamais inspectée avant la mesure)

| Clause | Contenu déclaré | Mesuré | Résultat |
|---|---|---|---|
| (a1) existence | si t_eff ≥ 140 : bande contiguë ≥ 10 temps avec Z < −3 | t_eff = 201,3 ≥ 140 ; bande [8,4 ; 66,2] = **57,8 temps contigus** (Z_min = −12,16 à T = 17,9) | **TENUE** |
| (a2) échelle | T_sup ∈ [0,32 ; 0,44]·t_eff | T_sup = 82,0 ; ratio = **0,407** ∈ [0,32 ; 0,44] | **TENUE** |
| (b) Lt sans bande | aucune bande Z < −3 sur ≥ 10 temps | **deux bandes : [11,6 ; 64,8] et [65,6 ; 78,0], Z_min = −16,63** | **FALSIFIÉE** |
| (c) Rdyn borné | Rdyn ∈ [0,10 ; 0,30] | Rdyn = **0,1978** à T* = 0,1 | **TENUE** |

Contrôles (statut H) : bruit blanc graine 43 sans bande ; sinus période 12
détecté (validation positive du protocole).

## Lecture honnête

1. **La loi d'échelle temporelle tient** (a1 + a2) : la bande de récurrence
   du résidu Nv couvre 40,7 % du plateau (calibration : 34,2 / 37,8 / 42,4 %),
   et la contiguïté est revenue en force sur ce plateau long (57,8 temps
   contigus — le plus long des quatre graines). La falsification d'EXP-017
   est définitivement expliquée : la fragmentation 2028 était la brièveté de
   son plateau (t_eff = 133,8, sous le seuil de domaine 140). La
   proportionnalité bande ↔ plateau est le premier résultat quantitatif
   **confirmé sur graine aveugle** de la série des commas.
2. **La distinction Nv/Lt n'est pas universelle** (b falsifiée) : tenue sur
   2026 (t_eff = 153,3), 2027 (199,2) et 2028 (133,8), elle cède sur 2029
   (201,3 — le plateau le plus long mesuré). Lecture candidate : à plateau
   très long, la géométrie des boucles finit par porter aussi la mémoire
   collective — la distinction serait une propriété des plateaux courts et
   moyens, pas une loi. Seuil apparent entre 199,2 (sans bande) et 201,3
   (bande forte) — remarquablement abrupt ; à consigner comme piste, toute
   clause de seuil exigerait une déclaration dédiée.
3. **Rdyn est le résultat le plus stable de la série** : 0,177 (2026),
   0,197 (2028), 0,198 (2029) — le défaut de fermeture de la relaxation sur
   la bi-exponentielle idéale est borné et reproductible à ~11 % près sur
   trois graines indépendantes. Le comma noétique mesure quelque chose de
   réel et de stable dans la dynamique E44.
4. t_eff(2029) = 201,3 — la série des durées de plateau (133,8 ; 153,3 ;
   199,2 ; 201,3) confirme la variabilité inter-graines qui rend ces
   prédictions risquées au sens fort.

## Discipline temporelle

Voir protocole C20 : calibration sur trois graines mesurées (2026 publiée,
2027 témoin, 2028 exp017), graine 2029 aveugle attestée (13:31:00Z) AVANT le
figement de l'attente (commit 0a4ffef), mesure après figement. Aucune donnée
2029 n'a été lue avant l'exécution de run/c20_comma.py.

## Reproduction

```
python3 run/c20_runner.py   # régénère les 2 signaux + témoin 2028 (octet-identique à exp017)
python3 run/c20_comma.py    # régénère evaluation_clauses.json + resultats_comma.json
```

Empreintes : run/manifest.json. Données sources : campagne exp013
(campagnes/exp013_2026-08-28, protocole C14).

## Corpus

Aucune signature ASH versée : le comma noétique n'est pas une observable de
l'instrument figé (le pont ne s'applique pas, regime_attendu = null — voir
notes d'EXP-018). Registre corpus inchangé (v0.7.0). Le verdict de la
campagne est porté par run/evaluation_clauses.json.
