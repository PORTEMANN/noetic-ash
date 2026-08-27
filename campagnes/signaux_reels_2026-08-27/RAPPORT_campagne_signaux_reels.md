# Campagne signaux réels publics — MIT-BIH & CWRU (2026-08-27)

Première campagne du pont mesure ↔ interprétation (bridge/, v1.2.0) sur des
**données réelles publiques** — après les 7 exemplaires synthétiques seedés.
Protocole C12.1 : noyau figé `ash_core` 1.0.0, grilles fixées par le domaine,
résultats publiés quelle que soit l'issue (B3-FAIL).

## Corpus (données réelles, sources publiques)

| Signal | Source | fs | Durée | Contexte |
|---|---|---|---|---|
| MIT-BIH record 100 | PhysioNet `mitdb`, canal MLII | 360 Hz | 100 s | ECG (sinusal + quelques APC) |
| MIT-BIH record 106 | PhysioNet `mitdb`, canal MLII | 360 Hz | 100 s | ECG arythmie marquée |
| NSRDB record 16265 | PhysioNet `nsrdb`, ECG1 | 128 Hz | 30 s | ECG normal longue durée |
| CWRU 97 | Bearing Data Center, canal DE | 12 kHz | 1 s | roulement **sain** |
| CWRU 105 | Bearing Data Center, canal DE | 12 kHz | 1 s | roulement **défaut inner race** |

## Verdicts

| Signal | Attente | Attendu | Mesuré | ReN (médiane) | Verdict |
|---|---|---|---|---|---|
| MIT-BIH 100 | EXP-002 | Cosmologique | Cosmologique | 0,63 | ✅ CONFORME |
| NSRDB 16265 | EXP-002 | Cosmologique | Cosmologique | 0,61 | ✅ CONFORME |
| MIT-BIH 106 | EXP-009 | — (exploration) | Cosmologique | ~0 | 🟡 EXPLORATION |
| CWRU 105 (défaut) | EXP-003 | Quantique | Quantique | 1904 | ✅ CONFORME |
| **CWRU 97 (sain)** | **EXP-008** | **Cosmologique** | **Quantique** | **535** | 🔴 **DIVERGENT** |

## Lecture — deux enseignements distincts

### 1. ECG (MIT-BIH) : la lecture ASH tient sur le réel

Les trois ECG réels — y compris le NSRDB longue durée cité dans le falsifieur
d'EXP-002 — sont classés **cosmologiques** (ReN médiane < 1), avec une minorité
de fenêtres méso (transitions QRS). Le falsifieur « des ECG normaux classés
majoritairement quantiques » n'est **pas** déclenché. EXP-002 passe du
synthétique seedé au réel public : son statut E est **consolidé**.

L'arythmie (record 106) reste cosmologique — l'instrument ne voit pas l'arythmie
comme de la torsion. Consigné en EXPLORATION (EXP-009, H) : aucune conclusion.

### 2. CWRU : B3-FAIL de campagne — la grille, pas l'invariant

**Le roulement sain CWRU est classé quantique** (ReN ≈ 535), tout comme le
défectueux (≈ 1904). L'attente EXP-008 (sain → cosmologique) est **infirmée**
sur ce protocole. Ce n'est pas une erreur de mesure mais une **inadéquation de
grille**, documentée :

| Signal | Énergie dominante | Part < 320 Hz (grille vibration f0=10, 5 oct) |
|---|---|---|
| CWRU 97 (sain) | ~1 037 Hz | 21,8 % |
| CWRU 105 (défaut) | ~3 586 Hz | **0,2 %** |

La grille vibration fixée par C12.1 (10–320 Hz) couvre les fréquences de
défaut *simulées* de l'exemple P34+ (BPFO ~129 Hz) mais **pas les raies
réelles CWRU** (kHz). Vu à travers la fenêtre de Welch, le contenu kHz se
projette sur la grille en un spectre riche multi-pics → ReN élevé → quantique,
**que le roulement soit sain ou non**. Le protocole ne sépare pas les deux.

**Conséquence** : le verdict « défaut = quantique » d'EXP-003, vrai en
synthétique, n'est **pas discriminant** sur CWRU réel — le sain donne la même
lecture. EXP-003 et EXP-008 doivent être relus comme des propriétés de la
*grille P34+ simulée*, pas du roulement réel. C'est un B3-FAIL publié :
l'instrument est correct, le protocole de grille ne couvre pas ce domaine.

## Piste documentée (non retenue comme résultat)

Une analyse par **enveloppe** (passe-bande autour des raies + détection de
chocs) est la démarche standard CWRU, et une grille acoustique (f0 = 100 Hz,
6 octaves) couvre le kHz. Aucune ne sépare nettement sain/défaut avec le ReN
seul dans cette configuration. La séparation exigerait soit une grille dédiée
(domaine `vibration_hf`), soit un invariant de texture de choc — **hors C12.1
actuel**. Consigné comme piste, statut H, jamais présenté comme résultat.

## Mises à jour induites

- EXP-002 : **consolidée** (réel MIT-BIH + NSRDB conformes).
- EXP-003 / EXP-008 : **relire** — propriété de la grille simulée P34+, non
  discriminant sur CWRU réel. Verdict DIVERGENT publié (B3-FAIL).
- EXP-009 : nouvelle (ECG arythmie, exploration H).
- Nécessité documentée : une campagne de grille haute fréquence pour la
  vibration réelle, à protocole figé ultérieur.

Signatures et verdicts : `campagnes/signaux_reels_2026-08-27/`.
Empreintes SHA-256 des signaux dans chaque signature (champ `signal.sha256`).
