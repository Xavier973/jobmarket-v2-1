import argparse
import os
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path


# Dictionnaire des métiers
JOBS = {
    "data engineer": (("data", "engineer"), ("data", "ingénieur")),
    "data architect": (("data", "architect"), ("architect", "si"), ("architect", "it")),
    "data scientist": (("data", "scientist"), ("science", "donnée")),
    "data analyst": (("data", "analyst"), ("data", "analytics")),
    "data steward": (("data", "steward"), ("data", "stewardship")),
    "data manager": (("data", "manager"), ("data", "management")),
    "software engineer": (("software", "engineer"), ("software", "developer"), ("développeur", "logiciel"), ("ingénieur", "logiciel"), ("Fullstack",)),
    "devops": ("devops",),
    "data warehousing engineer": ("data", "warehouse", "engineer"),
    "machine learning engineer": (("machine", "learning", "engineer"), ("ml", "engineer")),
    "cloud architect /engineer ": (("cloud", "architect"), ("cloud", "engineer"), ("cloud", "ingénieur"), ("cloud", "engineer"), ("AWS",), ("GCP",), ("azure",)),
    "solution architect": ("solution", "architect"),
    "big data engineer": (("big", "data", "engineer"), ("ingénieur", "big", "data")),
    "big data developer": (("big", "data", "developer"), ("développeur", "big", "data")),
    "data infrastructure engineer": (("data", "infrastructure", "engineer"), ("ingénieur", "infrastructure", "data")),
    "data pipeline engineer": (("data", "pipeline", "engineer"), ("ingénieur", "pipeline", "data")),
    "etl developer": ("etl",),
    "business developer": (("business", "developer"), ("sales", "developer")),
    "business analyst": ("business", "analyst"),
    "cybersecurity": (("cyber", "security"), ("cyber", "sécurité"), ("cyber", "risk"), ("cyber", "risque")),
    "sysops": (("sysops",), ("it", "operations"), ("it", "operation"), ("it", "opération"), ("it", "opérations")),
    "consultant data": ("data", "consultant"),
}


# Dictionnaire des variables et leurs mots-clés correspondants
skills = {
    "ProgLanguage": [
        "Python", "Java", "C++", "C#", "Scala", " R,", "/R/", " R ", "Julia", "Kotlin", "Bash",
    ],
    "DataBase": [
        "SQL", "NoSQL", "MongoDB", "Cassandra", "Neo4j", "HBase", "Elasticsearch",
    ],
    "DataAnalytics": ["Pandas", "NumPy", " R,", "/R/", " R ", "MATLAB"],
    "BigData": ["Hadoop", "Spark", "Databricks", "Flink", "Apache Airflow"],
    "MachineLearning": [
        "Scikit-Learn", "TensorFlow", "Keras", "PyTorch", "XGBoost", "LightGBM", "CatBoost", "Orange",
    ],
    "DataSerialization": [
        "Avro", "Protocol Buffers", "Json", "XML",
    ],
    "DataVisualisation": [
        "Tableau", "Power BI", "Matplotlib", "Seaborn", "Plotly",
    ],
    "Statistics": [
        "Statistiques Descriptives", "Inférentielles", "Bayesian Statistics", "Statistiques Bayésiennes",
    ],
    "CloudComputing": [
        "AWS", "Azure", "Google Cloud Platform", "GCP", "IBM Cloud", "Alibaba Cloud",
    ],
    "DevTools": ["Git", "Docker", "Jenkins", "Travis CI"],
    "OS": ["Linux", "Windows", "MacOS"],
    "DBMS": [
        "MySQL", "PostgreSQL", "Oracle SQL", "SQL Server", "Snowflake", "BigQuery", "Big Query", "SingleStore",
    ],
    "SoftBigDataProcessing": ["Apache Kafka", "Apache Flink", "HBase", "Cassandra"],
    "Automation": [
        "Ansible", "Kubernetes", "Puppet", "Chef", "Airflow",
    ],
    "InfrastructureAsCode": ["Terraform", "CloudFormation"],
    "NetworkSecurty": ["VPN", "Firewall", "SSL/TLS", "Wireshark"],
    "Virtualisation": ["VMware", "VirtualBox", "Hyper-V"],
    "Containers": ["Docker", "Kubernetes", "OpenShift"],
    "Collaboration": [
        "JIRA", "Confluence", "Slack", "Microsoft Teams", "Teams", "Discord",
    ],
    "Other": [
        "DevOps", "Backend Development", "Big Data", "ML", "Machine Learning", "Statistiques", "Cloud", "CI/CD", "CI / CD",
    ],
    "EnSoftSkils": [
        "Communication", "Teamwork", "Time Management", "Adaptability", "Problem Solving", "Leadership", "Creativity",
        "Empathy", "Collaboration", "Stress Management", "Organization", "Flexibility", "Initiative",
        "Critical Thinking", "Interpersonal Skills"
    ],
}

# Dictionnaire pour la conversion des villes et départements en numéro de département

# 📌 Fonction pour normaliser un nom de ville
def normaliser_nom_ville(nom):
    """ Normalise le nom de la ville : minuscules, suppression accents et espaces inutiles. """
    if nom is None:
        return None
    nom = str(nom).strip().lower()
    nom = unicodedata.normalize('NFD', nom).encode('ascii', 'ignore').decode("utf-8")
    return nom

# 📌 Fonction pour charger le dictionnaire depuis le fichier JSON
def charger_dictionnaire_villes(chemin_fichier):
    """ Charge le dictionnaire des villes et départements depuis un fichier JSON. """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Normaliser les clés du dictionnaire
            return {normaliser_nom_ville(ville): dep for ville, dep in data.items()}
    except FileNotFoundError:
        print(f"Erreur: Le fichier {chemin_fichier} n'existe pas")
        return {}
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier {chemin_fichier} n'est pas un JSON valide")
        return {}

# Modifier le chargement du dictionnaire
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
location_dict = charger_dictionnaire_villes(os.path.join(SCRIPT_DIR, "villes_departements.json"))

# 📌 Fonction pour convertir une ville en son département
def process_location(nom_location, location_dict):
    """ 
    Convertit une localisation en numéro de département.
    - Si c'est déjà un numéro de département (XX), le retourne
    - Si c'est une ville avec un département (VILLE XX), retourne XX
    - Si c'est un nom de ville ou de département, utilise le dictionnaire
    """
    if nom_location is None:
        return None
        
    # Nettoyer la chaîne d'entrée
    nom_location = str(nom_location).strip()
    #print(f"Processing location: {nom_location}")
    
    # Traitement spécial pour Marseille, Lyon et Paris. Résolution des problemes d'arrondissement
    if nom_location.lower().startswith('marseille'):
        print(f"Found Marseille: returning 13")
        return "13"
    
    if nom_location.lower().startswith('lyon'):
        print(f"Found Lyon: returning 69")
        return "69"
        
    if nom_location.lower().startswith('paris'):
        print(f"Found Paris: returning 75")
        return "75"
    
    # Normaliser le nom pour la recherche dans le dictionnaire des villes
    nom_normalise = normaliser_nom_ville(nom_location)
    # print(f"Nom normalisé: {nom_normalise}")
    
    # Debug: vérifier si la clé existe dans le dictionnaire
    # print(f"Clés similaires dans le dictionnaire: {[k for k in location_dict.keys() if nom_normalise in k]}")
    # print(f"Valeur dans le dictionnaire: {location_dict.get(nom_normalise)}")
    
    # Si c'est déjà un numéro de département seul
    if re.match(r'^\d{2,3}$', nom_location) or nom_location in ['2A', '2B']:
        # print(f"Found direct department number: {nom_location}")
        return nom_location
    
    # Chercher le pattern (XX) ou (XXX)
    match = re.search(r'\((\d{2,3})\)', nom_location)
    if match:
        result = match.group(1)
        # print(f"Found department in parentheses: {result}")  # Debug print
        return result
    
    # Chercher un numéro de département à la fin de la chaîne
    match = re.search(r'\s(\d{2,3})$', nom_location)
    if match:
        result = match.group(1)
        # print(f"Found department at end: {result}")  # Debug print
        return result
        
    # Normaliser le nom pour la recherche dans le dictionnaire des villes
    nom_normalise = normaliser_nom_ville(nom_location)
    
    # Chercher dans le dictionnaire des villes
    departement = location_dict.get(nom_normalise)
    if departement is not None:
        # print(f"Found in dictionary: {nom_normalise} -> {departement}")  # Debug print
        return str(departement)
    
    print(f"No match found for: {nom_location}")  # Debug print
    return None

def find_job_title(title, jobs_dict):
    title_lower = title.lower()
    for job, keywords in jobs_dict.items():

        if isinstance(keywords[0], tuple):
            for keyword_tuple in keywords:
                if all(word in title_lower for word in keyword_tuple):
                    # print("Job trouvé : ", job)
                    return job
        else:
            if all(word in title_lower for word in keywords):
                # print("Job trouvé : ", job)
                return job
    print("Job non trouvé = other")
    return "Other"

""" def clean_experience(liste):
    if liste is None:
        return None
    nettoye = [mot for mot in liste if mot is not None and mot.lower().strip() not in {'a', 'n', 's'}]
    return nettoye """

def process_experience(experience):
    experience = experience.lower()
    if "débutant accepté" in experience:
        return "débutant accepté"
    mois_match = re.search(r'(\d+)\s*mois', experience)
    if mois_match:
        return f"{mois_match.group(1)} mois"
    annees_match = re.search(r'(\d+)\s*(?:an|ans|année|années|year|years?)', experience)
    if annees_match:
        return f"{annees_match.group(1)} an(s)"
    comparaison_match = re.search(r'[<>]\s*(\d+)(?:\s*(?:an|ans|année|années|year|years?))?', experience)
    if comparaison_match:
        return f"{comparaison_match.group(1)} an(s)"
    nombre_match = re.search(r'\d+', experience)
    if nombre_match:
        return f"{nombre_match.group(0)} an(s)"
    return experience

def process_education_level(education_text):
    """
    Extrait le chiffre le plus bas des niveaux d'études mentionnés.
    Ex: "Bac+3, Bac+4 ou équivalents" -> 3
    """
    import re
    
    # Patterns pour trouver les nombres après "bac+" ou "bac +"
    numbers = re.findall(r'bac\s*\+\s*(\d+)', education_text.lower())
    
    # Si on trouve des nombres, retourner le plus petit
    if numbers:
        return min(int(num) for num in numbers)
    if 'cap' in education_text.lower() or 'bep' in education_text.lower():
        return -1
    if 'bac' in education_text.lower():
        return 0
    if 'licence' in education_text.lower():
        return 3
    if 'master' in education_text.lower() or 'bac+5' in education_text.lower():
        return 5
    if 'doctorat' in education_text.lower() or 'phd' in education_text.lower():
        return 8
    return None

def transform_list_to_string(liste):
    if isinstance(liste, list):
        return ', '.join(liste)
    return liste

def find_keywords(description, keywords):
    found_keywords = set()
    description_lower = description.lower()
    for keyword in keywords:
        keyword_lower = keyword.strip().lower()
        if re.search(r'\b' + re.escape(keyword_lower) + r'\b', description_lower):
            found_keywords.add(keyword.strip())
    return list(found_keywords)

def clean_contract_type(contract_type):
    if contract_type is None:
        return None
        
    contract_type = str(contract_type).strip()
    
    # Dictionnaire de correspondance pour standardiser les types de contrat
    contract_mapping = {
        "Contrat à durée indéterminée": "CDI",
        "Contrat à durée déterminée": "CDD",
        "Profession libérale": "Freelance",
        
        #"Contrat travail temporaire": "Intérim",
        #"Contrat de professionnalisation": "Alternance",
        #"Contrat d'apprentissage": "Apprentissage"
    }
    
    # Vérifier si le type de contrat est dans le mapping
    for key, value in contract_mapping.items():
        if key.lower() in contract_type.lower():
            contract_type = value
            break
    
    # Extraction du type de contrat principal (pour les cas avec durée)
    if " - " in contract_type:
        contract_type = contract_type.split(" - ")[0].strip()
    
    # Liste des types de contrat valides
    valid_contracts = {
        "CDI", "CDD", "Intérim", "Freelance", 
        "Stage", "Apprentissage", "Alternance", 
        "Franchise", "Indépendant"
    }
    
    # Retourner le type si valide, sinon None
    return contract_type if contract_type in valid_contracts else None

def transform_json_file(input_file, output_folder, log_file_path):
    print("Transformation de : ", input_file)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Ouvrir le fichier log en mode append ('a')
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        if input_file.endswith(".json"):
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for entry in data:
                if 'raw_description' in entry:
                    entry['description'] = entry.pop('raw_description')
                # title = entry.pop('title', '')
                if 'job_title' in entry:
                    entry['job'] = find_job_title(entry['job_title'].lower(), JOBS)
                else:
                    entry['job'] = "Other"
                if 'contract_type_raw' in entry:
                    entry['contract_type'] = clean_contract_type(entry['contract_type_raw'])
                else:
                    entry['contract_type'] = None

                if 'location_raw' in entry:
                    entry['location'] = process_location(entry['location_raw'], location_dict)
                    # Ajouter un log si location_raw existe mais pas de correspondance trouvée
                    if entry['location'] is None and entry['location_raw']:
                        log_file.write(f"{os.path.basename(input_file)} : Aucune correspondance trouvée pour location_raw: {entry['location_raw']}\n")
                else:
                    entry['location'] = None
                                
                if "experience_raw" in entry and entry["experience_raw"] is not None:
                    entry["experience"] = process_experience(entry["experience_raw"])

                if "education_level_raw" in entry and entry["education_level_raw"] is not None:
                    entry["education_level"] = process_education_level(entry["education_level_raw"])
                    
                description = entry.get('description', '')
                if description:
                    entry['skills'] = {}

                    for variable, keywords in skills.items():
                        found_keywords = find_keywords(description, keywords)
                        if found_keywords:
                            entry['skills'][variable] = found_keywords
            output_filepath = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(input_file))[0]}_updated.json")
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    print("Les données mises à jour ont été sauvegardées.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transformation des fichiers JSON.")
    parser.add_argument("input_file", type=str, help="Chemin du fichier JSON d'entrée")
    parser.add_argument("output_folder", type=str, help="Chemin du dossier de sortie pour les fichiers JSON transformés")

    args = parser.parse_args()
    
    # Utiliser les mêmes variables d'environnement que main.py
    log_base_dir = os.getenv('DATA_LOG_DIR', '/app/data/logs/')
    log_dir = os.path.join(log_base_dir, 'transform')
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file_path = os.path.join(log_dir, "transform_ft.log")
    
    print(f"Utilisation du fichier log: {log_file_path}")
    transform_json_file(args.input_file, args.output_folder, log_file_path)
