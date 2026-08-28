# Exploration locale — le comma noétique sur signaux réels CWRU (2026-08-28)

**Statut : exploration locale (H), non publiée.** Première application du
comma (pipeline figé C19) à des signaux réels hors E44 — corpus CWRU
(engineering.case.edu), capteur DE 12 kHz : sain (97, 20,3 s) et défaut
d'anneau interne (105, 10,1 s). Décide d'une éventuelle EXP-022 à déclarer
AVANT mesure.

## Ce qui a été mesuré

Pipeline C19 (résidu SG, auto-comma, 40 surrogates graine 2019) appliqué :
(a) à l'enveloppe de Hilbert (le protocole vibration_hf de l'ASH) ;
(b) au signal brut, courts retards (0–30 ms) et au lag caractéristique du
défaut.

## Résultats

1. **Le comma répond aux deux signaux réels** — c'est le premier point : la
   chaîne, conçue sur E44, tourne sur un signal de capteur industriel sans
   aucune modification.

2. **Enveloppe de Hilbert** : les deux signaux montrent une récurrence forte
   à long retard (modulation lente) — sain : Z_min = −13,3 à T = 266 ms ;
   défaut : Z_min = −37,5 à T = 167 ms. Non discriminant en l'état (les deux
   sont significatifs, à des retards différents). **Confondant identifié** :
   le sain a sa propre périodicité (rotation de l'arbre ~30 Hz → 33 ms et
   harmoniques) — le comma de l'enveloppe la voit, d'où les creux profonds
   du sain.

3. **Signal brut au lag du défaut (BPFI ≈ 6,16 ms / 162 Hz)** — le point
   discriminant : le comma y sépare les deux signaux, fenêtre par fenêtre
   (1 s) :
   - sain 97 : Z ≈ **+1,0** (six fenêtres, 0,95 à 1,19) — pas de récurrence
     au lag du défaut ;
   - défaut 105 : Z ≈ **−1,4 à −2,2** (quatre fenêtres) — récurrence
     présente mais sous le seuil −3 en fenêtre courte.
   Sur une fenêtre longue (2 s), le défaut atteint Z = −5,4 à T = 8,4 ms
   (proche du BPFI) et Z(BPFI) = −4,1, tandis que le sain reste hors
   structure au BPFI.

4. **Lecture** : le comma au lag du défaut sépare sain/défaut **en signe**
   (positif vs négatif) — le sain ne récurre pas à 6,2 ms, le défaut oui.
   Mais la magnitude dépend de la longueur de fenêtre (le seuil −3 exige
   ≥ 2 s). C'est le confondant à déclarer : la séparation est réelle mais sa
   calibration (fenêtre, seuil, lag) doit être figée AVANT mesure sur des
   fichiers non utilisés ici.

## Ce que ça change pour l'industrialisation

- Le comma **porte sur le réel** : il répond, il sépare, et son creux pointe
  le retard physique du défaut (BPFI).
- Mais l'observable « comma au lag caractéristique » exige de connaître le
  lag à l'avance (BPFI dépend du roulement) — pas agnostique tel quel. La
  version agnostique : balayer les lags et prendre le creux — mais alors le
  sain a aussi des creux (rotation). Le discriminant propre reste à formuler.
- Le point fort potentiel : le comma voit la récurrence **temporelle** du
  défaut (les impulsions), complémentaire de l'ASH spectral (qui voit les
  raies). Les deux ensemble = la vision « calendrier + spectre ».

## Vers une EXP-022 (à déclarer AVANT mesure)

Formulation possible, sur les 9 fichiers CWRU du corpus vibration_hf (sains
97/98/99, défauts 105/106/118/119/130/131) — dont les non utilisés ici
(98, 99, 106, 118, 119, 130, 131) sont neufs pour cette exploration :
« au lag caractéristique de chaque défaut (BPFI/BPFO/BSF, documentés CWRU),
le comma du signal brut sépare défectueux de sain (Z < 0 pour les
défectueux, Z ≥ 0 pour les sains) sur fenêtre figée de 2 s » — avec la
fenêtre, le détrending et les lags figés dans le protocole. La question
agnostique (sans lag connu) resterait une clause secondaire ou une attente
ultérieure.

## Fichiers

Exploration en session IPython. Données : corpus public CWRU
(engineering.case.edu, fichiers 97.mat et 105.mat), non commitées (règle
C13.1 §3 — téléchargeables).
