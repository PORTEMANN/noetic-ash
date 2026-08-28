# PROTOCOLE C25 — campagne exp023 (le comma au lag = détecteur de cohérence de phase, famille 14 mil aveugle)

Date : 2026-08-28. Attente : EXP-023 figée AVANT mesure
(bridge/expectations.json v1.5.0). Corpus public CWRU (engineering.case.edu).

## Objet

Tester la loi de fonctionnement du détecteur identifiée après la
falsification d'EXP-022 : le comma au lag caractéristique n'est pas un
détecteur de défaut mais un détecteur de **cohérence de phase** du train
d'impulsions à la période du défaut — il déclenche si et seulement si le
signal brut est positivement autocorrélé à cette période. Famille neuve
(14 mil, défauts plus grands, jamais lue par la chaîne).

## Corpus et discipline

- **Calibration** (déclarée, consignée dans
  run/exploration_coherence_phase_CWRU_LOCAL.md) : les 9 fichiers d'exp022
  (97, 98, 99 sains ; 105, 106 interne ; 118, 119 bille ; 130, 131 externe).
- **Test aveugle** : 7 fichiers jamais lus — 100 (sain, load 3), 169, 170
  (interne 14 mil), 185, 186 (bille 14 mil), 197, 198 (externe 14 mil).
  Téléchargés après figement, mesurés sans inspection préalable.

## Chaîne figée

1. **Runner** (`run/c25_runner.py`) : télécharge les 7 fichiers aveugles ;
   extrait le canal exact `X{N}_DE_time` (artefact du 99 corrigé — exp022
   addendum A1) ; écrit `signaux/cwru_{N}.csv` ; manifeste SHA-256.
2. **Pipeline** (`run/c25_comma.py`) : pour chaque fichier — signal brut,
   fenêtre 2 s (échantillons 24000:48000), détrending SG(501, 3) ;
   autocorrélation du brut détrendu au(x) lag(s) ; comma au(x) lag(s), 40
   surrogates graine 2019, Z = (C − μ)/σ.

## Clauses du falsifieur (texte faisant foi : attente EXP-023)

(a) mécanisme : sur un fichier défectueux, violation du signe (déclenchement
Z < 0 avec AC < 0, ou silence Z ≥ 0 avec AC > 0) falsifie ; zone morte
consignée : |AC| < 0,05 au lag du défaut → hors domaine pour (a), non
falsifiant ; (b) spécificité : le sain (100) lit Z < 0 à un des trois lags
falsifie. Une seule clause suffit.

## Reproduction

`run/c25_runner.py` (télécharge le corpus public) puis `run/c25_comma.py` —
chaîne auto-vérifiable, manifeste SHA-256.

## Statut

Protocole figé à la publication. Mesure exécutée après figement de
l'attente (registre v1.5.0) sur les fichiers aveugles.
