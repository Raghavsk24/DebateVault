import json

def update_event_in_json(file_path, old_topic, new_topic):
    # Load the JSON data
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Check that the data is a list
    if not isinstance(data, list):
        raise ValueError("The JSON data must be a list of objects.")
    
    # Update the event field
    updated_count = 0
    for card in data:
        if card.get('topic') == old_topic:
            card['topic'] = new_topic
            updated_count += 1
    
    # Save the updated JSON data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    print(f"Updated {updated_count} cards where event='{old_topic}' to event='{new_topic}'.")

# Parameters
file_path = r'C:\Users\senth\DebateVault\all_valid_cards.json'
old_topic = 'Jan/Feb 24'       
new_topic = 'Jan/Feb 25'            

# Run the function
update_event_in_json(file_path, old_topic, new_topic)
