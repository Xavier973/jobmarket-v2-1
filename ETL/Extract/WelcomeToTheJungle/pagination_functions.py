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

logger = logging.getLogger("Wttj.pagination_functions")

def handle_geographic_redirect(driver):
    """
    Gère la fenêtre de redirection géographique qui peut apparaître sur Welcome to the Jungle.
    Clique sur "Rester sur le site français" si la fenêtre est présente.
    :param driver: instance du navigateur Selenium
    """
    try:
        # Attendre un peu que la page se charge complètement
        WebDriverWait(driver, 5).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # Chercher le bouton "Rester sur le site français"
        redirect_button_selectors = [
            'button[data-testid="country-banner-redirect-button"]',
            'button:contains("Rester sur le site français")',
            'button.sc-kWJkYy.elPVoD',
            'button[class*="elPVoD"]'
        ]
        
        for selector in redirect_button_selectors:
            try:
                # Attendre que le bouton soit présent et cliquable
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info("Fenêtre de redirection géographique détectée, clic sur 'Rester sur le site français'")
                button.click()
                # Attendre que la fenêtre disparaisse
                WebDriverWait(driver, 5).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info("Fenêtre de redirection géographique fermée avec succès")
                return True
            except TimeoutException:
                continue
            except Exception as e:
                continue
        
        # print("Aucune fenêtre de redirection géographique détectée")
        return False
        
    except Exception as e:
        # print("Aucune fenêtre de redirection géographique détectée")
        return False

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
        # Gérer la redirection géographique si elle apparaît
        handle_geographic_redirect(driver)
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
            print(f"Chargement de la page {baseurl}")
            driver.get(baseurl)
            # Gérer la redirection géographique si elle apparaît
            handle_geographic_redirect(driver)
            # Dump du HTML pour debug dès que la page est chargée
            # with open(f"debug_{job}.html", "w", encoding="utf-8") as f:
            #    f.write(driver.page_source)
                # input("Press Enter to continue...")
            
            # Attendre que la page soit complètement chargée
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            
            # Vérifier d'abord s'il y a des éléments de pagination
            elements = driver.find_elements(By.CSS_SELECTOR, total_page_selector)
            
            if not elements:
                # Aucun élément de pagination trouvé, cela signifie qu'il n'y a qu'une seule page
                logger.info(f"Aucun élément de pagination trouvé - total pages fixé à 1")
                return 1
            
            # Si des éléments sont trouvés, prendre le dernier pour obtenir le nombre total de pages
            last = elements[-1]
            total_pages_text = last.text.strip()
            total_pages = int(total_pages_text)
            print(f"Nombre de pages trouvées : {total_pages}")
            return total_pages if total_pages else None
            
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