# Addendum A1 — correction du modèle nul des surrogates (2026-08-28)

**B3-FAIL — correction d'instrument.** Un bug de la chaîne publiée a été
découvert après publication, lors du figement du module `comma_core.py`. Il
est corrigé ici, avec le même soin qu'une campagne.

## Le bug

`run/c24_comma.py` (fonction `comma_au_lag`) appelait `surrogate()` **deux
fois par tirage** :

```python
Cs = [ …( surrogate(r, rng)[:-k] − surrogate(r, rng)[k:] )… ]
```

soit la différence de **deux surrogates indépendants**, au lieu du comma d'**un
même surrogate décalé** (`s[:-k] − s[k:]`). Le modèle nul mesurait donc une
différence entre deux réalisations indépendantes (plus grande d'un facteur
≈ √2) au lieu du comma d'un surrogate. Le dénominateur du Z était gonflé et
le Z-score exagéré en magnitude — les résultats publiés étaient trop
« significatifs ».

## Périmètre

Confiné aux campagnes au lag caractéristique (exp022, exp023, exp024). Les
campagnes E44 (exp017–021) ne sont **pas** affectées : leur pipeline
appelait `surrogate()` une seule fois par tirage (modèle nul correct). La
campagne vibration_hf (spectral, ReN) n'utilise pas le comma — intacte.

## Correction

Le modèle nul corrigé est le comma du surrogate décalé (un seul surrogate par
tirage ; la normalisation par la norme du surrogate est identique à ‖r‖ par
Parseval). Chaîne corrigée : `run/comma_corrige.py` ; évaluation corrigée :
`run/evaluation_corrigee.json`. La forme buggée reproduit exactement les
valeurs publiées (méthode validée) ; la forme corrigée donne les valeurs
révisées.

## Verdict révisé

**EXP-022 corrigée : FALSIFIÉE sur les deux clauses** (au lieu de : (a) seule).

- (a) séparation : détectent 118 (−0,08), 119 (−0,20), 130 (−0,94) ; ne
  détectent pas 106 (+1,64), 131 (+0,41) — la séparation par le signe ne
  tient pas (106, homologue du fichier de calibration 105, échoue au null
  corrigé) ;
- (b) spécificité : le sain 98 lit Z = −1,62 au BPFO (< 0) — fausse alarme ;
  la spécificité par le signe ne tient pas non plus au null corrigé.

Le dossier d'origine (attente figée v1.4.0, valeurs publiées) reste pour la
provenance ; la présente correction porte le verdict révisé. La leçon est
consignée : **toute chaîne à surrogates doit verrouiller le modèle nul (un
seul surrogate, décalé) et être validée contre un cas connu avant mesure** —
le bug a été détecté précisément par cette validation (le module figé ne
reproduisait pas les valeurs publiées).
