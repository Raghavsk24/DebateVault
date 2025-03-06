import pandas as pd
import argparse
import os

def split_csv(input_csv, output_dir):
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Calculate the number of rows per split
    chunk_size = len(df) // 5  # Integer division
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Split and save the files
    for i in range(5):
        start_idx = i * chunk_size
        end_idx = None if i == 4 else (i + 1) * chunk_size  # Last file takes all remaining rows
        
        df_chunk = df.iloc[start_idx:end_idx]
        output_file = os.path.join(output_dir, f"split_{i+1}.csv")
        df_chunk.to_csv(output_file, index=False)
        
        print(f"Saved {len(df_chunk)} rows to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a CSV file into 5 smaller CSV files.")
    parser.add_argument("--input_csv", required=True, help="Path to the input CSV file")
    parser.add_argument("--output_dir", required=True, help="Directory to save the output CSV files")
    
    args = parser.parse_args()
    
    split_csv(args.input_csv, args.output_dir)
