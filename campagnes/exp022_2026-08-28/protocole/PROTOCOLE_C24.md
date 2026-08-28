# PROTOCOLE C24 — campagne exp022 (comma au lag caractéristique sur CWRU réel, 7 fichiers aveugles)

Date : 2026-08-28. Attente : EXP-022 figée AVANT mesure
(bridge/expectations.json v1.4.0). Corpus public CWRU (engineering.case.edu).

## Objet

Premier portage du détecteur de comma sur un corpus industriel réel : au lag
caractéristique de chaque défaut, le comma du signal brut sépare-t-il le
défectueux du sain ? Formulation ciblée (le capteur et le roulement sont
connus — le lag est documenté), complémentaire de l'ASH spectral (campagne
vibration_hf, EXP-010/011) : l'ASH voit les raies, le comma voit le
calendrier des impulsions.

## Corpus et discipline

- **Calibration** (déclarée, consignée dans
  run/exploration_comma_CWRU_LOCAL.md) : fichiers 97 (sain) et 105 (défaut
  interne) — les seuls lus avant le figement.
- **Test aveugle** : 7 fichiers jamais lus par cette chaîne — 98, 99 (sains),
  106 (défaut interne), 118, 119 (bille), 130, 131 (externe). Téléchargés
  après figement de l'attente, mesurés sans inspection préalable.

## Lags caractéristiques (documentés, roulement 6205-2RS JEM SKF, ~1797 tr/min)

| Défaut | Fréquence | Lag |
|---|---|---|
| anneau interne (BPFI) | 162 Hz | 6,17 ms |
| anneau externe (BPFO) | 107 Hz | 9,31 ms |
| bille (BSF) | 141 Hz | 7,08 ms |

## Chaîne figée

1. **Runner** (`run/c24_runner.py`) : télécharge les 7 fichiers aveugles
   depuis engineering.case.edu ; extrait le canal DE (capteur 12 kHz) ;
   écrit `signaux/cwru_{N}.csv` (format canonique, décimales figées) ;
   manifeste SHA-256.
2. **Pipeline** (`run/c24_comma.py`) : pour chaque fichier — signal brut,
   fenêtre de 2 s (échantillons 24000:48000), détrending SG(501, 3), comma au
  (x) lag(s) caractéristique(s), 40 surrogates à phases randomisées graine
   2019, Z = (C − μ_surr)/σ_surr.

## Clauses du falsifieur (texte faisant foi : attente EXP-022)

(a) séparation : un fichier défectueux lit Z ≥ 0 au lag de son défaut
(106→BPFI, 118/119→BSF, 130/131→BPFO) falsifie ; (b) spécificité : un fichier
sain (98, 99) lit Z < 0 à un des trois lags falsifie. Une seule clause
suffit.

## Reproduction

`run/c24_runner.py` (télécharge le corpus public) puis `run/c24_comma.py` —
chaîne auto-vérifiable, manifeste SHA-256.

## Statut

Protocole figé à la publication. Mesure exécutée après figement de
l'attente (registre v1.4.0) sur les fichiers aveugles.
