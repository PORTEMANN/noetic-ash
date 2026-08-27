# ADDENDUM A2 au protocole C14 (2026-08-28) — volet b, boîte radiale

Constat à l'exécution (avant toute mesure ASH) : les valeurs par défaut du script
P1 (NR=4000, RMAX=40) ne sont PAS la configuration publiée. Avec RMAX=40 << a0=137,
tous les « états liés » sont des états de boîte à énergie positive (1s mesuré
+2,64e-3 au lieu de −2,66e-5) : l'objet analysé aurait été faux.

Critère de correction (déclaré ici, appliqué une fois) : retrouver la table P1
publiée (README non-abelian-gauge-model) — ratio 1s = 0,9994, dégénérescence
2s/2p = 1,0000. La configuration qui la reproduit : RMAX = 4000, NR = 4000 (dr = 1,
a0 ≈ 137, Rcore/a0 = 0,022).

Conséquence sur les paramètres ASH du volet b (les seuls autres changements) :
- fs = 1 (1 pt par unité r), f0 = 0,00390625 cycle/unité r (= 2^-8),
  5 octaves (max 0,125 < Nyquist 0,5), fenêtre 1024 pts (1024 unités r),
  overlap 0,5, nperseg = 1024, agrégation médiane.

Tout le reste du protocole C14 (+ addendum A1) est INCHANGÉ. Textes originaux conservés.
