"""
generate_financial_series.py
Génère une série de rendements avec transition de régime.
"""

import numpy as np
import pandas as pd

np.random.seed(42)
n_calm = 2000
n_agitated = 3000

# Régime calme
returns_calm = np.random.normal(0, 0.01, n_calm)

# Régime agité (volatilité plus forte, tendance légère, quelques chocs)
returns_agitated = np.random.normal(0, 0.04, n_agitated) + 0.0005 * np.arange(n_agitated)
# Ajout de 5 chocs aléatoires
shocks = np.random.choice(n_agitated, size=5, replace=False)
returns_agitated[shocks] += np.random.normal(0, 0.2, 5)

# Concaténation
returns = np.concatenate([returns_calm, returns_agitated])
time = np.arange(len(returns))

df = pd.DataFrame({'time': time, 'signal': returns})
df.to_csv('financial_returns_5000.csv', index=False)
print("Fichier financial_returns_5000.csv généré (5000 points)")
