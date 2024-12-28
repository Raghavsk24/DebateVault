import json
import orjson
from tqdm import tqdm

# Define input and output file paths
input_file = r'C:\Users\senth\DebateVault\dataset_cards.jsonl'  
output_file = r'C:\Users\senth\DebateVault\Dataset_Cards\first_100_dataset_cards.jsonl'  

# Define the number of cards to extract
NUM_CARDS = 100

# Get first 100 objects form jsonl file
def extract_first_n_cards(jsonl_path, n):
    extracted_cards = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f_in:
            for _ in tqdm(range(n), desc="Extracting Cards"):
                line = f_in.readline()
                if not line:
                    break  # End of file reached before extracting n cards
                try:
                    card = orjson.loads(line) # Load JSON object
                    extracted_cards.append(card) # Append the card onto extracted_cards list
                except orjson.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line. Error: {e}")
    except FileNotFoundError:
        print(f"Error: The file '{jsonl_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred while extracting cards: {e}")
    
    return extracted_cards

# Write list of first 100 JSON objects to jsonl file
def write_jsonl(cards, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for card in cards:
                try:
                    f_out.write(orjson.dumps(card).decode('utf-8') + '\n')
                except Exception as e:
                    print(f"Warning: Skipping card due to serialization error. Error: {e}")
        print(f"Successfully wrote {len(cards)} cards to '{output_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred while writing to the output file: {e}")


def main():
    # Extract the first 100 cards from the JSONL input file
    print(f"Starting extraction of the first {NUM_CARDS} cards from '{input_file}'...")
    first_n_cards = extract_first_n_cards(input_file, NUM_CARDS)
    
    if not first_n_cards:
        print("No cards were extracted. Please check the input file.")
        return
    
    # Write the extracted cards to the output JSONL file
    print(f"Writing the extracted cards to '{output_file}'...")
    write_jsonl(first_n_cards, output_file)
    
    print(f"\nProcessing complete. Extracted {len(first_n_cards)} cards to '{output_file}'.")

if __name__ == "__main__":
    main()
