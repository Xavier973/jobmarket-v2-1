from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def initialize_driver():
    print("Initialisation du driver")
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

def test_contract_type_extraction():
    driver = initialize_driver()
    print("Driver initialisé")
    wait = WebDriverWait(driver, 5)
    
    # Liste des URLs à tester
    urls = [
        "https://candidat.francetravail.fr/offres/recherche/detail/189LGZW",
        "https://candidat.francetravail.fr/offres/recherche/detail/189LHBJ",
        "https://candidat.francetravail.fr/offres/recherche/detail/189LHCK"
        # Ajoutez d'autres URLs ici
    ]
    
    results = {}  # Dictionnaire pour stocker les résultats

    try:
        # Gestion des cookies (une seule fois au début)
        driver.get(urls[0])
        time.sleep(5)
        
        # Gérer les cookies
        try:
            pe_cookies_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "pe-cookies")))
            shadow = driver.execute_script('return arguments[0].shadowRoot', pe_cookies_element)
            button_inside_shadow = shadow.find_element(By.ID, "pecookies-accept-all")
            button_inside_shadow.click()
            time.sleep(2)
        except Exception as e:
            print(f"Erreur cookies: {e}")

        # Traitement de chaque URL
        for url in urls:
            print(f"\nTraitement de l'URL: {url}")
            try:
                driver.get(url)
                time.sleep(3)  # Attente réduite car les cookies sont déjà gérés

                try:
                    # Version desktop
                    contract_element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'p.contrat:not(.visible-xs-inline-block)')
                    ))
                    contract_text = contract_element.text.split('\n')[0]
                except Exception:
                    try:
                        # Version mobile
                        contract_element = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'p.contrat.visible-xs-inline-block')
                        ))
                        contract_text = contract_element.text.split('-')[0].strip()
                    except Exception as e:
                        print(f"Erreur pour {url}: {e}")
                        contract_text = "Non trouvé"

                results[url] = contract_text
                print(f"Type de contrat trouvé: {contract_text}")

            except Exception as e:
                print(f"Erreur lors du traitement de {url}: {e}")
                results[url] = "Erreur"

    except Exception as e:
        print(f"Erreur générale: {e}")
    
    finally:
        # Affichage du résumé
        print("\nRésumé des résultats:")
        for url, contract in results.items():
            print(f"URL: {url}")
            print(f"Type de contrat: {contract}")
            print("-" * 50)

        driver.save_screenshot('debug_last_page.png')
        driver.quit()

if __name__ == "__main__":
    print("Test extraction type de contrat - Multiple URLs")
    test_contract_type_extraction()