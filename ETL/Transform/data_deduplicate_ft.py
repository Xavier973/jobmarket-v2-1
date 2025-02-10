import os
import json

# Détection du chemin de base en fonction de l'environnement
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin du script actuel
BASE_PATH = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Remonte de 2 niveaux
DATA_TRANSFORM_FOLDER = os.path.join(BASE_PATH, "data", "transformed", "francetravail")
DATA_PROCESSED_FOLDER = os.path.join(BASE_PATH, "data", "processed", "francetravail")

print(f"📂 Dossier de données transformées : {DATA_TRANSFORM_FOLDER}")
print(f"📂 Dossier de données traitées : {DATA_PROCESSED_FOLDER}")

# Dictionnaire pour stocker les offres uniques basées sur ft_reference
unique_offers = {}
duplicate_references = []

def load_json_file(file_path):
    """Charge un fichier JSON et retourne son contenu"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Erreur de lecture du fichier {os.path.basename(file_path)}. Il pourrait être corrompu.")
        return None

# Charger d'abord toutes les références des fichiers traités
processed_references = set()
for json_file in os.listdir(DATA_PROCESSED_FOLDER):
    if json_file.endswith(".json"):
        file_path = os.path.join(DATA_PROCESSED_FOLDER, json_file)
        data = load_json_file(file_path)
        if data:
            for job_offer in data:
                ft_ref = job_offer.get("ft_reference")
                if ft_ref:
                    processed_references.add(ft_ref)

print(f"📊 Nombre de références déjà traitées : {len(processed_references)}")

# Traitement des fichiers transformés
for json_file in os.listdir(DATA_TRANSFORM_FOLDER):
    if not json_file.endswith(".json"):
        continue
        
    file_path = os.path.join(DATA_TRANSFORM_FOLDER, json_file)
    data = load_json_file(file_path)
    if not data:
        continue

    # Vérification des doublons et des références déjà traitées
    cleaned_data = []
    for job_offer in data:
        ft_ref = job_offer.get("ft_reference")
        if not ft_ref:
            continue

        # Vérifier si l'offre est déjà dans les fichiers traités
        if ft_ref in processed_references:
            print(f"🔄 Offre déjà traitée : {ft_ref} (ignorée)")
            continue

        # Vérifier les doublons dans le fichier courant
        if ft_ref in unique_offers:
            duplicate_references.append(ft_ref)
            print(f"🔄 Doublon détecté : {ft_ref} (supprimé)")
        else:
            unique_offers[ft_ref] = job_offer
            cleaned_data.append(job_offer)

    # Écriture du fichier nettoyé
    if cleaned_data:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Fichier {json_file} nettoyé : {len(cleaned_data)} offres conservées")
    else:
        print(f"ℹ️ Fichier {json_file} vide après nettoyage, suppression...")
        os.remove(file_path)

# Résumé du traitement
print("\n📋 Résumé du traitement :")
print(f"- Nombre total d'offres uniques : {len(unique_offers)}")
print(f"- Nombre d'offres déjà traitées : {len(processed_references)}")
if duplicate_references:
    print(f"- Nombre de doublons supprimés : {len(set(duplicate_references))}")
    print("\nRéférences en double supprimées :")
    print(", ".join(set(duplicate_references)))
else:
    print("- Aucun nouveau doublon trouvé")

print("\n🚀 Traitement terminé.")
