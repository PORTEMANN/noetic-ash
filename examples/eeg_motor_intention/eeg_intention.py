import numpy as np
import pandas as pd

np.random.seed(42)  # C12.1 : reproductibilité du dataset (v1.0.0)

fs = 250
duration = 10.0
t = np.arange(0, duration, 1/fs)

# Intention : modulation de l'amplitude bêta entre 4 et 7 s
intention = np.zeros_like(t)
intention[(t>=4) & (t<=7)] = 1.0

# Alpha (fond)
alpha = 0.5 * np.sin(2*np.pi*10*t)
# Bêta modulée
beta = intention * 0.8 * np.sin(2*np.pi*20*t)
# Bruit rose simplifié (bruit coloré)
bruit_blanc = 0.1 * np.random.randn(len(t))
# Bruit rose (filtre passe-bas sur bruit blanc)
from scipy.signal import butter, filtfilt
b, a = butter(2, 30, fs=fs, btype='low')
bruit_rose = filtfilt(b, a, np.random.randn(len(t))) * 0.15

signal = alpha + beta + bruit_rose + bruit_blanc

df = pd.DataFrame({'time': t, 'signal': signal})
df.to_csv('eeg_intention.csv', index=False)
print("Fichier 'eeg_intention.csv' généré.")
