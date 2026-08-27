# Changelog

## [1.1.0] — 2026-08-27

### Ajouté
- **Programme P35+ : le régime Méso devient un objet mesuré** (`benchmarks/p35_meso/`).
  Corpus déterministe (logistique × 61 r, mélange harmonique+chaos × 51 λ, octave
  désaccordée × 13 δ), 125 points de mesure, hash gelé dans `benchmarks/SHASUMS.txt`.
- **Lexique d'interprétation multi-niveaux v0.2.0** (`lexicon/`) : 5 niveaux
  (M/S/N/T/PHI), 4 statuts (T>C>E>H), 14 entrées, moteur `contrib/lexicon/interpret.py`.

### B3-FAIL n°4
- **Conjecture LEX-004 falsifiée** (« méso = frontière entre ordre et chaos ») :
  le chaos logistique est lu 100 % cosmologique (la naissance du chaos à r∞ est
  invisible), la fenêtre de période 3 ordonnée est lue 100 % quantique, et le méso
  n'apparaît que sur des îlots épars (max 55,6 % des fenêtres à r=3.98).
  ReN mesure l'alignement spectral sur la grille f0·2^(n/12), pas l'ordre dynamique.
  L'entrée LEX-004 est **publiée comme falsifiée**, pas supprimée (C12.1).
- Propriétés mesurées ajoutées au lexique (statut C) : LEX-012 (ordre lu comme
  quantique), LEX-013 (ton pur = méso par construction), LEX-014 (Rdyn aveugle au
  désaccord sub-demi-ton).

## [1.0.0] — 2026-08-26

Import initial dans l'écosystème Noetic Physics (licence MIT).

### Ajouté
- Noyau consolidé `src/python/ash_core.py` (classe `ASH`), fusion de
  `ash_optimized.py` et `noetic_core_analyzer.py/_v2/_v3` — formules
  numériques identiques, vérifiées.
- API publique figée : `process_window()`, `process_signal()`, `from_csv()`.
- Exemples P32 (EEG intention motrice), P33 (ECG MIT-BIH), P34 (vibrations
  roulement) + cas synthétique sinusoïdal.
- Benchmarks : robustesse au bruit (SNR 20/10/5 dB), suite locale, pipelines
  MIT-BIH (wfdb, SMOTE+RF). Résultats de référence figés, `benchmarks/SHASUMS.txt`.
- `contrib/` : `mtr_mapper.py` (correspondance MTR-80, heuristique non validée),
  analyse financière, essaims de capteurs IoT (`swarm_ash.py`), analyse du chaos.
- Tests unitaires `tests/test_ash.py` (3/3) : pureté harmonique (octave exacte
  → Rdyn = 0), robustesse au bruit blanc (pas de fausse alarme quantique),
  invariance d'échelle des invariants Rtop/Rdyn/bandes.
- CI GitHub Actions : pytest + vérification SHA-256 des fichiers commités.
- Générateurs de datasets seedés (`np.random.seed(42)`) : EEG, ECG, vibrations —
  reproductibilité bit-à-bit (hashes dans `benchmarks/SHASUMS.txt`), régimes
  de classification inchangés par rapport aux valeurs de juin 2026.
- Port C++ `src/cpp/ash_core.cpp` : FFT radix-2 interne, zéro dépendance
  externe, compilation `g++ -std=c++17 -O2`.

### B3-FAIL — écarts documentation/code constatés lors de la consolidation
1. **§6.1 (docs/algorithm.md)** : le ReN n'est *pas* invariant par changement
   d'échelle d'amplitude — mesuré ReN ∝ 1/α (Rc au dénominateur). Seuls Rtop,
   Rdyn et les bandes normalisées sont strictement invariants. Correction de la
   documentation prévue en v1.0.1 (le comportement du code est figé par
   `test_scale_invariance`).
2. **§6.3** : un bruit blanc gaussien ne produit pas Rdyn → 1 ni un régime
   quantique en configuration par défaut (lissage de Welch). Mesuré sur
   100 graines : 39 % cosmologique, 60 % méso, 1 % quantique. La propriété
   effective — absence de fausse alarme sur bruit stationnaire — est
   documentée comme telle.
3. **Parseur CSV du port C++ (archive `ash_cpp.cpp`)** : la variable
   `first_num` passait à `false` dès la lecture de la colonne temps, ce qui
   empêchait toute lecture de la colonne signal — le signal analysé était
   identiquement nul. Conséquence : tous les résultats produits par l'ancien
   binaire C++ sont invalides. Constaté le 26/08/2026 par test sur sinus pur
   (Rc = 0 systématique). Parseur corrigé et validé dans
   `src/cpp/ash_core.cpp` (sinus 50 Hz → Rc ≈ 0.687, Rtop = 1).

### Modifié
- `contrib/swarm/swarm_ash.py` : dépendance `ash_pro.ASHPro` remplacée par
  `ash_core.ASH` (le facteur d'oubli β est géré par l'essaim).
- Régimes nommés Cosmologique / Méso / Quantique partout (terminologie CTFT).
