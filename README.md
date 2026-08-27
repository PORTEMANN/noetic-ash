# Noetic-ASH

**Analyseur spectral à géométrie harmonique** — extraction d'invariants topologiques en temps réel, complexité O(1) par fenêtre, sans apprentissage.

ASH (*Harmonic-Geometry Spectral Analyzer*) est la couche **acquisition** de l'écosystème [Noetic Physics](https://histoire-des-sciences.eu). Conçu à l'origine pour l'**industrie embarquée** et la **xAI** (explicabilité : chaque classification se décompose en invariants à formules fermées, auditable sans boîte noire), il est antérieur à la machine noétique — les deux approches sont distinctes. Il projette un signal temporel sur la grille spectrale `f_n = f0 · 2^(n/12)` — la discrétisation minimale du spectre du Koilon ([spectral-triple-minimality](https://github.com/PORTEMANN/spectral-triple-minimality), Thm T1) — et en extrait des invariants interprétables :

| Invariant | Signification | Interprétation noétique |
|---|---|---|
| `Rc` | Énergie spectrale totale | Pression hydrodynamique du Koilon |
| `Rtop` | Nombre de pics locaux (> 10 % du max) | Singularités topologiques |
| `Rdyn` | Désaccord harmonique entre pics | Écart à la torsion nulle |
| `E1..E7` | Projection sur 7 plans (octaves) | Plans noétiques |
| `ReN` | **Nombre de Reynolds noétique** | Discriminant de régime : **cosmologique** (< 1), **méso** (1–10), **quantique** (> 10) |

## Exemple

```python
from ash_core import ASH
import numpy as np

fs, t = 250.0, np.arange(0, 2, 1/250.0)
signal = np.sin(2*np.pi*4*t) + 0.8*np.sin(2*np.pi*8*t)   # octave exacte

ash = ASH(fs=fs, signal_type="generic")   # f0=1 Hz, 4 octaves — paramètres fixés par le domaine
r = ash.process_window(signal)
# Rtop=2, Rdyn=0.0 (torsion nulle), ReN≈3e-6 → régime Cosmologique
```

Ligne de commande : `python src/python/ash_core.py mon_signal.csv ecg`

## Écosystème

```
spectral-triple-minimality (fondations) → ko6-spectral-solver (solveurs)
      → noetic-machine (cœur physique) → noetic-ash (acquisition) ◄ ce dépôt
      → noetic-applications (études P32+–P34+) → noetic-machine-complete (archive SHA-256)
```

Convention de numérotation : les programmes de ce dépôt portent le suffixe « + » (P32+, P33+, P34+, P35+) ; les numéros nus P0–P33 appartiennent à l'atlas de la machine noétique.

Carte complète : [docs/ecosystem.md](docs/ecosystem.md) — Formalisme : [docs/algorithm.md](docs/algorithm.md)

## Structure

| Chemin | Contenu |
|---|---|
| `src/python/ash_core.py` | Noyau consolidé v1.0.0 (classe `ASH`) |
| `src/cpp/ash_core.cpp` | Version embarquée (STM32, ESP32 — FFT maison) |
| `examples/` | P32+ EEG intention motrice · P33+ ECG · P34+ vibrations roulement (datasets régénérés par scripts seedés, voir `benchmarks/SHASUMS.txt`) |
| `benchmarks/` | Protocole C12.1, MIT-BIH, bruit, résultats figés + `SHASUMS.txt` — incl. P35+ (campagne d'étalonnage du méso) |
| `lexicon/` | Lexique d'étalonnage et d'explicabilité (niveaux M/E/I/X/PHI, statuts T>C>E>H) |
| `contrib/` | `mtr_mapper` (MTR-80), finance, essaims IoT, chaos — hors garantie C12.1 |
| `tests/` | Tests unitaires des propriétés fondamentales |

## Méthodologie

Quatre piliers (voir [CONTRIBUTING.md](CONTRIBUTING.md)) :

1. **Zéro paramètre ajusté** — `f0` et `N_oct` fixés par le domaine physique, jamais fittés
2. **Reproductibilité SHA-256** — datasets, code et résultats figés par hash
3. **B3-FAIL** — les résultats nuls ou négatifs sont publiés avec la même rigueur que les succès
4. **Cohérence cross-repo** — compatibilité avec `noetic-machine` et `ko6-spectral-solver`

> *« La physique noétique est comparable à la théorie des cordes dans les années 1980 : une construction mathématique prometteuse en quête de validation empirique. »* — Auto-évaluation CTFT

## Citation

Voir [CITATION.bib](CITATION.bib).

## Licence

MIT — © 2026 Patrice Portemann. Voir [LICENSE](LICENSE).
