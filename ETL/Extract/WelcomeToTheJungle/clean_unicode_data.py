#!/usr/bin/env python3
"""
Script utilitaire pour nettoyer les caractères Unicode échappés dans les fichiers JSON existants.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime


def clean_unicode_escaped_string(text):
    """
    Nettoie les chaînes de caractères qui contiennent des séquences Unicode échappées.
    Exemple: "Consultant D\\u00e9cisionnel" -> "Consultant Décisionnel"
    """
    if isinstance(text, str):
        try:
            # Décoder les séquences Unicode échappées
            return text.encode('utf-8').decode('unicode_escape')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return text
    return text


def clean_unicode_in_data(data):
    """
    Nettoie récursivement tous les caractères Unicode échappés dans une structure de données.
    """
    if isinstance(data, dict):
        return {key: clean_unicode_in_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_unicode_in_data(item) for item in data]
    elif isinstance(data, str):
        return clean_unicode_escaped_string(data)
    else:
        return data


def clean_json_file(input_file_path, output_file_path=None):
    """
    Nettoie un fichier JSON en corrigeant les caractères Unicode échappés.
    
    Args:
        input_file_path (str): Chemin vers le fichier JSON à nettoyer
        output_file_path (str, optional): Chemin vers le fichier de sortie. 
                                        Si None, remplace le fichier original.
    """
    try:
        # Lire le fichier JSON
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Données chargées depuis {input_file_path}")
        
        # Nettoyer les données
        cleaned_data = clean_unicode_in_data(data)
        
        # Déterminer le fichier de sortie
        if output_file_path is None:
            output_file_path = input_file_path
        
        # Sauvegarder les données nettoyées
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        print(f"Données nettoyées sauvegardées dans {output_file_path}")
        
        # Afficher quelques exemples de corrections
        if isinstance(cleaned_data, list) and len(cleaned_data) > 0:
            print("\nExemples de corrections :")
            for i, item in enumerate(cleaned_data[:3]):
                if isinstance(item, dict) and 'title' in item:
                    print(f"  {i+1}. {item['title']}")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors du nettoyage du fichier {input_file_path}: {e}")
        return False


def clean_all_wttj_files(data_dir=None):
    """
    Nettoie tous les fichiers JSON WTTJ dans le répertoire de données.
    
    Args:
        data_dir (str, optional): Répertoire contenant les données. 
                                Si None, utilise DATA_RAW_DIR/wttj
    """
    if data_dir is None:
        data_dir = os.path.join(os.getenv('DATA_RAW_DIR', '/app/data/raw'), 'wttj')
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Le répertoire {data_path} n'existe pas.")
        return
    
    # Trouver tous les fichiers JSON WTTJ
    json_files = list(data_path.glob('wttj_database_*.json'))
    
    if not json_files:
        print(f"Aucun fichier JSON WTTJ trouvé dans {data_path}")
        return
    
    print(f"Trouvé {len(json_files)} fichier(s) JSON à nettoyer :")
    for file_path in json_files:
        print(f"  - {file_path.name}")
    
    # Demander confirmation
    response = input("\nVoulez-vous nettoyer ces fichiers ? (y/N): ")
    if response.lower() != 'y':
        print("Opération annulée.")
        return
    
    # Nettoyer chaque fichier
    success_count = 0
    for file_path in json_files:
        print(f"\nNettoyage de {file_path.name}...")
        if clean_json_file(str(file_path)):
            success_count += 1
    
    print(f"\nNettoyage terminé : {success_count}/{len(json_files)} fichiers traités avec succès.")


def main():
    """
    Fonction principale du script.
    """
    if len(sys.argv) > 1:
        # Mode fichier unique
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(input_file):
            print(f"Le fichier {input_file} n'existe pas.")
            sys.exit(1)
        
        clean_json_file(input_file, output_file)
    else:
        # Mode nettoyage de tous les fichiers
        print("Script de nettoyage des caractères Unicode échappés")
        print("=" * 50)
        clean_all_wttj_files()


if __name__ == "__main__":
    main() 