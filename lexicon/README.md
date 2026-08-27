# Lexique ASH — étalonnage et explicabilité

La couche sémantique **de l'instrument** : associer à toute signature
d'invariants ASH un ou plusieurs **concepts**, chacun portant son niveau
d'interprétation et son statut épistémique — sans jamais les mélanger.

## Principe

```
signal réel → ASH → invariants (Rc, Rtop, Rdyn, bandes, ReN)
                  → positionnement (régime, bande dominante)
                  → entrées du lexique dont la signature correspond
                  → lecture multi-niveaux [M | E | I | X | PHI]
```

L'ASH est la **couche acquisition/mesure** de l'écosystème : conçu pour
l'industrie embarquée et la xAI, il est **antérieur à la machine noétique**.
Ce sont des approches distinctes — le lexique décrit donc l'instrument dans
ses propres coordonnées (à quoi il répond, ses angles morts, comment ses
décisions s'expliquent), sans projeter sur lui la phénoménologie de la
machine. D'éventuels ponts entre les deux approches sont des pistes,
documentées dans les `notes` des entrées, datées, et jamais élevées au rang
de niveau.

## Les cinq niveaux

| Niveau | Sens | Source |
|--------|------|--------|
| **M** | Mathématique — définitions exactes des invariants | `docs/algorithm.md`, [spectral-triple-minimality](https://github.com/PORTEMANN/spectral-triple-minimality) |
| **E** | Étalonage — mesuré sur corpus figés C12.1 | `benchmarks/`, `benchmarks/SHASUMS.txt`, faits établis adossés à [references.histoire-des-sciences.eu](https://references.histoire-des-sciences.eu) |
| **I** | Industriel / embarqué — cas d'usage opérationnels | `examples/`, `hardware/`, [techniques.histoire-des-sciences.eu](https://techniques.histoire-des-sciences.eu) |
| **X** | xAI — explicabilité : comment les invariants justifient la décision | formules fermées, zéro paramètre appris |
| **PHI** | Philosophique — corpus Blavatsky / Besant & Leadbeater / Bailey | [theosophie.histoire-des-sciences.eu](https://theosophie.histoire-des-sciences.eu) |

Distinction à ne pas confondre : **E-niveau** (étalonnage) et **E-statut**
(empirique) sont deux axes indépendants — une entrée d'étalonnage est en
général de statut C.

Le niveau **PHI est toujours documentaire** : il éclaire la généalogie des
concepts (Koilon, ANU, septénaires), il ne prétend jamais au statut
scientifique.

La cartographie transversale (concepts, correspondances, prédictions) est
maintenue sur [index.portemann.eu](https://index.portemann.eu).

## Les quatre statuts (C12.1 étendu à la sémantique)

| Statut | Signification |
|--------|---------------|
| **T** | Adossé à un théorème ou protocole figé (T1–T4, KO-6) |
| **C** | Calibré, vérifié par test reproductible (tests unitaires, campagne d'étalonnage, propriété B3-FAIL mesurée) |
| **E** | Empirique, issu d'une étude de cas P##+ |
| **H** | Hypothèse / conjecture interprétative |

Règles :

1. Une entrée H ne se présente jamais comme T, C ou E.
2. Chaque entrée porte un **falsifieur** : l'observation qui la tuerait.
3. Une entrée falsifiée n'est pas supprimée — elle est publiée comme
   falsifiée (B3-FAIL appliqué au lexique).
4. Le `statut_global` d'une entrée est le **plancher** de ses niveaux.

## Convention de numérotation P## / P##+

Deux catalogues « P » coexistent dans l'écosystème :

- **P## nu** (P0…P33) : l'atlas de la machine noétique — ex. la trilogie de
  la frontière r₁₂ P31 → P32 → P33
  ([machine-noetique](https://machine-noetique.histoire-des-sciences.eu)).
- **P##+ suffixé** : les programmes du présent dépôt — P32+ (EEG), P33+
  (ECG), P34+ (vibrations), P35+ (campagne d'étalonnage du méso).

La convention est appliquée rétroactivement dans toute la documentation de
noetic-ash (v1.1.0). Voir LEX-011.

## Usage

```bash
# Lecture complète d'un signal (tous niveaux, PHI inclus)
python contrib/lexicon/interpret.py signal.csv ecg

# Lecture restreinte aux niveaux mathématique et étalonnage
python contrib/lexicon/interpret.py signal.csv vibration --niveaux M,E
```

## Fichiers

- `schema.json` — le passeport d'entrée (JSON Schema, v0.2.0)
- `lexicon.json` — les entrées (v0.3.0 : 14 entrées, niveaux M/E/I/X/PHI)
- `../contrib/lexicon/interpret.py` — le pipeline signal → lecture

## Contribuer (P35+)

Une nouvelle entrée = une PR avec : signature mesurée, passeport rempli,
falsifieur explicite, sources. Les entrées sans signature (`null`) sont des
entrées de contexte, jamais déclenchées automatiquement.

## Historique

- **v0.3.0** (2026-08-27) : restructuration ASH-native. Niveau N supprimé
  (l'ASH est antérieur à la machine noétique — approches distinctes) ;
  niveaux I (industriel/embarqué) et X (xAI) ajoutés ; LEX-004 recadrée en
  « piste d'analogie non retenue » après la campagne d'étalonnage P35+ ;
  convention P##+ appliquée.
- **v0.2.0** (2026-08-26) : 14 entrées, premières mesures P35+.
- **v0.1.0** (2026-08-26) : 11 entrées initiales, niveaux M/S/N/T/PHI.
