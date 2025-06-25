"""
Ce module contient toutes les fonctions nécessaires pour gérer la pagination et récupérer les pages HTML avec Selenium.
"""

import logging
import validators
from fake_useragent import UserAgent
from selectolax.parser import HTMLParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger("WelcomeToTheJungle.pagination_functions")

def get_html(driver, url: str):
    """
    Fonction pour parser la page HTML requise avec Selenium.
    :param driver: instance du navigateur Selenium
    :param url: url de la page à scraper
    :return: HTMLParser de la page
    """
    try:
        user_agent = UserAgent().random
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    except Exception as e:
        logger.warning(f"Impossible de changer le User-Agent : {e}")
    try:
        driver.get(url)
        # Attendre que la page soit chargée (on peut adapter le sélecteur si besoin)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        html = HTMLParser(driver.page_source)
        return html
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {url} : {e}")
        return None

def get_total_pages(driver, baseurl: str, total_page_selector: str, job: str):
    """
    Retourne le nombre total de pages pour une recherche donnée, en utilisant Selenium.
    :param driver: instance du navigateur Selenium
    :param baseurl: URL de la première page de recherche
    :param total_page_selector: sélecteur CSS de la pagination
    :param job: nom du job (pour debug)
    :return: int ou None
    """
    max_attempts = 2
    attempt = 0
    while attempt < max_attempts:
        try:
            if not validators.url(baseurl):
                raise ValueError("Invalid URL")
            driver.get(baseurl)
            # Dump du HTML pour debug dès que la page est chargée
            with open(f"debug_{job}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            # Attendre que la pagination soit présente
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, total_page_selector))
                )
                elements = driver.find_elements(By.CSS_SELECTOR, total_page_selector)
                if elements:
                    last = elements[-1]
                    total_pages_text = last.text.strip()
                    total_pages = int(total_pages_text)
                    return total_pages if total_pages else None
                else:
                    logger.info(f"Aucun élément trouvé - total pages fixé à 1")
                    return 1
            except TimeoutException:
                logger.error(f"Timeout lors de l'extraction du nombre de pages pour {baseurl}")
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction du nombre de pages : {e}")
        except ValueError as ve:
            logger.error(f"URL invalide : {str(ve)}")
            break
        except WebDriverException as e:
            logger.error(f"Erreur WebDriver : {str(e)}")
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'URL de base : {str(e)}")
        logger.info(f"Nouvelle tentative... {attempt + 1} sur {max_attempts}")
        attempt += 1
    logger.error("Impossible de récupérer le nombre de pages après plusieurs tentatives")
    return None