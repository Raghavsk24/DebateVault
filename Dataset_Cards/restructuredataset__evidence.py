import ijson
import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging
from decimal import Decimal

# Define input and output file paths
input_file = r"C:\Users\senth\DebateVault\Dataset_Cards\valid_dataset_cards.json"
output_file = "filtered_dataset_cards.json"

# Setup Logging
logging.basicConfig(
    filename='process_large_json.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Remove specified tag from object
def remove_first_tag(soup, tag_name):
    tag = soup.find(tag_name)
    if tag:
        tag.decompose()
    return soup

# Remove all html tags
def strip_html_tags(text):
    return re.sub(r'<.*?>', '', text)

# Get first n words from text
def get_first_n_words(text, n=3):
    words = text.split()
    return ' '.join(words[:n]).lower() if len(words) >= n else ' '.join(words).lower()

# Recursively convert Decimal values to float
def convert_decimals(obj):
    if isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

# Processes card by removing tag and citation and returning cleaned_markup
def process_card(card):
    try:
        markup = card.get("markup", "")
        fulltext = card.get("fulltext", "").strip()

        # Check if markup or fulltext exist
        if not markup or not fulltext:
            logging.warning(f"Skipping card due to missing 'markup' or 'fulltext'. Card ID: {card.get('id', 'N/A')}")
            return None

        # Remove first <h4> and <p> tags
        soup = BeautifulSoup(markup, 'lxml')
        soup = remove_first_tag(soup, 'h4')
        soup = remove_first_tag(soup, 'p')

        cleaned_markup = str(soup)
        plain_text = strip_html_tags(cleaned_markup).strip()

        # Check if first 3 words in fulltext match with first three words in cleaned_markup text
        first_three_fulltext = get_first_n_words(fulltext, 3)
        first_three_plain = get_first_n_words(plain_text, 3)

        if first_three_fulltext != first_three_plain:
            logging.info(f"Skipping card due to mismatched first three words. Card ID: {card.get('id', 'N/A')}\nFirst three words in fulltext: {first_three_fulltext}\nFirst three words in plain text: {first_three_plain}")
            return None

        card["cleaned_markup"] = cleaned_markup
        return card

    except KeyError as e:
        logging.error(f"Skipping card due to missing key: {e}. Card: {card}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred while processing card. Card ID: {card.get('id', 'N/A')}. Error: {e}")
    return None

# JSON serializer to handle decimal type object
def custom_json_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def main():
    processed_count = 0
    skipped_count = 0
    max_cards = 200000

    try:
        print(f"Processing up to {max_cards} cards from '{input_file}'...")

        with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
            # Initialize ijson parser
            parser = ijson.items(f_in, 'item')  
            
            # Write the output JSON as an array
            f_out.write('[\n')
            first = True

            for card_index, card in enumerate(tqdm(parser, desc="Processing Cards")):
                if card_index >= max_cards:
                    logging.info(f"Reached the maximum limit of {max_cards} cards to process.")
                    break

                processed_card = process_card(card)
                if processed_card:
                    processed_card = convert_decimals(processed_card)  # Convert Decimal values
                    try:
                        if not first:
                            f_out.write(',\n')
                        f_out.write(json.dumps(processed_card, ensure_ascii=False, indent=4, default=custom_json_serializer))
                        processed_count += 1
                        first = False
                    except Exception as e:
                        logging.warning(f"Skipping card due to serialization error. Card ID: {processed_card.get('id', 'N/A')}. Error: {e}")
                        skipped_count += 1
                else:
                    skipped_count += 1

            f_out.write('\n]')
        
        print(f"\nProcessing complete. Processed {processed_count} cards, skipped {skipped_count} cards.")
        logging.info(f"Successfully processed {processed_count} cards, skipped {skipped_count} cards.")

    except FileNotFoundError:
        logging.error(f"Error: The file '{input_file}' was not found.")
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
