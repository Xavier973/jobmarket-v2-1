'''
This module contains all the constants of the project.
That way, it'll be easily maintainable.
'''

# Liste des constantes
BASEURL = ['https://www.welcometothejungle.com/fr/jobs?query=', 'page=1&aroundQuery=worldwide']
JOBS = ["data architect",
    "data engineer",
    "data scientist",
    "data analyst",
    "data manager",
    "software engineer",
    "Machine Learning Engineer",
    "cloud architect",
    "solution architect",
    "cloud engineer",
    "big data engineer",
    "Data Infrastructure Engineer",
    "Data Pipeline Engineer",
    "ETL Developer",
    "sysops"]
RACINE_URL = 'https://www.welcometothejungle.com'
JOB_LINK_SELECTOR = 'div.sc-flttKd.hSdoDt > a'
TOTAL_PAGE_SELECTOR = "a.sc-kVjqSu.gEPmms"
CONTRACT_INFO_SELECTOR = '[data-testid="job-metadata-block"]'
COMPANY_INFO_SELECTOR = '.sc-bXCLTC.dBpdut'
CONTRACT_SELECTORS = {
    'title': 'h2',
    'contract_type': '[name="contract"]',
    'salary': '[name="salary"]',
    'company': '.sc-dPhEwk.bSVjaH.wui-text',
    'location': '[name="location"]',
    'remote': '[name="remote"]',
    'experience': '[name="suitcase"]',
    'education_level': '[name="education_level"]'
}
COMPANY_SELECTORS = {
    'sector': '[name="tag"]',
    'company_size': '[name="department"]',
    'turnover_in_millions': '[name="euro_currency"]',
}
RAW_DESCRIPTION_SELECTORS = 'div.sc-eCEBvo.jswODj'