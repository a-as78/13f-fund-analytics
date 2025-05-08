# 13F Holdings Scraper

This project scrapes investment manager data from [13f.info](https://13f.info/), extracts holdings data (particularly for common stock - COM), compares it across quarters, and infers transaction types. It also includes tools for visual analysis and CSV aggregation.

## Features

- 🔍 Scrape holdings and manager data using BeautifulSoup and Selenium
- 📊 Analyze changes in holdings and infer buy/sell/hold activity
- 📁 Combine and clean CSV data from multiple quarters
- 📈 Interactive dashboard with Streamlit and Plotly for data exploration

---

## Project Structure

```
13f_project_new/
├── analysis/
│   └── dashboard.py         # Streamlit dashboard for visual analysis
├── data/
│   └── *.csv                # CSV files containing transactions data grouped for each 5 managers
│   ├── scrape_holdings.py   # Scrapes holdings data
│   └── scrape_managers.py   # Scrapes manager-level data
│   └── scrape_filings.py    # Scrapes filigns data
├── combine_csv.py           # Merges CSV files for batch analysis
├── transactions.py          # Logic for detecting buy/sell transactions
├── utils.py                 # Helper functions
├── main.py                  # Entry point script
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Installation

First, ensure you have Python 3.8+ installed.

Then, install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Start Scraping

```bash
python main.py
```

### 2. Combine CSV Files

```bash
python combine_csv.py
```

### 3. Run Dashboard

```bash
streamlit run analysis/dashboard.py
```

---

## Notes

- Output CSVs will be saved in the working directory.
- Ensure a stable internet connection while scraping.
- Some scraping may be blocked by the website if rate limits are exceeded; use delays if needed.

