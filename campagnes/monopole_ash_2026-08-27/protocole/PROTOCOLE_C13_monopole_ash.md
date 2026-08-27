# Protocole C13.1 — Campagne `monopole_ash` (FIGÉ avant mesure)

Confrontation de la machine noétique à son instrument : les profils radiaux du
monopole SU(2) (programme P0, noetic-machine) passés dans l'analyseur ASH
(noetic-ash v1.0.0, noyau figé). Attente déclarée : **EXP-012** (statut E,
conjecturale pré-campagne). Résultats publiés **quelle que soit l'issue**
(règle B3-FAIL).

Toute modification de ce document après la première mesure le fait passer en
C13.2 ; la version ayant produit les signatures reste citée dans chacune.

## 1. Corpus — branches du monopole

Branches convergées du fonctionnel radial C(ρ), par **continuation L-BFGS**
depuis la branche calibrée ρ = 0,5 (P0 : C = 0,9981 ≈ BPS) :

| Branche | Rôle dans la campagne |
|---|---|
| ρ = 0,5 | **Référence BPS** (ancrage calibré P0, C ≃ 1) |
| ρ = 1,0 | Ancrage littérature (C = 1,3098, lit. 1,24–1,31) |
| ρ = 0,25 et ρ = 0,1 | Approche ρ → 0⁺ (la boîte finie interdit ρ = 0 — B3-FAIL P0 documenté) |
| ρ = 2,0 et ρ = 4,0 | Régime à potentiel dominant |

Contraintes de convergence héritées de P0 : gradient discret exact (métrique
DX×ana, validé par différences finies), conditions H(0)=0, K(0)=1, boîte
ξ_max = 30. Une branche non convergée est **exclue et consignée** (jamais
remplacée silencieusement).

## 2. Signaux analysés

Pour chaque branche, trois profils sur la grille radiale ξ :

1. **Signal primaire — densité d'énergie radiale** ε(ξ), intégrande exacte du
   fonctionnel :
   `ε(ξ) = K′² + (K²−1)²/(2ξ²) + (ξH′−H)²/(2ξ²) + K²H² + ρ(H²−1)²/4`
   (c'est elle qui « porte la masse » — le bon objet à lire).
2. **Contrôles** : H(ξ) et K(ξ) séparément, même protocole. Ils ne portent
   pas l'attente EXP-012 ; leurs signatures sont consignées (statut H
   d'exploration) pour interpréter le primaire en cas de divergence.

## 3. Échantillonnage et prétraitement (déterministe)

- Grille ξ uniforme : **4096 points** sur [ξ_min, 30], ξ_min = 30/4096
  (la singularité régulière en ξ = 0 est exclue du signal, documentée).
- Dérivées K′, H′ : différences finies centrées d'ordre 2 sur la grille
  uniforme (même opérateur pour toutes les branches).
- Fréquence d'échantillonnage équivalente déclarée : fs = 4096/30 ≈ 136,533
  échantillons par unité ξ.
- **Normalisation RMS = 1 obligatoire** sur chaque signal (B3-FAIL #1 :
  ReN ∝ 1/amplitude ; sans elle aucune comparaison inter-branches n'est licite).
- CSV canonique par signal : `xi,signal` en `%.10e`, SHA-256 porté par la
  signature. Les CSV ne sont pas commités (régénérables depuis
  `p0_monopole_su2.py` + ce protocole).

## 4. Grille ASH (figée)

| Paramètre | Valeur |
|---|---|
| Domaine déclaré | `soliton_radial` |
| fs | 136,533 (4096/30) |
| f0 | 0,125 cycle/unité ξ |
| Octaves | 5 (0,125 – 4 cycles/unité ξ) |
| Fenêtre | 1024 points (7,5 unités ξ) |
| Overlap | 0,5 |
| nperseg (Welch) | 1024 |
| Agrégation | médiane des fenêtres (7 fenêtres par signal) |

La couverture 0,125–4 cycles/unité ξ encadre les deux échelles physiques du
monopole : le cœur (ξ ≲ 1) et la queue exponentielle (échelle 1/(e·v) = 1 en
unités ξ).

## 5. Verdicts attendus et lecture

- Chaque profil ε(ξ) reçoit un verdict contre **EXP-012** ; les contrôles
  H(ξ), K(ξ) reçoivent des verdicts EXPLORATION (H).
- **Verdict central** : le régime de la branche ρ = 0,5 (BPS). Attendu méso.
- **Mesure de migration** : la séquence ReN(ρ) sur {0,1 ; 0,25 ; 0,5 ; 1 ; 2 ; 4}.
  Attendue monotone. Les DIVERGENT hors BPS ne sont pas des échecs : ils sont
  la mesure de l'écart à l'équilibre — publiés comme tels.
- Falsifieur EXP-012 : (a) BPS hors méso, ou (b) ReN non monotone en ρ.

## 6. Issue et publication

- Si CONFORME sur BPS + monotonie : la correspondance pression/torsion entre
  C(ρ) et ReN passe de conjecture à fait mesuré sur ce corpus — à éprouver
  ensuite sur d'autres solitons (vortex D1/D2, E4) avant toute généralisation.
- Si DIVERGENT sur BPS ou rupture de monotonie : B3-FAIL publié ; la
  correspondance est rejetée *sous cette grille* — le rapport documentera si
  la grille (f0, octaves) ou la correspondance elle-même est en cause.
- Artefacts : `campagnes/monopole_ash_AAAA-MM-JJ/` dans noetic-ash
  (signatures + verdicts + README + RAPPORT), entrées SIG-022… dans
  noetic-ash-corpus (append-only), expectations.json → v0.4.0 (EXP-012 ajoutée
  avant la campagne, EXP-001…011 inchangées).

## 7. Reproduction

```
# 1. branches : continuation L-BFGS depuis p0_r05.json (p0_monopole_su2.py)
# 2. profils  : ε(ξ), H(ξ), K(ξ) sur grille 4096 pts (§3)
# 3. mesure   : ash_core.ASH(domaine « soliton_radial » §4) — noyau v1.0.0 figé
# 4. verdicts : bridge/noetic_bridge.py contre expectations.json v0.4.0
```

Chaîne documentaire P0 : script `52929bda0603`, données `7d522eb5171a` /
`23680a35ef8f` (SHA-256 tronqués à 12 caractères, convention du corpus).
