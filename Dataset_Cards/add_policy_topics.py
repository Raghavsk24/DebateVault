import json

# Input and output JSON files
input_file = r'C:\Users\senth\DebateVault\Dataset_Cards\dataset_cards.json'  
output_file = r'C:\Users\senth\DebateVault\Dataset_Cards\ouptu1.json' 

# Read the JSON file 
try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Add a "topic" field if the event is "CX"
    for item in data:
        if 'event' in item and 'evidence_set' in item and item['event'] == 'CX':
            item['topic'] = str(item['evidence_set']) # Set topic field equal to evidence_set value

    # Write updated JSON data to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    print(f"Updated JSON data has been saved to {output_file}")
except UnicodeDecodeError as e:
    print(f"Error decoding the file: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON file: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
