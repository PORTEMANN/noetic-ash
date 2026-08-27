# Noetic-ASH — Position dans l'écosystème Noetic Physics

## Architecture en couches

```
┌─────────────────────────────────────────────────────────────────────┐
│  COUCHE 1 : FONDATIONS MATHÉMATIQUES                                │
│  spectral-triple-minimality                                         │
│  • Théorèmes T1-T4 (minimalité spectrale)                           │
│  • KO-6 (loi arithmétique)                                          │
│  • Justifie la grille 2^(1/12)                                      │
├─────────────────────────────────────────────────────────────────────┤
│  COUCHE 2 : SOLVEURS NUMÉRIQUES                                     │
│  ko6-spectral-solver                                                │
│  • Benchmarks B1-B3 (Taylor-Green, KdV, Ising 2D)                   │
│  • Validation numérique des méthodes spectrales                     │
├─────────────────────────────────────────────────────────────────────┤
│  COUCHE 3 : CŒUR PHYSIQUE                                           │
│  noetic-machine                                                     │
│  • SU(2) Georgi-Glashow                                             │
│  • 5 prédictions confirmées                                         │
│  • Interprétation physique du ReN                                   │
├─────────────────────────────────────────────────────────────────────┤
│  COUCHE 4 : RECHERCHE ACTIVE (private)                              │
│  non-abelian-gauge-model                                            │
│  • Modèle non-abélien                                               │
│  • Fonctionnel C(ρ)                                                 │
├─────────────────────────────────────────────────────────────────────┤
│  COUCHE 5 : ARCHIVE CANONIQUE                                       │
│  noetic-machine-complete                                            │
│  • P0-P31, SHASUMS, 34 scripts                                      │
│  • Protocole de reproductibilité                                    │
├─────────────────────────────────────────────────────────────────────┤
│  COUCHE 6 : APPLICATIONS                                            │
│  noetic-applications                                                │
│  • P7-P31 : 32 études de cas expérimentales                         │
│  • Données atomiques, nucléaires, particules, matière condensée     │
├─────────────────────────────────────────────────────────────────────┤
│  COUCHE 7 : ACQUISITION ◄── VOUS ÊTES ICI                           │
│  noetic-ash                                                         │
│  • P32+ : EEG intention motrice (BCI)                               │
│  • P33+ : ECG surveillance cardiaque                                │
│  • P34+ : Vibrations maintenance prédictive                         │
│  • P35+ : Campagne d'étalonnage du régime Méso                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Flux de données

```
Signal physique (EEG/ECG/vibration)
        ↓
┌─────────────────┐
│   noetic-ash    │  ← Acquisition, discrétisation 2^(1/12)
│   (ce dépôt)    │    Extraction invariants (Rc, Rtop, Rdyn, ReN)
└────────┬────────┘
         ↓
┌─────────────────┐
│ noetic-machine  │  ← Interprétation physique (SU(2), torsion, pression)
│   (cœur)        │    Prédictions, comparaison modèles
└────────┬────────┘
         ↓
┌─────────────────┐
│noetic-applications│  ← Validation expérimentale, publication
│   (vitrine)     │    Études de cas P32+–P34+
└─────────────────┘
```


## Pont mesure ↔ interprétation (`bridge/`)

Le bridge rend exécutable le « protocole de contribution cross-repo »
ci-dessous : il fige la mesure ASH en une **signature** JSON
(`ash-signature/0.1` : invariants, grille, contexte, SHA-256 du signal),
la confronte à un **registre d'attentes** et émet un **verdict**
(`ash-verdict/0.1` : CONFORME / DIVERGENT / EXPLORATION / HORS-CONTRAT).

```
série (temps, valeur) → ASH → signature → verdict → banque de signaux
```

- L'ASH est **agnostique** : toute série (temps, valeur) est analysable ;
  c'est le contexte déclaré qui consolide la sémantique des régimes.
- Le bridge n'est **pas un niveau du lexique** (v0.3.0) : il consigne des
  confrontations datées et falsifiables, sans projeter la phénoménologie
  de la machine sur l'instrument.
- Les verdicts alimentent la banque de signaux (registre contexte +
  résultats) : à terme, un signal inconnu peut être rapproché des
  signatures connues.
- Statuts et falsifieurs voyagent avec chaque attente ; la finance reste
  en exploration (EXP-007, statut H, contrôle négatif).

Voir [bridge/README.md](../bridge/README.md).

## Dépendances

| Dépendance | Direction | Nature |
|------------|-----------|--------|
| `spectral-triple-minimality` | noetic-ash ← fondations | La grille 2^(1/12) est justifiée par les théorèmes T1-T4 |
| `ko6-spectral-solver` | noetic-ash ← solveurs | Les benchmarks B4+ utilisent les méthodes de ko6 |
| `noetic-machine` | noetic-ash ↔ cœur | Le ReN est interprété physiquement par le modèle SU(2) |
| `noetic-applications` | noetic-ash → applications | Les études P32+–P34+ utilisent noetic-ash comme outil de mesure |
| `noetic-machine-complete` | noetic-ash → archive | Les résultats ASH sont archivés avec SHA-256 |

## Numérotation des artefacts (P0–P35+)

**Convention** : les numéros **nus** (P0–P33) appartiennent à l'atlas de la
machine noétique ; les programmes de **noetic-ash** portent le suffixe
« + » (P32+, P33+, P34+, P35+). L'ASH — couche acquisition/mesure, conçue
pour l'industrie embarquée et la xAI — est antérieur à la machine : ce sont
des approches distinctes, et leurs catalogues ne se recouvrent plus.

| Plage | Dépôt | Description |
|-------|-------|-------------|
| P0-P6 | spectral-triple-minimality | Fondements mathématiques |
| P7-P31 | noetic-applications | Études de cas expérimentales |
| P32+ | noetic-ash | EEG intention motrice |
| P33+ | noetic-ash | ECG surveillance cardiaque |
| P34+ | noetic-ash | Vibrations maintenance prédictive |
| P35+ | noetic-ash | Campagne d'étalonnage du régime Méso (`benchmarks/p35_meso/`) |

## Protocole de contribution cross-repo

1. **Mesure** : noetic-ash extrait les invariants d'un nouveau signal
2. **Interprétation** : noetic-machine fournit la prédiction physique
3. **Validation** : noetic-applications documente l'étude de cas
4. **Archivage** : noetic-machine-complete fige les artefacts avec SHA-256
5. **Publication** : spectral-triple-minimality fournit les fondements mathématiques

## Philosophie commune

Tous les dépôts partagent :
- **Zéro paramètre ajusté**
- **SHA-256 reproductibilité**
- **B3-FAIL** (échecs publiés avec succès)
- **Open Source** (MIT pour ASH, licence à vérifier pour les autres)
