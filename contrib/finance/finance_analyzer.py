"""
Analyse financière / séries temporelles lentes avec l'ASH
Usage: python finance_analyzer.py fichier.csv [freq_sampling] [f0] [octaves]
Auteur: Patrice Portemann
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch, find_peaks

def build_noetic_grid(f0, octaves):
    n_notes = octaves * 12
    return f0 * (2.0 ** (np.arange(n_notes) / 12.0))

def spectral_projection(signal, fs, freqs_noetic, nperseg=256):
    if len(signal) < nperseg:
        return np.zeros_like(freqs_noetic)
    freqs, psd = welch(signal, fs=fs, nperseg=nperseg, return_onesided=True)
    coeffs = np.interp(freqs_noetic, freqs, np.sqrt(psd), left=0, right=0)
    return coeffs

def compute_residues(coeffs, freqs_noetic):
    Rc = np.sum(coeffs)
    if Rc < 1e-12:
        return 0.0, 0, 1.0
    # Détection de pics
    thresh = 0.1 * np.max(coeffs) if np.max(coeffs) > 0 else 0
    peaks, _ = find_peaks(coeffs, height=thresh)
    Rtop = len(peaks)
    if Rtop >= 2:
        f_peaks = freqs_noetic[peaks]
        ratios = f_peaks[1:] / f_peaks[:-1]
        log_ratios = np.log(ratios)
        mean_log = np.mean(log_ratios)
        if mean_log > 1e-12:
            Rdyn = np.std(log_ratios) / mean_log
        else:
            Rdyn = 1.0
    else:
        Rdyn = 1.0
    return Rc, Rtop, Rdyn

def main():
    if len(sys.argv) < 2:
        print("Usage: python finance_analyzer.py fichier.csv [fs] [f0] [octaves]")
        print("  fs : fréquence d'échantillonnage (défaut 1)")
        print("  f0 : fréquence fondamentale (défaut 0.001 Hz, adaptée aux basses fréquences)")
        print("  octaves : nombre d'octaves (défaut 3)")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    fs = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    f0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.001
    octaves = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    
    # Lecture CSV
    df = pd.read_csv(csv_file)
    # Cherche colonne de signal
    sig_col = None
    for col in df.columns:
        if col.lower() == 'signal':
            sig_col = col
            break
    if sig_col is None:
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) == 0:
            print("Erreur : aucune colonne numérique trouvée")
            sys.exit(1)
        sig_col = num_cols[0]
    signal = df[sig_col].values
    # Si une colonne temps existe, on peut l'utiliser pour déterminer fs (non obligatoire)
    print(f"Signal : {len(signal)} points, fs={fs} Hz, f0={f0} Hz, octaves={octaves}")
    
    # Grille noétique adaptée aux basses fréquences
    freqs_noetic = build_noetic_grid(f0, octaves)
    # Vérifier que la plus haute fréquence ne dépasse pas fs/2
    if freqs_noetic[-1] > fs/2:
        print(f"Attention : la grille s'arrête à {freqs_noetic[-1]:.2f} Hz, au-delà de Nyquist ({fs/2:.2f} Hz). Réduisez f0 ou octaves.")
    
    # Analyse
    coeffs = spectral_projection(signal, fs, freqs_noetic, nperseg=min(256, len(signal)//2))
    Rc, Rtop, Rdyn = compute_residues(coeffs, freqs_noetic)
    
    # Résultats
    print("\n=== Résultats ASH (finance) ===")
    print(f"Rc    = {Rc:.6e}")
    print(f"Rtop  = {Rtop}")
    print(f"Rdyn  = {Rdyn:.4f}")
    
    # Sauvegarde
    with open("finance_results.txt", "w") as f:
        f.write(f"Rc={Rc}\nRtop={Rtop}\nRdyn={Rdyn}\n")
    np.savetxt("finance_coeffs.csv", coeffs, delimiter=",", header="coeffs", comments="")
    
    # Graphique optionnel du spectre (échelle linéaire, plus lisible pour basses fréquences)
    plt.figure()
    plt.plot(freqs_noetic, coeffs, 'b-')
    plt.scatter(freqs_noetic, coeffs, c='red', s=20)
    plt.xlabel('Fréquence (Hz)')
    plt.ylabel('Amplitude spectrale')
    plt.title(f'Spectre ASH (financier) – {csv_file}')
    plt.grid(True)
    plt.savefig("finance_spectrum.png")
    plt.show()
    print("Fichiers sauvegardés : finance_results.txt, finance_coeffs.csv, finance_spectrum.png")

if __name__ == "__main__":
    main()
