import pickle
with open('/mnt/agents/output/.deploy/tmp-bridge/fichiers.pkl','rb') as f:
    fichiers = pickle.load(f)
print(fichiers[0]['path'])