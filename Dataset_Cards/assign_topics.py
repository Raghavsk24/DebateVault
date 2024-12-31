import json
import ijson
import os

# Define file paths
file_path = r'C:\Users\senth\DebateVault\Dataset_Cards\transformed_dataset_cards_TEMP2.json'
out_path = r'C:\Users\senth\DebateVault\Dataset_Cards\transformed_dataset_cards_TEMP3.json'

# List of tournament names to match
tournament_names = ['Emory', 'Blake', 'ASU', 'Samford', 'Peninsula', 'MBA',
                    'Barkley Forum', 'Harvard Westlake', 'Gonzaga', 'Pennsbury',
                    'Churchill', 'Barkley Forum for High Schools', 'John Edie Holiday Debates Hosted by The Blake School',
                    'Harvard Westlake Debates', 'Arizona State HDSHC Invitational', 'Peninsula Invitational', 'College Prep',
                    'Sunvite', 'Harvard-Westlake', 'Strake', 'Lexington Winter Invitational', 'emory', 'University of Houston Cougar Classic',
                    'Columbia', 'Westlake', 'University of Houston'
                    ]  


def process_large_json():
    new_topics_count = 0  # Track how many times we assign a new 'topic'

    try:
        with open(file_path, 'rb') as infile, open(out_path, 'w', encoding='utf-8') as outfile:
            # Start a valid JSON array in the output
            outfile.write('[\n')
            first_item = True

            # Stream each object from the top-level array
            for item in ijson.items(infile, 'item'):
                # Check if 'tournament' exists and matches any in tournament_names
                if 'tournament' in item and any(
                    t_name.lower() in item['tournament'].lower() 
                    for t_name in tournament_names
                ):
                    # If 'event' and 'evidence_set' exist, we may assign a 'topic'
                    if 'event' in item and 'evidence_set' in item:
                        event = item['event']
                        evidence_set = item['evidence_set']

                        if event == 'CX':
                            item['topic'] = str(evidence_set)
                            new_topics_count += 1
                        elif event == 'PF':
                            item['topic'] = 'Jan ' + str(evidence_set%2000)
                            new_topics_count += 1
                        elif event == 'LD':
                            item['topic'] = 'Jan/Feb ' + str(evidence_set%2000)
                            new_topics_count += 1
                        

                        # If a topic was assigned, remove the 'tournament' field
                        if 'topic' in item:
                            del item['tournament']

                # Write comma+newline before each item except the first
                if not first_item:
                    outfile.write(',\n')
                first_item = False

                # Dump the (possibly updated) item
                json.dump(item, outfile, ensure_ascii=False)

            # Close the JSON array in the output file
            outfile.write('\n]\n')

        print(f"Done! A new JSON file with updated items has been saved to: {out_path}")
        print(f"Number of new topics assigned: {new_topics_count}")

    except UnicodeDecodeError as e:
        print(f"Error decoding the file: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if os.path.exists(out_path):
            os.remove(out_path)  # Optionally remove incomplete file on error


if __name__ == '__main__':
    process_large_json()
