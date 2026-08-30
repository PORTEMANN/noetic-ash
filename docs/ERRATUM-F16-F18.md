# ERRATUM F16 / F18 — ReN non portable, table de juin 2026 non reproductible

**31 août 2026 — conséquences des chantiers P43 et P45 de la Machine
Noétique** (corpus `noetic-machine-complete` : `data/p43_ash_sous_machine_verdict.json`,
`data/p45_bench_renormalise_verdict.json` ; registre A4, entrées F16 et F18).

L'ASH a été passée sous l'opérateur de verdict (P43, protocole
ASH-MACH-1.0, noyau v1.0.0 figé byte-à-byte, succès 7/7) puis les
benchmarks ont été rejoués sur invariants normalisés (P45, protocole
BM-RENORM-1.0). Deux errata en résultent.

## F16 — ReN n'est pas un discriminant de régime portable

**Mesure.** ReN suit la loi effective ReN ∝ 1/amplitude (déjà constaté au
B3-FAIL de v1.0.0, §6.1) : la pente log-log mesurée est **−0,996** sur la
batterie P43, et **exacte** (−1 à 7 chiffres, ECG : ReN·A = 0,5895
constant) pour tout signal à entropie non dégénérée. Conséquence mesurée :
**3 signaux sur 5** du benchmark franchissent un seuil de régime quand on
multiplie le signal par une constante, sans rien changer d'autre (ECG :
Cosmologique → Quantique ; moteur défaillant et EEG : Quantique →
Cosmologique).

**Mécanisme de saturation (détail d'implémentation, publié).** Pour un
signal à entropie dégénérée (H ≈ 0, ex. sinusoïde pure), le double
plancher ε de la formule (`Rc·(H+1e-8) + 1e-8`) borne ReN à ≈ 10¹⁰ : la
pente −1 n'y est plus pure.

**Décision.** La colonne « régime » est **retirée de la classification
officielle des benchmarks** (voir `benchmarks/README.md`, addendum
v1.1.0). ReN reste calculé par le noyau (API figée) et publié dans la
table v1.1.0 comme **indicateur relatif à gain de chaîne fixe et déclaré**
uniquement. F16 reste ouverte au registre du corpus : sa fermeture exige
un ReN normalisé en amplitude, validé sur la batterie P43.

## F18 — la table de juin 2026 n'était pas reproductible

**Mesure (P45-C1).** Les valeurs figées de juin 2026 (Rc, Rtop, Rdyn, ReN
de moteur sain / moteur défaillant / EEG intention / ECG normal) ne sont
reproduites à tolérance déclarée par **aucun** des deux pipelines publiés
(fenêtres classe 1–2 s ; fenêtres 256 éch./hop 128 de
`benchmark_local.py`), sauf *moteur_sain* (fenêtre classe ✓). Elles
proviennent d'une pipeline non figée.

**Réparation.** La table officielle est re-figée par
`benchmarks/refreeze_table_v110.py` (pipeline déclaré, noyau v1.1.0,
données régénérées bit-à-bit et vérifiées contre `benchmarks/SHASUMS.txt`
avant calcul) → `benchmarks/results/table_bench_v110.csv`, sha256
`1c9430c6f7676798021b0bf0405ebc5fd567146d164474fc8377c8ac2bd30199`
(reproductibilité C0 vérifiée : deux exécutions, même empreinte).
La table de juin 2026 reste dans l'historique git — addenda seulement.

## Ce qui remplace la classification par régime

La classification officielle repose désormais sur les invariants
**normalisés** (Rtop, Rdyn, E1..E7) : invariants d'amplitude mesurés à
1e-9 (P45-C2) et suffisants — **10/10 paires** des 5 signaux du benchmark
séparées à intervalles inter-fenêtres disjoints (P45-C3). Le classement
du benchmark ne dépendait pas de ReN ; son étiquette de régime, si.

## Grille EEG étendue (v1.1.0)

La grille EEG figée (4 octaves → 15,1 Hz max) ne voyait la bande β
(13–30 Hz) que par fuite des lobes de Welch sur les notes hautes (canal
parasite mesuré, P45-C4). `DEFAULTS["eeg"]["n_octaves"]` passe à **5**
(30,2 Hz) : la bouffée β du signal P32+ devient lisible en direct (plan
E5 × 3,66 pendant l'intention, pic dominant à la note 52 = 20,2 Hz).
Justification de domaine (C12.1) : la bande β fait partie du domaine EEG.
