import pandas as pd
import argparse
import os

def split_csv(input_csv, output_dir, chunks=10):
    os.makedirs(output_dir, exist_ok=True)

    # Count total rows in CSV 
    total_rows = sum(1 for _ in open(input_csv)) - 1  
    chunk_size = total_rows // chunks

    reader = pd.read_csv(input_csv, chunksize=chunk_size)

    # Split rows from CSV
    for i, df_chunk in enumerate(reader, 1):
        output_file = os.path.join(output_dir, f"split_{i}.csv")
        df_chunk.to_csv(output_file, index=False)
        print(f"Saved {len(df_chunk)} rows to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a large CSV file into smaller CSV files.")
    parser.add_argument("--input_csv", required=True, help="Path to the input CSV file")
    parser.add_argument("--output_dir", required=True, help="Directory to save the output CSV files")

    args = parser.parse_args()

    split_csv(args.input_csv, args.output_dir)
