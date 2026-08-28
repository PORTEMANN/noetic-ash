# Campagne exp021 — micro-rythme de la résurgence E44, six graines aveugles 2035–2040 (EXP-021) — CONFORME ; observation consignée sur 2036 (B3-FAIL)

Date : 2026-08-28. Attente EXP-021 figée AVANT mesure (bridge/expectations.json
v1.3.0, commit cd1fc86). Six graines 2035–2040 générées en aveugle le
2026-08-28 (sha256 épinglés 18:13–18:16 UTC dans
run/attestation_graines2035_2040.json, avant toute mesure). Témoins
d'intégrité : graines 2028 et 2029 octet-identiques aux campagnes exp017 et
exp018. Protocole C23 (protocole/PROTOCOLE_C23.md).

Verdict global : **EXP-021 CONFORME** — clause (a) tenue sur les deux graines
applicables, (b) tenue sur les cinq graines applicables, (c) tenue sur les
six. **Observation consignée** : la graine 2036 présente une résurgence sans
bande Lt — la biconditionnelle d'EXP-019 n'est pas universelle (voir lecture).

## Résultats (six graines aveugles, jamais inspectées avant la mesure)

| Graine | t_eff | Résurgence | Bande Lt | (a) micro-rythme | (b) Nv | (c) Rdyn |
|---|---|---|---|---|---|---|
| 2035 | 162,0 | non (trou 39,6) | non | hors domaine | ✓ (−9,80) | ✓ (0,227) |
| 2036 | 146,0 | **oui** (trou 63,2, reprise 6) | **non** | ✓ p=0,222 (n1=20, n2=5) | ✓ (−9,72) | ✓ (0,195) |
| 2037 | 204,8 | oui (trou 66,4, reprise 3) | oui | hors domaine (acte 2 < 5) | ✓ (−10,23) | ✓ (0,193) |
| 2038 | 173,3 | **oui** (trou 120,4, reprise 8) | **oui** | ✓ p=0,280 (n1=10, n2=7) | ✓ (−8,05) | ✓ (0,208) |
| 2039 | 139,9 | non (trou 84,8, reprise 2 < 3) | non | hors domaine | ✓ (−8,36) | ✓ (0,212) |
| 2040 | 90,1 | non (trou 6,4) | non | hors domaine | hors domaine (t_eff < 130) | ✓ (0,186) |

**EXP-021 CONFORME** : (a) applicable sur 2/6 graines (2036, 2038), tenue sur
les deux (micro-rythmes indistinguables) ; (b) applicable sur 5/6, tenue sur
les cinq ; (c) tenue sur les six.

## Lecture honnête

1. **La clause centrale (a) est testée et tenue** : sur les deux graines à
   résurgence avec assez d'épisodes en acte 2, les distributions
   d'espacements des deux actes sont indistinguables (p = 0,222 et 0,280 —
   ni proches du seuil 0,05). Le récit xAI « le même processus redémarre »
   est désormais validé sur graines aveugles, dans la direction qui le
   tuait (une différence franche de rythme aurait falsifié). L'interprétation
   de la résurgence est fermée pour le détecteur.
2. **Observation consignée : 2036 a une résurgence sans bande Lt** (trou
   63,2 ≥ 60, reprise 6 ≥ 3, mais Z_min Lt non significatif). La
   biconditionnelle d'EXP-019 (bande ⟺ résurgence), validée 2/2 sur les
   graines 2031/2032, n'est donc **pas universelle** : à la marge du seuil
   de trou (63,2, juste au-dessus de 60), une résurgence peut ne pas
   produire de bande. Le critère de trou avait été déclaré dès EXP-019 comme
   le point fragile (marge ×1,3). Consigné sans réparation post-hoc : toute
   généralisation future du détecteur doit tenir compte de cette classe de
   cas marginaux.
3. **La clause de domaine apprise d'EXP-020 fonctionne** : la graine 2040
   (t_eff = 90,1) aurait falsifié (b) sans elle (Z = −2,72 ≥ −3) ; elle est
   consignée hors domaine par la règle déclarée. La règle apprise par
   falsification a été appliquée proprement à la campagne suivante.
4. **Rdyn tient sur les six** : 0,186 à 0,227 — série sur treize graines
   toujours dans [0,16 ; 0,23]. Le défaut de fermeture reste l'observable
   la plus stable du comma.
5. La chaîne est saine : témoins 2028/2029 octet-identiques, régénération
   scratch 15/15 octet-identiques (12 signaux + évaluation + manifestes).

## État de la série des commas après exp021

| Attente | Verdict | Fait établi |
|---|---|---|
| EXP-017 | FALSIFIÉE (a) | la fragmentation suit t_eff |
| EXP-018 | FALSIFIÉE (b), échelle tenue | T_sup ≈ 0,38·t_eff (confirmé sur aveugle) |
| EXP-019 | CONFORME (2/2) | comma de Lt = détecteur de résurgence |
| EXP-020 | FALSIFIÉE (b) | la bande exige une durée minimale de plateau |
| EXP-021 | **CONFORME** | la résurgence est le redémarrage du même processus (micro-rythme partagé) ; mais 2036 : la biconditionnelle bande ⟺ résurgence n'est pas universelle (marge du seuil de trou) |

## Discipline temporelle

Six graines aveugles attestées (18:13–18:16 UTC) AVANT le figement de
l'attente (commit cd1fc86), mesure après figement. Aucune valeur lue avant
l'exécution de run/c23_comma.py.

## Reproduction

```
python3 run/c23_runner.py   # régénère les 12 signaux + témoins 2028/2029
python3 run/c23_comma.py    # régénère evaluation_clauses.json
```

Empreintes : run/manifest.json. Données sources : campagne exp013
(campagnes/exp013_2026-08-28, protocole C14).

## Corpus

Aucune signature ASH versée : le comma noétique n'est pas une observable de
l'instrument figé (le pont ne s'applique pas, regime_attendu = null).
Registre corpus inchangé (v0.7.0). Le verdict est porté par
run/evaluation_clauses.json.
