import pandas as pd
import ast
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup

tqdm.pandas()

# Converts string array of evidence into one string
def flatten_evidence(evidence):
    if isinstance(evidence, str):
        try:
            parsed = ast.literal_eval(evidence)
            if isinstance(parsed, list):
                return " ".join(parsed)
        except (SyntaxError, ValueError):
            pass
    return evidence

def extract_marked_text(df):
    for index, row in df.iterrows():
        soup = BeautifulSoup(row['evidence'], 'html.parser')
        # Find all <mark> tags and extract their text
        mark_tags = soup.find_all('mark')
        extracted_text = ' '.join([tag.get_text() for tag in mark_tags])
        df.loc[index, 'marked_evidence'] = extracted_text
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV files with evidence and filtering operations.")
    parser.add_argument("--input_csv", required=True, help="Path to the input CSV file")
    parser.add_argument("--output_csv", required=True, help="Path to the output CSV file")
    args = parser.parse_args()

    input_csv = args.input_csv
    output_csv = args.output_csv

    # 1) Read CSV
    df = pd.read_csv(input_csv)

    # 2) Flatten 'evidence' column
    if "evidence" in df.columns:
        df["evidence"] = df["evidence"].progress_apply(flatten_evidence)

    # 3) Create marked_evidence column
    df = extract_marked_text(df)

    # 4) Calculate word counts for each main field

    # Tagline
    if "tagline" in df.columns:
        df["tagline_count"] = df["tagline"].astype(str).progress_apply(lambda x: len(x.split()))
    else:
        print("'tagline' column does not exist in Dataframe")
    
    # Citation
    if "citation" in df.columns:
        df["citation_count"] = df["citation"].astype(str).progress_apply(lambda x: len(x.split()))
    else:
        print("'citation' column does not exist in Dataframe")

    # Evidence
    if "evidence" in df.columns:
        df["evidence_count"] = df["evidence"].astype(str).progress_apply(lambda x: len(x.split()))
    else:
        print("'evidence' column does not exist in Dataframe")
    
    # Marked Evidence
    if "marked_evidence" in df.columns:
        df["marked_evidence_count"] = df["marked_evidence"].astype(str).progress_apply(lambda x: len(x.split()))
    else:
        print("'marked_evidence' column does not exist in Dataframe")

    # 5) Filtering 

    # Drop rows where tagline contains http
    if "tagline" in df.columns:
        df = df[~df["tagline"].str.contains("http", na=False)]

    # Drop rows where evidence contains http
    if "evidence" in df.columns:
        df = df[~df["evidence"].str.contains("http", na=False)]

    # Keep taglines with tagline count between 5 and 29 
    df = df[df["tagline_count"].between(5, 29)]

    # Keep citations with citation count between 19 and 84 
    df = df[df["citation_count"].between(19, 84)]

    # Keep evidence with evidence count between 200 and 2701 
    df = df[df["evidence_count"].between(200, 2701)]

    # Keep marked_evidence with marked evidence count between 15 and 150
    df = df[df["marked_evidence_count"].between(15, 150)]

    # 6) Reset index
    df.reset_index(drop=True, inplace=True)

    # 7) Count duplicates by tagline and drop duplicates
    if "tagline" in df.columns:
        tagline_counts = df["tagline"].value_counts()
        df["duplicate_count"] = df["tagline"].map(tagline_counts)
        df = df.drop_duplicates(subset=["tagline"], keep="last")

    # 8) Drop unnecessary columns
    drop_cols = ['Unnamed: 0', 'tagline_count', 'citation_count', 'evidence_count', 'marked_evidence_count']
    df.drop([col for col in drop_cols if col in df.columns], axis=1, inplace=True)
    print(df.columns.tolist())

    # 9) Drop all rows with null values and reset index
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Output summary
    print(f'Final rows after filtering: {len(df)}')

    # 10) Write filtered CSV
    df.to_csv(output_csv, index=False)
    print(f'Filtered CSV saved to: {output_csv}')
