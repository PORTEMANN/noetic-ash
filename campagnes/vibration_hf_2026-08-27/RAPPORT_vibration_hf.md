# Campagne `vibration_hf` — roulements CWRU réels (2026-08-27)

Suite directe du B3-FAIL publié dans `../RAPPORT_campagne_signaux_reels.md` :
sur CWRU réel, la grille vibration P34+ (10–320 Hz sur le brut) lit le sain
comme le défectueux en quantique — l'énergie utile siège au-delà de la grille
(résonances ≈ 1–3,6 kHz). Cette campagne définit et éprouve le domaine
**vibration_hf**.

## Protocole déclaré (figé dans les signatures)

- **Prétraitement** : enveloppe de Hilbert du signal brut filtré 2–5 kHz
  (passe-bande Butterworth d'ordre 4), normalisée RMS = 1
  (`normalisation = "enveloppe_hilbert_2000-5000Hz_rms1"`).
- **Grille ASH** : fs = 12 000 Hz, f0 = 10 Hz, 5 octaves (10–320 Hz),
  fenêtre 0,5 s, overlap 0,5, nperseg = 2048.
- **Pourquoi l'enveloppe** : le diagnostic roulement standard (démodulation
  de résonance) montre que les fréquences de défaut — BPFO ≈ 107 Hz,
  BPFI ≈ 162 Hz, BSF/2 ≈ 71 Hz à 1797 tr/min — apparaissent dans le spectre
  d'enveloppe, donc *dans* la grille. Le brut, lui, est dominé par des
  résonances structurelles kHz sans structure de grille lisible.
- Corpus : 9 fichiers CWRU (engineering.case.edu), capteur DE 12 kHz,
  défauts 7 mil, charges 0–2 hp : sains 97/98/99, interne 105/106,
  bille 118/119, externe 130/131.

## Résultats (médianes de fenêtres, agrégation médiane)

| Fichier | Classe | ReN | Rtop | Rdyn | Rc | Bande dom. | Régime | Verdict |
|---|---|---|---|---|---|---|---|---|
| 97 | sain | 85,289 | 5 | 0,624 | 0,746 | E2 | Quantique | CONFORME (EXP-010) |
| 98 | sain | 67,399 | 6 | 0,636 | 0,485 | E2 | Quantique | CONFORME (EXP-010) |
| 99 | sain | 177,773 | 6 | 0,771 | 0,546 | E2 | Quantique | CONFORME (EXP-010) |
| 105 | interne | 1,831 | 5 | 0,385 | 1,090 | E5 | Méso | CONFORME (EXP-011) |
| 106 | interne | 2,317 | 5 | 0,382 | 1,128 | E3 | Méso | CONFORME (EXP-011) |
| 118 | bille | 3,976 | 6 | 0,615 | 1,345 | E2 | Méso | CONFORME (EXP-011) |
| 119 | bille | 4,131 | 6 | 0,534 | 1,263 | E2 | Méso | CONFORME (EXP-011) |
| 130 | externe | 17,932 | 4 | 0,306 | 1,433 | E4 | Quantique | CONFORME (EXP-011) |
| 131 | externe | 21,325 | 5 | 0,405 | 1,528 | E4 | Quantique | CONFORME (EXP-011) |

## Lecture

1. **Séparation sain / défectueux parfaite sur ce corpus** : sains
   ReN ∈ [67,4 ; 177,8], défectueux ReN ∈ [1,8 ; 21,3] — marge ×3,2.
   Seuil opérationnel proposé : ReN ≈ 30 (à éprouver hors CWRU).
2. **Le régime seul ne suffit pas** : sains et défauts externes lisent tous
   deux quantiques ; le discriminant est le couple (ReN, bande dominante).
   Lecture physique : le défaut imprime une modulation périodique
   (pression organisée, Rc > 1) qui effondre ReN ; l'enveloppe du sain est
   quasiment plate (Rc < 1), ReN élevé.
3. **Localisation indicative** : externe → E4 (BPFO ≈ 107 Hz, D ≈ 0,28–0,38),
   interne → E5/E3 (BPFI ≈ 160–162 Hz, D très faible), bille → non localisée
   (E2, modulation faible à cette taille de défaut). D = dominance des bandes
   est un second discriminant : élevée pour sain (ligne arbre en E2) et
   externe (BPFO franche), faible pour interne/bille.
4. **La normalisation RMS = 1 est obligatoire** : sans elle, ReN ∝ 1/amplitude
   (B3-FAIL #1) fait exploser le ReN du sain (5 427 au lieu de 85) et fausse
   toute comparaison inter-signatures.

## Honnêteté épistémique

- EXP-010 et EXP-011 sont des attentes **calibrées sur cette campagne** :
  leur valeur prédictive reste à tester (défauts 14/21 mil, charges 3 hp,
  autres machines, autres capteurs). Falsifieurs explicites dans
  `bridge/expectations.json` v0.3.0.
- Le protocole brut haute fréquence (grille f0 = 100 Hz, 6 octaves, sans
  enveloppe) a été testé et **rejeté** : tous les fichiers lisent quantiques
  (ReN 153–1432) sans séparation — la résonance kHz est sans structure de
  grille exploitable. Consigné ici pour mémoire.
- Artefact de données détecté en cours de campagne : le fichier `99.mat` du
  site CWRU embarque aussi les canaux X098 ; le canal exact `X099_DE_time`
  a été requis explicitement (sans cela, 98 et 99 donnaient des mesures
  strictement identiques).

## Reproduction

Données : `https://engineering.case.edu/sites/default/files/{N}.mat`,
N ∈ {97, 98, 99, 105, 106, 118, 119, 130, 131}. Canal `X%03d_DE_time`,
120 000 premiers points. Enveloppe : Butterworth 4, passe-bande 2–5 kHz,
`|hilbert(·)|`, division par RMS. Grille et agrégation : ci-dessus.
Chaque signature porte le SHA-256 du CSV canonique (`time,signal`, `%.10e`)
de l'enveloppe normalisée ; les CSV ne sont pas commités (données publiques,
prétraitement déterministe).
