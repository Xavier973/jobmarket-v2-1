"""
Ce module regroupe toutes les fonctions nécessaires pour obtenir des informations à partir des pages web (version Selenium).
"""

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configuration du journal dans un fichier
logger = logging.getLogger("WelcomeToTheJungle.data_extraction")

def extract_links(driver, job_search_url: str, job_links_selector: str):
    """
    Fonction qui extrait tous les liens d'offres à partir de chaque page de recherche (Selenium).
    :param driver: instance du navigateur Selenium
    :param job_search_url: url de la page de recherche
    :param job_links_selector: sélecteur CSS des liens d'offres
    :return: liste de liens
    """
    try:
        logger.info(f"Navigation vers {job_search_url}")
        driver.get(job_search_url)
        # Attendre que les liens soient présents
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, job_links_selector))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, job_links_selector)
        logger.info(f"Nombre d'éléments trouvés : {len(elements)}")
        links = [element.get_attribute("href") for element in elements]
        logger.info(f"Liens extraits : {links}")
        return links
    except TimeoutException:
        logger.error(f"Timeout lors de l'extraction des liens sur {job_search_url}")
        return []
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des liens : {str(e)}")
        return []

def get_info(html, selector, parent=True):
    """
    Function that extracts and formats all the information you need from job details pages.
    :param html: HTML code of the page to be scrapped
    :param selector: scraper information selector
    :param parent: For some tags, we had to use sub-tags because the generic tag was repeated in several places in the
    code. We then retrieve the parent tag to extract the information, as the desired information may lie outside the
    indentifiable tags.
    :return str: Text containing information
    """
    replacements = {
        "Salaire : ": "",
        "Expérience : ": "",
        "Éducation : ": "",
        " collaborateurs": "",
        "Créée en ": "",
        "Âge moyen : ": "",
        " ans": "",
        "Chiffre d'affaires : ": "",
        "M€": "",
        "%": "",
        "&nbsp;": " ",
        "&NBSP;": " ",
    }

    try:
        text = (
            html.css_first(selector).parent.text()
            if parent
            else html.css_first(selector).text()
        )
        for key, value in replacements.items():
            text = text.replace(key, value)
        return text
    except AttributeError:
        return None

def get_contract_elements(html, contract_info_selector, CONTRACT_SELECTORS):
    """
    Fonction qui extrait les éléments de contrat à partir du HTML (Selectolax).
    """
    contract_elements = html.css_first(contract_info_selector)
    try:
        title = get_info(contract_elements, CONTRACT_SELECTORS["title"], parent=False)
        contract_type = get_info(contract_elements, CONTRACT_SELECTORS["contract_type"])
        salary = get_info(contract_elements, CONTRACT_SELECTORS["salary"])
        company = get_info(
            contract_elements, CONTRACT_SELECTORS["company"], parent=False
        )
        location = get_info(contract_elements, CONTRACT_SELECTORS["location"])
        remote = get_info(contract_elements, CONTRACT_SELECTORS["remote"])
        experience = get_info(contract_elements, CONTRACT_SELECTORS["experience"])
        education_level = get_info(
            contract_elements, CONTRACT_SELECTORS["education_level"]
        )
        time_element = contract_elements.css_first("time")
        publication_date = (
            time_element.attributes["datetime"][0:10] if time_element else None
        )
        contract_data = {
            "title": title,
            "company": company,
            "location": location,
            "remote": remote,
            "publication_date": publication_date,
            "details": {
                "TypeContract": contract_type,
                "Salary": salary,
                "Experience": experience,
                "Level": education_level,
            },
        }
        return contract_data
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des éléments de contrat : {e}")
        raise

def get_company_elements(html, company_info_selector, COMPANY_SELECTORS):
    """
    Fonction qui extrait les éléments de l'entreprise à partir du HTML (Selectolax).
    """
    try:
        company_elements = html.css_first(company_info_selector)
        sector = get_info(company_elements, COMPANY_SELECTORS["sector"])
        company_size = get_info(company_elements, COMPANY_SELECTORS["company_size"])
        turnover_in_millions = get_info(
            company_elements, COMPANY_SELECTORS["turnover_in_millions"]
        )
        company_data = {
            "sector": sector,
            "company_size": company_size,
            "turnover_in_millions": turnover_in_millions,
        }
        return company_data
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des éléments de l'entreprise : {e}")
        raise

def get_raw_description(html, selector):
    try:
        description = html.css_first(selector)
        if description:
            return description.text()
        else:
            return None
    except Exception as e:
        logger.error(f"Erreur lors du parsing du HTML : {e}")
        return None