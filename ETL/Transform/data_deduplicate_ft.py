import os
import json

# Détection du chemin de base en fonction de l'environnement
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin du script actuel
BASE_PATH = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Remonte de 2 niveaux
DATA_TRANSFORM_FOLDER = os.path.join(BASE_PATH, "data", "transformed", "francetravail")

print(f"📂 Dossier de données : {DATA_TRANSFORM_FOLDER}")

# Dictionnaire pour stocker les offres uniques basées sur ft_reference
unique_offers = {}
duplicate_references = []

# Liste des fichiers JSON à traiter
json_files = [f for f in os.listdir(DATA_TRANSFORM_FOLDER) if f.endswith(".json")]

# Parcours des fichiers JSON
for json_file in json_files:
    file_path = os.path.join(DATA_TRANSFORM_FOLDER, json_file)
    
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Erreur de lecture du fichier {json_file}. Il pourrait être corrompu.")
            continue

    # Vérification des doublons
    cleaned_data = []
    for job_offer in data:
        ft_ref = job_offer.get("ft_reference")
        if ft_ref:
            if ft_ref in unique_offers:
                duplicate_references.append(ft_ref)
                print(f"🔄 Doublon détecté : {ft_ref} (supprimé)")
            else:
                unique_offers[ft_ref] = job_offer
                cleaned_data.append(job_offer)

    # Écriture du fichier nettoyé
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

# Résumé du traitement
if duplicate_references:
    print("\n✅ Suppression terminée. Références en double supprimées :")
    print(", ".join(set(duplicate_references)))
else:
    print("\n✅ Aucun doublon trouvé.")

print("🚀 Traitement terminé.")
