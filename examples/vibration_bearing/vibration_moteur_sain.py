import numpy as np
import pandas as pd

np.random.seed(42)  # C12.1 : reproductibilité du dataset (v1.0.0)

fs = 1000
duration = 5.0
t = np.arange(0, duration, 1/fs)
f1, f2 = 30.0, 60.0
signal = 0.8 * np.sin(2*np.pi*f1*t) + 0.4 * np.sin(2*np.pi*f2*t)
# bruit faible
signal += 0.05 * np.random.randn(len(t))

df = pd.DataFrame({'time': t, 'signal': signal})
df.to_csv('vibration_moteur_sain.csv', index=False)
print("Fichier 'vibration_moteur_sain.csv' généré.")
