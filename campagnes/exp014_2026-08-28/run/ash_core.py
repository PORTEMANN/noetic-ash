#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASH — Analyseur spectral à géométrie harmonique (noyau consolidé).

noetic-ash, couche 7 (acquisition) de l'écosystème Noetic Physics.
Auteur : Patrice Portemann
Licence : MIT
Version : 1.0.0

Consolidation de : ash_optimized.py (base), noetic_core_analyzer_v3.py
(formules identiques — vérifié le 26/08/2026), noetic_core_analyzer.py/_v2
(analysés, aucune divergence numérique).

Fondements noétiques : la grille f_n = f0 · 2^(n/12) est la discrétisation
spectrale minimale compatible avec la périodicité du champ de torsion du
Koilon (spectral-triple-minimality, Thm T1, dim_spec = 7 × 12 = 84).
Le ReN est une construction phénoménologique (voir docs/algorithm.md §7.4).
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, welch

__version__ = "1.0.0"

# Régimes dynamiques (classification du nombre de Reynolds noétique)
REGIME_COSMOLOGICAL = "Cosmologique (pression dominante)"   # ReN < 1
REGIME_MESO = "Méso (industriel / transition)"              # 1 ≤ ReN ≤ 10
REGIME_QUANTUM = "Quantique (torsion dominante)"            # ReN > 10
REGIME_UNDEFINED = "indéfini"

# Seuils de régime (fixés par le protocole C12.1, jamais ajustés sur données)
REN_THRESHOLD_COSMOLOGICAL = 1.0
REN_THRESHOLD_QUANTUM = 10.0

# Convention : avec moins de 2 pics, le désaccord harmonique est indéfini
# et fixé à 1.0 (désaccord maximal par convention — voir docs/algorithm.md §2.3)
RDYN_NO_PEAK_PAIR = 1.0


class ASH:
    """Analyseur spectral à géométrie harmonique (ASH).

    The equal-temperament grid $f_n = f_0 \\cdot 2^{n/12}$ implements the
    minimal spectral discretization compatible with the Koilon's torsion
    field periodicity (see spectral-triple-minimality, Thm T1).

    Args:
        fs: Sampling frequency (Hz). If None, taken from `signal_type` defaults.
        signal_type: 'eeg', 'ecg', 'vibration' or 'generic'.
        f0: Fundamental frequency of the noetic grid (Hz). Fixed by the
            physical domain — never fitted to data (C12.1).
        n_octaves: Number of octaves (12 notes each, max 7 bands used).
        window_duration: Analysis window length (seconds).
        overlap: Window overlap ratio in [0, 1).
        nperseg: Welch segment length (auto if None, clamped to [64, 1024]).

    Note (C12.1): all grid parameters are fixed by the physical domain.
    """

    #: Default parameters per physical domain (fixed, never fitted).
    DEFAULTS: Dict[str, Dict[str, float]] = {
        "eeg": {"fs": 250.0, "f0": 1.0, "n_octaves": 4, "window_dur": 2.0},
        "ecg": {"fs": 360.0, "f0": 1.0, "n_octaves": 4, "window_dur": 2.0},
        "vibration": {"fs": 1000.0, "f0": 10.0, "n_octaves": 5, "window_dur": 1.0},
        "generic": {"fs": 250.0, "f0": 1.0, "n_octaves": 4, "window_dur": 2.0},
    }

    def __init__(
        self,
        fs: Optional[float] = None,
        signal_type: str = "generic",
        f0: Optional[float] = None,
        n_octaves: Optional[int] = None,
        window_duration: Optional[float] = None,
        overlap: float = 0.5,
        nperseg: Optional[int] = None,
    ) -> None:
        if not 0.0 <= overlap < 1.0:
            raise ValueError("overlap doit être dans [0, 1)")
        defaults = self.DEFAULTS.get(signal_type, self.DEFAULTS["generic"])
        self.signal_type = signal_type
        self.fs = float(fs if fs is not None else defaults["fs"])
        self.f0 = float(f0 if f0 is not None else defaults["f0"])
        self.n_octaves = int(n_octaves if n_octaves is not None else defaults["n_octaves"])
        self.window_duration = float(
            window_duration if window_duration is not None else defaults["window_dur"]
        )
        self.overlap = float(overlap)
        self.nperseg = int(
            nperseg if nperseg is not None else self.window_duration * self.fs * 0.5
        )
        self.nperseg = max(64, min(self.nperseg, 1024))  # bornes raisonnables
        self._build_grid()

    # ------------------------------------------------------------------ #
    # Grille noétique                                                     #
    # ------------------------------------------------------------------ #

    def _build_grid(self) -> None:
        """Pré-calcule la grille f_n = f0 · 2^(n/12) (12 notes par octave)."""
        n_notes = self.n_octaves * 12
        self.freqs_noetic = self.f0 * (2.0 ** (np.arange(n_notes) / 12.0))

    # ------------------------------------------------------------------ #
    # Étapes de l'analyse                                                 #
    # ------------------------------------------------------------------ #

    def _spectral_projection(self, signal: np.ndarray) -> np.ndarray:
        """Projette le spectre de Welch (√PSD) sur la grille noétique."""
        freqs, psd = welch(
            signal, fs=self.fs, nperseg=min(self.nperseg, len(signal)),
            return_onesided=True,
        )
        return np.interp(self.freqs_noetic, freqs, np.sqrt(psd), left=0, right=0)

    def _compute_residues(self, coeffs: np.ndarray) -> Tuple[float, int, float]:
        """Triplet d'invariants (Rc, Rtop, Rdyn).

        - Rc : énergie spectrale totale sur la grille (pression du Koilon)
        - Rtop : nombre de pics locaux > 10 % du max (singularités topologiques)
        - Rdyn : écart-type normalisé des rapports logarithmiques inter-pics
          (écart à la pureté harmonique ; RDYN_NO_PEAK_PAIR si < 2 pics)
        """
        Rc = float(np.sum(coeffs))
        if Rc < 1e-12:
            return 0.0, 0, RDYN_NO_PEAK_PAIR
        peaks, _ = find_peaks(coeffs, height=0.1 * float(np.max(coeffs)))
        Rtop = int(len(peaks))
        if Rtop >= 2:
            f_peaks = self.freqs_noetic[peaks]
            log_ratios = np.log(f_peaks[1:] / f_peaks[:-1])
            Rdyn = float(np.std(log_ratios) / (np.mean(log_ratios) + 1e-8))
        else:
            Rdyn = RDYN_NO_PEAK_PAIR
        return Rc, Rtop, Rdyn

    def _project_bands(self, coeffs: np.ndarray) -> np.ndarray:
        """Projette sur les 7 plans noétiques E1..E7 (somme par octave, L2-normalisé)."""
        bands = np.zeros(7)
        for oct_idx in range(min(self.n_octaves, 7)):
            start = oct_idx * 12
            bands[oct_idx] = np.sum(coeffs[start : start + 12])
        norm = np.linalg.norm(bands)
        if norm > 1e-8:
            bands /= norm
        return bands

    @staticmethod
    def _compute_ren(
        Rc: float, Rtop: int, Rdyn: float, bands: np.ndarray
    ) -> Tuple[float, str]:
        """Nombre de Reynolds noétique : ReN = ((Rdyn+ε)·(Rtop·D))/(Rc·(H+ε)) × 100.

        Numérateur : torsion λT[Ψ] (Rdyn) × complexité topologique (Rtop·D).
        Dénominateur : pression J_cosmo(z) (Rc) × dispersion entropique (H).

        ATTENTION — propriété effective : ReN ∝ 1/amplitude (Rc est au
        dénominateur et croît linéairement avec l'amplitude). Seuls Rtop,
        Rdyn et les bandes normalisées sont strictement invariants par
        changement d'échelle. La §6.1 de docs/algorithm.md a été corrigée
        en conséquence (B3-FAIL constaté le 26/08/2026).
        """
        total = float(np.sum(bands))
        if total < 1e-12:
            return 0.0, REGIME_UNDEFINED
        p = bands / total
        entropy = float(-np.sum(p * np.log(p + 1e-12)))
        sorted_bands = np.sort(bands)[::-1]
        dominance = float(sorted_bands[0] - sorted_bands[1]) if len(sorted_bands) > 1 else float(sorted_bands[0])
        torsion = Rtop * dominance
        pressure = Rc * (entropy + 1e-8)
        ReN = float(((Rdyn + 1e-6) * torsion) / (pressure + 1e-8) * 100.0)
        if ReN > REN_THRESHOLD_QUANTUM:
            regime = REGIME_QUANTUM
        elif ReN < REN_THRESHOLD_COSMOLOGICAL:
            regime = REGIME_COSMOLOGICAL
        else:
            regime = REGIME_MESO
        return ReN, regime

    # ------------------------------------------------------------------ #
    # API publique (figée pour v1.0.0)                                    #
    # ------------------------------------------------------------------ #

    def process_window(self, signal_segment: np.ndarray) -> Dict:
        """Analyse une fenêtre unique.

        Returns:
            Dict(Rc, Rtop, Rdyn, bands, ReN, regime, coeffs) où ReN est le
            Reynolds Noetic Number discriminant les régimes cosmologique,
            méso et quantique.
        """
        signal_segment = np.asarray(signal_segment, dtype=float)
        coeffs = self._spectral_projection(signal_segment)
        Rc, Rtop, Rdyn = self._compute_residues(coeffs)
        bands = self._project_bands(coeffs)
        ReN, regime = self._compute_ren(Rc, Rtop, Rdyn, bands)
        return {
            "Rc": Rc,
            "Rtop": Rtop,
            "Rdyn": Rdyn,
            "bands": bands,
            "ReN": ReN,
            "regime": regime,
            "coeffs": coeffs,
        }

    def process_signal(
        self,
        signal: np.ndarray,
        save_csv: bool = False,
        csv_prefix: str = "ash",
    ) -> pd.DataFrame:
        """Analyse un signal 1D complet par fenêtrage glissant.

        Args:
            signal: série temporelle 1D.
            save_csv: si True, écrit `{csv_prefix}_results.csv` et
                `{csv_prefix}_bands.csv` dans le répertoire courant.
            csv_prefix: préfixe des fichiers de sortie.

        Returns:
            DataFrame (time, Rc, Rtop, Rdyn, bands, ReN, regime).
        """
        signal = np.asarray(signal, dtype=float)
        window_size = int(self.window_duration * self.fs)
        hop = max(1, int(window_size * (1.0 - self.overlap)))
        n_windows = (len(signal) - window_size) // hop + 1
        if n_windows <= 0:
            raise ValueError(
                f"Signal trop court ({len(signal)} pts) pour une fenêtre de {window_size} pts"
            )

        rows = []
        for i in range(n_windows):
            start = i * hop
            seg = signal[start : start + window_size]
            t_center = (start + window_size / 2.0) / self.fs
            if float(np.std(seg)) < 1e-6:
                # Fenêtre constante : pas de contenu spectral
                rows.append({
                    "time": t_center, "Rc": 0.0, "Rtop": 0,
                    "Rdyn": RDYN_NO_PEAK_PAIR, "bands": np.zeros(7),
                    "ReN": 0.0, "regime": REGIME_COSMOLOGICAL,
                })
            else:
                r = self.process_window(seg)
                rows.append({
                    "time": t_center, "Rc": r["Rc"], "Rtop": r["Rtop"],
                    "Rdyn": r["Rdyn"], "bands": r["bands"],
                    "ReN": r["ReN"], "regime": r["regime"],
                })

        df = pd.DataFrame(rows)
        if save_csv:
            df.to_csv(f"{csv_prefix}_results.csv", index=False)
            bands_df = pd.DataFrame(
                df["bands"].tolist(), columns=[f"B{i+1}" for i in range(7)]
            )
            bands_df.insert(0, "time", df["time"])
            bands_df.to_csv(f"{csv_prefix}_bands.csv", index=False)
        return df

    # ------------------------------------------------------------------ #
    # Construction depuis un CSV                                          #
    # ------------------------------------------------------------------ #

    @classmethod
    def from_csv(
        cls, csv_path: str, signal_type: str = "generic", **kwargs
    ) -> Tuple["ASH", np.ndarray]:
        """Crée une instance ASH et charge le signal depuis un CSV.

        La colonne `signal` est utilisée si présente, sinon la première
        colonne numérique. Si `fs` n'est pas fourni et qu'une colonne
        `time` existe, fs est déduit du pas temporel moyen.
        """
        df = pd.read_csv(csv_path)
        if "signal" in df.columns:
            signal = df["signal"].to_numpy(dtype=float)
        else:
            num_cols = df.select_dtypes(include=[np.number]).columns
            if len(num_cols) == 0:
                raise ValueError("Aucune colonne numérique trouvée")
            signal = df[num_cols[0]].to_numpy(dtype=float)
        if "fs" not in kwargs:
            if "time" in df.columns and len(df["time"]) > 1:
                dt = float(np.mean(np.diff(df["time"])))
                kwargs["fs"] = 1.0 / dt
            else:
                kwargs["fs"] = cls.DEFAULTS.get(signal_type, cls.DEFAULTS["generic"])["fs"]
        return cls(signal_type=signal_type, **kwargs), signal


# ---------------------------------------------------------------------- #
# Ligne de commande                                                       #
# ---------------------------------------------------------------------- #

def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ash_core.py fichier.csv [signal_type]")
        print("  signal_type : eeg, ecg, vibration, generic (défaut : generic)")
        sys.exit(1)

    csv_path = sys.argv[1]
    signal_type = sys.argv[2] if len(sys.argv) > 2 else "generic"
    print(f"Analyse de {csv_path} (signal_type={signal_type})")
    try:
        ash, signal = ASH.from_csv(csv_path, signal_type=signal_type)
        df = ash.process_signal(signal)
        print("\n=== Résumé ===")
        print(df[["time", "Rc", "Rtop", "Rdyn", "ReN", "regime"]].head())
        print(f"Rc moyen   = {df['Rc'].mean():.3e}")
        print(f"Rtop moyen = {df['Rtop'].mean():.2f}")
        print(f"Rdyn moyen = {df['Rdyn'].mean():.4f}")
        print(f"ReN moyen  = {df['ReN'].mean():.4f}")
        print(f"Régime majoritaire : {df['regime'].mode()[0]}")
    except Exception as exc:  # pragma: no cover
        print(f"Erreur : {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
