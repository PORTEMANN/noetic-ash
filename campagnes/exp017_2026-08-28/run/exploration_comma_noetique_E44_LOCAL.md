# Exploration locale — comma noétique sur E44 (2026-08-28)

**Statut : exploration locale (H), non publiée.** Aucune attente figée, aucun
registre modifié. Décide d'une éventuelle EXP-017 à déclarer AVANT mesure.

## Définition testée

Theorie_Residus §2.3 (éq. 4) : **Rdyn := inf_{T>0} ‖u(x,t+T) − u_mod(x,t+T)‖_{L²(M)}**
— le comma noétique est le défaut de fermeture temporelle entre dynamique
effective et dynamique idéale (analogue continu du comma pythagoricien
(3/2)¹²/2⁷ ≈ 1,0136). §9.3 : observable de transduction néguentropique si
non nul mais borné (< Rcrit).

L'instrument ASH ne possède pas cette observable : son Rdyn (écart-type des
rapports log inter-pics) est bloqué au fallback 1.0 sur toutes les familles
mono-bosse (C15) — le comma est une piste complémentaire, pas un remplacement.

## Données

exp013 volet a (protocole C14) : `run/exp013a_raw.npz` — Nv(t) 2048 pas
(dt=0,1), Lt(t) 512 échantillons (tous les 4 pas). Structure : quench violent
(10⁵ → ~300), regonflement vers ~2000, plateau d'annihilations discrètes
(t ∈ [5 ; 152]), effondrement final à t ≈ 150. 797 sauts négatifs,
tailles médianes ~6, cascades jusqu'à ~9000.

## Protocole d'exploration

1. Auto-comma : C(T) = ‖u(t+T) − u(t)‖₂/‖u‖₂ sur le résidu détrendu
   (Savitzky-Golay, fenêtre 51, robustesse testée 31/71/101).
2. Comma vs dynamique idéale (version §9.3) : u_mod = bi-exponentielle
   ajustée ; Rdyn = inf_T ‖Nv(t) − u_mod(t+T)‖/‖Nv‖.
3. Comma fenêtré RMS=1 (style maison) sur Nv brut.
4. Contrôles : bruit blanc, exponentielle bruitée, sinus (validation du
   protocole : le sinus donne des minima francs à ses multiples, le bruit
   plat à √2) ; surrogates à phases randomisées (60 tirages, seuil ±3σ) ;
   permutation des sauts.

## Résultats

| Mesure | Résultat |
|---|---|
| Rdyn vs idéal (bi-expo) | **0,1768**, atteint à T* = 0,1 — le cycle ferme sans décalage temporel, mais avec un défaut de 17,7 % RMS : **comma non nul et borné**, signature attendue d'un processus dissipatif réel à événements (critère §9.3) |
| Auto-comma du résidu Nv | **bande de récurrence significative T ∈ [10 ; 62]**, Z_min = −8,8 à T ≈ 26,4 (jusqu'à −9,6 selon détrending) — robuste aux 4 détrendings testés |
| Comma des événements (−ΔNv) | minimum large en U vers T ≈ 25–35, cohérent avec la bande |
| Comma fenêtré sur Nv brut | ruptures de pente à T ≈ 6,1 ; 31,7 ; 44,5 |
| Auto-comma du résidu Lt | **aucune bande significative** (Z_min = −2,57) |
| Autocorrélation fine des sauts | 53 pics vs 55,9 ± 2,4 sur permutations — **non significatif** : pas de métronome d'annihilation |
| Alignement grille tempérée | ratios des minima : médiane 0,29 demi-ton, 37 % à < 0,25 demi-ton (hasard : 25 %/médiane 0,5) — **faible, non probant** |

## Lecture

1. **Le comma distingue les deux observables du même processus** : Nv porte
   une récurrence méso-échelle (T ~ 11–55), Lt n'en porte pas. C'est cohérent
   avec la clause (b) d'EXP-013a (les deux séries peuvent diverger) — le
   comptage de plaquettes garde la mémoire de la modulation du plateau,
   la longueur des boucles la perd.
2. **La récurrence n'est pas un métronome** : l'autocorrélation fine des
   sauts est indiscernable de permutations. Ce qui récurre, c'est la
   **modulation collective** du taux d'annihilation (paquets d'événements),
   pas les événements eux-mêmes.
3. **Pas d'alignement tempéré** : contrairement à la grille spectrale de
   l'ASH (f0·2^(n/12), justifiée par T1), les temps de récurrence E44 ne
   tombent pas sur la gamme tempérée — la structure temporelle de
   l'annihilation n'est pas celle de la grille spectrale. Fait à consigner
   honnêtement : le pont ASH↔machine ne passe pas par là.
4. Le minimum à T ≈ 26,4 : le plateau d'annihilation a une échelle de
   cohérence collective d'environ 26 unités de temps (≈ 1/6 de la durée du
   plateau). Ruptures du comma fenêtré à 6,1 / 31,7 / 44,5 compatibles.

## Leçon pour une éventuelle EXP-017

Si on déclare, la formulation honnête serait du type : « sur la dynamique de
relaxation E44 (protocole C14 figé, graine 2026), le comma noétique du résidu
Nv présente une bande de récurrence à Z < −3 contre surrogates à phases
randomisées, avec minimum dans [20 ; 35] ; le résidu Lt n'en présente pas »
— avec les contrôles (bruit, exponentielle, permutations) figés dans le
protocole. ATTENTION : la présente exploration a déjà vu les données —
toute attente serait calibrée, à tester sur une graine E44 neuve
(ex. graine 2027) jamais mesurée.

## Fichiers

Exploration exécutée en session IPython (figures /tmp/comma1..4.png,
non conservées par design). Reproduction : données
`campagnes/exp013_2026-08-28/run/exp013a_raw.npz` (régénérables par
`c14_runner.py`, octet-identique).
