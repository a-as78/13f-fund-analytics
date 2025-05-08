from scrapers.scrape_managers import get_manager_ids
from scrapers.scrape_filings import get_filings_for_manager
from scrapers.scrape_holdings import get_com_holdings
from transactions import compute_transactions

import csv
from tqdm import tqdm

OUTPUT_FILE = 'data/transactions'
MANAGER_BATCH_SIZE = 5

def main():
    manager_ids = get_manager_ids()  # adjust limit for testing
    print(f"Found {len(manager_ids)} managers to scrape.")
    for batch_start in tqdm(range(0, len(manager_ids), MANAGER_BATCH_SIZE), desc="getting managers' holings batches", unit="batch"):
        all_transactions = []
        tqdm.write(f"\n🔍 Scraping {batch_start / MANAGER_BATCH_SIZE} batch")
        for manager_id in manager_ids[batch_start:batch_start + MANAGER_BATCH_SIZE]:
            filings = get_filings_for_manager(manager_id)
            tqdm.write(f"Found {len(filings)} filings for manager {manager_id}")
            previous_holdings = None
            for filing in reversed(filings):
                new_holdings = get_com_holdings(filing)
                tqdm.write(f"Found {len(new_holdings)} new COM holdings.")
                transactions = compute_transactions(previous_holdings, new_holdings)
                all_transactions.append(transactions)
                previous_holdings = new_holdings

        if all_transactions:
            with open(OUTPUT_FILE + f'batch_{batch_start}-{batch_start+MANAGER_BATCH_SIZE}.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_transactions[0][0].keys())
                writer.writeheader()
                for transaction in all_transactions:
                    writer.writerows(transaction)
            print(f"\n This Batch aved {len(all_transactions)} transactions to '{OUTPUT_FILE}.csv'")
        else:   
            print("\n No transactions found.")

if __name__ == "__main__":
    main()
