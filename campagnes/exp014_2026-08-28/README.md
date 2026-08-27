# exp014 — Note de calibration C15 : grille ASH étendue vers le bas sur les orbitales P1

**Échec de calibration documenté (B3-FAIL).** Date : 2026-08-28.

## Contexte

La campagne exp013 (protocole C14+A2, `campagnes/exp013_2026-08-28/`) a mesuré
les 10 orbitales radiales u_{n,l}(r) du hamiltonien P1 (fond monopole ρ=1,
boîte RMAX=NR=4000) sur la grille figée f0 = 2⁻⁸ : toutes lues Cosmologique
avec ReN ≡ 0 — **artefact de plancher de grille** (pic Welch du 1s à
f = 9,765625·10⁻⁴, sous le plancher ; Rtop ≡ 0 tue le numérateur de ReN).

Question posée ici : peut-on **calibrer** une grille plus basse qui
(a) lise le fondamental 1s Quantique (attente EXP-013b d'origine) et
(b) rende la structure nodale visible ?

## Cadre épistémique

Cette note **n'est pas une attente**. Le balayage a été effectué avant toute
déclaration : ajouter une EXP-014 à `bridge/expectations.json` maintenant
serait post-hoc, donc interdit par la règle de la maison. Conséquences :

- `bridge/expectations.json` (v0.5.0) **inchangé** ;
- registre corpus (v0.5.0) **inchangé** — pas de signature/verdict, statut
  exploration : consigné, rien n'est conclu au sens du pont ;
- la note est publiée comme **étude de calibration**, avec le même soin
  qu'une campagne (chaîne auto-vérifiable, empreintes épinglées).

## Méthode

Instrument figé : `run/ash_core.py` (ASH v1.0.0, sha256
`338dbda7b499fdc8…`), agrégation médiane identique à `c14_analyse.py`
(normalisation RMS=1, 5 octaves, fenêtre 1024 pts, overlap 0,5,
nperseg 1024, fs=1). Chaîne autonome `run/c15_calibrage.py` :

1. fond monopole ρ=1 (L-BFGS-B ; C = 1,3033212195, conforme à C14) ;
2. spectres P1 (`eigh_tridiagonal`, boîte A2 ; énergies identiques à C14,
   ex. 1s : −2,661006·10⁻⁵ vs Balmer −2,662568·10⁻⁵, ratio 0,9994) ;
3. balayage **f0 = 2⁻¹¹·2^(k/12), k = −10…+13** (2,74·10⁻⁴ … 1,03·10⁻³)
   sur les 10 orbitales (1s,2s,2p,3s,3p,3d,4s,4p,4d,4f) — 240 mesures ;
4. contrôles bruit blanc graine 43 et exp(−t/40) aux grilles k=0 et k=+2
   (paramètres ASH du volet a de C14 : fs=10, fenêtre 512, nperseg 256) ;
5. diagnostic « masse sous plancher » (fraction de √PSD Welch sous f0).

Sorties : `donnees/balayage_f0.csv`, `donnees/controles.csv`,
`donnees/resume.json` — empreintes dans `run/manifest.json`. Régénération
testée en dépôt vierge : octets identiques.

## Résultats

### (a) Le régime « 1s Quantique » n'est pas calibrable — rampe de divergence au bord du plancher

ReN(1s) en fonction de k (f0 = 2⁻¹¹·2^(k/12)) :

| k | f0 | ReN(1s) | régime |
|---|---|---|---|
| −10 | 2,740·10⁻⁴ | 0,838 | Cosmologique |
| −5 | 3,658·10⁻⁴ | 0,228 | Cosmologique |
| 0 | 4,883·10⁻⁴ | 4,313 | Méso |
| +2 | 5,481·10⁻⁴ | 8,555 | Méso |
| +3 | 5,807·10⁻⁴ | 11,122 | Quantique |
| +7 | 7,316·10⁻⁴ | 26,348 | Quantique |
| +11 | 9,218·10⁻⁴ | 56,638 | Quantique |
| **+12** | **9,766·10⁻⁴ = pic** | **0,000** | **Cosmologique (Rtop=0)** |
| +13 | 1,035·10⁻³ | 0,000 | Cosmologique |

Entre k=0 et k=+12, ReN passe de 4,31 à 56,64 puis **s'effondre à 0**
exactement quand f0 atteint le pic — 6 % de variation de f0 séparent
« Quantique saturé » de « invisible ». La masse spectrale sous le plancher
est pourtant constante (8,99 %, le seul bin DC) sur toute la rampe : ce n'est
pas de la troncature de masse. Le mécanisme est la **concentration en E1** :
quand f0 approche le pic par en dessous, le pic et son flanc raide tombent
dans la première octave → dominance D croît (2,08 → 8,10), entropie H
décroît (9,24 → 5,28), Rc décroît (1,41 → 0,73) → ReN = Rdyn·Rtop·D/(Rc·H)·100
diverge. **Aucun plateau stable en Quantique** : toute grille « calibrée »
pour lire 1s Quantique serait posée sur l'artefact de bord. Calibration
refusée.

Cause physique : la bosse spectrale du 1s est **large** (largeur ~1/a₀,
a₀ = 137 u.l., très supérieure à la position du pic). Quantique exige un
spectre étroit (Rc·H petit). L'attente EXP-013b « 1s Quantique » était donc
**mal fondée dès sa déclaration** — raisonnée par analogie avec le profil
étroit de C13.1, sans vérification de la largeur spectrale de l'orbitale.
Correction de fond consignée ici.

### (b) Structure nodale : succès partiel

- **Rc croît avec le nombre de nœuds radiaux (n−l−1) sur toutes les grilles
  testées** — indicateur le plus robuste de la note (ex. f0 = 2⁻¹², moyennes
  par groupe : ~100 → 151 → 219 → 278 pour 0→3 nœuds, hors 1s dont le pic
  est décalé d'une octave).
- ReN décroît strictement le long des séries l fixe (s : 1s>2s>3s>4s ;
  p : 2p>3p>4p) sur deux **plateaux** : k ≤ −3 et k = +1…+2.
- **Bande d'instabilité moiré** entre k = −2 et k = 0 : l'ordre vacille
  (mono_s faux à k=−1 et k=0, mono_p faux à k=−2) quand les raies de la
  grille balayent la bosse — l'instrument est sensible au placement fin,
  pas seulement au contenu.
- Rtop ne dépasse jamais 1 : le spectre d'une orbitale radiale reste
  mono-bosse ; l'hypothèse des notes d'EXP-013b (Rtop > 1 débloquant Rdyn)
  est réfutée sur cette famille de signaux.

### Spécificité

Contrôles bruit blanc (graine 43) et exponentielle pure aux grilles k=0 et
k=+2 : tous deux Cosmologique, ReN = 0, Rtop = 0 (contenu hors bande — test
trivial, aucune fausse alarme Quantique).

## Verdict de calibration

| Clause | Résultat |
|---|---|
| (a) 1s Quantique | **ÉCHEC** — atteint uniquement dans la rampe de divergence au bord du plancher ; artefact, calibration refusée |
| (b) structure nodale | **SUCCÈS PARTIEL** — ordre nodal présent sur plateaux via ReN, robuste partout via Rc ; bande moiré documentée |
| spécificité | conservée (trivial) |

## Piste qui reste ouverte

La structure nodale de P1 est visible par **Rc** (pression spectrale), pas
par le régime. Une future attente honnête devrait porter sur Rc (ou ReN
relatif) avec une grille déclarée dans un plateau de stabilité, et une valeur
prédictive testée sur des orbitales non utilisées ici (5s, 5p, … ou fond
ρ ≠ 1). Déclaration AVANT mesure, comme toujours.

## Reproduction

```
python3 run/c15_calibrage.py   # régénère donnees/ + run/manifest.json
```

Empreintes SHA-256 : `run/manifest.json`. Instrument : `run/ash_core.py`
(figé, sha256 `338dbda7b499fdc8ea00beb0ddc696270f47eda38253902edc77cba28eedeb0e`).

## Contenu publié

`README.md`, `run/c15_calibrage.py`, `run/ash_core.py`, `run/manifest.json`,
`donnees/balayage_f0.csv`, `donnees/controles.csv`, `donnees/resume.json`.
Registres (`expectations.json`, corpus) volontairement inchangés — voir
« Cadre épistémique ».
