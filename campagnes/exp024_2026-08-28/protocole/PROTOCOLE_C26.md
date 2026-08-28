# PROTOCOLE C26 — campagne exp024 (spécificité du comma à magnitude + réplication du mécanisme, corpus aveugles)

Date : 2026-08-28. Attente : EXP-024 figée AVANT mesure
(bridge/expectations.json v1.6.0). Corpus public CWRU (engineering.case.edu).

## Objet

Corriger la spécificité du détecteur (leçon d'EXP-023 : le signe seul est trop
strict, la magnitude est le bon seuil) et répliquer le mécanisme de cohérence
de phase (validé 7 mil et 14 mil) sur une troisième famille. Deux corpus
aveugles : les canaux FE (fan-end) des sains (jamais analysés) et la famille
21 mil (jamais lue).

## Corpus et discipline

- **Calibration** (déclarée) : sains DE d'exp022/023 (Z ∈ [−0,29 ; +1,68]) ;
  mécanisme validé sur 7 mil (9/9) et 14 mil (sans violation).
- **Test aveugle** : (a) canaux FE des 4 sains (97, 98, 99, 100 — canaux
  jamais analysés) ; (b) famille 21 mil (209, 210 interne ; 222, 223 bille ;
  234, 235 externe). Mesurés après figement, sans inspection préalable.

## Chaîne figée (= C25 à l'identique)

1. **Runner** (`run/c26_runner.py`) : (a) extrait les canaux FE exacts
   `X{N}_FE_time` des .mat déjà téléchargés (97–100) ; (b) télécharge la
   famille 21 mil et extrait `X{N}_DE_time` exact ; écrit
   `signaux/cwru_{N}_{DE|FE}.csv` ; manifeste SHA-256.
2. **Pipeline** (`run/c26_comma.py`) : fenêtre 2 s (24000:48000), détrending
   SG(501, 3) ; comma au(x) lag(s), 40 surrogates graine 2019 ;
   autocorrélation du brut au lag du défaut (pour b).

## Clauses du falsifieur (texte faisant foi : attente EXP-024)

(a) spécificité à magnitude : un canal FE sain lit Z ≤ −3 à un des trois lags
falsifie ; (b) réplication du mécanisme : sur un fichier 21 mil, violation du
signe (Z<0 avec AC<0, ou Z≥0 avec AC>0) falsifie, zone morte |AC|<0,05 hors
domaine. Une seule clause suffit.

## Reproduction

`run/c26_runner.py` puis `run/c26_comma.py` — chaîne auto-vérifiable,
manifeste SHA-256. Les .mat CWRU sont publics (non commités, règle C13.1 §3).

## Statut

Protocole figé à la publication. Mesure exécutée après figement de
l'attente (registre v1.6.0) sur les corpus aveugles.
