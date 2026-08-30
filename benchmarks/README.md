# Benchmarks ASH — protocole C12.1

Comparaison d'ASH avec l'état de l'art (FFT+LDA, ondelettes+SVM, CNN-1D) sur
données publiques. Constantes pré-calculées avant tout ajustement, versions
figées, résultats négatifs publiés (**B3-FAIL**).

## Datasets

| Dataset | Source | Tâche | Acquisition |
|---|---|---|---|
| MIT-BIH Arrhythmia (`mitdb`) | [PhysioNet](https://physionet.org/content/mitdb/) | Classification ECG | `wfdb` — record 100 vérifié par `SHASUMS.txt` |
| MIT-BIH Normal Sinus Rhythm (`nsrdb`) | [PhysioNet](https://physionet.org/content/nsrdb/) | Régimes longue durée (~10 h 51, record 16265, 128 Hz) | export CSV via `wfdb`, hash `SHASUMS.txt` |
| ECG5000 | [UCR Archive](https://www.cs.ucr.edu/~eamonn/time_series_data_2018/) | Binaire normal/anormal | voir `ecg5000/README.md` |
| NASA Bearing | NASA Ames Prognostics | Détection de changement de régime | lien dans le protocole |

**Les données brutes ne sont pas commitées.** Datasets externes : téléchargement
PhysioNet/UCR + hash `SHASUMS.txt`. Datasets synthétiques : régénérés par les
scripts **seedés** (`np.random.seed(42)`, v1.0.0) des exemples — même hash à
l'identique, régimes inchangés (EEG→Quantique ReN≈41, ECG→Cosmologique ReN≈0,6,
moteur sain→Cosmologique, moteur défaut→Quantique ReN≈82).

## Contenu

| Fichier | Rôle |
|---|---|
| `benchmark_noise.py` | Robustesse : ASH vs FFT+LDA à SNR 20/10/5 dB |
| `benchmark_local.py` | Suite locale générique (signaux synthétiques) |
| `mitdb/benchmark_mitdb_real.py` | Pipeline MIT-BIH de référence (wfdb) |
| `mitdb/benchmark_mitdb_rf_smote.py` | Variante SMOTE + Random Forest |
| `refreeze_table_v110.py` | **Pipeline déclaré v1.1.0** — re-figeage de la table officielle (F18) |
| `results/` | Résultats de référence figés (hashes dans `SHASUMS.txt`) |

## Résultats de référence (juin 2026, ASH v2.0 ≡ noyau consolidé v1.0.0)

| Signal | Rc moy | Rtop moy | Rdyn moy | ReN moy | Régime majoritaire |
|---|---|---|---|---|---|
| Moteur sain | 1,107 | 2,0 | 0,000 | 0,00015 | Cosmologique |
| Moteur défaillant | 1,030 | 3,67 | 0,302 | 74,3 | **Quantique** |
| EEG intention | 1,661 | 1,22 | 0,778 | 40,4 | **Quantique** |
| ECG normal (MIT-BIH 100) | 1,233 | 2,0 | 0,411 | 1,55 | Cosmologique |

Robustesse : ASH résiste mieux que FFT+LDA à SNR ≤ 5 dB. Ondelettes+SVM
meilleures sur certaines tâches, au prix d'un apprentissage (B3-FAIL publié).

## Déclarations B3-FAIL

- [x] **CNN-1D peu adapté** aux petits jeux de données testés — résultat nul publié.
- [x] **Bruit blanc non classé quantique** (contrairement à une affirmation
  antérieure) : 1 % de fausses alarmes sur 100 graines, seuil phénoménologique.
  Voir CHANGELOG v1.0.0.
- [x] **ReN non invariant d'échelle** (ReN ∝ 1/amplitude). Voir CHANGELOG v1.0.0.
- [x] **Table de juin 2026 non reproductible** par les pipelines publiés
  (P45-C1, corpus noetic-machine-complete) — re-figée en v1.1.0 (F18, voir
  addendum ci-dessous).

## Rapport de benchmark (format attendu)

Voir [CONTRIBUTING.md](../CONTRIBUTING.md) — tableau Accuracy/F1/ROC-AUC/temps,
validation croisée 5-fold stratifiée, test de bruit 20/10/0 dB, SHA-256 du
dataset + du code + des résultats.


---

## Addendum v1.1.0 (31/08/2026) — errata F16/F18 (audit Machine Noétique, P43/P45)

### F16 — la colonne « Régime » est retirée de la classification officielle

ReN ∝ 1/amplitude (pente mesurée −0,996 ; exacte à 7 chiffres hors entropie
dégénérée) : **3 signaux sur 5** de la table ci-dessus franchissent un seuil
de régime quand le signal est multiplié par une constante. La colonne
« Régime majoritaire » et la classification par ReN sont **non portables**
et retirées de la classification officielle ; ReN reste publié comme
indicateur relatif à gain fixe déclaré. Détail : `docs/ERRATUM-F16-F18.md`.

### F18 — table officielle re-figée (v1.1.0)

La table de juin 2026 n'était reproduite par aucun pipeline publié (P45-C1,
B3-FAIL d'archive). Table officielle désormais :
`results/table_bench_v110.csv` (sha256 `1c9430c6…`, SHASUMS.txt),
produite par le pipeline déclaré `refreeze_table_v110.py` (noyau v1.1.0,
fenêtrage `process_signal`, données régénérées bit-à-bit et vérifiées).
Reproductibilité C0 vérifiée (deux exécutions, même empreinte).

### Classification officielle : invariants normalisés

P45-C3 : les 10/10 paires des 5 signaux sont séparées par au moins un
invariant normalisé (Rtop, Rdyn, E1..E7) à intervalles inter-fenêtres
disjoints ; invariance d'amplitude mesurée à 1e-9 (P45-C2). **La
classification du benchmark tient sans ReN** — elle est promue officielle.

### Grille EEG 5 octaves (v1.1.0)

La bande β (13–30 Hz) était hors grille figée (4 octaves → 15,1 Hz) :
l'intention du signal P32+ n'était visible que par fuite de Welch (canal
parasite mesuré). À 5 octaves, la bouffée β est lue en direct
(E5 × 3,66 pendant l'intention, pic note 52 = 20,2 Hz).
