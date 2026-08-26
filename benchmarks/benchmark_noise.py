"""
benchmark_noise.py - Comparaison de robustesse au bruit
ASH vs FFT+LDA vs Ondelettes+SVM sur signaux synthétiques avec bruit
Auteur : Patrice Portemann

Datasets : régénérer d'abord via les générateurs seedés de examples/
(les CSV sont ignorés par git — voir ../.gitignore et SHASUMS.txt).
"""

import numpy as np
import pandas as pd
from scipy.signal import welch, find_peaks
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pywt
import os

# ---------- Paramètres ----------
WINDOW_SIZE = 256
HOP = 128
SEED = 42
np.random.seed(SEED)

# ---------- Fonctions ASH ----------
def build_noetic_grid(f0, octaves):
    n_notes = octaves * 12
    return f0 * (2.0 ** (np.arange(n_notes) / 12.0))

def extract_ash_features(signal, fs, f0, octaves, nperseg=256):
    if len(signal) < nperseg:
        return np.zeros(10)
    freqs_noetic = build_noetic_grid(f0, octaves)
    freqs, psd = welch(signal, fs=fs, nperseg=nperseg, return_onesided=True)
    coeffs = np.interp(freqs_noetic, freqs, np.sqrt(psd), left=0, right=0)
    Rc = np.sum(coeffs)
    if Rc < 1e-12:
        return np.zeros(10)
    peaks, _ = find_peaks(coeffs, height=0.1*np.max(coeffs))
    Rtop = len(peaks)
    if Rtop >= 2:
        f_peaks = freqs_noetic[peaks]
        log_ratios = np.log(f_peaks[1:] / f_peaks[:-1])
        Rdyn = np.std(log_ratios) / (np.mean(log_ratios) + 1e-8)
    else:
        Rdyn = 1.0
    bands = np.zeros(7)
    for o in range(min(octaves, 7)):
        start = o*12
        bands[o] = np.sum(coeffs[start:start+12])
    norm = np.linalg.norm(bands)
    if norm > 1e-8:
        bands /= norm
    return np.concatenate(([Rc, Rtop, Rdyn], bands))

# ---------- Autres features ----------
def fft_features(signal, fs, nbins=30):
    freqs, psd = welch(signal, fs=fs, nperseg=min(WINDOW_SIZE, len(signal)))
    return psd[:nbins]

def wavelet_features(signal, fs, levels=5):
    coeffs = pywt.wavedec(signal, 'sym4', level=levels)
    energies = [np.sum(np.square(c)) for c in coeffs]
    return np.array(energies)

# ---------- Chargement et fenêtrage ----------
def load_signal(filepath):
    df = pd.read_csv(filepath)
    if 'signal' in df.columns:
        return df['signal'].values
    num_cols = df.select_dtypes(include=[np.number]).columns
    return df[num_cols[0]].values

def extract_windows(signal, window_size, hop):
    windows = []
    for start in range(0, len(signal) - window_size + 1, hop):
        windows.append(signal[start:start+window_size])
    return np.array(windows)

# ---------- Ajout de bruit ----------
def add_noise(signal, snr_db):
    """Ajoute un bruit blanc gaussien pour un SNR donné (en dB)."""
    signal_power = np.mean(signal**2)
    noise_power = signal_power / (10**(snr_db/10))
    noise = np.sqrt(noise_power) * np.random.randn(len(signal))
    return signal + noise

# ---------- Construction du dataset avec bruit ----------
def build_dataset_noisy(fichiers, snr_db):
    X_ash, X_fft, X_wav, y = [], [], [], []
    for fname, params in fichiers.items():
        if not os.path.exists(fname):
            print(f"Fichier manquant : {fname}")
            continue
        signal = load_signal(fname)
        # Ajouter du bruit à tout le signal
        noisy_signal = add_noise(signal, snr_db)
        windows = extract_windows(noisy_signal, WINDOW_SIZE, HOP)
        if len(windows) == 0:
            continue
        for win in windows:
            feat_ash = extract_ash_features(win, params['fs'], params['f0'], params['octaves'])
            X_ash.append(feat_ash)
            X_fft.append(fft_features(win, params['fs']))
            X_wav.append(wavelet_features(win, params['fs']))
            y.append(params['label'])
    return (np.array(X_ash), np.array(X_fft), np.array(X_wav), np.array(y))

# ---------- Évaluation ----------
def evaluate(features_train, y_train, features_test, y_test, classifier):
    clf = classifier
    clf.fit(features_train, y_train)
    y_pred = clf.predict(features_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    return acc, f1

# ---------- Main ----------
def main():
    # Fichiers et paramètres
    fichiers = {
        'signal_sinusoidal.csv': {'fs': 250, 'f0': 1.0, 'octaves': 4, 'label': 0},
        'vibration_moteur_sain.csv': {'fs': 1000, 'f0': 10.0, 'octaves': 5, 'label': 1},
        'ecg_normal.csv': {'fs': 360, 'f0': 1.0, 'octaves': 4, 'label': 2},
        'eeg_intention.csv': {'fs': 250, 'f0': 1.0, 'octaves': 4, 'label': 3}
    }

    snr_levels = [float('inf'), 20, 10, 5, 0]  # inf = propre
    results = []

    for snr in snr_levels:
        snr_label = "Propre" if snr == float('inf') else f"{snr} dB"
        print(f"\n--- SNR = {snr_label} ---")

        # Construire dataset bruité
        X_ash, X_fft, X_wav, y = build_dataset_noisy(fichiers, snr)
        if len(y) == 0:
            print("  Aucune fenêtre générée")
            continue

        # Split train/test (70/30)
        X_ash_train, X_ash_test, y_train, y_test = train_test_split(
            X_ash, y, test_size=0.3, random_state=SEED, stratify=y)
        X_fft_train, X_fft_test, _, _ = train_test_split(
            X_fft, y, test_size=0.3, random_state=SEED, stratify=y)
        X_wav_train, X_wav_test, _, _ = train_test_split(
            X_wav, y, test_size=0.3, random_state=SEED, stratify=y)

        # Normalisation et PCA pour FFT
        scaler_fft = StandardScaler()
        X_fft_train = scaler_fft.fit_transform(X_fft_train)
        X_fft_test = scaler_fft.transform(X_fft_test)
        pca = PCA(n_components=min(20, X_fft_train.shape[1]))
        X_fft_train_pca = pca.fit_transform(X_fft_train)
        X_fft_test_pca = pca.transform(X_fft_test)

        # Normalisation pour ondelettes
        scaler_wav = StandardScaler()
        X_wav_train = scaler_wav.fit_transform(X_wav_train)
        X_wav_test = scaler_wav.transform(X_wav_test)

        # ASH + k-NN
        acc_ash, f1_ash = evaluate(X_ash_train, y_train, X_ash_test, y_test, KNeighborsClassifier(n_neighbors=3))
        # FFT + PCA + LDA
        acc_fft, f1_fft = evaluate(X_fft_train_pca, y_train, X_fft_test_pca, y_test, LinearDiscriminantAnalysis())
        # Ondelettes + SVM
        acc_wav, f1_wav = evaluate(X_wav_train, y_train, X_wav_test, y_test, SVC(kernel='rbf', gamma='scale'))

        results.append((snr_label, acc_ash, f1_ash, acc_fft, f1_fft, acc_wav, f1_wav))

        print(f"  ASH + kNN   : acc={acc_ash:.4f}, f1={f1_ash:.4f}")
        print(f"  FFT+LDA     : acc={acc_fft:.4f}, f1={f1_fft:.4f}")
        print(f"  Ond+SVM     : acc={acc_wav:.4f}, f1={f1_wav:.4f}")

    # Affichage tableau final
    print("\n" + "="*80)
    print("Résumé de robustesse au bruit (classification 4 classes)")
    print("="*80)
    print(f"{'SNR':>8} | {'ASH acc':>8} | {'ASH f1':>8} | {'FFT acc':>8} | {'FFT f1':>8} | {'Ond acc':>8} | {'Ond f1':>8}")
    print("-"*80)
    for row in results:
        snr, a_acc, a_f1, f_acc, f_f1, o_acc, o_f1 = row
        print(f"{snr:>8} | {a_acc:>8.4f} | {a_f1:>8.4f} | {f_acc:>8.4f} | {f_f1:>8.4f} | {o_acc:>8.4f} | {o_f1:>8.4f}")

if __name__ == "__main__":
    main()
