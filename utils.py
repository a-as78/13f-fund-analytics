import pandas as pd
import glob
import os

def parse_shares(shares_str):
    return int(shares_str.replace(',', '')) if shares_str else 0

def concatenate_csv_files(folder_path):
    """
    Concatenate all CSV files in a specified folder into a single DataFrame.
    """

    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    df_list = [pd.read_csv(file) for file in csv_files]
    combined_df = pd.concat(df_list, ignore_index=True)

    combined_df.to_csv('combined_output_transactions.csv', index=False)

    print(f"Combined {len(csv_files)} files into a single DataFrame with {combined_df.shape[0]} rows.")
