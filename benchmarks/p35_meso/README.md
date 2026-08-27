# Programme P35+ — Le régime Méso comme objet mesuré

**Verdict : B3-FAIL n°4.** La conjecture LEX-004 (« le régime Méso est la frontière
entre ordre et chaos, analogue du point auto-dual ρ*≈0.75 de la machine noétique »)
est **falsifiée sous sa forme naïve** par ce programme. L'entrée du lexique est
conservée et publiée comme falsifiée (C12.1).

## Protocole

Corpus **100 % déterministe** (aucun RNG, aucune donnée externe) :

| Famille | Signal | Paramètre balayé | Points |
|---|---|---|---|
| A | Logistique xₙ₊₁ = r·xₙ(1−xₙ), tenue 32 éch./itéré, fs = 250 Hz | r ∈ [3.40 ; 4.00] pas 0,01 | 61 |
| B | (1−λ)·ton pur 100 Hz + λ·chaos logistique (r=4) normalisé | λ ∈ [0 ; 1] pas 0,02 | 51 |
| C | Tons à 100 Hz et 400·2^(δ/12) Hz (octave désaccordée) | δ ∈ [0 ; 6] demi-tons pas 0,5 | 13 |

Condition initiale X0 = 0,3 (à r=4, l'orbite issue de 0,5 est dégénérée :
0,5 → 1 → 0). Transitoire de 1000 itérés supprimé. 20 s analysées par point.
Reproduction : `python3 sweep_meso.py` → `results_p35_meso.csv`, dont le SHA-256
est gelé dans `../SHASUMS.txt`.

## Résultats

### Famille A — la naissance du chaos est invisible

| Zone de r | Lecture ASH |
|---|---|
| 3,40 – 3,73 (traverse r∞ = 3,56995) | **100 % cosmologique** sur toutes les fenêtres |
| 3,83 – 3,86 (fenêtre de période 3, ordonnée) | **100 % quantique** (Rtop = 4, Rdyn = 0,396) |
| 3,87 – 4,00 (chaos développé) | îlots épars de méso, max **55,6 %** des fenêtres à r = 3,98 |

L'accumulation de Feigenbaum — le moment précis où naît le chaos — ne laisse
**aucune signature** dans ReN. La fenêtre de période 3, qui est de l'ordre
dynamique pur, est lue comme le régime le plus « quantique » du balayage.

### Famille B — le mélange n'a pas de frontière

λ = 0 (ton pur) : méso, ReN ≈ 2,47. Dès λ > 0,34 : ReN → 0, régime cosmologique.
**0 % de fenêtres quantiques sur tout λ.** La transition est monotone, sans
couche-frontière méso intermédiaire : le méso n'est pas « entre » l'ordre et le
chaos, il disparaît dès que le chaos monte.

### Famille C — Rdyn est aveugle au sub-demi-ton

Rdyn = 0 pour **toutes** les valeurs de δ ∈ [0 ; 6], alors même que l'oreille et
la théorie musicale distinguent nettement une octave juste d'une octave
désaccordée d'un demi-ton. Rdyn ne résout pas les écarts inférieurs au pas de la
grille (12 TET).

## Ce que P35 mesure (ajouté au lexique, statut C)

- **LEX-012** — L'ordre périodique multi-composantes est lu comme quantique
  (fenêtre de période 3 : Rtop = 4 pics alignés, Rdyn faible).
- **LEX-013** — Le ton pur est méso *par construction* : un seul pic sur la grille
  ⇒ Rdyn = 1,0 (repli Rtop < 2) ⇒ ReN ≈ 2,5.
- **LEX-014** — Rdyn est aveugle au désaccord sub-demi-ton (résolution = pas de
  grille).

## Leçon

**ReN mesure l'alignement spectral sur la grille f0·2^(n/12), pas l'ordre
dynamique.** La conjecture LEX-004 supposait une correspondance entre la
classification spectrale de l'ASH et la frontière ordre/chaos du diagramme de
phases de la machine noétique. Il n'y en a pas — du moins pas sous cette forme.
Le régime Méso est un objet réel et mesurable (LEX-013), mais ce n'est pas la
frontière de Feigenbaum.

## Falsifieurs (comment réfuter ces conclusions)

1. Régénérer le corpus (`python3 sweep_meso.py`) : un SHA-256 différent de celui
   gelé dans `../SHASUMS.txt` invalide la reproductibilité.
2. Exhiber un r ∈ [3,40 ; 3,73] dont la lecture médiane n'est pas cosmologique.
3. Exhiber un δ ∈ ]0 ; 6] donnant Rdyn ≠ 0 dans la famille C.
