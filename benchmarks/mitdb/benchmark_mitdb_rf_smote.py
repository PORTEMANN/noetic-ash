"""
benchmark_mitdb_rf_smote.py
Validation ASH sur MIT-BIH 100 avec SMOTE + Random Forest.
Comparaison ASH, FFT+LDA, Ondelettes+SVM.

Dépendances : numpy, scipy, wfdb, scikit-learn, imbalanced-learn, pywt
Note C12.1 : ce script réimplémente l'extraction des invariants en local
(extract_ash_features) pour produire un vecteur de descripteurs 10-dim
[Rc, Rtop, Rdyn, E1..E7] destiné au classifieur. La référence canonique
reste src/python/ash_core.py (classe ASH).
"""

import numpy as np
import wfdb
from scipy.signal import welch, find_peaks
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, recall_score, precision_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import pywt
import os

# ---------- Paramètres ----------
RECORD_NAME = '100'
WINDOW_SIZE = 256
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

def fft_features(signal, fs, nbins=30):
    freqs, psd = welch(signal, fs=fs, nperseg=min(WINDOW_SIZE, len(signal)))
    return psd[:nbins]

def wavelet_features(signal, levels=5):
    coeffs = pywt.wavedec(signal, 'sym4', level=levels)
    return np.array([np.sum(np.square(c)) for c in coeffs])

# ---------- Chargement ----------
def download_and_load_mitdb(record_name):
    if not os.path.exists(f"{record_name}.dat"):
        print(f"Téléchargement de l'enregistrement {record_name}...")
        wfdb.dl_database('mitdb', dl_dir='.', records=[record_name])
    record = wfdb.rdrecord(record_name)
    signal = record.p_signal[:, 0]
    fs = record.fs
    annotation = wfdb.rdann(record_name, 'atr')
    return signal, fs, annotation.sample, annotation.symbol

def create_labels(signal_len, fs, ann_samples, ann_symbols, window_size, hop):
    abnormal_symbols = {'V', 'A', 'F', 'L', 'R', 'f', 'j', 'E', 'J', 'S', 'a', 'e'}
    n_windows = (signal_len - window_size) // hop + 1
    labels = []
    for i in range(n_windows):
        start = i * hop
        end = start + window_size
        is_abnormal = False
        for sa, sym in zip(ann_samples, ann_symbols):
            if start <= sa < end and sym in abnormal_symbols:
                is_abnormal = True
                break
        labels.append(1 if is_abnormal else 0)
    return np.array(labels)

def extract_descriptors(signal, fs, labels, window_size, hop):
    n_windows = len(labels)
    X_ash, X_fft, X_wav = [], [], []
    for i in range(n_windows):
        start = i * hop
        seg = signal[start:start+window_size]
        X_ash.append(extract_ash_features(seg, fs))
        X_fft.append(fft_features(seg, fs))
        X_wav.append(wavelet_features(seg))
    return np.array(X_ash), np.array(X_fft), np.array(X_wav)

# ---------- Évaluation avec SMOTE ----------
def evaluate_smote(X_train, y_train, X_test, y_test, clf):
    smote = SMOTE(random_state=RANDOM_SEED)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    clf.fit(X_train_res, y_train_res)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return acc, f1, recall, precision, cm

# ---------- Main ----------
def main():
    print("=== Validation ASH sur ECG réel (MIT-BIH 100) avec SMOTE et Random Forest ===")
    signal, fs, ann_samples, ann_symbols = download_and_load_mitdb(RECORD_NAME)
    print(f"Signal : {len(signal)} échantillons, fs={fs} Hz")
    labels = create_labels(len(signal), fs, ann_samples, ann_symbols, WINDOW_SIZE, HOP)
    print(f"Fenêtres : {len(labels)} (normaux={np.sum(labels==0)}, anormaux={np.sum(labels==1)})")

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

    # Split
    X_ash_train, X_ash_test, y_train, y_test = train_test_split(X_ash, labels, test_size=0.3, random_state=RANDOM_SEED, stratify=labels)
    X_fft_train, X_fft_test, _, _ = train_test_split(X_fft_pca, labels, test_size=0.3, random_state=RANDOM_SEED, stratify=labels)
    X_wav_train, X_wav_test, _, _ = train_test_split(X_wav, labels, test_size=0.3, random_state=RANDOM_SEED, stratify=labels)

    # Classifieurs
    methods = [
        ("ASH + Random Forest", RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED)),
        ("ASH + kNN", KNeighborsClassifier(3)),
        ("ASH + SVM", SVC(kernel='rbf', gamma='scale')),
        ("FFT + LDA", LinearDiscriminantAnalysis()),
        ("Ondelettes + SVM", SVC(kernel='rbf', gamma='scale'))
    ]

    print("\n=== Avec SMOTE (rééquilibrage) ===")
    for name, clf in methods:
        if "ASH" in name:
            acc, f1, rec, prec, cm = evaluate_smote(X_ash_train, y_train, X_ash_test, y_test, clf)
        elif "FFT" in name:
            acc, f1, rec, prec, cm = evaluate_smote(X_fft_train, y_train, X_fft_test, y_test, clf)
        else:
            acc, f1, rec, prec, cm = evaluate_smote(X_wav_train, y_train, X_wav_test, y_test, clf)
        print(f"\n{name} :")
        print(f"  Accuracy = {acc:.4f}, F1 = {f1:.4f}, Recall = {rec:.4f}, Precision = {prec:.4f}")
        print(f"  Matrice de confusion :\n{cm}")

if __name__ == "__main__":
    main()
