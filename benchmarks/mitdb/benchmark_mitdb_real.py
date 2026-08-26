# -*- coding: utf-8 -*-
"""
benchmark_mitdb_real.py
Validation de l'ASH sur la base MIT-BIH (enregistrement 100)
Classification binaire : battement normal vs anomalie (PVC)
Comparaison ASH, FFT+LDA, ondelettes+SVM
Nécessite : pip install wfdb numpy scipy scikit-learn pywt

Dataset : PhysioNet mitdb, record 100 — vérification SHA-256 dans ../SHASUMS.txt.
"""

import numpy as np
import wfdb
from scipy.signal import welch, find_peaks
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import os

# ---------- Paramètres ----------
RECORD_NAME = '100'          # Enregistrement MIT-BI
WINDOW_SIZE = 256            # points (environ 0,7 s à 360 Hz)
HOP = 128
F0 = 1.0
OCTAVES = 4
NPERSEG = 256
RANDOM_SEED = 42

# ---------- Grille noétique ----------
def build_noetic_grid(f0=F0, octaves=OCTAVES):
    n_notes = octaves * 12
    return f0 * (2.0 ** (np.arange(n_notes) / 12.0))

def extract_ash_features(signal, fs, f0=F0, octaves=OCTAVES, nperseg=NPERSEG):
    if len(signal) < nperseg:
        return np.zeros(10)
    freqs_grid = build_noetic_grid(f0, octaves)
    freqs, psd = welch(signal, fs=fs, nperseg=nperseg, return_onesided=True)
    coeffs = np.interp(freqs_grid, freqs, np.sqrt(psd), left=0, right=0)
    Rc = np.sum(coeffs)
    if Rc < 1e-12:
        return np.zeros(10)
    peaks, _ = find_peaks(coeffs, height=0.1 * np.max(coeffs))
    Rtop = len(peaks)
    if Rtop >= 2:
        f_peaks = freqs_grid[peaks]
        log_ratios = np.log(f_peaks[1:] / f_peaks[:-1])
        Rdyn = np.std(log_ratios) / (np.mean(log_ratios) + 1e-8)
    else:
        Rdyn = 1.0
    bands = np.zeros(7)
    for o in range(min(octaves, 7)):
        start = o * 12
        bands[o] = np.sum(coeffs[start:start+12])
    norm = np.linalg.norm(bands)
    if norm > 1e-8:
        bands /= norm
    return np.concatenate(([Rc, Rtop, Rdyn], bands))

# ---------- Autres méthodes ----------
def fft_features(signal, fs, nbins=30):
    freqs, psd = welch(signal, fs=fs, nperseg=min(WINDOW_SIZE, len(signal)))
    return psd[:nbins]

def wavelet_features(signal, levels=5):
    import pywt
    coeffs = pywt.wavedec(signal, 'sym4', level=levels)
    return np.array([np.sum(np.square(c)) for c in coeffs])

# ---------- Téléchargement et lecture ----------
def download_and_load_mitdb(record_name):
    """Télécharge l'enregistrement MIT-BIH s'il n'existe pas, et retourne signal+annotations."""
    # Télécharger si le dossier n'existe pas
    if not os.path.exists(f"{record_name}.dat"):
        print(f"Téléchargement de l'enregistrement {record_name}...")
        wfdb.dl_database('mitdb', dl_dir='.', records=[record_name])
    # Lecture du signal
    record = wfdb.rdrecord(record_name)
    signal = record.p_signal[:, 0]  # canal MLII
    fs = record.fs
    # Lecture des annotations (symboles)
    annotation = wfdb.rdann(record_name, 'atr')
    return signal, fs, annotation.sample, annotation.symbol

# ---------- Création des étiquettes binaires (normal vs anomalie) ----------
def create_labels(signal_len, fs, ann_samples, ann_symbols, window_size, hop):
    """Étiquette chaque fenêtre : 0 = normal, 1 = anomalie (PVC, VEB, etc.)"""
    # Symboles anormaux typiques : 'V' (PVC), 'A' (APB), 'F' (fusion), 'L','R',...
    abnormal_symbols = {'V', 'A', 'F', 'L', 'R', 'f', 'j', 'E', 'J', 'S', 'a', 'e'}
    labels = []
    n_windows = (signal_len - window_size) // hop + 1
    for i in range(n_windows):
        start = i * hop
        end = start + window_size
        # Vérifier si une annotation anormale tombe dans la fenêtre
        is_abnormal = False
        for sa, sym in zip(ann_samples, ann_symbols):
            if start <= sa < end and sym in abnormal_symbols:
                is_abnormal = True
                break
        labels.append(1 if is_abnormal else 0)
    return np.array(labels)

# ---------- Extraction des descripteurs ----------
def extract_descriptors(signal, fs, labels, window_size, hop):
    n_windows = len(labels)
    X_ash = []
    X_fft = []
    X_wav = []
    for i in range(n_windows):
        start = i * hop
        seg = signal[start:start+window_size]
        X_ash.append(extract_ash_features(seg, fs))
        X_fft.append(fft_features(seg, fs))
        X_wav.append(wavelet_features(seg))
    return np.array(X_ash), np.array(X_fft), np.array(X_wav)

# ---------- Évaluation ----------
def evaluate_clf(features_train, y_train, features_test, y_test, clf):
    clf.fit(features_train, y_train)
    y_pred = clf.predict(features_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    return acc, f1

# ---------- Main ----------
def main():
    print("=== Validation ASH sur ECG réel (MIT-BIH 100) ===")
    # Chargement
    signal, fs, ann_samples, ann_symbols = download_and_load_mitdb(RECORD_NAME)
    print(f"Signal : {len(signal)} échantillons, fs={fs} Hz")

    # Création des étiquettes
    labels = create_labels(len(signal), fs, ann_samples, ann_symbols, WINDOW_SIZE, HOP)
    print(f"Nombre de fenêtres : {len(labels)} (normaux={np.sum(labels==0)}, anormaux={np.sum(labels==1)})")

    # Extraction des descripteurs
    print("Extraction des descripteurs...")
    X_ash, X_fft, X_wav = extract_descriptors(signal, fs, labels, WINDOW_SIZE, HOP)
    print(f"  ASH: {X_ash.shape}, FFT: {X_fft.shape}, Wavelet: {X_wav.shape}")

    # Normalisation
    scaler_fft = StandardScaler()
    X_fft = scaler_fft.fit_transform(X_fft)
    scaler_wav = StandardScaler()
    X_wav = scaler_wav.fit_transform(X_wav)

    # PCA pour FFT
    pca = PCA(n_components=min(20, X_fft.shape[1]))
    X_fft_pca = pca.fit_transform(X_fft)

    # Split train/test (70/30)
    from sklearn.model_selection import train_test_split
    idx = np.arange(len(labels))
    train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=RANDOM_SEED, stratify=labels)
    X_ash_train, X_ash_test = X_ash[train_idx], X_ash[test_idx]
    X_fft_train, X_fft_test = X_fft_pca[train_idx], X_fft_pca[test_idx]
    X_wav_train, X_wav_test = X_wav[train_idx], X_wav[test_idx]
    y_train, y_test = labels[train_idx], labels[test_idx]

    # Classifieurs
    print("\n=== Comparaison des méthodes ===")
    # ASH + kNN
    acc, f1 = evaluate_clf(X_ash_train, y_train, X_ash_test, y_test, KNeighborsClassifier(n_neighbors=3))
    print(f"ASH + kNN      : acc={acc:.4f}, f1={f1:.4f}")

    # ASH + SVM
    acc, f1 = evaluate_clf(X_ash_train, y_train, X_ash_test, y_test, SVC(kernel='rbf', gamma='scale'))
    print(f"ASH + SVM      : acc={acc:.4f}, f1={f1:.4f}")

    # FFT + PCA + LDA
    acc, f1 = evaluate_clf(X_fft_train, y_train, X_fft_test, y_test, LinearDiscriminantAnalysis())
    print(f"FFT + LDA      : acc={acc:.4f}, f1={f1:.4f}")

    # Ondelettes + SVM
    acc, f1 = evaluate_clf(X_wav_train, y_train, X_wav_test, y_test, SVC(kernel='rbf', gamma='scale'))
    print(f"Ondelettes + SVM: acc={acc:.4f}, f1={f1:.4f}")

if __name__ == "__main__":
    main()
