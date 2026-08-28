# Addendum A1 — correction du modèle nul des surrogates (2026-08-28)

**B3-FAIL — correction d'instrument.** Un bug de la chaîne publiée a été
découvert après publication, lors du figement du module `comma_core.py`. Il
est corrigé ici, avec le même soin qu'une campagne.

## Le bug

`run/c25_comma.py` (fonction `comma_au_lag`) appelait `surrogate()` **deux
fois par tirage** — la différence de deux surrogates indépendants au lieu du
comma d'un même surrogate décalé. Le modèle nul était gonflé (≈ √2) et le
Z-score exagéré en magnitude. Détail complet et correction : campagne exp022,
protocole/ADDENDUM_A1.md ; chaîne corrigée : `run/comma_corrige.py` ;
évaluation corrigée : `run/evaluation_corrigee.json`.

## Périmètre

Confiné aux campagnes au lag caractéristique (exp022, exp023, exp024). Les
campagnes E44 (exp017–021) et vibration_hf ne sont pas affectées.

## Verdict révisé

**EXP-023 corrigée : FALSIFIÉE sur les deux clauses** (au lieu de : (a)
tenue, (b) falsifiée). **La conclusion centrale publiée ne tient pas au null
corrigé.**

- (a) mécanisme : au null corrigé, la loi « déclenchement ⟺ cohérence de
  phase au lag du défaut » est **falsifiée** sur la famille 14 mil aveugle —
  violations : 169 (AC = +0,074 mais Z = +0,33 : cohérent, ne déclenche pas),
  185 (AC = +0,099 mais Z = +0,08), 186 (AC = −0,121 mais Z = −4,89 :
  déclenche sans cohérence). La « confirmation du mécanisme sur famille
  aveugle » publiée était un artefact du modèle nul gonflé ;
- (b) spécificité : le sain 100 lit Z = −0,24 au BPFI (< 0) — falsifiée
  (comme publié).

**Correction de la lecture** : le comma au lag caractéristique, au null
correct, **n'est pas** un détecteur fiable de cohérence de phase sur ce
corpus. Ce qui tient sur CWRU reste la séparation spectrale (ReN,
vibration_hf). La leçon méthodologique est consignée : le modèle nul d'une
chaîne à surrogates doit être verrouillé et validé contre un cas connu avant
mesure.
