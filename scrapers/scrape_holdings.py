from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

def get_com_holdings(filing):
    url = filing['filing_url']
    manager_id = filing['manager_id']
    manager_name = filing['manager_name']
    quarter = filing['quarter']
    date_filed = filing['date_filed']

    print(f"Fetching filing: {url}")
    holdings = []

    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tables = soup.find_all('table')

        target_table = None
        for tbl in tables:
            headers_check = [th.get_text(strip=True).lower() for th in tbl.find_all('th')]
            if 'cl' in headers_check:
                target_table = tbl
                break

        if not target_table:
            print("    ⚠️ Holdings table not found.")
            return []

        filing_headers = [th.get_text(strip=True) for th in target_table.find_all('th')]

        for tr in target_table.find_all('tr'):
            td_cells = tr.find_all('td')
            if len(td_cells) != len(filing_headers):
                continue

            row = {filing_headers[i]: td_cells[i].get_text(strip=True) for i in range(len(filing_headers))}
            class_val = row.get('Class', '') or row.get('Cl', '')
                # === Skip options like PUT or CALL ===
            option_type = row.get('Option Type') or row.get('option_type') or ''
            if option_type.strip().upper() in ['PUT', 'CALL']:
                continue
            if 'COM' in class_val.upper():
                row.update({
                    'manager_id': manager_id,
                    'manager_name': manager_name,
                    'filing_url': url,
                    'quarter': quarter,
                    'date_filed': date_filed
                })
                holdings.append(row)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return holdings

