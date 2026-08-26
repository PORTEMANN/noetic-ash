# Changelog

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

### Modifié
- `contrib/swarm/swarm_ash.py` : dépendance `ash_pro.ASHPro` remplacée par
  `ash_core.ASH` (le facteur d'oubli β est géré par l'essaim).
- Régimes nommés Cosmologique / Méso / Quantique partout (terminologie CTFT).
