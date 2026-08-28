# exp014_mesure — Campagne C16 : couche n=5 de P1, attente EXP-014

**EXP-014 : falsifiée par la clause (b) — publiée avec le même soin (B3-FAIL).**
Date : 2026-08-28. Attente figée AVANT mesure : commit `9bce034`
(`bridge/expectations.json` v0.6.0), protocole `protocole/PROTOCOLE_C16.md`.

## Résultats

| Signal | nœuds | Rc | ReN | régime | verdict (pont) |
|---|---|---|---|---|---|
| p1_orb_5g | 0 | 76,526678 | 0,103355 | Cosmologique | CONFORME |
| p1_orb_5f | 1 | 129,691506 | 0,056580 | Cosmologique | CONFORME |
| p1_orb_5d | 2 | 231,612627 | 0,030875 | Cosmologique | CONFORME |
| p1_orb_5p | 3 | 293,130890 | 0,036270 | Cosmologique | CONFORME |
| p1_orb_5s | 4 | 325,431991 | 0,023837 | Cosmologique | CONFORME |
| temoin_4f | — | 74,239503 | 0,102742 | Cosmologique | HORS-CONTRAT (H) |
| controle_bruit43 | — | 10,855368 | 0,000000 | Cosmologique | HORS-CONTRAT (H) |

## Évaluation des trois clauses du falsifieur (texte faisant foi : attente EXP-014)

| Clause | Contenu | Résultat |
|---|---|---|
| **(a) ordre** | Rc(5g)<Rc(5f)<Rc(5d)<Rc(5p) strict, Rc(5s) ≥ 0,99·Rc(5p) | **TENUE** — 76,53 < 129,69 < 231,61 < 293,13 < 325,43 (5s/5p = 1,110) |
| **(b) échelle** | r₁ = Rc(5f)/Rc(5g) ∈ [1,7 ; 2,2] ; r₂ = Rc(5d)/Rc(5f) ∈ [1,3 ; 1,6] | **FALSIFIÉE** — r₁ = 1,6947 (sous la borne, de 0,3 %) ; r₂ = 1,7859 (hors borne, +12 %) |
| **(c) régime** | les 5 états lisent Cosmologique | **TENUE** — tous Cosmologique, ReN ∈ [0,024 ; 0,103] |

**EXP-014 est falsifiée (clause b), une seule clause suffit.** L'échelle des
rapports calibrée sur la couche n=4 (pas 0→1 : 1,96 ; pas 1→2 : 1,45) ne se
transfère pas à la couche n=5 (1,69 ; 1,79) : non seulement les bornes sont
franchies, mais l'ordre des pas s'inverse (r₂ > r₁ alors que la calibration
donnait une échelle décroissante).

## Lecture honnête

1. **Le structurel tient** : la clause centrale (a) — Rc ordonne strictement
   le nombre de nœuds radiaux — est vérifiée sur une couche entière jamais
   utilisée au réglage, avec la marge confortable 5s/5p = 1,11 (la tolérance
   de jointure calibrée était 0,99). La structure nodale de P1 **est** visible
   par la pression spectrale, comme calibré sur C15. La clause (c) tient
   également : l'explication « bosse spectrale large » se généralise à une
   couche entière.
2. **Le quantitatif ne tient pas** : la loi d'échelle chiffrée (deux bornes à
   ±12 % calibrées sur **une seule** couche, n=4) échoue sur la couche
   suivante. C'est la fragilité attendue d'une attente calibrée sur un
   échantillon de un — consigné comme tel, sans réparer les bornes après
   coup (toute borne ajustée maintenant serait post-hoc).
3. **Découverte documentée (artefact de boîte, précédent A2)** : dans la
   boîte RMAX=4000 du protocole, 5s (E = +9,07·10⁻⁷), 5p (+6,63·10⁻⁷) et
   5d (+2,54·10⁻⁷) sont des **états de boîte à énergie positive** (le puits
   Coulomb tronqué ne lie que 4s/3p/2d sous le seuil) ; seuls 5g (−6,97·10⁻⁷)
   et 5f (−2,27·10⁻⁷) sont liés. Les nombres de nœuds (0…4) restent corrects
   pour chaque état — l'échelle nodale mesurée est donc bien celle déclarée,
   mais les trois profils les plus excités sont des modes de boîte oscillants,
   pas des bosses décroissantes. La tenue de la clause (a) dans ces conditions
   renforce (a posteriori) la robustesse de Rc ; elle invite aussi à traiter
   la clause (b) avec prudence : les rapports calibrés sur des états liés de
   n ≤ 4 sont confrontés ici à des états de boîte.

## Témoins d'intégrité (figés dans le protocole)

- **temoin_4f** : CSV octet-identique à exp013 (`p1_orb_4f.csv`,
  sha256 `423604b8…`) — la chaîne de production n'a pas dérivé ;
- **controle_bruit43** : CSV octet-identique à exp013 (sha256 `a3909a6b…`),
  lu Cosmologique (ReN = 0) — spécificité conservée (test trivial à cette
  grille).

## Chaîne auto-vérifiable

`run/c16_runner.py` régénère les 7 signaux ; `run/c16_analyse.py` régénère
signatures, verdicts et `run/evaluation_clauses.json` depuis les signaux.
Testé en dépôt vierge : **22/22 fichiers octet-identiques**. Empreintes :
`run/manifest.json` (29 entrées : protocole + signaux + signatures + verdicts
+ scripts). Signaux non commités (règle C13.1 §3), régénérables bit-à-bit.

Instrument : `run/ash_core.py` v1.0.0 figé (sha256 `338dbda7…`), aucun
post-traitement. Pont : `run/noetic_bridge.py` v0.1.0 (sha256 `7e9f3705…`),
attentes `run/expectations_v060.json` (= `bridge/expectations.json` v0.6.0).

## Contenu publié

`README.md`, `protocole/PROTOCOLE_C16.md`, `protocole/attente_EXP-014.json`,
`run/c16_runner.py`, `run/c16_analyse.py`, `run/ash_core.py`,
`run/noetic_bridge.py`, `run/expectations_v060.json`,
`run/evaluation_clauses.json`, `run/manifest_signaux.json`,
`run/manifest.json`, `signatures/` (7), `verdicts/` (7).
