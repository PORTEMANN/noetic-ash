# Addendum A1 — correction du modèle nul des surrogates (2026-08-28)

**B3-FAIL — correction d'instrument.** Un bug de la chaîne publiée a été
découvert après publication, lors du figement du module `comma_core.py`. Il
est corrigé ici, avec le même soin qu'une campagne.

## Le bug

`run/c26_comma.py` (fonction `comma_au_lag`) appelait `surrogate()` **deux
fois par tirage** — la différence de deux surrogates indépendants au lieu du
comma d'un même surrogate décalé. Le modèle nul était gonflé (≈ √2) et le
Z-score exagéré en magnitude. Détail complet et correction : campagne exp022,
protocole/ADDENDUM_A1.md ; chaîne corrigée : `run/comma_corrige.py` ;
évaluation corrigée : `run/evaluation_corrigee.json`.

## Périmètre

Confiné aux campagnes au lag caractéristique (exp022, exp023, exp024). Les
campagnes E44 (exp017–021) et vibration_hf ne sont pas affectées.

## Verdict révisé

**EXP-024 corrigée : FALSIFIÉE sur les deux clauses** (au lieu de CONFORME).
La conformité publiée était un artefact du modèle nul gonflé.

- (a) spécificité à magnitude : le canal FE sain 98 lit Z = −3,30 au BSF
  (≤ −3) — fausse alarme significative ; la spécificité à magnitude ne tient
  pas au null corrigé ;
- (b) réplication du mécanisme : violation sur 209 (AC = +0,213 mais
  Z = +0,88 : cohérent, ne déclenche pas) — la loi de cohérence de phase ne
  se réplique pas sur la famille 21 mil au null corrigé.

**Correction de la lecture** : le détecteur de comma au lag caractéristique,
au null correct, ne satisfait ni la spécificité ni la loi de cohérence de
phase sur ce corpus. Le détecteur industriel présenté dans le README
d'origine n'est pas validé. Ce qui tient sur CWRU reste la séparation
spectrale (ReN, vibration_hf). La leçon méthodologique (verrouiller et
valider le modèle nul avant mesure) est consignée.
