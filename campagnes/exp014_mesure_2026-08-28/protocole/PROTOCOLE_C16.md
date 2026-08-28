# PROTOCOLE C16 — Campagne exp014_mesure : couche n=5 de P1 (attente EXP-014)

**Statut : FIGÉ le 2026-08-28, AVANT toute mesure.** Toute modification ultérieure
se fait par addendum, le texte original est conservé.

## 1. Objet

Tester l'attente **EXP-014** (calibrée, `protocole/attente_EXP-014.json`,
`bridge/expectations.json` v0.6.0) : la pression spectrale **Rc** ordonne
strictement le nombre de nœuds radiaux dans la couche n=5 du hamiltonien P1
(fond monopole ρ=1). La couche n=5 n'a servi à **aucun** réglage : la
calibration (note exp014 C15, `campagnes/exp014_2026-08-28/`) porte sur les
orbitales n ≤ 4.

## 2. Production des signaux (chaîne figée, identique à C14+A2 et C15)

1. Fond monopole ρ=1 : minimisation L-BFGS-B du fonctionnel radial
   (grille ξ : XMAX=30, NPTS=4096 ; `maxiter=20000`, `ftol=1e-14`,
   `gtol=1e-10`). Attendu : C = 1,3033212195.
2. Hamiltonien radial P1 : boîte RMAX=4000, NR=4000, dr=1 ; Coulomb tronqué
   (R_CORE=3,04, α=1/137,036, M_E=1) ; `eigh_tridiagonal`, 9 premiers états
   par moment cinétique l = 0…4.
3. États retenus (couche n=5, un par nombre de nœuds radiaux n−l−1) :
   **5g** (l=4, idx 0, 0 nœud), **5f** (l=3, idx 1, 1 nœud),
   **5d** (l=2, idx 2, 2 nœuds), **5p** (l=1, idx 3, 3 nœuds),
   **5s** (l=0, idx 4, 4 nœuds).
4. Témoin d'intégrité : l'orbitale **4f** est recalculée ; son CSV doit être
   **octet-identique** à celui de la campagne exp013
   (`p1_orb_4f.csv`, sha256 `423604b88d31dc88fbd802adfbf68eb5515d7f72b7d25f1f1ddb64244b66f7c4`).
   Tout écart invalide la chaîne avant analyse.
5. Contrôle de spécificité : bruit blanc gaussien graine 43 (2048 pas,
   SeedSequence(43)), mesuré aux paramètres du volet a de C14
   (fs=10, fenêtre 512, nperseg 256) sur la grille du présent protocole.
   Statut H : consigné sans attente (HORS-CONTRAT).

## 3. Instrument et grille (figés, AUCUN post-traitement)

- `ash_core.py` v1.0.0 (sha256 `338dbda7b499fdc8ea00beb0ddc696270f47eda38253902edc77cba28eedeb0e`) ;
- normalisation RMS=1 (B3-FAIL #1) ; `signal_type="generic"` ;
- **f0 = 2⁻¹¹ = 4,8828125·10⁻⁴** — centre du domaine de robustesse calibré
  (k ∈ [−3,+2] de la note C15 : ordre strict de Rc vérifié sur toute cette
  plage, bande moiré incluse) ;
- 5 octaves, fenêtre 1024 pts, overlap 0,5, nperseg 1024, fs=1 ;
- agrégation : médiane sur fenêtres (identique à `c14_analyse.py`) ;
- **aucune couche de post-traitement** (la couche anti-moiré KO-6 a été
  testée localement et rejetée : inefficace sur les quasi-dégénérescences,
  coûteuse en masse, inutile pour Rc — note locale non publiée).

## 4. Mesures consignées

Pour chacun des 5 états + témoin 4f + contrôle : signature `ash-signature/0.1`
(Rc, Rtop, Rdyn, ReN, H, D, 7 bandes, régime, bande dominante) et verdict
`ash-verdict/0.1` confronté à EXP-014 (témoin et contrôle : attente null,
HORS-CONTRAT). Empreintes SHA-256 épinglées dans `run/manifest.json`.
CSV signaux non commités, régénérables bit-à-bit par `run/c16_runner.py`
(règle C13.1 §3).

## 5. Falsifieur

Texte faisant foi : `protocole/attente_EXP-014.json` (identique à l'entrée
EXP-014 de `bridge/expectations.json` v0.6.0). Trois clauses (ordre strict
de Rc, échelle des rapports, régime Cosmologique) — une seule suffit à
falsifier.

## 6. Publication

Résultats publiés quels qu'ils soient (B3-FAIL), avec le même soin qu'une
conformité. Registre corpus : entrées ajoutées en append-only après
vérification octet par octet.
