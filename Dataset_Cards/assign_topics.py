import json

# Input and output JSON files
input_file = r'C:\Users\senth\DebateVault\Dataset_Cards\dataset_cards.json'
output_file = r'C:\Users\senth\DebateVault\Dataset_Cards\dataset_cards_topics1.json'

# List of tournament names to match
tournament_names = [
    'Grapevine', 'Greenhill Fall Classic', 'National Speech and Debate Season Opener', 'Trevian',
    'Jack Howe Memorial', 'Loyola', 'UK Season Opener', 'Marist Ivy Street Invitational',
    'New York City Invitational Debate And Speech Tournament', 'Yale University Invitational',
    'Washburn Rural', 'Greenhill RR', 'New Trier Season Opener', 'Niles Township Invitational',
    'University of Kentucky Season Opener', 'Jack Howe Memorial Invitational 2022',
    '2 - Georgetown Day School', '3 - Yale University Invitational', 'A - Greenhill',
    'SO - Greenhill', 'Loyola Invitational', 'Kentucky season opener', '02 -- Greenhill Fall Classic',
    '02 - Greenhill', '02---Greenhill', 'TREVIAN INVITATIONAL', '03 - New York City Invitational Debate and Speech Tournament',
    '03 - New York City Invitational', '01---Niles', '01 - Washburn Rural', '01 - Grapevine',
    '1 - Greenhill', '1 - Niles', '1 - Grapevine Classic', '2.Trevian Invitational', '2 - Greenhill',
    '3 - Trevian', 'greenhill rr', 'YALE UNIVERSITY INVITATIONAL', 'grapevine', 'Jack Howe',
    'Jack Howe Aff', 'Jacke Howe', 'Greenhill Round Robin', 'Jack HoweLong Beach',
    'Trevian Invitational', 'Yale Invitational', 'Grapevine Classic', 'New York City Invitational',
    'Yale University Invitational 2021', 'Marist', 'New York City Invitational Debate and Speech Tournament',
    'Jack Howe Memorial Invitational 2022', 'Greenhill Fall Classic RR', 'National Speech and Debate Season Opener',
    'New Trier Season Opener', 'Uk opener 2021', 'Loyola Invitational', 'Greenhill Fall Classic',
    'Grapevine', 'Greenhill'
]

# Read the JSON file with UTF-8 encoding
try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Add a "topic" field based on the event type
    for item in data:
        if 'event' in item and 'evidence_set' in item:
            evidence_set = item['evidence_set']
            event = item['event']
            if event == 'PF':
                item['topic'] = "Sep/Oct " + str(evidence_set%2000) # PF Topic
            elif event == 'LD':
                item['topic'] = "Sep/Oct " + str(evidence_set%2000) # LD Topic

        # Check if tournament field exists
        if 'tournament' in item and any(tournament_name.lower() in item['tournament'].lower() for tournament_name in tournament_names):
            item['matching_tournament'] = True
        else:
            item['matching_tournament'] = False

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
