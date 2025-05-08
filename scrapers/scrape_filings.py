import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://13f.info'
MANAGER_PAGE_URL = BASE_URL + '/manager/'

def get_filings_for_manager(manager_id):
    filings = []
    try:
        res = requests.get(MANAGER_PAGE_URL + manager_id)
        soup = BeautifulSoup(res.text, 'html.parser')
        manager_name = soup.find("h1").get_text(strip=True)
        table = soup.find("table")

        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]

        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) != len(headers):
                continue
            row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}
            if row_data.get("Form Type", "").strip() != "13F-HR":
                continue

            filing_link = row.find('a')
            if not filing_link or not filing_link['href']:
                continue

            filing_url = BASE_URL + filing_link['href']
            quarter_name = row_data.get("Quarter", "").strip() or row_data.get("Filing Date", "").strip()
            date_filed = row_data.get("Date Filed", "").strip()
            filings.append({
                "manager_id": manager_id,
                "manager_name": manager_name,
                "filing_url": filing_url,
                "quarter": quarter_name,
                "date_filed": date_filed
            })
    except Exception as e:
        print(f"Error with manager {manager_id}: {e}")
    return filings
