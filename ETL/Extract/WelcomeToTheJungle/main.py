import datetime
import json
import logging
import logging.config
import sys
from pathlib import Path
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from fake_useragent import UserAgent
from selenium_stealth import stealth

from constants import (
    COMPANY_INFO_SELECTOR,
    COMPANY_SELECTORS,
    CONTRACT_INFO_SELECTOR,
    CONTRACT_SELECTORS,
    JOB_LINK_SELECTOR,
    JOBS,
    RACINE_URL,
    RAW_DESCRIPTION_SELECTORS,
    TOTAL_PAGE_SELECTOR,
)
from data_extraction import (
    extract_links,
    get_company_elements,
    get_contract_elements,
    get_raw_description,
    extract_wttj_ref,
)
from file_operations import save_file
from pagination_functions import get_html, get_total_pages, handle_geographic_redirect

# Nom de la source
SOURCE_NAME = "wttj"

# Obtenir la date et l'heure actuelle pour le nom du fichier de log
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Définir les chemins de sauvegarde à partir des variables d'environnement
json_raw_directory = os.path.join(os.getenv('DATA_RAW_DIR', '/app/data/raw'), SOURCE_NAME)
json_transformed_directory = os.path.join(os.getenv('DATA_TRANSFORMED_DIR', '/app/data/transformed'), SOURCE_NAME)
log_file_path = os.path.join(
    os.getenv('DATA_LOG_DIR', '/app/data/logs'),
    SOURCE_NAME,
    f'wttj_scraping_log_{current_datetime}.log'
)

# Créer les dossiers s'ils n'existent pas
os.makedirs(json_raw_directory, exist_ok=True)
os.makedirs(json_transformed_directory, exist_ok=True)
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

print("===============================================================================\n")
print("********* Scraping de Welcome To The Jungle - Projet JobMarket V2.2.1 *********\n")
print("===============================================================================\n")

# Debug info
print("================================ Configuration ================================")
print(f"-> Dossier de sauvegarde : {json_raw_directory}")
print(f"-> Dossier transformé : {json_transformed_directory}")
print(f"-> Fichier de log : {log_file_path}")
print(f"-> ES_HOST : {os.getenv('ES_HOST')}")
print("================================================================================\n")

# Configuration du logging
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": log_file_path,
            "formatter": "default",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
    "loggers": {
        "my_lib": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Apply logging configuration
logging.config.dictConfig(logging_config)

# Fonction de logging des résultats
def log_scraping_results(log_file_path, term, num_jobs, status="success", error_message=""):
    time_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(log_file_path, 'a') as log_file:
        log_entry = f"{time_file} - Term: {term} - Jobs added: {num_jobs} - Status: {status}"
        if error_message:
            # Ne garder que la première ligne du message d'erreur si elle ne contient pas "<unknown>"
            error_lines = [line for line in error_message.split('\n') if "<unknown>" not in line]
            if error_lines:
                log_entry += f" - Error: {error_lines[0]}"
        log_entry += "\n"
        log_file.write(log_entry)


def generate_job_search_url(job, page_number):
    url = f"https://www.welcometothejungle.com/fr/jobs?query={job.replace(' ', '%20')}&page={page_number}&aroundQuery=worldwide"
    logging.info(f"Generated URL: {url}")
    return url


def append_to_json_list(file_path, item):
    try:
        if (
            file_path.exists() and file_path.stat().st_size > 2
        ):  # If the file is not empty and not just '[]'
            with open(file_path, "r+", encoding="utf-8") as f:
                f.seek(0, 2)  # Go to the end of the file
                f.seek(
                    f.tell() - 1, 0
                )  # Move back one character (to before the last ])
                f.truncate()  # Remove the last character
                f.write(
                    ",\n"
                )  # Add a comma (to separate this from the previous dict) and a newline
                json.dump(item, f, ensure_ascii=False)  # Dump the new dictionary with proper Unicode handling
                f.write("]")  # Close the list
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([item], f, ensure_ascii=False)  # Create a new list with the first item
    except Exception as e:
        logging.error(f"Error while appending to JSON list: {e}")


def launch_browser():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')  # Commenté pour afficher le navigateur
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--proxy-server="direct://"')
    chrome_options.add_argument('--proxy-bypass-list=*')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--user-data-dir=/tmp/chrome-user-data')
    chrome_options.binary_location = "/usr/bin/chromium"
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)  # Timeout après 30 secondes
    return driver

def close_browser(driver):
    driver.quit()


def scrape_job_offers(driver, job, page_number, final_file):
    job_search_url = generate_job_search_url(job, page_number)
    logging.info(f"Scraping URL: {job_search_url}")
    try:
        print(f"Scraping job offers for {job} on page {page_number}")
        # Dump du HTML de la page de résultats (avant extraction des liens)
        driver.get(job_search_url)
        # Gérer la redirection géographique si elle apparaît
        handle_geographic_redirect(driver)
        # page_html = driver.page_source
        # safe_job = job.replace(' ', '_').replace('/', '_')
        # html_capture = f"html_dump_{safe_job}_{page_number}.html"
        # print(f"HTML dump: {html_capture}")
        #with open(html_capture, "w", encoding="utf-8") as f:
        #    f.write(page_html)
        
        # Extraction des liens sur la page
        job_links = extract_links(driver, job_search_url, JOB_LINK_SELECTOR)
        # logging.info(f"Extracted job links: {job_links}")
        # print(f"Job links: {job_links}")
        if not job_links:
            logging.warning(f"No job links found for URL: {job_search_url}")
            return []
        job_offers = []
        for link in job_links:
            if link is None:
                logging.error("Extracted link is None, skipping...")
                continue
            if link.startswith('http'):
                complete_url = link
            else:
                complete_url = f"{RACINE_URL}{link}"
            # logging.info(f"Fetching job details from: {complete_url}")
            wait = round(random.uniform(1, 3), 2)
            # print(f"Waiting for {wait} seconds")
            WebDriverWait(driver, wait)
            try:
                html = get_html(driver, complete_url)
                if html:
                    # logging.info(f"Fetched HTML for {complete_url}")
                    job_offer = {
                        "source": "wttj",
                        **get_contract_elements(
                            html, CONTRACT_INFO_SELECTOR, CONTRACT_SELECTORS
                        ),
                        "wttj_ref": extract_wttj_ref(link),
                        "company_data": get_company_elements(
                            html, COMPANY_INFO_SELECTOR, COMPANY_SELECTORS
                        ),
                        "link": complete_url,
                        "description": get_raw_description(
                            html, RAW_DESCRIPTION_SELECTORS
                        ),
                    }
                    job_offers.append(job_offer)
                    append_to_json_list(final_file, job_offer)
                    # logging.info(f"Successfully wrote job offer to {final_file}")
                else:
                    logging.error(f"Failed to fetch HTML from {complete_url}, got None")
            except Exception as e:
                logging.error(f"Failed to fetch job details from {complete_url}: {e}")
        return job_offers
    except Exception as e:
        logging.error(f"Failed to scrape {job_search_url}: {e}")
        return []


def scrape_jobs(driver, final_file):
    total_jobs_scraped = 0
    for job in JOBS:
        print(f"Scraping job: {job}")
        job_count = 0
        try:
            baseurl = generate_job_search_url(job, 1)
            total_pages = get_total_pages(driver, baseurl, TOTAL_PAGE_SELECTOR, job)
            if total_pages is None:
                logging.error(f"Could not determine total pages for job: {job}")
                log_scraping_results(log_file_path, job, 0, "error", "Could not determine total pages")
                continue
            
            for page_number in range(1, total_pages + 1):
                job_offers = scrape_job_offers(driver, job, page_number, final_file)
                job_count += len(job_offers)
            
            total_jobs_scraped += job_count
            log_scraping_results(log_file_path, job, job_count, "success")
            print(f"Scraped {job_count} jobs for '{job}'")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error scraping job '{job}': {error_msg}")
            log_scraping_results(log_file_path, job, job_count, "error", error_msg)
    
    print(f"\nTotal jobs scraped: {total_jobs_scraped}")
    return total_jobs_scraped


def main():
    # print("Scraping Welcome to the Jungle")
    logger = logging.getLogger(__name__)

    # Obtenir la date actuelle sous forme de chaîne formatée
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Construire le nom de fichier final avec la date
    final_file = Path(os.path.join(json_raw_directory, f"wttj_{current_date}.json"))
    print(f"Json: {final_file}")
    # Initialize final file with an empty list if it doesn't exist
    if not final_file.exists():
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("[]")  # Initialize with empty list

    # Launch browser
    driver = launch_browser()
    print("Browser launched")

    try:
        # Scrape jobs
        total_scraped = scrape_jobs(driver, final_file)
        print(f"\nScraping terminé. Total: {total_scraped} offres d'emploi extraites.")
    finally:
        # Ensure browser is closed
        close_browser(driver)


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


if __name__ == "__main__":
    main()
    sys.exit()