# Campagne « signaux réels publics » — 2026-08-27

Première campagne de l'analyseur ASH (v1.0.0) sur des signaux réels publics,
avec le pont mesure ↔ interprétation (bridge v0.1.0) pour émettre signatures
(`ash-signature/0.1`) et verdicts (`ash-verdict/0.1`).

## Corpus

| Signal | Source publique | fs | Durée analysée | Domaine |
|---|---|---|---|---|
| MIT-BIH 100 | PhysioNet `mitdb` (wfdb) | 360 Hz | 100 s (MLII) | ecg |
| MIT-BIH 106 | PhysioNet `mitdb` (wfdb) | 360 Hz | 100 s (MLII) | ecg |
| NSRDB 16265 | PhysioNet `nsrdb` (wfdb) | 128 Hz | 30 s | ecg |
| CWRU 97 | engineering.case.edu, `97.mat` | 12 kHz | 1 s (DE) | vibration |
| CWRU 105 | engineering.case.edu, `105.mat` | 12 kHz | 1 s (DE) | vibration |

Les CSV bruts ne sont pas commités : ce sont des données publiques
retéléchargeables ; chaque signature porte le SHA-256 du CSV canonique
(`time,signal`, `%.10e`) pour vérification.

## Verdicts

| Signal | Régime mesuré | ReN | Attente | Verdict |
|---|---|---|---|---|
| mitbih_100_ecg | Cosmologique | 0.630721 | EXP-002 (E) | CONFORME |
| mitbih_106_ecg | Cosmologique | 7e-06 | EXP-009 (H) | EXPLORATION |
| nsrdb_16265_ecg | Cosmologique | 0.608946 | EXP-002 (E) | CONFORME |
| cwru_97_normal_vib | Quantique | 535.088186 | EXP-008 (E) | **DIVERGENT** |
| cwru_105_inner_vib | Quantique | 1904.415365 | EXP-003 (E) | CONFORME |

## Enseignements

1. **ECG consolidé sur réel** : trois enregistrements indépendants, tous
   cosmologiques — EXP-002 passe du synthétique P33+ au réel public.
2. **B3-FAIL publié sur CWRU** : le roulement *sain* lit quantique comme le
   défectueux. Le diagnostic spectral montre que l'énergie utile siège au-delà
   de la grille 10–320 Hz (≈1037 Hz sain, ≈3586 Hz défectueux) : EXP-003 et
   EXP-008 décrivent la grille simulée P34+, pas le roulement réel. Un domaine
   `vibration_hf` (grille haute fréquence) est requis — voir le rapport.

Le détail complet : `RAPPORT_campagne_signaux_reels.md`.
