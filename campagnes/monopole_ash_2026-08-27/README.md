# Campagne monopole_ash — 2026-08-27 (protocole C13.1)

Première confrontation du pont mesure ↔ interprétation à un **soliton de la
machine noétique** : le monopole SU(2) radial de 't Hooft–Polyakov (artefact
P0 du dépôt privé `non-abelian-gauge-model`, sha256 `52929bda0603…`).

**Verdict central : EXP-012 FALSIFIÉE — 6/6 DIVERGENT (B3-FAIL publié).**

## Chaîne de confiance

| Maillon | Valeur |
|---|---|
| Attente | EXP-012 (`monopole_su2_radial`, Méso attendu, statut E) publiée **avant mesure** — expectations.json v0.4.0, commit `b1c0153`, sha256 `12ff6672…` |
| Artefact | `p0_monopole_su2.py` sha256 `52929bda060344213298890bf14e4856c46d6119d240379d8a6161ac37cb6f73` |
| Instrument | `ash_core.py` 1.0.0 sha256 `338dbda7b499fdc8…` ; pont `noetic_bridge.py` 0.1.0 sha256 `7e9f3705c15dd6ec…` |
| Protocole | C13.1 figé (`protocole/PROTOCOLE_C13_monopole_ash.md`) |
| Reproductibilité | `run/c13_1_runner.py` + `run/c13_1_analyse.py` régénèrent CSV, signatures et verdicts à l'octet près (scripts commités avec la campagne) ; empreintes dans `run/runs_c13_1.json` |

## Résolution numérique (grille C13.1)

4096 points uniformes de [30/4096, 30] (dx = 30/4096, fs ≈ 136,533),
différences centrées ordre 2, CL dures H(0)=0, K(0)=1, L-BFGS-B.
Calibration : ρ = 0,5 depuis le guess tanh/cosh → **C = 0,9964** (borne BPS
C = 1 ✓). Continuation : 0,5 → 0,25 → 0,1 et 0,5 → 1 → 2 → 4.
Contrôle ρ = 1 : **C = 1,3001** (artefact grille native : 1,3098 ; littérature
1,24–1,31 ✓). C(ρ) strictement croissant sur les 6 branches.

## Résultats

| ρ | C(ρ) | E_gauge | E_higgs | E_pot | ReN | Rtop | Rdyn | Rc | Bande | Régime | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.4811 | 0.1925 | 0.0620 | 0.2266 | 369.7 | 1 | 1.00 | 0.429 | E1 | Quantique | DIVERGENT |
| 0.25 | 0.7352 | 0.2944 | 0.1139 | 0.3269 | 408.4 | 1 | 1.00 | 0.381 | E1 | Quantique | DIVERGENT |
| 0.5 | 0.9964 | 0.4038 | 0.1887 | 0.4040 | 608.0 | 1 | 1.00 | 0.259 | E1 | Quantique | DIVERGENT |
| 1.0 | 1.3001 | 0.5226 | 0.2901 | 0.4873 | 882.7 | 1 | 1.00 | 0.178 | E1 | Quantique | DIVERGENT |
| 2.0 | 1.6677 | 0.6372 | 0.4539 | 0.5766 | 1264.6 | 1 | 1.00 | 0.124 | E1 | Quantique | DIVERGENT |
| 4.0 | 2.1057 | 0.7274 | 0.6863 | 0.6921 | 1548.9 | 1 | 1.00 | 0.090 | E1 | Quantique | DIVERGENT |

Contrôles H(ξ) et K(ξ) (statut H, consignés sans attente) : **12/12
HORS-CONTRAT**, tous lus Quantique eux aussi (ReN 19,5 – 40 600).

## Analyse de la falsification

EXP-012 portait deux clauses ; la **clause (a)** est déclenchée : la branche
ancrée BPS (ρ = 0,5, C ≃ 1) **lit hors méso** (Quantique, ReN = 608). La
correspondance phénoménologique pression ↔ Rc / torsion ↔ Rdyn, telle que
conjecturée, **ne survit pas** à la mesure sur un soliton statique.

Mécanisme de l'écart, consigné avec la même rigueur qu'une conformité :

1. **Profil statique mono-pic.** ε(ξ) est une densité d'énergie localisée au
   cœur du monopole : un seul maximum → Rtop = 1 partout → **Rdyn = 1,0 par
   convention de repli** (LEX-013). Le ReN repose donc sur le fallback
   mono-pic : l'instrument ne mesure aucune dynamique, car il n'y en a pas —
   un soliton statique n'a pas de « torsion spectrale » au sens Rdyn.
2. **Normalisation RMS = 1 + queue étalée.** Après normalisation, l'énergie
   spectrale Rc décroît quand ρ croît (le potentiel concentre le profil :
   cœur plus étroit, queue relativement plus plate) → ReN ∝ 1/Rc **croît**
   avec ρ. La migration est bien **monotone** (369,7 → 1548,9), mais dans le
   **sens inverse** de la conjecture (qui attendait pression croissante →
   ReN décroissant).
3. **Lecture de l'instrument.** Pour l'ASH, un profil statique localisé est
   « torsion dominante » (E1 dominant, D ≈ 0,81, H ≈ 0,51). C'est cohérent
   avec la leçon LEX des campagnes : l'instrument répond à la **structure
   spectrale du signal donné**, pas à la physique du système sous-jacent.

## Ce qui survit / ce qui meurt

- **Mort** : EXP-012 en l'état — ni le régime méso de l'équilibre de
  Bogomolny, ni le sens de la migration. La correspondance naive
  E_gauge+E_pot ↔ pression / E_higgs ↔ torsion ne passe pas par la densité
  ε(ξ) statique.
- **Vivant** : la monotonie en ρ (fait mesuré, reproductible) ; la
  calibration BPS de l'instrument numérique (C(0,5) ≃ 1, C(1) = 1,30) ;
  la grille C13.1 comme protocole soliton.
- **Leçon** : pour parler à l'ASH, il faut un signal **dynamique** —
  fluctuation autour du profil (modes de vibration du monopole), flux
  d'énergie, ou série temporelle issue de la solution — pas la densité
  statique elle-même. Une attente recalibrée sur cette campagne (pattern
  EXP-010/011) est envisageable, mais ce serait une **nouvelle** attente,
  à déclarer avant toute nouvelle mesure — pas une retouche d'EXP-012.

## Contenu

- `protocole/` : PROTOCOLE_C13_monopole_ash.md (figé avant mesure) + attente_EXP-012.json
- `signaux/` : 18 CSV `xi,signal` (%.10e, LF) — ε primaire, H/K contrôles, 6 branches ρ — **non commités** (protocole §3 : régénérables bit-à-bit par `run/c13_1_runner.py` ; empreintes dans `run/runs_c13_1.json`)
- `run/` : c13_1_runner.py (régénération à l'octet près) + runs_c13_1.json (C, décompositions, empreintes)
- `signatures/` : 18 signatures `ash-signature/0.1` (SIG-022…SIG-039 au registre noetic-ash-corpus)
- `verdicts/` : 18 verdicts `ash-verdict/0.1` (6 DIVERGENT vs EXP-012, 12 HORS-CONTRAT contrôles)
