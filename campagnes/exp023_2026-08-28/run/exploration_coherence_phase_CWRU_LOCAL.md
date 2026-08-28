# Exploration locale — pourquoi 118 tient et 119 non : le comma est un détecteur de COHÉRENCE DE PHASE, pas de régularité (2026-08-28)

**Statut : exploration locale (H), non publiée.** Suite de la falsification
d'EXP-022 clause (a) (2/5 défauts non détectés : 119 bille, 131 externe).
Question : pourquoi le comma déclenche-t-il sur 118 et pas sur 119 ?

**Note d'intégrité** : le canal du fichier 99 a été corrigé en cours
d'exploration (99.mat embarque aussi X098 ; le bon canal est X099_DE_time).
Voir addendum A1 de la campagne exp022.

## Ce qui a été testé (9 fichiers CWRU, tous mesurés)

Trois candidats discriminateurs, mesurés sur les 9 fichiers (2 sains, 7
défauts, fenêtre 2 s figée) :

1. **Régularité du calendrier des impulsions** (CV des intervalles inter-pics
   de l'enveloppe à la période du défaut) : 118 = 0,66 vs 119 = 0,61 —
   **ne sépare pas**. Rejeté.

2. **Périodicité de l'enveloppe au lag du défaut** (autocorrélation de
   l'enveloppe) : 131 = +0,79 (fortement périodique) mais ne déclenche pas ;
   118 = −0,09 mais déclenche — **contradictoire**. Rejeté.

3. **Cohérence de phase du signal brut au lag du défaut** (autocorrélation
   du brut détrendu à T = période du défaut) : **sépare parfaitement**.

## Le discriminant : signe de l'autocorrélation brute au lag

| fichier | type | AC brut à T | Z comma | accord |
|---|---|---|---|---|
| 105 | interne | +0,376 | −3,73 | ✓ |
| 106 | interne | +0,157 | −1,73 | ✓ |
| 118 | bille | +0,079 | −1,54 | ✓ |
| 119 | bille | −0,100 | +0,05 | ✓ |
| 130 | externe | +0,295 | −3,04 | ✓ |
| 131 | externe | **−0,417** | +0,52 | ✓ |
| 97 | sain | −0,358 | +1,48 | ✓ |
| 98 | sain | −0,235 | +1,44 | ✓ |
| 99 | sain | −0,043 | +0,49 | ✓ |

**Accord signe(AC) ↔ déclenchement : 9/9.** Corrélation AC vs (−Z) : +0,931.

Le comma au lag caractéristique déclenche **si et seulement si** le signal
brut est positivement autocorrélé à la période du défaut. 119 n'est pas
cohérent en phase à BSF (AC = −0,10) ; 131 est **anti-cohérent** à BPFO
(AC = −0,42 — son train d'impulsions est en alternance de phase : la forme
d'onde à t+T est l'inverse de celle à t).

## Le test « 2T » (train en alternance) — rejeté

Un train anti-corrélé à T devrait être cohérent à 2T (si x(t+T) = −x(t),
alors x(t+2T) = x(t)). Mesuré : 131 à 2×BPFO → Z = −0,65 (non significatif) ;
119 à 2×BSF → Z = −0,94 (non significatif). **Le sauvetage par 2T ne marche
pas** — 119 et 131 ne sont pas des trains périodiques en alternance propre,
mais des trains sans cohérence de phase stable. De plus les sains donnent des
fausses alarmes à 2×BPFI (98 : −2,30 ; 99 : −2,72) — le 2T est rejeté comme
clause (il dégrade la spécificité).

## Lecture physique (candidate, consignée)

Le comma au lag caractéristique n'est pas un détecteur de défaut : c'est un
détecteur de **cohérence de phase du train d'impulsions à la période du
défaut**. Un défaut déclenche le comma si ses impulsions se ressemblent d'une
période à la suivante (même forme, même phase). 105/106 (interne) et 130
(externe) sont cohérents ; 118 (bille) faiblement ; 119 et 131 non. La
régularité du calendrier (quand tombent les impulsions) ne suffit pas — il
faut que la *forme* se répète. Lecture candidate sur la physique du défaut :
l'alternance de phase de 131 suggère une modulation de polarité (charge /
glissement) ; à tester sur une famille neuve si on poursuit.

## Vers une EXP-023 (à déclarer AVANT mesure)

Le corpus aveugle disponible : les familles 14 mil et 21 mil (défauts plus
grands, jamais mesurés par cette chaîne). Formulation possible :
« sur les fichiers 14 mil aveugles, le comma au lag du défaut déclenche
(Z < 0) si et seulement si l'autocorrélation brute au lag est positive » —
test du mécanisme (la loi de fonctionnement du détecteur) sur une famille
neuve. Ou, plus physique : une clause sur la *prévalence* de la cohérence
de phase par type de défaut et par taille.

## Fichiers

Exploration en session IPython. Données : corpus public CWRU
(engineering.case.edu), non commitées (règle C13.1 §3).
