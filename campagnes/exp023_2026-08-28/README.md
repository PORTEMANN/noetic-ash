# ⚠️ CORRECTION (addendum A1, 2026-08-28) — verdict révisé

**EXP-023 corrigée : FALSIFIÉE sur les DEUX clauses — la « confirmation du
mécanisme » ne tient PAS.** Un bug du modèle nul des surrogates (double appel
au lieu d'un même surrogate décalé) gonflait le Z-score publié. Au null
corrigé, la clause (a) est falsifiée (169, 185, 186) : la loi de cohérence de
phase ne tient pas. Voir `protocole/ADDENDUM_A1.md` ; évaluation corrigée :
`run/evaluation_corrigee.json` ; chaîne corrigée : `run/comma_corrige.py`.
Le dossier d'origine est conservé pour la provenance. État publié d'origine :
FALSIFIÉE par la clause (b), mécanisme tenu.

---

# Campagne exp023 — le comma au lag caractéristique est un détecteur de cohérence de phase, famille CWRU 14 mil aveugle (EXP-023) — FALSIFIÉE par (b), mécanisme tenu (B3-FAIL)

Date : 2026-08-28. Attente EXP-023 figée AVANT mesure (bridge/expectations.json
v1.5.0, commit 1865b0e). Corpus public CWRU (engineering.case.edu, capteur DE
12 kHz, roulement 6205-2RS, ~1797 tr/min). Calibration déclarée : les 9
fichiers d'exp022 (consignés dans run/exploration_coherence_phase_CWRU_LOCAL.md).
Test aveugle : 7 fichiers jamais lus (100 sain load 3 ; 169, 170 interne ;
185, 186 bille ; 197, 198 externe — famille 14 mil), téléchargés après
figement. Protocole C25 (protocole/PROTOCOLE_C25.md).

Verdict global : **EXP-023 FALSIFIÉE par la clause (b)** — la clause centrale
(a), le mécanisme de cohérence de phase, **tient** sur la famille aveugle.

## Résultats (7 fichiers aveugles ; fenêtre 2 s figée)

### Clause (a) — mécanisme (déclenchement ⟺ cohérence de phase) : **TENUE**

| Fichier | Type | Lag du défaut | AC au lag | Z au lag | Signe |
|---|---|---|---|---|---|
| 169 | interne | BPFI | +0,074 | −2,38 | ✓ tenu |
| 170 | interne | BPFI | +0,042 | −1,29 | hors domaine (\|AC\|<0,05), cohérent |
| 185 | bille | BSF | +0,099 | −2,93 | ✓ tenu |
| 186 | bille | BSF | −0,121 | +1,82 | ✓ tenu |
| 197 | externe | BPFO | −0,033 | +0,44 | hors domaine, cohérent |
| 198 | externe | BPFO | −0,025 | +0,32 | hors domaine, cohérent |

**Aucune violation du signe** : sur la famille aveugle, le comma déclenche
exactement quand le train d'impulsions est phase-cohérent à la période du
défaut (169, 185 : AC > 0 → déclenchement) et reste silencieux quand il ne
l'est pas (186 : AC < 0 → silence). La loi de fonctionnement du détecteur —
*le comma mesure la cohérence de phase, pas la présence du défaut* — est
**confirmée sur une famille neuve jamais calibrée**.

### Clause (b) — spécificité (le sain ne lit Z < 0 à aucun lag) : **FALSIFIÉE**

| Fichier | BPFI | BPFO | BSF |
|---|---|---|---|
| 100 (sain) | **−0,29** | +1,39 | +0,92 |

Le sain 100 lit **Z = −0,29 au BPFI** — négatif, donc une fausse alarme au
sens de la clause déclarée (le sain doit lire Z ≥ 0 partout). La magnitude
est faible (loin du seuil −3), mais la clause portait sur le signe ; la
falsification est consignée telle quelle.

## Lecture honnête

1. **Le mécanisme est confirmé, et c'est le résultat central** : la loi
   « déclenchement ⟺ cohérence de phase au lag du défaut », établie sur la
   famille 7 mil (9/9), tient sur la famille 14 mil aveugle (aucune
   violation, deux fichiers hors domaine mais cohérents). Le détecteur est
   désormais **compris** : il mesure la cohérence de phase du train
   d'impulsions à la période du défaut.
2. **La spécificité par le signe est trop stricte** : le sain 100 lit
   −0,29 au BPFI — un Z marginalement négatif, physiquement insignifiant
   (le seuil de significativité est −3). La clause (b) portait sur le signe
   seul ; une lecture « fausse alarme » n'a de sens qu'à magnitude
   significative. Conséquence consignée : toute clause de spécificité future
   doit combiner signe ET magnitude (|Z| ≥ un seuil), pas le signe seul.
   La falsification est réelle au regard du texte figé — elle est publiée
   sans réparation post-hoc.
3. **Observations hors clauses (consignées)** : 197 (externe) déclenche
   fortement au BSF (−3,83) et non à son BPFO — tir croisé ; 185 (bille)
   déclenche au BPFO comme au BSF. La sélectivité du lag n'est pas
   systématique ; la cohérence de phase à un lag donné n'est pas toujours
   spécifique du type de défaut.
4. **La série CWRU est cohérente** : sur les trois campagnes (vibration_hf
   spectral, exp022 séparation, exp023 mécanisme), le tableau qui émerge est
   — le ReN spectral sépare parfaitement sain/défectueux ; le comma au lag
   est un détecteur de cohérence de phase, spécifique en magnitude mais pas
   universel (les trains non cohérents y échappent).

## Discipline temporelle

Calibration déclarée (9 fichiers d'exp022) ; attente figée (v1.5.0, commit
1865b0e) ; 7 fichiers aveugles téléchargés après figement, mesurés sans
inspection préalable. Canal exact X{N}_DE_time (artefact corrigé).

## Reproduction

```
python3 run/c25_runner.py   # télécharge les 7 fichiers (corpus public CWRU)
python3 run/c25_comma.py    # régénère evaluation_clauses.json
```

Empreintes : run/manifest.json. Fichiers .mat CWRU publics, non commités
(règle C13.1 §3).

## Corpus

Aucune signature ASH versée (observable hors instrument figé, regime_attendu
= null). Registre corpus inchangé (v0.7.0). Verdict porté par
run/evaluation_clauses.json.

## Suite

Le détecteur est compris (cohérence de phase) et sa spécificité exige une
magnitude, pas un signe. Suite naturelle : une formulation de spécificité à
seuil de magnitude (|Z| ≥ 3) sur corpus neuve ; ou le couplage ASH (spectre)
+ comma (cohérence de phase) comme détecteur industriel complet — l'ASH
sépare sain/défaut, le comma dit si le train est phase-cohérent.
