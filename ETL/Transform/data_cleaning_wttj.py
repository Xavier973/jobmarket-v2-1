import os
import json
import re
import unicodedata
from pathlib import Path
import shutil

# Dictionnaire des métiers (repris de data_cleaning_ft.py)
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

skills = {
    "ProgLanguage": ["Python", "Java", "C++", "C#", "Scala", " R,", "/R/", " R ", "Julia", "Kotlin", "Bash"],
    "DataBase": ["SQL", "NoSQL", "MongoDB", "Cassandra", "Neo4j", "HBase", "Elasticsearch"],
    "DataAnalytics": ["Pandas", "NumPy", " R,", "/R/", " R ", "MATLAB"],
    "BigData": ["Hadoop", "Spark", "Databricks", "Flink", "Apache Airflow"],
    "MachineLearning": ["Scikit-Learn", "TensorFlow", "Keras", "PyTorch", "XGBoost", "LightGBM", "CatBoost", "Orange"],
    "DataSerialization": ["Avro", "Protocol Buffers", "Json", "XML"],
    "DataVisualisation": ["Tableau", "Power BI", "Matplotlib", "Seaborn", "Plotly"],
    "Statistics": ["Statistiques Descriptives", "Inférentielles", "Bayesian Statistics", "Statistiques Bayésiennes"],
    "CloudComputing": ["AWS", "Azure", "Google Cloud Platform", "GCP", "IBM Cloud", "Alibaba Cloud"],
    "DevTools": ["Git", "Docker", "Jenkins", "Travis CI"],
    "OS": ["Linux", "Windows", "MacOS"],
    "DBMS": ["MySQL", "PostgreSQL", "Oracle SQL", "SQL Server", "Snowflake", "BigQuery", "Big Query", "SingleStore"],
    "SoftBigDataProcessing": ["Apache Kafka", "Apache Flink", "HBase", "Cassandra"],
    "Automation": ["Ansible", "Kubernetes", "Puppet", "Chef", "Airflow"],
    "InfrastructureAsCode": ["Terraform", "CloudFormation"],
    "NetworkSecurty": ["VPN", "Firewall", "SSL/TLS", "Wireshark"],
    "Virtualisation": ["VMware", "VirtualBox", "Hyper-V"],
    "Containers": ["Docker", "Kubernetes", "OpenShift"],
    "Collaboration": ["JIRA", "Confluence", "Slack", "Microsoft Teams", "Teams", "Discord"],
    "Other": ["DevOps", "Backend Development", "Big Data", "ML", "Machine Learning", "Statistiques", "Cloud", "CI/CD", "CI / CD"],
    "EnSoftSkils": ["Communication", "Teamwork", "Time Management", "Adaptability", "Problem Solving", "Leadership", "Creativity", "Empathy", "Collaboration", "Stress Management", "Organization", "Flexibility", "Initiative", "Critical Thinking", "Interpersonal Skills"]
}

# Fonctions utilitaires (repris et simplifié de data_cleaning_ft.py)
def find_job_title(title, jobs_dict):
    title_lower = title.lower()
    for job, keywords in jobs_dict.items():
        if isinstance(keywords[0], tuple):
            for keyword_tuple in keywords:
                if all(word in title_lower for word in keyword_tuple):
                    return job
        else:
            if all(word in title_lower for word in keywords):
                return job
    return "Other"

def clean_contract_type(contract_type):
    if contract_type is None:
        return None
    contract_type = str(contract_type).strip()
    contract_mapping = {
        "Contrat à durée indéterminée": "CDI",
        "Contrat à durée déterminée": "CDD",
        "Profession libérale": "Freelance",
    }
    for key, value in contract_mapping.items():
        if key.lower() in contract_type.lower():
            contract_type = value
            break
    if " - " in contract_type:
        contract_type = contract_type.split(" - ")[0].strip()
    valid_contracts = {"CDI", "CDD", "Intérim", "Freelance", "Stage", "Apprentissage", "Alternance", "Franchise", "Indépendant"}
    return contract_type if contract_type in valid_contracts else None

def process_experience(experience):
    if not experience:
        return None
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
    if not education_text:
        return None
    numbers = re.findall(r'bac\s*\+\s*(\d+)', education_text.lower())
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

def find_keywords(description, keywords):
    found_keywords = set()
    description_lower = description.lower()
    for keyword in keywords:
        keyword_lower = keyword.strip().lower()
        if re.search(r'\b' + re.escape(keyword_lower) + r'\b', description_lower):
            found_keywords.add(keyword.strip())
    return list(found_keywords)

def clean_company_data(company_data):
    # On ne garde que les champs du mapping
    allowed = ["sector", "company_size", "creation_date", "address", "average_age_of_employees", "turnover_in_millions", "proportion_female", "proportion_male"]
    if not isinstance(company_data, dict):
        return {}
    return {k: v for k, v in company_data.items() if k in allowed and v is not None}

def clean_skills(skills_dict):
    allowed = ["ProgLanguage", "DataBase", "DataAnalytics", "BigData", "MachineLearning", "DataSerialization", "DataVisualisation", "Statistics", "CloudComputing", "DevTools", "OS", "DBMS", "SoftBigDataProcessing", "Automation", "InfrastructureAsCode", "NetworkSecurty", "Virtualisation", "Containers", "Collaboration", "Other", "EnSoftSkils"]
    if not isinstance(skills_dict, dict):
        return {}
    return {k: v for k, v in skills_dict.items() if k in allowed and v}

def normaliser_nom_ville(nom):
    if nom is None:
        return None
    nom = str(nom).strip().lower()
    nom = unicodedata.normalize('NFD', nom).encode('ascii', 'ignore').decode("utf-8")
    return nom

def charger_dictionnaire_villes(chemin_fichier):
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {normaliser_nom_ville(ville): dep for ville, dep in data.items()}
    except Exception:
        return {}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
location_dict = charger_dictionnaire_villes(os.path.join(SCRIPT_DIR, "villes_departements.json"))

def process_location(nom_location, location_dict):
    if nom_location is None:
        return None
    nom_location = str(nom_location).strip()
    if nom_location.lower().startswith('marseille'):
        return "13"
    if nom_location.lower().startswith('lyon'):
        return "69"
    if nom_location.lower().startswith('paris'):
        return "75"
    nom_normalise = normaliser_nom_ville(nom_location)
    if re.match(r'^\d{2,3}$', nom_location) or nom_location in ['2A', '2B']:
        return nom_location
    match = re.search(r'\((\d{2,3})\)', nom_location)
    if match:
        return match.group(1)
    match = re.search(r'\s(\d{2,3})$', nom_location)
    if match:
        return match.group(1)
    departement = location_dict.get(nom_normalise)
    if departement is not None:
        return str(departement)
    return None

def clean_entry(entry, log_file=None, input_filename=None):
    # Champs attendus par le mapping
    mapping_fields = [
        "source",
        "job_title",
        "job",
        "contract_type",
        "contract_type_raw",
        "salary",
        "company",
        "location",
        "location_raw",
        "remote",
        "experience",
        "experience_raw",
        "education_level",
        "education_level_raw",
        "publication_date",
        "wttj_reference",
        "company_data",
        "skills",
        "link",
        "description"
    ]
    cleaned = {}
    # Champs simples
    for field in mapping_fields:
        if field in entry:
            cleaned[field] = entry[field]
        else:
            cleaned[field] = None
    # Nettoyage spécifique
    if cleaned["job"] in [None, "", "Other"] and cleaned["job_title"]:
        cleaned["job"] = find_job_title(cleaned["job_title"], JOBS)
    if cleaned["contract_type"] is None and cleaned["contract_type_raw"]:
        cleaned["contract_type"] = clean_contract_type(cleaned["contract_type_raw"])
    if cleaned["experience"] is None and cleaned["experience_raw"]:
        cleaned["experience"] = process_experience(cleaned["experience_raw"])
    if cleaned["education_level"] is None and cleaned["education_level_raw"]:
        cleaned["education_level"] = process_education_level(cleaned["education_level_raw"])
    if "location_raw" in entry and entry["location_raw"]:
        location = process_location(entry["location_raw"], location_dict)
        cleaned["location"] = location
        if location is None and log_file is not None and input_filename is not None:
            log_file.write(f"{input_filename} : Aucune correspondance trouvée pour : {entry['location_raw']}\n")
    else:
        cleaned["location"] = None
    if cleaned["company_data"]:
        cleaned["company_data"] = clean_company_data(cleaned["company_data"])
    else:
        cleaned["company_data"] = {}
    # Skills
    description = cleaned.get("description", "")
    if description:
        skills_found = {}
        for variable, keywords in skills.items():
            found_keywords = find_keywords(description, keywords)
            if found_keywords:
                skills_found[variable] = found_keywords
        cleaned["skills"] = clean_skills(skills_found)
    else:
        cleaned["skills"] = {}
    return cleaned

def main():
    input_dir = "/home/ubuntu/jobmarket-v2-1/data/raw/wttj/"
    output_dir = "/home/ubuntu/jobmarket-v2-1/data/transformed/wttj/"
    log_dir = "/home/ubuntu/jobmarket-v2-1/data/logs/Transform"
    raw_cleaned_dir = "/home/ubuntu/jobmarket-v2-1/data/raw/wttj/raw_cleaned/"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(raw_cleaned_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "transform.log")

    # Lister tous les fichiers .json du dossier (hors sous-dossiers)
    for filename in os.listdir(input_dir):
        input_file = os.path.join(input_dir, filename)
        if not os.path.isfile(input_file):
            continue
        if not filename.endswith(".json"):
            continue
        output_file = os.path.join(output_dir, filename.replace('.json', '_clean.json'))
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            cleaned_data = [clean_entry(entry, log_file, os.path.basename(input_file)) for entry in data]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        print(f"Fichier nettoyé sauvegardé sous : {output_file}")
        # Déplacer le fichier d'entrée vers raw_cleaned
        shutil.move(input_file, os.path.join(raw_cleaned_dir, filename))
    print(f"Log écrit dans : {log_file_path}")

if __name__ == "__main__":
    main() 