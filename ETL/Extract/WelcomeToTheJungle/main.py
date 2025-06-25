import datetime
import json
import logging
import logging.config
import sys
from pathlib import Path
import os
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
)
from file_operations import save_file
from pagination_functions import get_html, get_total_pages

SOURCE_NAME = "welcometothejungle"
# output_dir = os.path.join(os.getenv('DATA_RAW_DIR', '/app/data/raw'), SOURCE_NAME)
output_dir = Path(os.path.join('data/raw', SOURCE_NAME))
output_dir.mkdir(parents=True, exist_ok=True)
# json_transformed_dir = os.path.join(os.getenv('DATA_TRANSFORMED_DIR', '/app/data/transformed'), SOURCE_NAME)

# Ensure log directory exists
log_file = output_dir / "wttj_scraper.log"

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
            "filename": str(log_file),
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
                json.dump(item, f)  # Dump the new dictionary
                f.write("]")  # Close the list
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([item], f)  # Create a new list with the first item
    except Exception as e:
        logging.error(f"Error while appending to JSON list: {e}")


def launch_browser():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    user_agent = UserAgent().random
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    # Appliquer selenium-stealth
    stealth(driver,
        languages=["fr-FR", "fr"],
        vendor="Google Inc.",
        platform="Linux x86_64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def close_browser(driver):
    driver.quit()


def scrape_job_offers(driver, job, page_number, final_file):
    job_search_url = generate_job_search_url(job, page_number)
    logging.info(f"Scraping URL: {job_search_url}")
    try:
        # Dump du HTML de la page de résultats (avant extraction des liens)
        driver.get(job_search_url)
        page_html = driver.page_source
        safe_job = job.replace(' ', '_').replace('/', '_')
        html_capture = f"html_dump_{safe_job}_{page_number}.html"
        print(f"HTML dump: {html_capture}")
        with open(html_capture, "w", encoding="utf-8") as f:
            f.write(page_html)
        # Extraction des liens sur la page
        job_links = extract_links(driver, job_search_url, JOB_LINK_SELECTOR)
        logging.info(f"Extracted job links: {job_links}")
        if not job_links:
            logging.warning(f"No job links found for URL: {job_search_url}")
            return []
        job_offers = []
        for link in job_links:
            if link is None:
                logging.error("Extracted link is None, skipping...")
                continue
            complete_url = f"{RACINE_URL}{link}"
            logging.info(f"Fetching job details from: {complete_url}")
            try:
                html = get_html(driver, complete_url)
                if html:
                    logging.info(f"Fetched HTML for {complete_url}")
                    job_offer = {
                        "source": "welcometothejungle",
                        "link": complete_url,
                        **get_contract_elements(
                            html, CONTRACT_INFO_SELECTOR, CONTRACT_SELECTORS
                        ),
                        "company_data": get_company_elements(
                            html, COMPANY_INFO_SELECTOR, COMPANY_SELECTORS
                        ),
                        "description": get_raw_description(
                            html, RAW_DESCRIPTION_SELECTORS
                        ),
                    }
                    job_offers.append(job_offer)
                    append_to_json_list(final_file, job_offer)
                    logging.info(f"Successfully wrote job offer to {final_file}")
                else:
                    logging.error(f"Failed to fetch HTML from {complete_url}, got None")
            except Exception as e:
                logging.error(f"Failed to fetch job details from {complete_url}: {e}")
        return job_offers
    except Exception as e:
        logging.error(f"Failed to scrape {job_search_url}: {e}")
        return []


def scrape_jobs(driver, final_file):
    for job in JOBS:
        baseurl = generate_job_search_url(job, 1)
        total_pages = get_total_pages(driver, baseurl, TOTAL_PAGE_SELECTOR, job)
        if total_pages is None:
            logging.error(f"Could not determine total pages for job: {job}")
            continue
        for page_number in range(1, total_pages + 1):
            scrape_job_offers(driver, job, page_number, final_file)


def main():
    print("Scraping Welcome to the Jungle")
    logger = logging.getLogger(__name__)

    # Obtenir la date actuelle sous forme de chaîne formatée
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Construire le nom de fichier final avec la date
    final_file = output_dir / f"wttj_database_{current_date}.json"
    print(f"Final file: {final_file}")
    # Initialize final file with an empty list if it doesn't exist
    if not final_file.exists():
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("[]")  # Initialize with empty list

    # Launch browser
    driver = launch_browser()
    print("Browser launched")

    try:
        # Scrape jobs
        scrape_jobs(driver, final_file)
    finally:
        # Ensure browser is closed
        close_browser(driver)


if __name__ == "__main__":
    main()
    sys.exit()