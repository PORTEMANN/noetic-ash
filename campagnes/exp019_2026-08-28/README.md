# Campagne exp019 — le comma noétique de Lt est un détecteur de résurgence (EXP-019) — CONFORME sur les deux graines aveugles

Date : 2026-08-28. Attente EXP-019 figée AVANT mesure (bridge/expectations.json
v1.1.0, commit 3f97c14). Graines 2031 et 2032 générées en aveugle le
2026-08-28 (sha256 57c590a6a96f8c45… à 15:04:45Z et 431e68fc823b74fe… à
15:06:39Z, épinglés dans run/attestation_graines2031_2032.json avant toute
mesure) ; régénérations vérifiées identiques aux fichiers attestés. Témoins
d'intégrité : graines 2028 et 2029 octet-identiques aux campagnes exp017 et
exp018. Protocole C21 (protocole/PROTOCOLE_C21.md).

Verdict global : **EXP-019 CONFORME sur les deux graines** — la première
attente entièrement tenue de la série des commas, et la première
biconditionnelle : le comma de Lt détecte la résurgence, dans les deux sens.

## Résultats (graines 2031 et 2032, jamais inspectées avant la mesure)

| Graine | t_eff | Résurgence (déf. figée) | Bande Lt | Biconditionnelle (a) |
|---|---|---|---|---|
| 2031 | 204,8 | **OUI** (trou 116,4 temps, reprise 4 épisodes) | **OUI** (Z = −10,79) | ✓ |
| 2032 | 204,8 | non (trou max 13,2) | non (Z = −1,55) | ✓ |

| Clause | Contenu déclaré | Mesuré | Résultat |
|---|---|---|---|
| (a) bande ⟺ résurgence | coïncidence sur chaque graine | 2031 : oui/oui ; 2032 : non/non | **TENUE (2/2)** |
| (b) Nv significatif | ≥ 1 point Z < −3 | 2031 : Z = −6,96 ; 2032 : Z = −11,78 | **TENUE (2/2)** |
| (c) Rdyn ∈ [0,10 ; 0,30] | borné | 2031 : 0,224 ; 2032 : 0,160 | **TENUE (2/2)** |

Contrôle (statut H) : la série binaire d'activité (timing seul, amplitudes
jetées) reproduit la bande Lt à |ΔZ| < 3 sur les deux graines (1,45 et 0,90)
— le comma lit la structure temporelle des événements, pas leurs amplitudes.

## Lecture

1. **Le comma noétique de Lt est un détecteur de résurgence** : il répond
   si et seulement si la série a un second acte — un silence prolongé
   (≥ 60 temps) suivi d'une reprise (≥ 3 épisodes). Les deux graines
   aveugles couvrent les deux cas (2031 avec, 2032 sans) : la
   biconditionnelle est testée dans les deux sens et tenue dans les deux.
2. **La chaîne causale de la journée se lit dans les verdicts** : EXP-017
   falsifiée (fragmentation) → la fragmentation suit t_eff ; EXP-018 :
   loi d'échelle T_sup ≈ 0,38·t_eff confirmée, mais distinction Nv/Lt
   réfutée ; l'exploration du seuil : pas de seuil en t_eff, un discriminant
   structurel ; EXP-019 : le discriminant validé sur graines aveugles.
   Quatre falsifications ont produit les faits qui ont fondé la première
   conformité complète.
3. **Rdyn : 0,177 / 0,197 / 0,198 / 0,224 / 0,160** sur cinq graines
   indépendantes — le défaut de fermeture du cycle temporel reste borné et
   stable (critère §9.3 : 0 < Rdyn < Rcrit) sur toute la série.
4. **Portée pour l'instrument agnostique** : la résurgence est une structure
   universelle de signal temporel (reprise après dormance — capteur de gaz,
   EEG, cybersécurité). Le comma la détecte avec une explication lisible :
   le Z-score pointe le T de la récurrence, la définition de la résurgence
   est trois lignes. C'est la première brique « interprétation » validée
   avant-lettre entre la théorie (machine noétique) et l'instrument (ASH
   étendu).

## Correction consignée

Les notes d'EXP-018 affirmaient la distinction Nv/Lt « tenue sur 2026, 2027
et 2028 » sans que la Lt de 2027 ait été mesurée — elle présente une bande
(découvert le 2026-08-28, consigné dans
run/exploration_seuil_NvLt_resurgence_LOCAL.md). L'erreur est celle déjà
identifiée sur la clause (c) d'EXP-015 : clause déclarée sans vérification
complète de la calibration. La leçon est désormais écrite dans les deux
README.

## Discipline temporelle

Voir protocole C21 : calibration sur 5 graines mesurées (2026–2030, toutes
consignées), graines 2031/2032 aveugles attestées avant le figement de
l'attente, mesure après figement.

## Reproduction

```
python3 run/c21_runner.py   # régénère les 4 signaux + témoins 2028/2029
python3 run/c21_comma.py    # régénère evaluation_clauses.json
```

Empreintes : run/manifest.json. Données sources : campagne exp013
(campagnes/exp013_2026-08-28, protocole C14).

## Corpus

Aucune signature ASH versée : le comma noétique n'est pas une observable de
l'instrument figé (le pont ne s'applique pas, regime_attendu = null).
Registre corpus inchangé (v0.7.0). Le verdict est porté par
run/evaluation_clauses.json.
