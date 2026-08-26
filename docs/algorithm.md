# Formalisme mathématique de l'ASH
## Fondements noétiques et implémentation opérationnelle

---

## 1. Origine noétique de la grille $2^{1/12}$

### 1.1 Le Koilon comme substrat spectral

Dans le cadre de la **CTFT** (Théorie des Champs Topologiques Continus), le Koilon est un fluide granulaire hyper-dense possédant [^MTR_LDRs_ASH^] :
- Une mémoire structurelle encodée par la dérivée fractionnaire d'Atangana-Baleanu ($0 < \mu < 1$)
- Un champ de torsion intrinsèque $T(x)$
- Une dynamique hydrodynamique intentionnelle

L'équation maîtresse s'écrit :
$$\mathcal{D}_{AB}^{\mu} \Psi(x,t) + \lambda T[\Psi] + \mathcal{G}[\Psi] + \mathcal{R}_{3 \to 4}[\Psi] = J_{cosmo}(z)$$

### 1.2 La discrétisation spectrale minimale

Le **Théorème T1** de [`spectral-triple-minimality`](https://github.com/PORTEMANN/spectral-triple-minimality) établit que la dimension spectrale minimale compatible avec un triplet spectral réel à structure réelle KO-6 est :

$$\dim_{\mathrm{spec}} = 7 \times 12 = 84$$

Cette dimension se décompose en :
- **7 plans noétiques** ($E_1$ à $E_7$) correspondant aux octaves
- **12 notes par octave** correspondant à la ramification spectrale $\mathcal{R}_{3 \to 4}$

La progression géométrique $f_n = f_0 \cdot 2^{n/12}$ n'est donc pas un choix musical arbitraire, mais la **discrétisation minimale** du spectre continu du Koilon préservant :
1. L'invariance par octave (symétrie d'échelle)
2. La structure de ramification entre plans E3 et E4
3. La périodicité du champ de torsion $T(x)$

### 1.3 Loi d'échelle harmonique

L'application de la CTFT à la taxonomie hadronique (MTR-80) montre que les masses suivent une loi d'échelle [^MTR_LDRs_ASH^] :

$$M_n = M_p \cdot \delta^n$$

où $M_p = 938$ MeV et $\delta$ est l'invariant harmonique. La même structure d'échelle gouverne la grille spectrale ASH :

$$f_n = f_0 \cdot \delta_{\mathrm{spec}}^n, \quad \delta_{\mathrm{spec}} = 2^{1/12}$$

L'incertitude typique de prédiction est $\Delta M_n \approx 0.1$ MeV pour les hadrons et $\Delta f_n / f_n \approx 5.9\%$ (un demi-ton) pour la grille spectrale.

---

## 2. Invariants topologiques

### 2.1 Énergie spectrale $R_c$

$$R_c = \sum_{n=0}^{N_{\mathrm{notes}}-1} a_n$$

$R_c$ mesure l'énergie totale du signal dans la bande $[f_0, f_0 \cdot 2^{N_{\mathrm{oct}}}]$. Dans le Koilon, cette énergie correspond à la **pression hydrodynamique** du fluide granulaire.

### 2.2 Nombre de pics $R_{top}$

Un pic local en $n$ vérifie :
$$a_n > a_{n-1} \quad \wedge \quad a_n > a_{n+1} \quad \wedge \quad a_n > 0.1 \cdot \max_m(a_m)$$

$$R_{top} = \# \{ n \mid n \text{ est un pic local} \}$$

**Interprétation noétique :** $R_{top}$ compte les **singularités topologiques** (modes propres) du spectre. Dans le cadre MTR-80, cela correspond au nombre de modes topologiques résonants (MTR) excités dans le signal.

| $R_{top}$ | Analogie hadronique | Interprétation physique |
|-----------|---------------------|------------------------|
| 1 | MTR-1 (proton) | Mode fondamental unique |
| 2 | MTR-7 + MTR-13 (D⁰ + J/ψ) | Deux modes en octave |
| 3+ | MTR-17+ (états exotiques) | Spectre riche, complexité élevée |

### 2.3 Indice de désaccord harmonique $R_{dyn}$

Soient $\{f_k\}_{k=1}^{K}$ les fréquences des pics détectés, avec $K = R_{top}$.

Si $K \geq 2$ :
$$r_k = \ln\left(\frac{f_{k+1}}{f_k}\right), \quad R_{dyn} = \frac{\mathrm{std}(\{r_k\})}{\mathrm{mean}(\{r_k\}) + \varepsilon}$$

**Interprétation noétique :** $R_{dyn}$ quantifie l'**écart à la pureté harmonique** du Koilon. Un signal parfaitement harmonique a des pics séparés par exactement une octave ($r_k = \ln 2$), donc $R_{dyn} = 0$. Cela correspond à un état de **torsion nulle** dans le fluide granulaire.

| $R_{dyn}$ | Régime du Koilon | État physique |
|-----------|-----------------|---------------|
| $\approx 0$ | Torsion nulle, pression dominante | Signal périodique stable |
| $0.3$–$0.5$ | Torsion modérée | Complexité multi-mode |
| $> 0.8$ | Torsion maximale | Chaos, bruit, transition |

---

## 3. Projection sur les plans noétiques

### 3.1 Les sept bandes $E_1$–$E_7$

Chaque octave (12 notes) contribue à un plan noétique $E_j$ :

$$E_j = \sum_{n=12(j-1)}^{12j-1} a_n \quad (j \leq N_{\mathrm{oct}})$$

Le vecteur normalisé :
$$\mathbf{s} = \frac{(E_1, \ldots, E_7)}{\|\mathbf{E}\|_2}$$

**Correspondance avec la CTFT :**

| Plan | Plage (Hz, $f_0=1$) | Rythme EEG | Secteur CTFT |
|------|----------------------|------------|--------------|
| $E_1$ | 1–2 | Delta | $J_{cosmo}(z)$ — sommeil profond |
| $E_2$ | 2–4 | Thêta | $\mathcal{G}[\Psi]$ — relaxation |
| $E_3$ | 4–8 | Alpha | Transition $E_3 \to E_4$ — calme |
| $E_4$ | 8–16 | Bêta bas | $\mathcal{R}_{3 \to 4}$ — attention |
| $E_5$ | 16–32 | Bêta haut | $\lambda T[\Psi]$ — tension |
| $E_6$ | 32–64 | Gamma | Intégration cognitive |
| $E_7$ | 64–128 | Gamma haut | États modifiés |

La **ramification spectrale** $\mathcal{R}_{3 \to 4}$ entre les plans E3 et E4 est particulièrement significative : elle correspond à la transition entre le régime cosmologique (pression dominante) et le régime quantique (torsion dominante).

---

## 4. Nombre de Reynolds noétique ($ReN$)

### 4.1 Définition

Soit $H = -\sum_j s_j \ln(s_j + \varepsilon)$ l'entropie de Shannon des plans (mesure de la dispersion spectrale) et $D = \max(\mathbf{s}) - \mathrm{second\_max}(\mathbf{s})$ la dominance spectrale.

$$ReN = \frac{(R_{dyn} + \varepsilon) \cdot (R_{top} \cdot D)}{R_c \cdot (H + \varepsilon)} \times 100$$

### 4.2 Fondement physique

Le $ReN$ est l'analogue spectral du **nombre de Reynolds hydrodynamique** dans le Koilon :

$$Re = \frac{\text{forces inertielles (torsion)}}{\text{forces visqueuses (pression)}}$$

Dans le cadre de la CTFT, les termes correspondent à :
- **Numérateur** $(R_{dyn} + \varepsilon)(R_{top} \cdot D)$ : torsion $\lambda T[\Psi]$ + complexité topologique
- **Dénominateur** $R_c \cdot (H + \varepsilon)$ : pression $J_{cosmo}(z)$ + entropie de dispersion

### 4.3 Classification des régimes

| Régime | Seuil | Interprétation CTFT | Équation maîtresse |
|--------|-------|---------------------|-------------------|
| **Cosmologique** | $ReN < 1$ | Pression dominante, torsion nulle | $J_{cosmo}(z) \gg \lambda T[\Psi]$ |
| **Méso** | $1 \leq ReN \leq 10$ | Transition, équilibre dynamique | $\mathcal{G}[\Psi]$ actif |
| **Quantique** | $ReN > 10$ | Torsion dominante, singularités | $\lambda T[\Psi] \gg J_{cosmo}(z)$ |

### 4.4 Analogie avec la MTR-C (cosmologie)

Dans l'application MTR-C aux Little Red Dots (LRDs), la matière noire noétique est interprétée comme de la **torsion résiduelle non condensée** [^MTR_LDRs_ASH^]. De même, un signal EEG ou vibratoire avec $ReN \gg 1$ indique une forte composante de torsion résiduelle — marqueur d'anomalie ou d'intention.

---

## 5. Complexité et implantation

### 5.1 Par fenêtre

| Opération | Complexité | Remarque |
|-----------|-----------|----------|
| FFT (Welch) | $\mathcal{O}(N_{\mathrm{FFT}} \log N_{\mathrm{FFT}})$ | $N_{\mathrm{FFT}}$ fixe $\rightarrow$ constant |
| Interpolation | $\mathcal{O}(N_{\mathrm{notes}})$ | $N_{\mathrm{notes}} = 48$ fixe |
| Détection pics | $\mathcal{O}(N_{\mathrm{notes}})$ | Linéaire sur la grille |
| Calcul $R_{dyn}$ | $\mathcal{O}(R_{top})$ | $R_{top} \ll N_{\mathrm{notes}}$ |
| Projection plans | $\mathcal{O}(N_{\mathrm{notes}})$ | Sommation par octave |
| Calcul $ReN$ | $\mathcal{O}(1)$ | 7 termes |
| **Total** | **$\mathcal{O}(1)$** | **Tous paramètres fixes** |

### 5.2 Mémoire

| Composant | Taille | Commentaire |
|-----------|--------|-------------|
| Buffer signal | $N$ floats | $N = f_s T_w$, typ. 256–1024 |
| Grille fréquences | $N_{\mathrm{notes}}$ floats | Pré-calculée, 48–84 |
| Coefficients spectraux | $N_{\mathrm{notes}}$ floats | Résultat interpolation |
| Spectre Welch | $N_{\mathrm{FFT}}/2 + 1$ floats | Résultat intermédiaire |
| FFT (travail) | $2 N_{\mathrm{FFT}}$ floats | Partie réelle + imaginaire |
| Vecteur plans | 7 floats | Résultat |
| **Total** | **$< 10$ Ko** | **En float32, config. par défaut** |

---

## 6. Propriétés mathématiques

### 6.1 Invariance par changement d'échelle d'amplitude

> ⚠ **B3-FAIL (v1.0.0, 26/08/2026)** : l'affirmation ci-dessous est **infirmée
> par la mesure**. Le ReN n'est pas invariant par changement d'échelle :
> $R_c$ croît linéairement avec l'amplitude au dénominateur, donc
> $ReN(\alpha \cdot x) = ReN(x)/\alpha$ (vérifié : ×10 → ÷10, ×100 → ÷100).
> Seuls $R_{top}$, $R_{dyn}$ et les bandes normalisées sont strictement
> invariants. Voir `CHANGELOG.md` et `tests/test_ash.py::test_scale_invariance`.

~~Le $ReN$ est invariant par multiplication de $a_n$ par $\alpha > 0$ : les grandeurs physiques du Koilon ne dépendent pas de l'échelle de mesure, seulement de la structure spectrale.~~

### 6.2 Invariance par dilatation temporelle (octave exacte)

Si $y(t) = x(\lambda t)$ avec $\lambda = 2^k$ (octave exacte), les pics restent sur les mêmes indices de note relatifs et $R_{dyn}$ est conservé. C'est la **symétrie d'échelle** du Koilon.

### 6.3 Robustesse au bruit

> ⚠ **B3-FAIL (v1.0.0, 26/08/2026)** : l'affirmation ci-dessous est **infirmée
> par la mesure** en configuration par défaut (lissage de Welch). Sur
> 100 graines de bruit blanc gaussien : 39 % cosmologique, 60 % méso,
> 1 % quantique. La propriété effective — **absence de fausse alarme sur
> bruit stationnaire** — est documentée dans `benchmarks/README.md`.

~~Pour un bruit blanc gaussien, $R_{dyn} \to 1$ (désaccord maximal) et $ReN$ augmente — le régime est correctement classifié comme quantique (torsion maximale).~~

---

## 7. Limites théoriques

1. **Résolution fréquentielle** : limitée par $\Delta f = f_s / N_{\mathrm{FFT}}$. Deux pics séparés de moins de $\Delta f$ ne sont pas résolus.

2. **Condition de Nyquist** : $f_0 \cdot 2^{N_{\mathrm{oct}}} < f_s/2$. Pour $f_0 = 1$ Hz et 4 octaves, $f_{max} = 16$ Hz — compatible avec EEG ($f_s = 250$ Hz) mais filtre le bruit musculaire > 16 Hz (souhaitable).

3. **Stationnarité locale** : l'ASH suppose la stationnarité sur $T_w$. Les transitoires rapides ($< T_w$) sont lissés.

4. **$ReN$ ad hoc** : la formule est une construction phénoménologique calibrée sur les signaux testés. Elle n'est pas dérivée de première principe de l'équation maîtresse — cette dérivation est un objectif de recherche future (lien avec `gauge-non-abelian`).

---

## 8. Références croisées

| Référence | Lien | Contenu |
|-----------|------|---------|
| CTFT formalism | [`spectral-triple-minimality`](https://github.com/PORTEMANN/spectral-triple-minimality) | Théorèmes T1–T4, KO-6, loi arithmétique |
| Solveur spectral | [`ko6-spectral-solver`](https://github.com/PORTEMANN/ko6-spectral-solver) | Benchmarks B1-B3, validation numérique |
| Cœur physique | [`noetic-machine`](https://github.com/PORTEMANN/noetic-machine) | SU(2) Georgi-Glashow, prédictions |
| Archive canonique | [`noetic-machine-complete`](https://github.com/PORTEMANN/noetic-machine-complete) | P0-P31, SHASUMS, scripts |
| Applications | [`noetic-applications`](https://github.com/PORTEMANN/noetic-applications) | P7-P31, études expérimentales |
| MTR-C cosmologie | [MTR_LDRs_ASH.pdf](https://histoire-des-sciences.eu) | LRDs, expansion fractionnaire |

---

> *"La physique noétique est comparable à la théorie des cordes dans les années 1980 : une construction mathématique prometteuse en quête de validation empirique."* — Auto-évaluation CTFT, §9.2
