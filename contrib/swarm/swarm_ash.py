#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
swarm_ash.py - ASH distribué pour essaims de capteurs (IoT, drones)
Auteur : Patrice Portemann
Date : 2026-06-07

Implémente :
- Une classe `SwarmASH` qui gère un réseau de nœuds.
- Chaque nœud possède une instance locale de `ASH` (noyau consolidé).
- Propagation d'alerte via consensus P2P avec facteur d'oubli spatial β.
- Détection collective d'anomalies (basée sur ReN moyen du voisinage).
- Simulation de topologie en étoile, grille ou aléatoire.
"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
# Migration noetic-ash v1.0.0 (26/08/2026) : le noyau consolidé remplace ash_pro.
# Le facteur beta est géré par SwarmNode/SwarmASH, plus besoin de le passer à l'analyseur.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / "src" / "python"))
from ash_core import ASH

class SwarmNode:
    """Un nœud (capteur) dans l'essaim."""
    def __init__(self, node_id, signal, fs, signal_type='generic', beta=0.1, **ash_kwargs):
        self.id = node_id
        self.signal = signal
        self.fs = fs
        self.beta = beta  # facteur d'oubli spatial (propre au nœud, hérité de l'essaim)
        # Instance ASH locale
        self.ash = ASH(fs=fs, signal_type=signal_type, **ash_kwargs)
        # Résultats locaux
        self.results = None          # DataFrame des résultats temporels
        self.last_ReN = 0.0          # dernier ReN (pour mémoire temporelle)
        self.alert = False            # alerte locale
        self.shared_state = {}        # pour la propagation (reçu des voisins)

    def process(self):
        """Analyse le signal local et met à jour les invariants."""
        self.results = self.ash.process_signal(self.signal, save_csv=False)
        # On prend la dernière fenêtre (ou la moyenne) comme état courant
        if len(self.results) > 0:
            last = self.results.iloc[-1]
            self.last_ReN = last['ReN']
            self.alert = last['ReN'] > 10.0  # alerte locale si ReN > 10
        return self.last_ReN, self.alert

class SwarmASH:
    """
    Gère un essaim de nœuds (capteurs) avec propagation de l'information.
    Paramètres :
        nodes : list of SwarmNode
        topology : str ('full', 'grid', 'random') ou matrice d'adjacence
        beta : float (facteur d'oubli spatial global)
        consensus_iterations : int (nombre d'itérations de propagation)
    """
    def __init__(self, nodes, topology='full', beta=0.1, consensus_iterations=3):
        self.nodes = nodes
        self.n_nodes = len(nodes)
        self.beta = beta
        self.consensus_iterations = consensus_iterations
        self.adjacency = self._build_topology(topology)
        # Historique des alertes collectives
        self.collective_alerts = []

    def _build_topology(self, topology):
        """Construit une matrice d'adjacence (0/1) entre nœuds."""
        adj = np.zeros((self.n_nodes, self.n_nodes), dtype=int)
        if topology == 'full':
            # graphe complet
            adj = np.ones((self.n_nodes, self.n_nodes), dtype=int) - np.eye(self.n_nodes, dtype=int)
        elif topology == 'grid':
            # grille 1D (chaîne linéaire)
            for i in range(self.n_nodes-1):
                adj[i, i+1] = adj[i+1, i] = 1
        elif topology == 'random':
            # graphe aléatoire avec proba 0.3
            np.random.seed(42)
            prob = 0.3
            for i in range(self.n_nodes):
                for j in range(i+1, self.n_nodes):
                    if np.random.rand() < prob:
                        adj[i, j] = adj[j, i] = 1
        else:
            # Si une matrice est fournie, on l'utilise
            adj = np.array(topology)
        return adj

    def _spatial_forgetting(self, value_matrix, iteration):
        """
        Applique un facteur d'oubli spatial exponentiel :
        plus le nombre d'itérations est grand, plus l'information se propage.
        Ici on utilise un filtre itératif : x_new = (1-beta)*x_old + beta * moyenne des voisins.
        """
        new_vals = value_matrix.copy()
        for _ in range(iteration+1):
            for i in range(self.n_nodes):
                neighbors = np.where(self.adjacency[i] == 1)[0]
                if len(neighbors) > 0:
                    neighbor_mean = np.mean(value_matrix[neighbors])
                    new_vals[i] = (1 - self.beta) * value_matrix[i] + self.beta * neighbor_mean
            value_matrix = new_vals.copy()
        return value_matrix

    def run_simulation(self):
        """
        Exécute l'analyse sur chaque nœud, puis propage l'information.
        Retourne :
            - collective_ReN : ReN moyen après propagation
            - collective_alerts : décision collective (vote majoritaire ou seuil)
        """
        # 1. Collecte des ReN locaux (dernière fenêtre) et alertes individuelles
        local_ReN = []
        local_alerts = []
        for node in self.nodes:
            ren, alert = node.process()
            local_ReN.append(ren)
            local_alerts.append(alert)
        local_ReN = np.array(local_ReN)

        # 2. Propagation spatiale avec facteur d'oubli β
        # On crée une matrice des ReN (une colonne par itération, mais on fait simple)
        # Pour la propagation, on applique le filtre itératif
        propagated_ReN = self._spatial_forgetting(local_ReN.copy(), self.consensus_iterations)

        # 3. Décision collective : on considère qu'une anomalie est détectée si le ReN propagé > seuil
        collective_threshold = 10.0
        collective_alerts = propagated_ReN > collective_threshold

        # Stockage pour affichage
        self.local_ReN = local_ReN
        self.propagated_ReN = propagated_ReN
        self.collective_alerts = collective_alerts

        return propagated_ReN, collective_alerts

    def plot_swarm(self):
        """Visualisation des ReN locaux vs propagés."""
        if not hasattr(self, 'local_ReN'):
            print("Exécutez run_simulation() d'abord.")
            return
        x = np.arange(self.n_nodes)
        width = 0.35
        fig, ax = plt.subplots()
        ax.bar(x - width/2, self.local_ReN, width, label='ReN local')
        ax.bar(x + width/2, self.propagated_ReN, width, label='ReN propagé')
        ax.axhline(y=10, color='r', linestyle='--', label='Seuil d\'alerte')
        ax.set_xlabel('Nœud ID')
        ax.set_ylabel('ReN')
        ax.set_title('Essaim ASH : propagation spatiale')
        ax.legend()
        plt.tight_layout()
        plt.savefig('swarm_ash.png', dpi=150)
        plt.show()


# ---------- Exemple d'utilisation (simulation) ----------
if __name__ == "__main__":
    # Création de signaux synthétiques pour 5 capteurs
    np.random.seed(42)
    n_nodes = 5
    fs = 250
    duration = 5  # secondes
    t = np.arange(0, duration, 1/fs)
    signals = []
    for i in range(n_nodes):
        # Signal de base sinusoïdal + bruit
        base = np.sin(2*np.pi*10*t)
        noise = 0.1 * np.random.randn(len(t))
        # Anomalie pour le capteur 2 (intention EEG)
        if i == 2:
            anomaly = 0.8 * np.sin(2*np.pi*20*t) * np.exp(-((t-2.5)**2)/0.5)
        else:
            anomaly = 0
        signal = base + noise + anomaly
        signals.append(signal)

    # Création des nœuds
    nodes = []
    for i, sig in enumerate(signals):
        node = SwarmNode(node_id=i, signal=sig, fs=fs, signal_type='eeg', beta=0.1)
        nodes.append(node)

    # Essaim (topologie en ligne)
    swarm = SwarmASH(nodes, topology='grid', beta=0.3, consensus_iterations=2)
    prop_ren, alerts = swarm.run_simulation()

    print("ReN locaux :", swarm.local_ReN)
    print("ReN propagés :", prop_ren)
    print("Alertes collectives :", alerts)

    swarm.plot_swarm()
