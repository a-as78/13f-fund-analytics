from utils import parse_shares


def build_transaction(holding, shares_str, change, pct_change, txn_type, quarter, date_filed):
    return {
        'fund_name': holding['manager_name'],
        'filing_date': date_filed,
        'quarter': quarter,
        'stock_symbol': holding['Sym'],
        'cl': holding.get('Class', ''),
        'value_($000)': holding.get('Value ($000)', ''),
        'shares': shares_str,
        'change': change,
        'pct_change': pct_change,
        'inferred_transaction_type': txn_type
    }


def compute_sells(old_dict, new_dict, quarter, date_filed):
    sells = []

    for cusip, old in old_dict.items():
        if cusip in new_dict:
            continue

        old_shares = parse_shares(old['Shares'])
        sells.append(build_transaction(
            holding=old,
            shares_str=old['Shares'],
            change=-old_shares,
            pct_change=-100.0 if old_shares else 0,
            txn_type='SELL',
            quarter=quarter,
            date_filed=date_filed
        ))

    return sells


def compute_buys_and_holds(old_dict, new_dict, quarter, date_filed):
    results = []

    for cusip, new in new_dict.items():
        new_shares = parse_shares(new['Shares'])
        old = old_dict.get(cusip)

        if old:
            old_shares = parse_shares(old['Shares'])
            change = new_shares - old_shares
            pct_change = (change / old_shares) * 100 if old_shares else 0
            txn_type = 'HOLD' if change == 0 else ('BUY' if change > 0 else 'SELL')
        else:
            change = new_shares
            pct_change = None
            txn_type = 'BUY'

        results.append(build_transaction(
            holding=new,
            shares_str=new['Shares'],
            change=change,
            pct_change=pct_change,
            txn_type=txn_type,
            quarter=quarter,
            date_filed=date_filed
        ))

    return results


def compute_transactions(old_holdings, new_holdings):
    if not new_holdings:
        return []

    quarter = new_holdings[0]['quarter']
    date_filed = new_holdings[0]['date_filed']

    old_dict = {h['CUSIP']: h for h in old_holdings} if old_holdings else {}
    new_dict = {h['CUSIP']: h for h in new_holdings}

    transactions = []
    transactions += compute_sells(old_dict, new_dict, quarter, date_filed)
    transactions += compute_buys_and_holds(old_dict, new_dict, quarter, date_filed)

    return transactions