# Bridge — pont mesure ↔ interprétation

Le **bridge** est le contrat d'échange entre la mesure (ASH) et
l'interprétation (écosystème noétique). Il ne crée **aucun niveau
d'interprétation nouveau** : le lexique v0.3.0 a supprimé le niveau N
parce que l'ASH, conçu pour l'industrie embarqué et la xAI, est antérieur
à la machine noétique. Le bridge respecte cette frontière : il consigne
des **confrontations datées, falsifiables et reproductibles** — rien de
plus, rien de moins.

## Principe

L'ASH est un analyseur **agnostique** : toute série (temps, valeur) est
analysable — EEG, ECG, vibrations, acoustique, chaos, finance… L'instrument
détecte des régimes à partir d'invariants ; c'est le **contexte déclaré**
(`contexte.etiquette`) qui consolide la sémantique d'interprétation de ces
régimes, en reliant la mesure au registre d'attentes.

```
série (temps, valeur)              toute entrée est analysable
        ↓  ash_core.ASH (zéro paramètre ajusté)
signature (ash-signature/0.1)      invariants + grille + contexte + SHA-256
        ↓  noetic_bridge.py
verdict (ash-verdict/0.1)          CONFORME / DIVERGENT / EXPLORATION / HORS-CONTRAT
        ↓
banque de signaux                  registre (contexte, résultats, verdicts)
        ↓                          → un signal inconnu peut être rapproché
                                     des signatures connues
```

## Les quatre verdicts

| Verdict | Sens |
|---|---|
| **CONFORME** | Le régime mesuré est dans l'attente du contexte. |
| **DIVERGENT** | Écart mesure/attente — consigné avec la même rigueur qu'une conformité (B3-FAIL), avec le falsifieur de l'attente cité. |
| **EXPLORATION** | L'attente est sans prédiction (statut H) : la banque consigne la signature, **rien n'est conclu**. Cas de la finance (EXP-007) : l'agnosticisme de l'instrument n'est pas une promesse de structure. |
| **HORS-CONTRAT** | Aucune attente enregistrée pour ce contexte. |

## Discipline épistémique

- Les **statuts voyagent** : une attente H ne produit jamais un verdict qui
  se présente comme calibré ; les signatures C et E exigent un falsifieur.
- Le **sha256 du verdict exclut l'horodatage** : un même couple
  signature + attentes redonne le même verdict, bit à bit.
- Les **mises en garde d'étalonnage** sont automatiques : fallback Rdyn
  mono-pic (LEX-013/014), dépendance ReN ∝ 1/amplitude (B3-FAIL #1) — la
  comparaison inter-signaux exige une normalisation commune déclarée
  (champ `normalisation`).

## Contenu

| Chemin | Rôle |
|---|---|
| `schema/signature.schema.json` | Contrat `ash-signature/0.1` (le format d'échange) |
| `schema/verdict.schema.json` | Contrat `ash-verdict/0.1` |
| `expectations.json` | Registre d'attentes EXP-001…EXP-007 (statut, source, falsifieur) |
| `noetic_bridge.py` | Moteur du pont — **stdlib uniquement**, embarquable |
| `examples/` | 7 signatures réelles + verdicts figés, régénérables par `generate_examples.py` |

## Exemple

```bash
python bridge/noetic_bridge.py bridge/examples/ecg_normal_p33plus.signature.json \
    --attentes bridge/expectations.json
# → CONFORME : ReN ≈ 1e-5 (médiane de 9 fenêtres) → régime Cosmologique,
#   comme prévu par EXP-002 (statut E, P33+ / MIT-BIH).
```

Régénération complète des exemples (seedés, C12.1) :

```bash
python bridge/examples/generate_examples.py
```

## Ce que le bridge ne fait pas

- Il ne modifie ni la grille ni les seuils (fixés par C12.1).
- Il ne déclare aucune correspondance ASH ↔ machine noétique au rang de
  niveau ou de résultat : chaque attente reste datée, sourcée, falsifiable.
- Il ne conclut rien sur un domaine nouveau tant que la banque n'a pas
  accumulé un échantillon à protocole figé (cf. EXP-007, finance, H).
