import numpy as np
import pandas as pd
from scipy.signal import welch, find_peaks
import matplotlib.pyplot as plt

# ---------- 1. Chargement ----------
df = pd.read_csv('test_chaos.csv')
signal = df['Value'].values
time = df['Time'].values
fs = 1.0 / np.mean(np.diff(time))  # ~999 Hz
print(f"fs = {fs:.2f} Hz, signal length = {len(signal)}")

# ---------- 2. Paramètres ASH ----------
window_size = 256
hop = 128
f0 = 1.0
octaves = 4
n_notes = octaves * 12
freqs_noetic = f0 * (2.0 ** (np.arange(n_notes) / 12.0))

# ---------- 3. Fonction d'extraction ----------
def extract_features(seg, fs, freqs_noetic):
    if len(seg) < 256:
        return 0, 0, 1.0, np.zeros(7)
    freqs, psd = welch(seg, fs=fs, nperseg=min(256, len(seg)), return_onesided=True)
    coeffs = np.interp(freqs_noetic, freqs, np.sqrt(psd), left=0, right=0)
    Rc = np.sum(coeffs)
    if Rc < 1e-12:
        return 0, 0, 1.0, np.zeros(7)
    peaks, _ = find_peaks(coeffs, height=0.05*np.max(coeffs))
    Rtop = len(peaks)
    if Rtop >= 2:
        f_peaks = freqs_noetic[peaks]
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
    return Rc, Rtop, Rdyn, bands

# ---------- 4. Fenêtrage ----------
n_windows = (len(signal) - window_size) // hop + 1
print(f"Nombre de fenêtres : {n_windows}")

times_center = []
Rc_list, Rtop_list, Rdyn_list, bands_list = [], [], [], []

for i in range(n_windows):
    seg = signal[i*hop : i*hop+window_size]
    t_center = time[i*hop + window_size//2]
    Rc, Rtop, Rdyn, bands = extract_features(seg, fs, freqs_noetic)
    times_center.append(t_center)
    Rc_list.append(Rc)
    Rtop_list.append(Rtop)
    Rdyn_list.append(Rdyn)
    bands_list.append(bands)
    if i == 0:
        print(f"Fenêtre 0: Rc={Rc:.3e}, Rtop={Rtop}, Rdyn={Rdyn:.4f}")

# ---------- 5. Visualisations ----------
plt.figure(figsize=(12,8))

plt.subplot(3,1,1)
plt.plot(times_center, Rc_list)
plt.ylabel('Rc (énergie)')
plt.grid(True)

plt.subplot(3,1,2)
plt.plot(times_center, Rtop_list, 'r-')
plt.ylabel('Rtop (nombre de pics)')
plt.grid(True)

plt.subplot(3,1,3)
plt.plot(times_center, Rdyn_list, 'g-')
plt.ylabel('Rdyn (désaccord)')
plt.xlabel('Temps (s)')
plt.grid(True)
plt.suptitle('Évolution des résidus ASH - test_chaos.csv')
plt.tight_layout()
plt.savefig('chaos_residus.png')
plt.show()

# Camembert moyen des bandes
mean_bands = np.mean(bands_list, axis=0)
labels = ['B1','B2','B3','B4','B5','B6','B7']
plt.figure()
plt.pie(mean_bands, labels=labels, autopct='%1.1f%%')
plt.title('Répartition moyenne des bandes (signal chaos)')
plt.savefig('chaos_bands_pie.png')
plt.show()

print("Graphiques sauvegardés : chaos_residus.png, chaos_bands_pie.png")
