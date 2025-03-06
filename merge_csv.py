import os
import pandas as pd
from tqdm import tqdm

def merge_csvs(input_folder, output_file):
    # List and sort CSV files in the input folder
    all_csv_files = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.endswith('.csv')
    ]
    all_csv_files.sort()

    # Keep only the first 30
    all_csv_files = all_csv_files[:]

    df_list = []

    # Use tqdm to display a progress bar for reading CSV files
    for csv_file in tqdm(all_csv_files, desc="Reading CSVs", unit="file"):
        df = pd.read_csv(csv_file)
        df_list.append(df)

    # Concatenate all DataFrames
    merged_df = pd.concat(df_list, ignore_index=True)

    # Save the merged DataFrame to a single CSV
    merged_df.to_csv(output_file, index=False)
    print(f"\nMerged {len(all_csv_files)} CSV files into {output_file}")

if __name__ == "__main__":
    input_folder = "output2"       # Folder containing your CSV files
    output_file = "hspolicy24_all_2025_03_04.csv"    # Name of the output CSV file
    merge_csvs(input_folder, output_file)
