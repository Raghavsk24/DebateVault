import os
import pandas as pd
from tqdm import tqdm
import argparse

def merge_csvs(input_folder, output_file):
    # Store CSV Files in input folder
    all_csv_files = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.endswith('.csv')
    ]
    all_csv_files.sort()

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
    parser = argparse.ArgumentParser(description="Merge CSV Files in input directory.")
    parser.add_argument("--input_dir", required=True, help="Path to the input directory with CSVs")
    parser.add_argument("--output_csv", required=True, help="Path to the output CSV")
    args = parser.parse_args()
    merge_csvs(args.input_dir, args.output_csv)
