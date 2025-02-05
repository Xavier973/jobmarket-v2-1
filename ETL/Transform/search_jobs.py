import json
import glob
from pathlib import Path

# Chemin vers le dossier contenant les fichiers JSON
path = "/home/xadmin/projets/jobmarket-v2-1/data/transformed/francetravail/*.json"

# Parcourir tous les fichiers JSON
for file_path in glob.glob(path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Pour chaque offre dans le fichier
        for offer in data:
            title = offer.get('job_title', '').lower()
            # Si le titre contient les deux mots
            if 'it' in title and 'operation' in title:
                print(f"Fichier: {Path(file_path).name}")
                print(f"Titre: {offer['job_title']}")
                print("-" * 50)