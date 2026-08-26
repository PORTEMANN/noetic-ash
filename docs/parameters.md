# Paramètres ASH — fixés par le domaine physique (C12.1)

Les paramètres de la grille noétique ne sont **jamais ajustés sur les données**
(pilier 1 du protocole C12.1). Ils dérivent du domaine physique du signal.

## Paramètres par défaut (`ash_core.ASH.DEFAULTS`)

| Domaine | `fs` (Hz) | `f0` (Hz) | `n_octaves` | Fenêtre (s) | Couverture spectrale |
|---|---|---|---|---|---|
| `eeg` | 250 | 1.0 | 4 | 2.0 | 1–16 Hz (delta → bêta bas ; filtre le bruit musculaire > 16 Hz) |
| `ecg` | 360 | 1.0 | 4 | 2.0 | 1–16 Hz (composantes QRS basses) |
| `vibration` | 1000 | 10.0 | 5 | 1.0 | 10–320 Hz (fréquences de défauts roulement) |
| `generic` | 250 | 1.0 | 4 | 2.0 | 1–16 Hz |

Paramètres communs : `overlap = 0.5`, `nperseg` auto (borné à [64, 1024]).

## Constantes du protocole (jamais modifiées)

| Constante | Valeur | Rôle |
|---|---|---|
| Pas de grille | `2^(1/12)` | Discrétisation minimale du Koilon (Thm T1) |
| Seuil de pics | 10 % du max | Détection des singularités (`Rtop`) |
| `Rdyn` si < 2 pics | 1.0 | Désaccord maximal par convention |
| Seuil cosmologique | ReN < 1 | Pression dominante |
| Seuil quantique | ReN > 10 | Torsion dominante (alarme `NOETIC_THRESHOLD`) |
| ε régularisation | 1e-6 / 1e-8 | Stabilité numérique du ReN |

## Limites

- Résolution fréquentielle : `Δf = fs / N_FFT` — deux pics plus proches que Δf ne sont pas résolus.
- Nyquist : `f0 · 2^(n_octaves) < fs/2`.
- Stationnarité locale sur la fenêtre `Tw` ; les transitoires < Tw sont lissés.
- **ReN ∝ 1/amplitude** (Rc au dénominateur) : comparer des ReN entre signaux
  exige une normalisation d'amplitude préalable commune. Voir CHANGELOG v1.0.0.
