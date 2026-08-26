# Lexique noétique multi-niveaux

La couche sémantique de l'écosystème : associer à toute signature d'invariants
ASH un ou plusieurs **concepts**, chacun portant son niveau d'interprétation
et son statut épistémique — sans jamais les mélanger.

## Principe

```
signal réel → ASH → invariants (Rc, Rtop, Rdyn, bandes, ReN)
                  → positionnement (régime, bande dominante)
                  → entrées du lexique dont la signature correspond
                  → lecture multi-niveaux [M | S | N | T | PHI]
```

« Laisser parler les maths » veut dire ici : la sémantique s'attache à
l'**invariant**, pas au formalisme. Une même entrée vaut pour l'ASH qui
mesure un signal et pour la machine qui calcule un mode — c'est le même
point de l'espace des invariants.

## Les cinq niveaux

| Niveau | Sens | Source |
|--------|------|--------|
| **M** | Mathématique — définitions exactes des invariants | `docs/algorithm.md`, [spectral-triple-minimality](https://github.com/PORTEMANN/spectral-triple-minimality) |
| **S** | Scientifique — faits établis, analogies étiquetées | [references.histoire-des-sciences.eu](https://references.histoire-des-sciences.eu) |
| **N** | Machine noétique — verdicts et frontières P0–P33 | [machine-noetique.histoire-des-sciences.eu](https://machine-noetique.histoire-des-sciences.eu) |
| **T** | Technique / empirique — nucléides, CODATA, pont ANU | [techniques.histoire-des-sciences.eu](https://techniques.histoire-des-sciences.eu) |
| **PHI** | Philosophique — corpus Blavatsky / Besant & Leadbeater / Bailey | [theosophie.histoire-des-sciences.eu](https://theosophie.histoire-des-sciences.eu) |

Le niveau **PHI est toujours documentaire** : il éclaire la généalogie des
concepts (Koilon, ANU, septénaires), il ne prétend jamais au statut
scientifique.

La cartographie transversale (concepts, correspondances, prédictions) est
maintenue sur [index.portemann.eu](https://index.portemann.eu).

## Les quatre statuts (C12.1 étendu à la sémantique)

| Statut | Signification |
|--------|---------------|
| **T** | Adossé à un théorème ou protocole figé (T1–T4, KO-6, verdict machine « succès ») |
| **C** | Calibré, vérifié par test reproductible (tests unitaires, propriété B3-FAIL mesurée) |
| **E** | Empirique, issu d'une étude de cas P## |
| **H** | Hypothèse / conjecture interprétative |

Règles :

1. Une entrée H ne se présente jamais comme T, C ou E.
2. Chaque entrée porte un **falsifieur** : l'observation qui la tuerait.
3. Une entrée falsifiée n'est pas supprimée — elle est publiée comme
   falsifiée (B3-FAIL appliqué au lexique).
4. Le `statut_global` d'une entrée est le **plancher** de ses niveaux.

## ⚠️ Collision de numérotation P##

Les catalogues « P » de l'atlas machine et de noetic-ash **se chevauchent** :
P32/P33 désignent la trilogie de la frontière r₁₂ dans
[machine-noetique](https://machine-noetique.histoire-des-sciences.eu), mais
EEG/ECG dans noetic-ash (`docs/ecosystem.md`). Toute référence P## dans le
lexique est donc qualifiée : « P32 au sens noetic-ash » vs « P32 au sens
atlas machine ». Une harmonisation de la numérotation est à prévoir
(candidat B3-FAIL organisationnel).

## Usage

```bash
# Lecture complète d'un signal (tous niveaux, PHI inclus)
python contrib/lexicon/interpret.py signal.csv ecg

# Lecture restreinte aux niveaux mathématique et scientifique
python contrib/lexicon/interpret.py signal.csv vibration --niveaux M,S
```

## Fichiers

- `schema.json` — le passeport d'entrée (JSON Schema)
- `lexicon.json` — les entrées (v0.1.0 : 11 entrées)
- `../contrib/lexicon/interpret.py` — le pipeline signal → lecture

## Contribuer (P35+)

Une nouvelle entrée = une PR avec : signature mesurée, passeport rempli,
falsifieur explicite, sources. Les entrées sans signature (`null`) sont des
entrées de contexte, jamais déclenchées automatiquement.
