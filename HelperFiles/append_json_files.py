import json
import os
import sys

# Load json file
def load_json(file_path):

    # Check if json file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Error: JSON data in '{file_path}' is not a list.") # Check if json has array structure
                sys.exit(1)
            return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
        sys.exit(1)

# Save json data to output file path
def save_json(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Combined JSON data saved to '{file_path}'.")
    except Exception as e:
        print(f"Error saving JSON to '{file_path}': {e}")
        sys.exit(1)

# Combine multiple input json file sinto one output file
def combine_json_files(input_files, output_file):
    combined_data = []
    for file in input_files:
        print(f"Loading data from '{file}'...")
        data = load_json(file)
        combined_data.extend(data)
        print(f"Loaded {len(data)} cards from '{file}'.")
    
    print(f"Total cards: {len(combined_data)}")
    save_json(combined_data, output_file)

def main():
    # Define input JSON file paths
    input_files = [
        r'C:\Users\senth\DebateVault\valid_CX_cards2.json',
        r'C:\Users\senth\DebateVault\valid_LD_cards2.json',
        r'C:\Users\senth\DebateVault\valid_PF_cards2.json'
    ]
    
    # Define output JSON file path
    output_file = r'C:\Users\senth\DebateVault\all_valid_cards.json'
    
    combine_json_files(input_files, output_file)

if __name__ == "__main__":
    main()
