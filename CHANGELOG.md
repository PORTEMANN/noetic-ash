# Changelog

## [Unreleased] — noyau v1.1.0 (2026-08-31) — errata F16/F18 (audit Machine Noétique)

### Corrigé — B3-FAIL (F18, archive)
- **Table des benchmarks de juin 2026 non reproductible** par les pipelines
  publiés (P45-C1, corpus noetic-machine-complete) : re-figée par
  `benchmarks/refreeze_table_v110.py` (pipeline déclaré) →
  `benchmarks/results/table_bench_v110.csv` (sha256 `1c9430c6…`, C0
  vérifié). L'ancienne table reste dans l'historique (addenda seulement).

### Modifié
- **F16 — ReN retiré de la classification officielle** : non portable
  (ReN ∝ 1/amplitude, pente mesurée −0,996 ; 3/5 signaux du benchmark
  franchissent un seuil de régime à signal inchangé). ReN reste dans
  l'API figée comme indicateur relatif à gain fixe. Classification
  officielle = invariants normalisés (Rtop, Rdyn, E1..E7 — 10/10 paires
  séparées, invariants à 1e-9 ; P45-C2/C3). Voir `docs/ERRATUM-F16-F18.md`.
- `src/python/ash_core.py` v1.1.0 : `DEFAULTS["eeg"]["n_octaves"]` 4 → 5
  (couverture de la bande β 13–30 Hz — justification de domaine C12.1 ;
  la grille 4-octaves ne lisait β que par fuite de Welch, P45-C4).
  Tests : `tests/test_ash.py` inchangés (domaine generic).


## [Unreleased]

### Corrigé — B3-FAIL (instrument)
- **Bug du modèle nul des surrogates** dans la chaîne du comma au lag
  caractéristique (`comma_au_lag`, campagnes exp022/023/024) : `surrogate()`
  était appelé deux fois par tirage (différence de deux surrogates
  indépendants) au lieu du comma d'un même surrogate décalé. Le modèle nul
  était gonflé (≈ √2) et le Z-score exagéré. Campagnes recalculées au null
  corrigé et verdicts révisés : exp022 FALSIFIÉE (a et b), exp023 FALSIFIÉE
  (a et b — la confirmation du mécanisme de cohérence de phase ne tient pas),
  exp024 FALSIFIÉE (a et b — la conformité était un artefact). Addenda A1 +
  `run/comma_corrige.py` + `run/evaluation_corrigee.json` dans les trois
  campagnes. Non affectés : la série E44 (exp017–021, null correct dès
  l'origine) et la séparation spectrale (vibration_hf). Leçon consignée :
  verrouiller le modèle nul (un seul surrogate décalé) et valider la chaîne
  contre un cas connu avant mesure.

### Ajouté
- `src/python/comma_core.py` v1.0.0 (figé, sha256 21c60ed3…) — le comma
  noétique, première extension mesurée de l'instrument : auto-comma,
  surrogates à phases randomisées (null corrigé, verrouillé), bande de
  récurrence, détecteur de résurgence (validé E44), comma contre dynamique
  idéale (Rdyn), sortie xAI structurée. Le détecteur de cohérence de phase
  sur capteur (CWRU) y est conservé comme observable NON validée au null
  corrigé (voir addenda A1), à recalibrer.


## [Unreleased]

### Ajouté
- `bridge/expectations.json` v0.4.0 : ajout append-only d'EXP-012
  (`monopole_su2_radial`, statut E conjectural déclaré AVANT mesure) —
  EXP-001…011 inchangées (leur `source` entre dans l'empreinte des verdicts).
  Attente : le profil BPS du monopole SU(2) radial (équilibre exact pression
  ↔ torsion) lit au voisinage de la frontière méso (ReN ≈ 1–10) et ReN est
  monotone en ρ. Falsifieur dual : branche BPS lue hors méso, ou migration
  non monotone en ρ sur {0,1 ; 0,25 ; 0,5 ; 1 ; 2 ; 4}. Prépare la campagne
  `monopole_ash` (protocole C13.1 figé) — première confrontation du pont à
  un soliton de la machine noétique (dépôt `non-abelian-gauge-model`,
  artefact P0 hash 52929bda0603).

## [1.3.0] — 2026-08-27

### Campagnes — 2026-08-27
- **`campagnes/signaux_reels_2026-08-27/`** : première campagne sur signaux
  réels publics (MIT-BIH 100 & 106, NSRDB 16265, CWRU 97 & 105) — 5
  signatures + 5 verdicts figés (3 CONFORME, 1 EXPLORATION, 1 DIVERGENT).
  EXP-002 (ECG normal) consolidée du synthétique P33+ au réel public.
  **B3-FAIL publié** : sur CWRU réel, sain (97) et défectueux (105) lisent
  quantiques — la grille vibration 10–320 Hz est aveugle aux lignes de défaut
  kHz (≈1037/3586 Hz) ; EXP-003/EXP-008 décrivent la grille simulée P34+, pas
  le roulement réel. Domaine `vibration_hf` requis.
- **`campagnes/vibration_hf_2026-08-27/`** : suite du B3-FAIL CWRU — domaine
  `vibration_hf` (enveloppe Hilbert 2–5 kHz, RMS=1, grille 10–320 Hz) éprouvé
  sur 9 fichiers CWRU réels : séparation sain/défectueux parfaite sur le
  corpus (ReN 67–178 vs 1,8–21,3), 9/9 CONFORME contre EXP-010/EXP-011
  (attentes calibrées, falsifieurs définis pour défauts 14/21 mil et autres
  machines). Le brut haute fréquence (grille 100 Hz – 6,4 kHz) est testé et
  rejeté : pas de séparation sans enveloppe.
- `bridge/expectations.json` v0.3.0 : ajout append-only d'EXP-008
  (vibration_roulement_sain, E), EXP-009 (ecg_arythmie, H), EXP-010
  (vibration_hf_roulement_sain) et EXP-011 (vibration_hf_roulement_defaut) —
  EXP-001…007 inchangées (leur `source` entre dans l'empreinte des verdicts).
  (La v0.2.0 — EXP-008/EXP-009 seules — est restée une version intermédiaire
  non publiée.)
- Registre `noetic-ash-corpus` v0.3.0 : SIG-008…SIG-021 (campagnes signaux
  réels + vibration_hf), avec documentation de la convention d'empreintes
  (`convention_empreintes`).

### Corrigé
- Falsifieur d'EXP-011 resserré avant publication : la clause « bande
  dominante E2 » était non distinctive (les sains la partagent) ; le
  falsifieur porte désormais sur ReN > 30 pour un défaut avéré. Signatures,
  verdicts et registre réévalués en conséquence (empreintes recalculées,
  chaîne vérifiée 14/14).
- Durées des signaux de la campagne signaux réels alignées sur les
  signatures (MIT-BIH : 100 s, CWRU brut : 1 s) dans le README et le
  rapport de campagne.

## [1.2.0] — 2026-08-27

### Ajouté
- **Pont mesure ↔ interprétation** (`bridge/`) : contrat d'échange
  `ash-signature/0.1` (invariants + grille + contexte + SHA-256 du signal),
  registre d'attentes `expectations.json` (EXP-001…EXP-007, statuts et
  falsifieurs), moteur `noetic_bridge.py` (stdlib uniquement) émettant des
  verdicts `ash-verdict/0.1` — CONFORME / DIVERGENT / EXPLORATION /
  HORS-CONTRAT. Le pont n'est pas un niveau du lexique (v0.3.0) : il
  consigne des confrontations datées et falsifiables.
- `bridge/examples/` : 7 signatures réelles + verdicts figés (EEG P32+,
  ECG P33+, vibration P34+, ton pur LEX-013, logistique période 3 LEX-012,
  bruit blanc LEX-005, finance GBM synthétique EXP-007 en statut H),
  régénérables par `generate_examples.py` (seedé).
- `tests/test_bridge.py` : 11 tests (validation, quatre issues de verdict,
  discipline H, reproductibilité des empreintes).

### Corrigé
- `docs/ecosystem.md` : le dépôt privé de la couche 4 s'appelle
  `non-abelian-gauge-model` (et non « gauge-non-abelian »).

## [1.1.0] — 2026-08-27

### Ajouté
- **Programme P35+ : campagne d'étalonnage du régime Méso** (`benchmarks/p35_meso/`).
  Corpus déterministe (logistique × 61 r, mélange harmonique+chaos × 51 λ, octave
  désaccordée × 13 δ), 125 points de mesure, hash gelé dans `benchmarks/SHASUMS.txt`.
- **Lexique d'étalonnage et d'explicabilité** (`lexicon/`) : 5 niveaux
  (M/E/I/X/PHI), 4 statuts (T>C>E>H), 14 entrées, moteur `contrib/lexicon/interpret.py`.

### Étalonage — propriétés mesurées (lexique, statut C)
- LEX-012 : l'ordre périodique multi-composantes (fenêtre de période 3) est lu
  comme quantique ; la naissance du chaos logistique (r∞ = 3,56995) est invisible.
- LEX-013 : le ton pur est méso par construction (repli Rdyn = 1.0).
- LEX-014 : Rdyn est aveugle au désaccord sub-demi-ton (résolution = pas de grille).
- Leçon d'étalonnage : ReN mesure l'alignement spectral sur la grille
  f0·2^(n/12), pas l'ordre dynamique. Les régimes sont des lectures au cadran
  de l'instrument, dans ses propres coordonnées.

### Modifié
- **Positionnement** : l'ASH est la couche acquisition/mesure de l'écosystème,
  conçue pour l'industrie embarquée et la xAI — antérieure à la machine
  noétique (approches distinctes). La piste d'analogie LEX-004 (méso ↔ point
  auto-dual ρ* ≈ 0,75) n'est pas retenue ; elle reste documentée dans les
  notes de l'entrée.
- **Lexique v0.3.0** : niveau N (machine noétique) supprimé ; niveaux I
  (industriel/embarqué) et X (xAI) ajoutés.
- **Convention de numérotation** : les programmes de ce dépôt portent le
  suffixe « + » (P32+, P33+, P34+, P35+) ; les numéros nus P0–P33 appartiennent
  à l'atlas de la machine noétique. Appliqué rétroactivement dans toute la
  documentation.

## [1.0.0] — 2026-08-26

Import initial dans l'écosystème Noetic Physics (licence MIT).

### Ajouté
- Noyau consolidé `src/python/ash_core.py` (classe `ASH`), fusion de
  `ash_optimized.py` et `noetic_core_analyzer.py/_v2/_v3` — formules
  numériques identiques, vérifiées.
- API publique figée : `process_window()`, `process_signal()`, `from_csv()`.
- Exemples P32+ (EEG intention motrice), P33+ (ECG MIT-BIH), P34+ (vibrations
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
