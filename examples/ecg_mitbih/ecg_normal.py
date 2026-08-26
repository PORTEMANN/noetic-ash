import numpy as np
import pandas as pd

np.random.seed(42)  # C12.1 : reproductibilité du dataset (v1.0.0)

fs = 360
duration = 10.0
t = np.arange(0, duration, 1/fs)

# Fonction de battement cardiaque synthétique
def ecg_synthetic(t, hr=72):
    # hr: battements par minute
    period = 60.0 / hr
    phase = 2 * np.pi * (t % period) / period
    # Simuler QRS (pic étroit)
    qrs = 1.2 * np.exp(-((phase - 0.3)*20)**2)
    # Onde P
    p_wave = 0.25 * np.exp(-((phase - 0.0)*30)**2)
    # Onde T
    t_wave = 0.35 * np.exp(-((phase - 0.6)*15)**2)
    return qrs + p_wave + t_wave

signal = ecg_synthetic(t, hr=72)
# Ajout de bruit et dérive
signal += 0.05 * np.random.randn(len(t))
signal += 0.02 * np.sin(2 * np.pi * 0.5 * t)   # dérive lente

df = pd.DataFrame({'time': t, 'signal': signal})
df.to_csv('ecg_normal.csv', index=False)
print("Fichier 'ecg_normal.csv' généré.")
