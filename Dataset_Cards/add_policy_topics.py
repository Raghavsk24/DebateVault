import json
import ijson
from tqdm import tqdm

# Input and output JSON files
input_file = r'C:\Users\senth\DebateVault\Dataset_Cards\dataset_cards.json'  
output_file = r'C:\Users\senth\DebateVault\Dataset_Cards\dataset_cards1.json' 

# Read the JSON file using ijson for efficient streaming
try:
    updated_data = []
    
    # Count the total number of items for progress bar
    with open(input_file, 'r', encoding='utf-8') as file:
        total_items = sum(1 for _ in ijson.items(file, 'item'))

    with open(input_file, 'r', encoding='utf-8') as file:
        for item in tqdm(ijson.items(file, 'item'), total=total_items, desc="Processing items"):
            if 'event' in item and 'evidence_set' in item and item['event'] == 'CX':
                item['topic'] = str(item['evidence_set'])  # Set topic field equal to evidence_set value
            updated_data.append(item)

    # Write updated JSON data to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(updated_data, file, indent=4)

    print(f"Updated JSON data has been saved to {output_file}")
except UnicodeDecodeError as e:
    print(f"Error decoding the file: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON file: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
