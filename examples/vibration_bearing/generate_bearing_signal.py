"""
generate_bearing_signal.py
Génère un signal de vibration de roulement : sain puis défaut (pitting)
fs = 1000 Hz, durée = 10 s
Défaut : apparition progressive de raies latérales à partir de t=5s
"""

import numpy as np
import pandas as pd

np.random.seed(42)  # C12.1 : reproductibilité du dataset (v1.0.0)

fs = 1000
t = np.arange(0, 10, 1/fs)

# Fréquence de rotation (Hz)
fr = 30
# Fréquence de défaut (BPFO typique)
fd = 4.3 * fr   # ~129 Hz

# Signal sain : fondamentales et harmoniques
signal_sain = 0.5 * np.sin(2*np.pi*fr*t) + 0.3 * np.sin(2*np.pi*2*fr*t) + 0.1 * np.sin(2*np.pi*3*fr*t)

# Défaut : modulation d'amplitude + raies latérales
enveloppe_defaut = np.exp(-((t-5)/1.5)**2)   # pic centré à 5s
defaut = enveloppe_defaut * (0.4 * np.sin(2*np.pi*fd*t) * (1 + 0.3*np.sin(2*np.pi*fr*t)))

signal = signal_sain + defaut + 0.02 * np.random.randn(len(t))

df = pd.DataFrame({'time': t, 'signal': signal})
df.to_csv('vibration_bearing.csv', index=False)
print("Fichier 'vibration_bearing.csv' généré.")
