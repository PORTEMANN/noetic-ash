import numpy as np
import pandas as pd

fs = 250          # Hz
duration = 10.0   # s
t = np.arange(0, duration, 1/fs)
freq = 10.0       # Hz
signal = np.sin(2 * np.pi * freq * t)

df = pd.DataFrame({'time': t, 'signal': signal})
df.to_csv('signal_sinusoidal.csv', index=False)
print("Fichier 'signal_sinusoidal.csv' généré.")
