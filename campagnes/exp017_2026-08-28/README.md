# Campagne exp017 — comma noétique sur E44, graine aveugle 2028 (EXP-017) — FALSIFIÉE documentée (B3-FAIL)

Date : 2026-08-28. Attente EXP-017 figée AVANT mesure (bridge/expectations.json
v0.9.0, commit 65b192b). Graine 2028 générée en aveugle le 2026-08-28T12:21:43Z
(sha256 a3fc0e61c5eab17e… épinglé dans run/attestation_graine2028.json) ;
régénération par run/c19_runner.py vérifiée identique au fichier attesté.
Protocole C19 (protocole/PROTOCOLE_C19.md).

Verdict global : **EXP-017 FALSIFIÉE par la clause (a)** — clauses (b) et (c)
tenues. Première campagne sur une observable hors ASH (extension de
l'instrument) : le comma noétique Rdyn = inf_{T>0} ‖u(t+T) − u_mod(t+T)‖
(Theorie_Residus §2.3 éq. 4).

## Résultats (graine 2028, jamais inspectée avant la mesure)

| Clause | Contenu déclaré | Mesuré | Résultat |
|---|---|---|---|
| (a) récurrence Nv | bande contiguë ≥ 10 temps où Z(T) < −3, minimum dans [20 ; 35] | Z_min = −5,85 à T = 31,9 (dans la fenêtre ✓) ; 255 points sous −3 entre T = 13,8 et 45,7 ; mais **largeur contiguë max = 6,2 temps < 10** | **FALSIFIÉE** |
| (b) Lt sans bande | aucune bande Z < −3 sur ≥ 10 temps | aucune bande (Z_min = −0,47) | **TENUE** |
| (c) Rdyn borné | Rdyn ∈ [0,10 ; 0,30] | Rdyn = 0,1968 à T* = 0,1 | **TENUE** |

Contrôles (statut H) : bruit blanc graine 43 sans bande (Z_min = −2,81) ;
sinus période 12 : minima francs aux multiples (Z = −706) — le protocole
détecte une récurrence exacte quand elle existe.

## Lecture honnête

1. **Le critère déclaré échoue, le phénomène partiellement présent.** La
   récurrence de la modulation collective existe sur la graine 2028 (255
   points significatifs, minimum à T = 31,9 dans la fenêtre calibrée
   [20 ; 35]), mais elle est **fragmentée** : pas de bande contiguë de
   10 temps. Sur la graine 2026 (calibration), la bande était contiguë
   [10 ; 62] — la contiguïté n'est donc pas stable inter-graines. Le critère
   « bande ≥ 10 temps » était trop strict ; toute correction serait post-hoc
   et est refusée : la falsification est consignée telle quelle.
2. **La distinction Nv/Lt tient** (clause b) : le comptage de plaquettes
   garde une trace de la modulation du plateau, la longueur des boucles
   n'en garde pas — reproduit sur graine neuve.
3. **Le comma vs dynamique idéale tient** (clause c) : Rdyn = 0,197 (calibre
   2026 : 0,177) — le défaut de fermeture de la relaxation sur la
   bi-exponentielle idéale est borné et stable inter-graines (écarts 11 %).
   C'est le résultat le plus robuste de la campagne : le processus à
   événements ne se réduit pas à une relaxation lisse, avec une amplitude de
   défaut reproductible.
4. t_eff(2028) = 133,8 — plateau plus court que 2026 (~150) et 2027 (~199) :
   la variabilité inter-graines de la durée du plateau est confirmée ; la
   récurrence fragmentée pourrait en être la signature (moins de plateau →
   moins de contiguïté). Piste pour une éventuelle EXP-018, à déclarer
   AVANT toute nouvelle mesure.

## Discipline temporelle

Voir protocole C19 : calibration sur graine 2026 (publiée, C14), inspection
d'intégrité grossière de la graine 2027 consignée, graine 2028 aveugle
attestée avant figement de l'attente, mesure après figement. Aucune donnée
2028 n'a été lue avant l'exécution de run/c19_comma.py.

## Reproduction

```
python3 run/c19_runner.py   # régénère les 2 signaux (octet-identiques au npz attesté)
python3 run/c19_comma.py    # régénère evaluation_clauses.json + resultats_comma.json
```

Empreintes : run/manifest.json. Données sources : campagne exp013
(campagnes/exp013_2026-08-28, protocole C14), graine 2026.

## Corpus

Aucune signature ASH versée : le comma noétique n'est pas une observable de
l'instrument figé (le pont ne s'applique pas, regime_attendu = null — voir
notes d'EXP-017). Registre corpus inchangé (v0.7.0). Le verdict de la
campagne est porté par run/evaluation_clauses.json.
