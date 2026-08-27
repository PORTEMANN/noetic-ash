# ADDENDUM A1 au protocole C14 (2026-08-28) — volet a, condition initiale

Constat à l'exécution (avant toute mesure ASH) : la condition initiale figée
(phase gaussienne filtrée ξc = 2, amplitude uniforme 1) ne nuclée AUCUN vortex
(N_v(t) ≡ 0 sur 2048 pas). La campagne serait vacuante.

Correction (remplace le point « Condition initiale » du volet a) :
- ψ(x,0) = bruit blanc complexe gaussien complet (parties réelle et imaginaire
  indépendantes, graine numpy SeedSequence 2026), SANS filtre ni normalisation
  d'amplitude. Quench dur : le champ relaxe vers |ψ|=1 en nucléant un enchevêtrement
  dense de vortex qui s'annihile ensuite — régime pour lequel e44_core est construit.
- Tout le reste du protocole C14 est INCHANGÉ (grille, propagateur, durée,
  séries, paramètres ASH, contrôles, formats).

Le texte C14 original est conservé tel quel (règle « conserver les versions »).
L'attente EXP-013a est inchangée : elle ne porte pas sur la condition initiale.
