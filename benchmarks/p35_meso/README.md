# Programme P35+ — Campagne d'étalonnage : à quoi répond l'instrument ?

**Objet.** Établir, sur des corpus à vérité terrain connue, à quoi
l'instrument ASH répond — et à quoi il ne répond pas. L'ASH est la couche
acquisition/mesure de l'écosystème ; comme tout instrument, il doit être
étalonné avant d'être interprété.

**Contexte.** Une piste d'analogie entre le régime Méso (1 ≤ ReN ≤ 10) et le
point auto-dual ρ* ≈ 0,75 du diagramme de phases de la machine noétique avait
été évoquée. Elle n'est **pas retenue** : l'ASH (industrie embarquée, xAI) est
antérieur à la machine noétique — ce sont des approches distinctes — et les
mesures ci-dessous montrent que le méso ne trace aucune frontière ordre/chaos.
Cette piste reste documentée dans les notes de LEX-004 (`lexicon/lexicon.json`).

## Protocole

Corpus **100 % déterministe** (aucun RNG, aucune donnée externe) :

| Famille | Signal | Paramètre balayé | Points |
|---|---|---|---|
| A | Logistique xₙ₊₁ = r·xₙ(1−xₙ), tenue 32 éch./itéré, fs = 250 Hz | r ∈ [3,40 ; 4,00], 61 valeurs (linspace) | 61 |
| B | (1−λ)·sinus 4 Hz + λ·chaos logistique (r=4) normalisé | λ ∈ [0 ; 1], 51 valeurs (linspace) | 51 |
| C | Tons à 4 Hz et 4·2^((12+δ)/12) Hz (octave désaccordée) | δ ∈ [0 ; 6] demi-tons, 13 valeurs | 13 |

Condition initiale X0 = 0,3 (à r=4, l'orbite issue de 0,5 est dégénérée :
0,5 → 1 → 0). Transitoire de 1000 itérés supprimé. 20 s analysées par point.
Reproduction : `python3 sweep_meso.py` → `results_p35_meso.csv`, dont le
SHA-256 est gelé dans `../SHASUMS.txt`.

## Résultats d'étalonnage

### Famille A — la naissance du chaos est invisible

| Zone de r | Lecture ASH |
|---|---|
| 3,40 – 3,73 (traverse r∞ = 3,56995) | **100 % cosmologique** sur toutes les fenêtres |
| 3,83 – 3,86 (fenêtre de période 3, ordonnée) | **100 % quantique** (Rtop = 4, Rdyn = 0,396) |
| 3,87 – 4,00 (chaos développé) | îlots épars de méso, max **55,6 %** des fenêtres à r = 3,98 |

L'accumulation de Feigenbaum — le moment précis où naît le chaos — ne laisse
aucune signature dans ReN. La fenêtre de période 3, qui est de l'ordre
dynamique pur, donne la lecture la plus « quantique » du balayage.

### Famille B — le mélange n'a pas de frontière

λ = 0 (ton pur) : méso, ReN ≈ 2,47. Dès λ > 0,34 : ReN → 0, régime
cosmologique. **0 % de fenêtres quantiques sur tout λ.** La transition est
monotone, sans couche intermédiaire méso.

### Famille C — Rdyn est aveugle au sub-demi-ton

Rdyn = 0 pour **toutes** les valeurs de δ ∈ [0 ; 6], alors même qu'une octave
désaccordée d'un demi-ton est nettement distinguée par l'oreille. Rdyn ne
résout pas les écarts inférieurs au pas de la grille (12 TET).

## Propriétés mesurées (lexique, statut C)

- **LEX-012** — L'ordre périodique multi-composantes est lu comme quantique
  (fenêtre de période 3 : Rtop = 4 pics alignés, Rdyn faible).
- **LEX-013** — Le ton pur est méso *par construction* : un seul pic sur la
  grille ⇒ Rdyn = 1,0 (repli Rtop < 2) ⇒ ReN ≈ 2,5.
- **LEX-014** — Rdyn est aveugle au désaccord sub-demi-ton (résolution = pas
  de grille).

## Leçon d'étalonnage

**ReN mesure l'alignement spectral sur la grille f0·2^(n/12), pas l'ordre
dynamique.** Les régimes Cosmologique / Méso / Quantique sont des lectures au
cadran de l'instrument, dans ses propres coordonnées — pas des détecteurs de
transitions de phase dynamiques.

## Falsifieurs (comment réfuter ces mesures)

1. Régénérer le corpus (`python3 sweep_meso.py`) : un SHA-256 différent de
   celui gelé dans `../SHASUMS.txt` invalide la reproductibilité.
2. Exhiber un r ∈ [3,40 ; 3,73] dont la lecture médiane n'est pas
   cosmologique.
3. Exhiber un δ ∈ ]0 ; 6] donnant Rdyn ≠ 0 dans la famille C.
