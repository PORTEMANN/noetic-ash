"""
generate_ecg_mitdb.py
Nécessite : pip install wfdb
"""

import wfdb
import pandas as pd
import numpy as np

# Téléchargement et lecture (crée les fichiers .dat .hea .atr dans le dossier courant)
record = wfdb.rdrecord('100', sampto=30*360)   # 30 secondes à 360 Hz
signal = record.p_signal[:, 0]                 # canal MLII
fs = record.fs

# Sauvegarde CSV
df = pd.DataFrame({'time': np.arange(len(signal))/fs, 'signal': signal})
df.to_csv('ecg_mitdb_100_30s.csv', index=False)
print(f"Fichier ecg_mitdb_100_30s.csv généré ({len(signal)} échantillons, fs={fs} Hz)")
