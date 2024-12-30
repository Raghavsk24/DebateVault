import json

# Input JSON file and output text file
input_file = r'C:\Users\senth\DebateVault\Dataset_Cards\transformed_dataset_cards.json'  
output_file = 'C:\Users\senth\DebateVault\Dataset_Cards\matching_tournaments.txt'

# tournaments to search for
keywords = ['loyola', 'niles', 'opener', 'grapevine', 'washburn', 'greenhill', 'yale', 'georgetown', 'marist', 'howe', 'nova', 'delores', 'tennent', 'york', 'trevian', 'averill']

# Read the JSON file 
try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract matching tournaments
    matching_tournaments = [
        item['tournament'] for item in data
        if any(keyword.lower() in item['tournament'].lower() for keyword in keywords)
    ]

    # Write matching tournaments to a text file
    with open(output_file, 'w', encoding='utf-8') as file:
        for tournament in matching_tournaments:
            file.write(tournament + '\n')

    print(f"Matching tournaments have been written to {output_file}")
except UnicodeDecodeError as e:
    print(f"Error decoding the file: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON file: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
