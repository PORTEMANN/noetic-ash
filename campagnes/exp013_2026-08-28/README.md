# Campagne exp013 — rapport local (EXP-013a / EXP-013b)

**Date : 2026-08-28. Statut : campagne LOCALE, non publiée. Protocole C14 + addenda A1, A2 (conservés, discipline « versions »).**
**Attentes déclarées AVANT mesure : `protocole/attente_EXP-013.json` (sha256 8edd18e87821902c…).**

## Résultat — les deux volets sont DIVERGENT (B3-FAIL consigné)

### Volet a — EXP-013a falsifiée (dynamique vortex E44)

| Signal | ReN | Rc | Rtop | Rdyn | régime lu | verdict |
|---|---|---|---|---|---|---|
| N_v(t) plaquettes | 168,16 | 0,071 | **10,0** | 0,559 | Quantique | DIVERGENT (clause a) |
| L(t) boucles | 27,45 | 1,076 | **10,0** | 0,552 | Quantique | DIVERGENT (clause a ; 1 fenêtre) |
| bruit graine 43 (H) | 0,33 | 25,15 | 13,0 | 0,434 | Cosmologique | HORS-CONTRAT |
| exp(−t/40) (H) | 0,00 | 0,035 | 0,0 | 1,000 | Cosmologique | HORS-CONTRAT |

La dynamique réelle (99 743 plaquettes → 0, annihilation complète) est lue Quantique comme les profils statiques de C13.1. **Mais la lecture a changé de nature** : Rtop = 10 (multi-pics, fallback LEX-013 levé, Rdyn réel ≈ 0,55) contre Rtop = 1 en C13.1. Ce qui sature ReN, c'est Rc : la pression spectrale d'une relaxation événementielle reste faible. Les contrôles se comportent sainement (bruit → cosmologique, exponentielle → cosmologique avec Rtop=0). L'instrument discrimine — il ne classe pas la relaxation vortex où on l'attendait.

### Volet b — EXP-013b falsifiée (orbitales P1), avec artefact de plancher

10/10 orbitales lues Cosmologique, ReN ≡ 0, Rtop ≡ 0. Diagnostic : le pic spectral du fondamental 1s est à f = 0,00025 cycle/unité r, **16× sous le plancher de grille figé** (f0 = 2⁻⁸ = 0,0039). L'instrument n'a jamais vu l'échelle propre des orbitales ; le verdict est marqué par la discrétisation — même catégorie que les artefacts de boîte publiés en P0/P4 par la machine elle-même. La question « structure nodale » reste OUVERTE : elle exige une grille descendant sous 10⁻³ (protocole futur, attente nouvelle).

## Ce que la campagne établit

1. Le passage statique → dynamique ne suffit pas : EXP-012 falsifiée sur profil, EXP-013a falsifiée sur processus. Le déterminant du classement Quantique n'est pas la pauvreté du signal (C13.1) mais la faiblesse de Rc dans les relaxations localisées.
2. L'instrument a un plancher basse fréquence opérationnel : sous f0, Rtop s'effondre à 0 et tout lit Cosmologique (volet b).
3. Les contrôles confirment que l'instrument n'est pas cassé : il lit le bruit et la monotone là où ils doivent être lus.

## Chaîne de preuve locale

- attente figée avant mesure ; protocole C14 + addenda A1 (condition initiale vacuante → quench Kibble-Zurek) et A2 (boîte P1 corrigée, table publiée reproduite : 1s ratio 0,9994, 2s/2p = 1,0000).
- 14 CSV signaux (%.10e, LF), 14 signatures, 14 verdicts — hashes consignés dans run/manifest.json.
- Fond monopole ρ=1 régénéré : C = 1,3033 (références : artefact 1,3098, campagne 1,3001, littérature 1,24–1,31).

## Contenu publié

- `protocole/` : PROTOCOLE_C14.md (figé), ADDENDUM_A1.md (condition initiale), ADDENDUM_A2.md (boîte P1), attente_EXP-013.json (déclarée avant mesure).
- `run/` : c14_runner.py (régénère les 14 CSV bit-à-bit), c14_analyse.py (régénère signatures + verdicts bit-à-bit), e44_core.py (copie figée, blob GitHub 2baf8d8d…), manifest.json (sha256 de tous les artefacts, CSV compris).
- `signatures/` (14), `verdicts/` (14).
- Les CSV ne sont pas commités (régénérables bit-à-bit par c14_runner.py ; empreintes épinglées dans run/manifest.json) — même règle que C13.1 §3.

Publication : EXP-013a/b ajoutées en append-only à bridge/expectations.json (v0.5.0) ; entrées SIG-040…SIG-053 au corpus noetic-ash-corpus (append-only). Règle B3-FAIL appliquée : les deux volets sont DIVERGENT et publiés tels quels ; l'artefact de plancher du volet b est publié comme artefact documenté (précédent : artefacts de boîte P0/P4 de la machine).
