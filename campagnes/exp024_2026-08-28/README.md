# Campagne exp024 — spécificité du comma à seuil de magnitude + réplication du mécanisme (EXP-024) — CONFORME

Date : 2026-08-28. Attente EXP-024 figée AVANT mesure (bridge/expectations.json
v1.6.0, commit 7af19a0). Corpus public CWRU (engineering.case.edu, roulement
6205-2RS). Calibration déclarée : exp022/023. Test aveugle : canaux FE des 4
sains (jamais analysés) et famille 21 mil (jamais lue). Protocole C26
(protocole/PROTOCOLE_C26.md).

Verdict global : **EXP-024 CONFORME** — les deux clauses tenues sur corpus
aveugles. Le détecteur corrigé est validé.

## Résultats

### Clause (a) — spécificité à seuil de magnitude (sains FE aveugles) : **TENUE**

| Canal FE (sain) | BPFI | BPFO | BSF |
|---|---|---|---|
| 97 | +0,26 | +1,09 | −0,73 |
| 98 | +0,29 | +0,99 | −0,24 |
| 99 | +0,08 | +1,38 | −0,29 |
| 100 | +0,24 | +2,50 | −1,09 |

Aucun canal FE sain n'atteint Z ≤ −3 (le plus négatif : −1,09). **Aucune
fausse alarme significative.** La correction d'EXP-023 (magnitude, pas signe)
est validée sur un capteur aveugle (le fan-end, position différente du DE
calibré) : le seuil de magnitude élimine les fausses alarmes significatives.

### Clause (b) — réplication du mécanisme (famille 21 mil aveugle) : **TENUE**

| Fichier | Type | AC au lag | Z au lag | Signe |
|---|---|---|---|---|
| 209 | interne | +0,213 | −2,95 | ✓ tenu |
| 210 | interne | +0,021 | −0,48 | hors domaine (\|AC\|<0,05) |
| 222 | bille | +0,012 | −0,37 | hors domaine |
| 223 | bille | −0,121 | +1,63 | ✓ tenu |
| 234 | externe | +0,028 | −0,91 | hors domaine |
| 235 | externe | −0,113 | +2,33 | ✓ tenu |

Aucune violation du signe : 209 (cohérent) déclenche, 223 et 235 (non
cohérents) restent silencieux. La loi « déclenchement ⟺ cohérence de phase à
la période du défaut » tient sur une **troisième famille** (après 7 mil 9/9
et 14 mil sans violation).

## Lecture honnête

1. **Le détecteur corrigé est validé de bout en bout sur aveugle** : la
   spécificité à magnitude tient (pas de fausse alarme significative sur un
   capteur aveugle), le mécanisme de cohérence de phase se réplique sur une
   troisième famille. La correction d'EXP-023 (magnitude, pas signe) était la
   bonne — elle a été apprise par falsification et validée ici.
2. **Trois fichiers 21 mil hors domaine** (\|AC\| < 0,05) : 210, 222, 234 —
   la cohérence de phase y est trop faible pour trancher le signe. Consigné
   par la règle déclarée (non falsifiant). La cohérence de phase n'est pas
   systématique même sur gros défauts — fait physique consigné.
3. **Le détecteur industriel est désormais complet et compris** : il répond
   « récurrence significative ET phase-cohérente à la période du défaut » —
   pas de fausse alarme significative sur le sain (magnitude), déclenchement
   lisible sur le défaut cohérent (mécanisme). Sa limite est connue et
   déclarée : les trains non phase-cohérents y échappent (119, 131, 186…).
4. **Série CWRU complète** : vibration_hf (ReN spectral, sépare parfaitement)
   ; exp022 (comma, spécifique mais pas universel) ; exp023 (mécanisme =
   cohérence de phase, validé) ; exp024 (spécificité à magnitude + réplication,
   conforme). L'ASH voit les raies, le comma voit la cohérence du calendrier.

## Discipline temporelle

Calibration déclarée (exp022/023) ; attente figée (v1.6.0, commit 7af19a0) ;
corpus aveugles extraits/téléchargés après figement, mesurés sans inspection
préalable. Canaux exacts (artefact 99 corrigé).

## Reproduction

```
python3 run/c26_runner.py   # extrait FE + télécharge la famille 21 mil (public)
python3 run/c26_comma.py    # régénère evaluation_clauses.json
```

Empreintes : run/manifest.json. Fichiers .mat CWRU publics, non commités
(règle C13.1 §3).

## Corpus

Aucune signature ASH versée (observable hors instrument figé, regime_attendu
= null). Registre corpus inchangé (v0.7.0). Verdict porté par
run/evaluation_clauses.json.
