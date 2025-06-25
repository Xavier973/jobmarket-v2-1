"""
This module contains all the functions needed to manage pagination and retrieve pages from html code.
"""

import logging

import httpx
import validators
from fake_useragent import UserAgent
from playwright.async_api import TimeoutError, async_playwright
from playwright_stealth import Stealth
from selectolax.parser import HTMLParser

logger = logging.getLogger("WelcomeToTheJungle.pagination_functions")


async def get_html(url: str):
    """
    Function for parsing the required html page.
    A different UserAgent is used for each function call to avoid being blocked by the scraped site.
    :param url: url of the page we want to scrape (job details pages)
    """
    user_agent = UserAgent().random  # Generate a random User-Agent for each call
    headers = {"User-Agent": user_agent}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = HTMLParser(resp.text)
        except httpx.HTTPError as e:
            logging.error(f"HTTP error while fetching {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"An error occurred while fetching {url}: {e}")
            return None
    return html


import logging

import validators
from playwright.async_api import TimeoutError, async_playwright


async def get_total_pages(baseurl: str, total_page_selector: str, job: str):
    """
    Function to return the total number of pages in our search.
    Use of playwright because the page is coded in JavaScript.

    :param baseurl: URL of the first page returned after entering the desired job in the search bar.
    :param total_page_selector: JavaScript selector containing the number of pages.
    :return int: The number corresponding to the last page of our search.
    """
    max_attempts = 2
    attempt = 0

    while attempt < max_attempts:
        try:
            if not validators.url(baseurl):
                raise ValueError("Invalid URL")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                print(f"Browser launched")
                stealth = Stealth()
                context = await browser.new_context()
                for script in stealth.enabled_scripts:
                    await context.add_init_script(script)
                page = await context.new_page()
                try:
                    print(f"Going to {baseurl}")
                    await page.goto(baseurl, timeout=5000)

                    # Dump du HTML pour debug
                    html = await page.content()
                    with open(f"debug_{job}.html", "w", encoding="utf-8") as f:
                        f.write(html)

                    # Attendre que les liens de pagination soient attachés au DOM
                    await page.wait_for_selector(total_page_selector, state="attached", timeout=15000)
                    elements = await page.query_selector_all(total_page_selector)
                    if elements:
                        last = elements[-1]
                        total_pages_text = await last.inner_text()
                        total_pages = int(total_pages_text.strip())
                        print(f"Total pages: {total_pages}")
                        return total_pages if total_pages else None
                    else:
                        print(f"No elements found - total pages fixed to 1")
                        return 1

                except TimeoutError as e:
                    logging.error(
                        f"Timeout error while extracting total number of pages: {str(e)}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error while extracting total number of pages: {str(e)}"
                    )
                finally:
                    await browser.close()

        except ValueError as ve:
            logging.error(f"Invalid URL: {str(ve)}")
            break
        except Exception as e:
            logging.error(f"Error while processing the base URL: {str(e)}")

        logging.info(f"Retrying... Attempt {attempt + 1} of {max_attempts}")
        attempt += 1

    logging.error("Failed to retrieve total number of pages after multiple attempts")
    return None