import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import string

BASE_URL = 'https://13f.info'
MANAGER_DIR_URL = BASE_URL + '/managers/'

def get_manager_ids(limit=None):
    suffixes = ['0'] + list(string.ascii_lowercase)
    manager_ids = []

    # for suffix in suffixes:
    for suffix in tqdm(suffixes, desc="Scraping manager IDs", unit="suffix"):
        url = MANAGER_DIR_URL + suffix
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            if not table:
                continue
            for row in table.find_all('tr'):
                link = row.find('a')
                if link and '/manager/' in link['href']:
                    manager_id = link['href'].split('/manager/')[-1]
                    manager_ids.append(manager_id)
                    if limit and len(manager_ids) >= limit:
                        return manager_ids
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    return manager_ids
