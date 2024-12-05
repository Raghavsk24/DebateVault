import os
import re
import pandas as pd

# File paths
input_csv = r'C:\Users\senth\Debate GPT\Cards\Raw_Cards.csv'
output_csv = r'C:\Users\senth\Debate GPT\Cards\Valid_Card.csv'

# Load the raw cards CSV into a DataFrame
df = pd.read_csv(input_csv)

# Define URL pattern
url_pattern = re.compile(r'http[s]?://\S+')

# Define list of debate jargon
debate_terms = ['AC', 'NC', 'aff', 'plan', 'Plan', 'Counter Plan', 'counter-plan', 'counterplan', 'CP', 'OFF', 
                'framework', 'Framework', 'contention', 'Contention', 'C1', 'C2', 'C3', 'C4', 'C5']

# Define date pattern
date_patterns = [
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),  # MM/DD/YYYY
    re.compile(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b"),  # YYYY-MM-DD
    re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s\d{1,2},?\s\d{4}\b"),  # Month DD, YYYY
    re.compile(r"\b\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b")  # DD Month YYYY
]

# Validate each card
def is_row_valid(row):
    try:
        
        # Check that tagline is less than 50 words and greater than 6 words
        tagline = str(row['Tagline'])
        if not (6 <= len(tagline.split()) <= 50):
            return False

        # Validate Citation
        citation = str(row['Citation'])
        if not url_pattern.search(citation): # Check that citation has url
            return False
        if len(citation.split()) >= 150: # Check that citation is less than 150 words
            return False
        if any(term in citation for term in debate_terms): # Check that citation doesn't have any debate terms
            return False

        # Validate evidence
        evidence = str(row['Evidence'])
        if len(evidence.split()) <= 20: # Check that evidence text is greater than 20 words
            return False
        if url_pattern.search(evidence): # Check that URL is not in evidence text
            return False
        if any(term in evidence for term in debate_terms): # Check that evidence text doesn't have any debate terms
            return False

        # Validate side
        side = str(row['Side'])
        if side not in ['Aff', 'Neg']:
            return False

        return True

    except Exception as e:
        print(f"Error validating row: {e}")
        return False

# Remove duplicated rows and keep first if taglines are the same
def remove_duplicates(df):
    return df.drop_duplicates(subset=['Tagline'], keep='first')

# Rename topic column values
def rename_topic_column(df):
    df['Topic'] = df['Topic'].replace('Wealth Tax', 'Nov/Dec 24')
    return df

def main():
    # Validate rows
    valid_rows = df[df.apply(is_row_valid, axis=1)]
    valid_rows = remove_duplicates(valid_rows)
    valid_rows = rename_topic_column(valid_rows)

    # Check if the output CSV exists
    file_exists = os.path.exists(output_csv)

    # Write or append to the output CSV
    valid_rows.to_csv(
        output_csv,
        mode='a' if file_exists else 'w',  # Append if file exists, write otherwise
        header=not file_exists,           # Write headers only if creating a new file
        columns=['Tagline', 'Citation', 'Evidence', 'Side', 'Debate_Type', 'Topic'],
        index=False,
        encoding='utf-8'
    )
    print(f"Validated and appended data to '{output_csv}'.")
    print(f"Final valid rows appended: {len(valid_rows)}")

if __name__ == "__main__":
    main()
