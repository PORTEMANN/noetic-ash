# Benchmark ECG5000

Le dataset **ECG5000** (UCR Time Series Classification Archive) n'est pas
commité dans ce dépôt.

## Acquisition

1. Télécharger depuis l'UCR Archive :
   https://www.cs.ucr.edu/~eamonn/time_series_data_2018/ (dossier `ECG5000`)
   ou miroir : https://www.timeseriesclassification.com/aeon-toolkit/ECG5000.zip
2. Vérifier l'intégrité, puis compléter `../SHASUMS.txt` avec le hash du
   fichier téléchargé.
3. 5000 séries de 140 échantillons — tâche binaire normal/anormal,
   fenêtre unique de 140 échantillons.

> Historique : l'archive locale d'origine (juin 2026) était corrompue
> (44 octets, message d'erreur HTTP). B3-FAIL documenté — d'où la règle :
> hash SHA-256 systématique à l'acquisition.
