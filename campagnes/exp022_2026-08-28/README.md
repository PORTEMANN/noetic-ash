# Campagne exp022 — comma au lag caractéristique sur roulements réels CWRU, 7 fichiers aveugles (EXP-022) — FALSIFIÉE par (a), spécificité tenue (B3-FAIL)

Date : 2026-08-28. Attente EXP-022 figée AVANT mesure (bridge/expectations.json
v1.4.0, commit e59c0d8). Corpus public CWRU (engineering.case.edu, capteur DE
12 kHz, roulement 6205-2RS, ~1797 tr/min). Calibration déclarée : fichiers 97
(sain) et 105 (interne) — les seuls lus avant figement (consignés dans
run/exploration_comma_CWRU_LOCAL.md). Test aveugle : 7 fichiers jamais lus
(98, 99, 106, 118, 119, 130, 131), téléchargés après figement. Protocole C24
(protocole/PROTOCOLE_C24.md).

Verdict global : **EXP-022 FALSIFIÉE par la clause (a)** — la spécificité (b)
tient. Première mesure du comma sur corpus réel hors E44.

## Résultats (7 fichiers aveugles ; Z au lag caractéristique, fenêtre 2 s figée)

| Fichier | Type | BPFI (6,17 ms) | BPFO (9,31 ms) | BSF (7,08 ms) | Clause (a) |
|---|---|---|---|---|---|
| 98 | sain | +1,44 | +0,36 | +1,68 | (b) ✓ |
| 99 | sain | +1,44 | +0,36 | +1,68 | (b) ✓ |
| 106 | interne | **−1,73** | +0,11 | −1,46 | ✓ (BPFI < 0) |
| 118 | bille | −2,33 | −1,31 | **−1,54** | ✓ (BSF < 0) |
| 119 | bille | +0,05 | −0,18 | **+1,49** | **✗ (BSF ≥ 0)** |
| 130 | externe | −0,13 | **−3,04** | −0,27 | ✓ (BPFO < 0) |
| 131 | externe | +0,52 | **+3,86** | −1,16 | **✗ (BPFO ≥ 0)** |

**Clause (a) FALSIFIÉE** : deux fichiers sur cinq (119 bille, 131 externe) ne
lisent pas Z < 0 au lag de leur défaut. **Clause (b) TENUE** : les deux sains
lisent Z ≥ 0 aux trois lags (pas de fausse alarme).

## Lecture honnête

1. **La séparation est réelle mais pas universelle** : trois défauts sur cinq
   lisent la récurrence à leur lag (106 interne −1,73, 118 bille −1,54, 130
   externe −3,04) ; deux n'y lisent rien (119, 131). Le mécanisme « le comma
   voit le calendrier des impulsions du défaut » est confirmé sur une
   majorité, mais pas sur tous — et les deux contre-exemples sont dans les
   familles **jamais calibrées** (bille et externe ; seul l'interne avait été
   calibré, sur 105, et son homologue 106 tient).
2. **La spécificité tient parfaitement** : aucun sain ne lit Z < 0 à aucun
   lag. Pas de fausse alarme — le comma au lag caractéristique ne crie pas au
   défaut sur un roulement sain. C'est la moitié industrielle de l'histoire,
   et elle est tenue.
3. **Valeur prédictive assumée** : les lags BSF et BPFO étaient entièrement
   neufs (jamais calibrés) — c'est là que la clause (a) tombe. Lecture
   candidate (consignée, non testée) : l'impulsion d'un défaut de bille ou
   d'anneau externe est moins régulièrement périodique que celle d'un défaut
   interne (glissement de la bille, charge variable sur l'externe) — le
   comma, qui cherche une *récurrence temporelle*, la perd quand le
   calendrier des impulsions est irrégulier. À tester si on poursuit.
4. **Complémentarité avec l'ASH confirmée dans son principe** : la campagne
   vibration_hf (EXP-010/011) séparait parfaitement ces 9 fichiers par le ReN
   spectral ; le comma y ajoute une lecture temporelle qui tient sur
   l'interne et une partie de la bille/externe. Les deux observables ne
   voient pas la même chose.

## Discipline temporelle

Calibration déclarée (97, 105) avant figement ; attente figée (v1.4.0,
commit e59c0d8) ; 7 fichiers aveugles téléchargés après figement, mesurés
sans inspection préalable. Formulation A (lag connu) choisie et validée —
la version agnostique (balayage des lags) reste une attente ultérieure.

## Reproduction

```
python3 run/c24_runner.py   # télécharge les 7 fichiers (corpus public CWRU)
python3 run/c24_comma.py    # régénère evaluation_clauses.json
```

Empreintes : run/manifest.json. Les fichiers .mat CWRU sont publics et
retéléchargeables (non commités — règle C13.1 §3).

## Addendum A1 — artefact de canal sur le fichier 99 (corrigé le 2026-08-28)

Le fichier `99.mat` du site CWRU embarque, en plus de ses propres canaux,
les canaux du fichier 98 (artefact déjà documenté dans la campagne
vibration_hf). La première version de `run/c24_runner.py` sélectionnait le
premier canal `DE_time` du dictionnaire — soit `X098_DE_time` au lieu de
`X099_DE_time` : le `signaux/cwru_99.csv` initialement publié mesurait donc
le canal de 98 (les Z publiés pour « 99 » étaient ceux du canal X098).

**Correction** : le runner sélectionne désormais le canal exact
`X{N}_DE_time` ; le fichier 99 a été re-mesuré au bon canal
(BPFI +0,49 / BPFO +0,85 / BSF +1,04). **Le verdict est inchangé** : la
clause (b) tient au bon canal (aucun sain ne lit Z < 0 à aucun lag), la
clause (a) reste falsifiée par 119 et 131. La correction porte sur
l'intégrité du signal, pas sur le résultat — consignée avec le même soin
(B3-FAIL s'applique aussi aux données).

## Corpus

Aucune signature ASH versée : le comma au lag caractéristique n'est pas une
observable de l'instrument figé (le pont ne s'applique pas, regime_attendu =
null). Registre corpus inchangé (v0.7.0). Le verdict est porté par
run/evaluation_clauses.json.

## Suite

La formulation A est validée comme *spécifique* (pas de fausse alarme) mais
pas comme *universelle* (2/5 défauts non détectés). Suites possibles :
EXP-023 sur la régularité du calendrier des impulsions par type de défaut
(pourquoi 118 tient et 119 non) ; ou la version agnostique (option B) pour la
recherche pure ; ou le couplage ASH + comma (spectre + calendrier) comme
détecteur industriel complet.
