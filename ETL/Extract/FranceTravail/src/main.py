""" Program that loads the France Travail search page and initiates the job search for the defined search terms.
Determines, for each search term, the number of pages based on the number of job offers, then clicks on the "Show the next 20 offers" button as many times as necessary.
For each offer: Extracts data from the search page, then loads the offer page and extracts the remaining data.

Option to display the browser (firefox or chrome) or not.

Command line argument '--all' : allow the script to retrieve all aoffers without any date restrictions.
No argument : applies a filter for 'the last day'
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.firefox.service import Service as FirefoxService
import argparse
import time
import json
import os
from ETL.Transform.transform_date_ft import transform_date
from datetime import datetime
from ETL.Transform.data_cleaning_ft import transform_json_file

start_time = time.time()
base_url = "https://candidat.francetravail.fr/offres/recherche?motsCles={}&offresPartenaires=true&rayon=10&tri=0"

# Definition of local variables
Racine_url = "https://candidat.francetravail.fr/offres/recherche/detail/"
jobs = []
# Data recording file name
time_file = datetime.now().strftime("%Y%m%d_%H%M%S")
time_offer = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Définir les chemins de sauvegarde à partir des variables d'environnement
json_raw_directory = os.getenv('DATA_RAW_DIR', '/app/data/raw/francetravail')
json_transformed_directory = os.getenv('DATA_TRANSFORMED_DIR', '/app/data/transformed/francetravail')
log_file_path = os.path.join(
    os.getenv('DATA_LOG_DIR', '/app/data/logs/francetravail'),
    'ft_scraping_log.txt'
)

# Créer les dossiers s'ils n'existent pas
os.makedirs(json_raw_directory, exist_ok=True)
os.makedirs(json_transformed_directory, exist_ok=True)
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

print("====================================================================\n")
print("******* Scraping de France Travail - Projet JobMarket V2.2.1 *******\n")
print("====================================================================\n")

# Debug info
print("\n================= Configuration =================\n")
print(f"Dossier de sauvegarde : {json_raw_directory}")
print(f"Dossier transformé : {json_transformed_directory}")
print(f"Fichier de log : {log_file_path}")
print(f"ES_HOST : {os.getenv('ES_HOST')}")
print("==================================================\n")

# List of search terms for web scraping.
Search_term = [
    "data architect",
    "data engineer",
    "data scientist",
    "data analyst",
    "software engineer",
    "Data Warehousing Engineer",
    "Machine Learning Engineer",
    "cloud architect",
    "solution architect",
    "cloud engineer",
    "big data engineer",
    "Data Infrastructure Engineer",
    "Data Pipeline Engineer",
    "ETL Developer",
    "sysops"
]
# log function
def log_scraping_results(log_file_path, term, num_jobs, status="success", error_message=""):
    with open(log_file_path, 'a') as log_file:
        log_entry = f"{time_file} - Term: {term} - Jobs added: {num_jobs} - Status: {status}"
        if error_message:
            # Ne garder que la première ligne du message d'erreur si elle ne contient pas "<unknown>"
            error_lines = [line for line in error_message.split('\n') if "<unknown>" not in line]
            if error_lines:
                log_entry += f" - Error: {error_lines[0]}"
        log_entry += "\n"
        log_file.write(log_entry)

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--proxy-server="direct://"')
    chrome_options.add_argument('--proxy-bypass-list=*')
    chrome_options.add_argument('--start-maximized')
    chrome_options.binary_location = "/usr/bin/chromium"
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)  # Timeout après 30 secondes
    return driver

def get_total_offers(url, collect_all):
    # Charger la page
    driver.get(url)
    time.sleep(8)
    wait = WebDriverWait(driver, 10)
    
    #fermeture de la fenetre cookies
    try:
        pe_cookies_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "pe-cookies")))
        shadow = driver.execute_script('return arguments[0].shadowRoot', pe_cookies_element)
        button_inside_shadow = shadow.find_element(By.ID, "pecookies-accept-all")
        button_inside_shadow.click()
        print(" --- cookies fermés ---")
        time.sleep(5)
    except Exception as e:
        print("--- Pas de fenetre des cookies - ")

    # Click on 'Date de creation' then 'Un jour'
    if not collect_all:
        try:
            # Attendre que le bouton de filtre soit cliquable
            filter_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#filter-date-creation"))
            )
            
            # Faire défiler jusqu'au bouton
            driver.execute_script("arguments[0].scrollIntoView(true);", filter_button)
            time.sleep(5) # ToTest
            
            # Essayer de cliquer avec différentes méthodes
            try:
                # Méthode 1: Clic normal
                filter_button.click()
            except:
                try:
                    # Méthode 2: Clic JavaScript
                    driver.execute_script("arguments[0].click();", filter_button)
                except:
                    # Méthode 3: Actions chains
                    actions = webdriver.ActionChains(driver)
                    actions.move_to_element(filter_button).click().perform()
            
            time.sleep(5) # ToTest
            
            # Sélectionner "Un jour"
            one_day_option = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".radio:nth-child(1) > .control-label"))
            )
            driver.execute_script("arguments[0].click();", one_day_option)
            time.sleep(5) # ToTest
            
            # Cliquer sur le bouton de validation
            submit_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#btnSubmitDateCreation"))
            )
            driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(5) # ToTest
            
            print("Filtre 'Un jour' selectionné")
            
        except Exception as e:
            # Enregistrement de screenshots dans logs/francetravail/screenshots/
            screenshot_dir = os.path.join(os.getenv('DATA_LOG_DIR'), 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)          
            screenshot_name = f"error_screenshot_{time_file}_{term.replace(' ', '_')}.png"
            screenshot_path = os.path.join(screenshot_dir, screenshot_name)
            
            print(f"impossible d'appliquer le filtre 'Un jour' pour '{term}'. Erreur : {e}")
            print(f"Screenshot sauvegardé : {screenshot_path}")
            
            driver.save_screenshot(screenshot_path)
            return None
    
    try:
        # Find the number of job offers for the search term
        if driver.find_elements(By.XPATH, "//div[@id='zoneAfficherListeOffres']//h1[contains(@class, 'title')]"):
            total_offers_element = driver.find_element(By.XPATH, "//div[@id='zoneAfficherListeOffres']//h1[contains(@class, 'title')]")
            total_offers_text = total_offers_element.text
            total_offers = int(total_offers_text.split()[0])
            return total_offers
        else:
            no_offers_element = driver.find_element(By.XPATH, "//div[@class='media-body']/h1[contains(@class, 'title')]")
            no_offers_text = no_offers_element.text
            if "Aucune offre" in no_offers_text:
                print(f"{term} - aucune annonce")
                return None
    except Exception as e:
        print(f"-{term} Impossible de trouver le nombre d'offre. Erreur : {e}")
        return None

def click_show_more_offers(driver, times_to_click):
    wait = WebDriverWait(driver, 10)
    max_retries = 3  # Nombre maximum de tentatives par clic
    
    try:
        for n in range(times_to_click):
            print(f"Chargement de la page d'annonces {n+1} sur {times_to_click}")
            
            for attempt in range(max_retries):
                try:
                    # Attendre que le bouton soit visible et cliquable
                    show_more_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "p.results-more.text-center a.btn-primary"))
                    )
                    
                    # Faire défiler jusqu'au bouton
                    driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
                    time.sleep(1)  # Petit délai pour le défilement
                    
                    # Tenter le clic avec JavaScript si le clic normal échoue
                    try:
                        show_more_button.click()
                    except:
                        driver.execute_script("arguments[0].click();", show_more_button)
                    
                    # Attendre que la page se mette à jour
                    time.sleep(4)
                    
                    # Vérifier que de nouvelles offres sont chargées
                    wait.until(
                        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'li.result')) > (n + 1) * 20
                    )
                    
                    break  # Sortir de la boucle de tentatives si le clic réussit
                    
                except Exception as e:
                    if attempt == max_retries - 1:  # Dernière tentative
                        print(f"Échec après {max_retries} tentatives pour le clic {n+1}: {str(e)}")
                        return False
                    print(f"Tentative {attempt + 1} échouée pour le clic {n+1}, nouvelle tentative...")
                    time.sleep(2)  # Attendre avant la prochaine tentative
        
        return True
        
    except Exception as e:
        print(f"Erreur lors du chargement des offres: {str(e)}")
        return False
    
def scraping_and_process(term, driver, collect_all=False):
    try:
        # Définir filename au début de la fonction
        filename = os.path.join(json_raw_directory, f'ft_jobs_{time_file}.json')
        
        # Fetch the total number of offers
        url = base_url.format(term.replace(" ", "+"))
        total_offers = get_total_offers(url, collect_all)
                
        if total_offers is not None:
            print(f"---> {term} - Nombre total d'annonces : {total_offers} <---")

            # Click the necessary number of times to display all offers.

            clicks_needed = ((total_offers - 1) // 20)
            if clicks_needed > 49:
                print("(Nombre de pages à charger supérieur à 49)", clicks_needed)
                clicks_needed = 49
            print(f'Nombre de pages à charger : {clicks_needed}')
            click_result = click_show_more_offers(driver, clicks_needed)

            if click_result:
                if clicks_needed != 0:
                    print(f"Bouton 'show more offers' cliqué avec succès {clicks_needed} fois.")
                print("début du scraping")
                try:
                    offer_elements = driver.find_elements(By.CSS_SELECTOR, 'li.result')
                except:
                    print("Impossible de récuperer la liste de résultat")
                
                nb_annonce = 1
                for offer_element in offer_elements:
                    # Extraction of offer data from the results page.
                    try:
                        job_ref = offer_element.get_attribute('data-id-offre')
                    except:
                        job_ref = None
                    try:
                        job_url = Racine_url + job_ref
                    except:
                        job_url = None
                    try:
                        job_title = offer_element.find_element(By.CSS_SELECTOR, 'h2[data-intitule-offre]').text
                    except:
                        job_title = None
                    try:
                        company_location_element = offer_element.find_element(By.CSS_SELECTOR, 'p.subtext')
                        company_and_location = company_location_element.text.split(' - ')
                        # La localisation est toujours le dernier élément
                        Location = company_and_location[-1]
                        # L'entreprise est le premier élément
                        Company = company_and_location[0]
                        if Company.isdigit():
                            Location += ' ' + Company
                            Company = None
                    except:
                        Company = Location = None
                    #try:
                    #    Full_contract_type = offer_element.find_element(By.CSS_SELECTOR, 'div.media-right.media-middle.hidden-xs p.contrat').text
                    #    Contract_type = Full_contract_type.split()[0]
                    #except:
                    #    Contract_type = None
                    try :
                        Date = offer_element.find_element(By.CSS_SELECTOR, 'p.date').text
                        Date = transform_date(Date)
                    except :
                        Date = None
                    # Load the link to the offer in a new tab
                    main_window = driver.current_window_handle
                    driver.execute_script("window.open();")
                    driver.switch_to.window(driver.window_handles[1])
                    try :
                        driver.get(job_url)
                    except :
                        print("erreur dans l'URL")
                        break

                    try:
                        salary = driver.find_element(By.CSS_SELECTOR, 'ul[style="list-style-type: none; margin:0; padding: 0"] li').text
                    except:
                        salary = None
                    try:
                        experience = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="experienceRequirements"].skill-name').text
                    except:
                        experience = None
                    try:
                        education_level = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="educationRequirements"].skill-name').text
                    except:
                        education_level = None
                    try:
                        contract_element = driver.find_element(By.CSS_SELECTOR, 'div.description-aside dd')
                        # Prendre uniquement la première ligne du texte (avant le <br>)
                        Contract_type = contract_element.text.split('\n')[0].strip()
                    except:
                        Contract_type = None
                    try:
                        description = driver.find_element(By.CSS_SELECTOR, 'div.description.col-sm-8.col-md-7').text
                    except:
                        description = None
                    try:
                        sector = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="industry"]').text
                    except:
                        sector = None
                    try:
                        company_size = driver.find_element(By.CSS_SELECTOR, 'div.media > div.media-body > p').text
                    except:
                        company_size = None

                    driver.close()
                    driver.switch_to.window(main_window)
                    job = {
                        "source": "France Travail",
                        "job_title": job_title,
                        "job": "",
                        "contract_type_raw": Contract_type,
                        "salary": salary,
                        "company": Company,
                        "location_raw": Location,
                        "location": None,
                        "remote": None,
                        "experience_raw": experience,
                        "experience": None,
                        "education_level_raw": education_level,
                        "education_level": None,
                        "publication_date": Date,
                        "company_data":{
                            "sector": sector,
                            "company_size": company_size,
                            "creation_date": None,#"average_age_of_employees": None,
                            "address": None,
                            "average_age_of_employees": None,
                            "turnover_in_millions": None,
                            "proportion_female": None,
                            "proportion_male": None
                            },
                        "link": job_url,
                        "description": description,
                        #"skills": extracted_skills,          
                        #"search_term": term,
                        "ft_reference": job_ref,                
                        #"createdAt": time_offer
                    }
                    jobs.append(job)

                    # Enregistrement des données
                    filename = os.path.join(json_raw_directory, "FT_" + time_file + "_" + term + ".json")
                    file_exists = os.path.isfile(filename)
                    if not file_exists or os.stat(filename).st_size == 0:
                        with open(filename, 'w', encoding='utf-8') as f:
                        # Pour le premier job, écrire une liste ouvrante et le job
                            json.dump([job], f, ensure_ascii=False, indent=4)
                    else:
                        with open(filename, 'r+', encoding='utf-8') as f:
                            f.seek(0, os.SEEK_END)  # Allez à la fin du fichier
                            f.seek(f.tell() - 1, os.SEEK_SET)  # Reculer de 1 pour enlever le crochet fermant ']'
                            # Si fichier vide ou contient seulement '[]'
                            if f.tell() > 1:
                                f.write(', ') # Écrire une virgule avant d'ajouter le nouvel objet
                            else:
                                f.seek(0, os.SEEK_SET)  # Retour au début du fichier pour écrire le premier objet
                                f.write('[')
                            json.dump(job, f, ensure_ascii=False, indent=4)
                            f.write(']')  # Ajouter le crochet fermant pour clôturer le tableau JSON
                    print("Annonce", nb_annonce,"sur", total_offers,  job_url, "OK")
                    job = {}
                    nb_annonce += 1
                    time.sleep(2)
            else:
                print("Erreur lors du clic sur le bouton.")
                nb_annonce = 0
                log_scraping_results(log_file_path, term, nb_annonce, status="error", error_message="Unable to click on the button")
            log_scraping_results(log_file_path, term, nb_annonce)
        elif total_offers is None:
            print(f"{term} - aucune annonce")
            log_scraping_results(log_file_path, term, 0, status="no_offers")
            return
        else:
            nb_annonce = 0
            log_scraping_results(log_file_path, term, nb_annonce, status="error", error_message="Unable to get total offers")
    except Exception as e:
        print(f"Erreur lors du scraping pour {term}: {str(e)}")
        log_scraping_results(log_file_path, term, 0, status="error", error_message=str(e))
    # Nettoyage des donnée
    try:
        # Création du nom du fichier transformé
        output_filename = os.path.join(
            json_transformed_directory,
            os.path.splitext(os.path.basename(filename))[0] + "_transformed.json"
        )
        
        # Génération du nom de fichier log avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        transform_log_path = os.path.join(
            os.getenv('DATA_LOG_DIR', '/app/data/logs/francetravail'),
            f"transform_ft_{timestamp}.txt"
        )
        
        transform_json_file(
            input_file=filename,
            output_folder=os.path.dirname(output_filename),
            log_file_path=transform_log_path
        )
        print(f"---> Nettoyage des données terminé pour {term} <---")
    except Exception as e:
        print(f"ERREUR lors du nettoyage des données pour {term}: {e}")

if __name__ == "__main__":
    #log_file_path = os.path.join(current_directory, "scraping_log.txt")
    parser = argparse.ArgumentParser(description="Scrape job offers from France Travail.")
    parser.add_argument("--all", action='store_true', help="Collect all offers without date filtering.")
    #parser.add_argument("--browser", type=str, default="chrome", help="Type of browser to use ('chrome' or 'firefox').")
    args = parser.parse_args()

    #print("**** Scraping de France Travail - Projet JobMarket V2 ****")
    if args.all:
        print("-> Scraping des 3 derniers mois. (totalité des offres)")
    else:
        print("-> Scraping du dernier jour.")
    
    print("initialisation du driver")
    driver = initialize_driver()
    for term in Search_term:
        scraping_and_process(term, driver, collect_all=args.all)


end_time = time.time()
execution_time = end_time - start_time
minutes, seconds = divmod(execution_time, 60)
print("Scraping France Travail terminé")

print("Durée d'exécution :", int(execution_time), "secondes ({} minutes et {} secondes)".format(int(minutes), int(seconds)))
