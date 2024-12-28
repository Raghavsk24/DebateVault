import json
import re
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

# Validates single card based on criteria
def validate_card(card):
    # Define url pattern
        url_pattern = re.compile(r'https?://\S+')

        # Validate tagline
        tagline = card.get('tag', "")
        tagline_word_count = len(tagline.split())
        if not (4 <= tagline_word_count <= 150): # Checks that tagline is between 4 and 150 words
            return False

        # Validate citation
        citation = card.get('fullcite', "")
        citation_word_count = len(citation.split())
        if not url_pattern.search(citation): # Checks that url is in citation
            return False
        if not (7 < citation_word_count < 200):  # Check citation is between 7 and 200 words
            return False


        # Validate evidence
        evidence = card.get('fulltext', '')
        evidence_word_count = len(evidence.split())
        if not (20 < evidence_word_count <= 4000): # Checks that evidence has between 20 and 4000 words
            return False
        if url_pattern.search(evidence): # Checks that url is not in evidence
            return False
        return True

def main():
    input_file = r'C:\Users\senth\DebateVault\dataset_cards.jsonl'  #
    output_file = r'valid_dataset_cards.json'  

    try:

        # Checks if input file exists and is not empty
        if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
            print(f"Error: Input file '{input_file}' does not exist or is empty.")
            return

        print(f"Processing file: {input_file}")
        file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
        print(f"File size: {file_size_mb:.2f} MB")

        # Open input and output files
        with open(input_file, 'r', encoding='utf-8') as f_in, \
             open(output_file, 'w', encoding='utf-8') as f_out:

            # Initialize tqdm progress bar
            pbar = tqdm(f_in, desc="Processing Cards", unit="card")

            # Write the beginning of the JSON array
            f_out.write('[\n')

            first_item = True  # Flag to handle commas between items

            # Get each line in jsonl file
            for line in pbar:
                line = line.strip()
                if not line:
                    continue  

                try:
                    card = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError: {e} - Skipping line.")
                    continue  # Skip invalid JSON lines

                if validate_card(card):
                    card_json = json.dumps(card, ensure_ascii=False)

                    if not first_item:
                        # Add a comma before the next item
                        f_out.write(',\n')
                    else:
                        first_item = False  # First valid item handled

                    # Write the card JSON
                    f_out.write(card_json)

            # Write the end of the JSON array
            f_out.write('\n]')

        print(f"\nProcessing complete. Validated cards saved to '{output_file}'.")

    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
