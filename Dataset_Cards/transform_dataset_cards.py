import ijson
import json
from tqdm import tqdm


# Define input and output file paths
input_file = r"C:\Users\senth\DebateVault\filtered_dataset_cards.json"
output_file = r"C:\Users\senth\DebateVault\Dataset_Cards\transformed_dataset_cards.json"

# Transfrom card based on rules
def transform_card(card):

    # Exclude cards with any null fields
    if any(value is None for value in card.values()):
        return None

    transformed = {}  # Initalize set to hold transformed cards

    # Capitalize 'event' field
    if 'event' in card:
        transformed['event'] = card['event'].upper()

    # Convert 'year' to 'evidence_set' as int
    if 'year' in card:
        transformed['evidence_set'] = int(card['year'])

    # Rename 'tag' to 'tagline'
    if 'tag' in card:
        transformed['tagline'] = card['tag']

    # Rename 'fullcite' to 'citation'
    if 'fullcite' in card:
        transformed['citation'] = card['fullcite']

    # Rename 'cleaned_markup' to 'evidence'
    if 'cleaned_markup' in card:
        transformed['evidence'] = card['cleaned_markup']

    # Change 'side' value
    if 'side' in card:
        if card['side'] == 'A':
            transformed['side'] = 'Aff'
        elif card['side'] == 'N':
            transformed['side'] = 'Neg'

    # Copy remaining fields that don't require transformation
    for key in card:
        if key not in {'event', 'year', 'tag', 'fullcite', 'markup', 'cleaned_markup', 'side', 'level', 'fulltext'}: # Omit markup, level and fulltext
            transformed[key] = card[key]

    return transformed

def main():
    # Initalize counters
    processed_count = 0
    skipped_count = 0

    try:
        print(f"Reading cards from '{input_file}'...")

        with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
            # Initialize ijson parser
            parser = ijson.items(f_in, 'item')

            # Write the output JSON as an array
            f_out.write('[\n')
            first = True

            print("Transforming cards...")
            for card in tqdm(parser, desc="Transforming Cards"):
                transformed_card = transform_card(card)
                if transformed_card:  # Only add valid cards
                    if not first:
                        f_out.write(',\n')
                    f_out.write(json.dumps(transformed_card, ensure_ascii=False, indent=4))
                    processed_count += 1
                    first = False
                else:
                    skipped_count += 1

            f_out.write('\n]')

        print(f"Processing complete. Processed {processed_count} cards, skipped {skipped_count} cards.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
