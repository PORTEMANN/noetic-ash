"""
benchmark_local.py - Comparaison ASH / FFT+LDA / Ondelettes+SVM / CNN 1D
Utilise les 4 fichiers CSV : sinusoïde, vibration moteur, ECG, EEG.
Auteur : Patrice Portemann

Dépendances : numpy, pandas, scipy, scikit-learn, pywt, tensorflow (CNN).
Datasets : régénérer via les générateurs seedés de examples/ (voir SHASUMS.txt).
B3-FAIL : le CNN 1D est peu adapté à ce petit jeu de données — résultat publié.
"""

import numpy as np
import pandas as pd
from scipy.signal import welch, find_peaks
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras import layers, models
import pywt
import os

# ---------- Paramètres ASH ----------
def build_noetic_grid(f0, octaves):
    n_notes = octaves * 12
    return f0 * (2.0 ** (np.arange(n_notes) / 12.0))

def extract_ash_features(signal, fs, f0, octaves, nperseg=256):
    """Extrait les 10 descripteurs ASH (Rc, Rtop, Rdyn, 7 bandes)"""
    freqs_noetic = build_noetic_grid(f0, octaves)
    if len(signal) < nperseg:
        return np.zeros(10)
    freqs, psd = welch(signal, fs=fs, nperseg=nperseg, return_onesided=True)
    coeffs = np.interp(freqs_noetic, freqs, np.sqrt(psd), left=0, right=0)
    Rc = np.sum(coeffs)
    peaks, _ = find_peaks(coeffs, height=0.1*np.max(coeffs) if np.max(coeffs)>0 else 0)
    Rtop = len(peaks)
    if Rtop >= 2:
        f_peaks = freqs_noetic[peaks]
        log_ratios = np.log(f_peaks[1:] / f_peaks[:-1])
        Rdyn = np.std(log_ratios) / (np.mean(log_ratios) + 1e-8)
    else:
        Rdyn = 1.0
    bands = np.zeros(7)
    for o in range(min(octaves,7)):
        start = o*12
        bands[o] = np.sum(coeffs[start:start+12])
    norm = np.linalg.norm(bands)
    if norm > 1e-8:
        bands /= norm
    return np.concatenate(([Rc, Rtop, Rdyn], bands))

# ---------- Features concurrentes ----------
def fft_power_features(signal, fs, nbins=30):
    """Retourne les 30 premières bandes de puissance spectrale (Welch)"""
    freqs, psd = welch(signal, fs=fs, nperseg=min(256, len(signal)))
    return psd[:nbins]

def wavelet_energy_features(signal, fs, levels=5):
    """Energies des coefficients d'ondelettes (Symlet 4)"""
    coeffs = pywt.wavedec(signal, 'sym4', level=levels)
    energies = [np.sum(np.square(c)) for c in coeffs]
    return np.array(energies)

# ---------- Modèle CNN ----------
def build_cnn(input_shape, num_classes):
    model = models.Sequential()
    model.add(layers.Conv1D(32, 3, activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling1D(2))
    model.add(layers.Conv1D(64, 3, activation='relu'))
    model.add(layers.GlobalAveragePooling1D())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(num_classes, activation='softmax'))
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# ---------- Chargement des signaux ----------
def load_signal_from_csv(filepath, signal_col='signal'):
    df = pd.read_csv(filepath)
    if signal_col not in df.columns:
        # Prendre la première colonne numérique
        num_cols = df.select_dtypes(include=[np.number]).columns
        signal_col = num_cols[0]
    return df[signal_col].values

def prepare_dataset(file_list, fs_dict, f0_dict, oct_dict, label_dict, window_size=256, hop=128):
    """
    Découpe chaque signal en fenêtres.
    file_list : noms de fichiers
    fs_dict : dict {nom: fs}
    f0_dict, oct_dict, label_dict : idem
    """
    X_ash = []
    X_fft = []
    X_wavelet = []
    X_raw = []
    y = []
    for name in file_list:
        signal = load_signal_from_csv(name)
        fs = fs_dict[name]
        f0 = f0_dict[name]
        oct = oct_dict[name]
        label = label_dict[name]
        n_windows = max(1, (len(signal) - window_size) // hop + 1)
        for i in range(n_windows):
            start = i * hop
            seg = signal[start:start+window_size]
            if len(seg) < window_size:
                break
            # ASH
            feat_ash = extract_ash_features(seg, fs, f0, oct)
            X_ash.append(feat_ash)
            # FFT
            feat_fft = fft_power_features(seg, fs)
            X_fft.append(feat_fft)
            # Wavelet
            feat_wav = wavelet_energy_features(seg, fs)
            X_wavelet.append(feat_wav)
            # Raw pour CNN
            X_raw.append(seg)
            y.append(label)
    return (np.array(X_ash), np.array(X_fft), np.array(X_wavelet),
            np.array(X_raw), np.array(y))

# ---------- Évaluation ----------
def evaluate_classifier(features_train, y_train, features_test, y_test, classifier):
    clf = classifier
    clf.fit(features_train, y_train)
    y_pred = clf.predict(features_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    return acc, f1

def evaluate_cnn(X_train, y_train, X_test, y_test, epochs=15, batch_size=32):
    num_classes = len(np.unique(y_train))
    input_shape = (X_train.shape[1], 1)
    model = build_cnn(input_shape, num_classes)
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0, validation_split=0.2)
    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    return acc, f1

# ---------- Main ----------
def main():
    # Fichiers (ajustez les noms exacts)
    file_list = [
        'signal_sinusoidal.csv',
        'vibration_moteur_sain.csv',
        'ecg_normal.csv',
        'eeg_intention.csv'
    ]
    # Paramètres pour chaque fichier (fs, f0, octaves, label)
    fs_dict = {
        'signal_sinusoidal.csv': 250,
        'vibration_moteur_sain.csv': 1000,
        'ecg_normal.csv': 360,
        'eeg_intention.csv': 250
    }
    f0_dict = {
        'signal_sinusoidal.csv': 1.0,
        'vibration_moteur_sain.csv': 10.0,
        'ecg_normal.csv': 1.0,
        'eeg_intention.csv': 1.0
    }
    oct_dict = {
        'signal_sinusoidal.csv': 4,
        'vibration_moteur_sain.csv': 5,
        'ecg_normal.csv': 4,
        'eeg_intention.csv': 4
    }
    label_dict = {
        'signal_sinusoidal.csv': 0,
        'vibration_moteur_sain.csv': 1,
        'ecg_normal.csv': 2,
        'eeg_intention.csv': 3
    }
    print("Chargement et extraction des features...")
    X_ash, X_fft, X_wavelet, X_raw, y = prepare_dataset(
        file_list, fs_dict, f0_dict, oct_dict, label_dict
    )
    print(f"Nombre total de fenêtres : {len(y)}")

    # Split train/test (70/30)
    X_ash_train, X_ash_test, y_train, y_test = train_test_split(
        X_ash, y, test_size=0.3, random_state=42, stratify=y
    )
    X_fft_train, X_fft_test, _, _ = train_test_split(
        X_fft, y, test_size=0.3, random_state=42, stratify=y
    )
    X_wavelet_train, X_wavelet_test, _, _ = train_test_split(
        X_wavelet, y, test_size=0.3, random_state=42, stratify=y
    )
    X_raw_train, X_raw_test, _, _ = train_test_split(
        X_raw, y, test_size=0.3, random_state=42, stratify=y
    )

    # Normalisation pour FFT et wavelet
    scaler_fft = StandardScaler()
    X_fft_train = scaler_fft.fit_transform(X_fft_train)
    X_fft_test = scaler_fft.transform(X_fft_test)

    scaler_wav = StandardScaler()
    X_wavelet_train = scaler_wav.fit_transform(X_wavelet_train)
    X_wavelet_test = scaler_wav.transform(X_wavelet_test)

    # Réduction PCA pour FFT+LDA
    pca = PCA(n_components=min(20, X_fft_train.shape[1]))
    X_fft_train_pca = pca.fit_transform(X_fft_train)
    X_fft_test_pca = pca.transform(X_fft_test)

    # 1. ASH + k-NN
    print("\n=== ASH + k-NN (k=3) ===")
    acc, f1 = evaluate_classifier(X_ash_train, y_train, X_ash_test, y_test,
                                  KNeighborsClassifier(n_neighbors=3))
    print(f"Accuracy: {acc:.4f}, F1-macro: {f1:.4f}")

    # 2. ASH + SVM
    print("\n=== ASH + SVM (RBF) ===")
    acc, f1 = evaluate_classifier(X_ash_train, y_train, X_ash_test, y_test,
                                  SVC(kernel='rbf', gamma='scale'))
    print(f"Accuracy: {acc:.4f}, F1-macro: {f1:.4f}")

    # 3. FFT + PCA + LDA
    print("\n=== FFT + PCA + LDA ===")
    acc, f1 = evaluate_classifier(X_fft_train_pca, y_train, X_fft_test_pca, y_test,
                                  LinearDiscriminantAnalysis())
    print(f"Accuracy: {acc:.4f}, F1-macro: {f1:.4f}")

    # 4. Ondelettes + SVM
    print("\n=== Ondelettes (Sym4) + SVM ===")
    acc, f1 = evaluate_classifier(X_wavelet_train, y_train, X_wavelet_test, y_test,
                                  SVC(kernel='rbf', gamma='scale'))
    print(f"Accuracy: {acc:.4f}, F1-macro: {f1:.4f}")

    # 5. CNN 1D
    print("\n=== CNN 1D ===")
    X_raw_train_cnn = X_raw_train.reshape(X_raw_train.shape[0], X_raw_train.shape[1], 1)
    X_raw_test_cnn = X_raw_test.reshape(X_raw_test.shape[0], X_raw_test.shape[1], 1)
    acc, f1 = evaluate_cnn(X_raw_train_cnn, y_train, X_raw_test_cnn, y_test, epochs=10)
    print(f"Accuracy: {acc:.4f}, F1-macro: {f1:.4f}")

if __name__ == "__main__":
    main()
