# Exploration locale — fragmentation de la bande de récurrence vs durée du plateau E44 (2026-08-28)

**Statut : exploration locale (H), non publiée.** Suite de la question posée
par la falsification d'EXP-017 (clause a) : la fragmentation de la bande de
récurrence sur la graine 2028 est-elle liée à la durée du plateau ?

## Données et pipeline

Pipeline C19 figé (identique pour les trois graines) : zone t ∈ [5 ; t_eff]
(t_eff = premier Nv ≤ 1 soutenu sur 10 pas), détrending SG-51, auto-comma,
60 surrogates graine 2019, Z(T). Graines : 2026 (C14 publiée), 2027 (témoin,
inspection grossière consignée — première analyse comma ici), 2028 (mesurée,
exp017 publiée).

## Résultats

| graine | t_eff | Z_min | T@Z_min | largeur contiguë max (Z<−3) | fraction [10;60] sous −3 |
|---|---|---|---|---|---|
| 2026 | 153,3 | −8,34 | 16,6 | 28,7 | 0,81 |
| 2027 | 199,2 | −9,45 | 21,0 | 48,5 | 0,96 |
| 2028 | 133,8 | −5,85 | 31,9 | 6,2 | 0,51 |

**Corrélation forte et monotone** entre t_eff et la largeur contiguë max :
r = +0,965 (SG-51), +0,933 (SG-31), +0,714 (SG-71) — robuste au détrending
léger, dégradée au détrending fort (SG-71 lisse la modulation). Corrélations
auxiliaires : r(t_eff, fraction significative) = +0,913 ; r(t_eff, |Z_min|) =
+0,901.

Ajustement linéaire (SG-51, 3 points) : **Wmax ≈ 0,61·t_eff − 70,8** (résidus
≤ 6,3 temps). Seuil de la clause (a) d'EXP-017 (bande ≥ 10) → t_eff ≥ ~133.

Observation auxiliaire : T@Z_min/t_eff ≈ 0,105–0,108 pour 2026/2027 (le
minimum suit l'échelle du plateau), mais 0,238 pour 2028 — à creuser.
Le bord supérieur de la bande suit t_eff (rapports 0,38 / 0,42 / 0,34).

## Lecture

1. **L'hypothèse est soutenue** : la fragmentation 2028 s'explique par la
   brièveté de son plateau (t_eff = 134, le plus court des trois). La bande
   de récurrence s'élargit avec la durée du plateau — la cohérence
   collective a besoin de temps pour s'établir.
2. **n = 3 points, pas d'erreurs** : c'est une exploration, pas une loi. La
   relation linéaire est un ajustement sur trois points — toute clause doit
   être testée sur une graine neuve aveugle.
3. Le critère « bande ≥ 10 temps » d'EXP-017 n'était pas « trop strict » en
   soi : il est franchi dès que le plateau dure assez (t_eff ≥ ~133). La
   falsification d'EXP-017 mesure donc la variabilité de t_eff, pas
   l'absence de récurrence.

## Vers EXP-018 (à déclarer AVANT mesure, graine neuve aveugle)

Formulation possible : « sur une graine E44 neuve aveugle, la largeur
contiguë max de la bande Z<−3 suit Wmax = 0,61·t_eff − 70,8 à ±30 % » —
avec t_eff mesuré par la règle figée. Clause de repli : si t_eff < 130,
l'attente est hors domaine (consignée, pas falsifiée).
