import os
import json
import re
import zipfile
import tempfile
from docx import Document

# Define Global Dictioanry of Tournaments
TOURNAMENTS= {
        "Sep/Oct 24":  ['Loyola-', 'Opener-', 'Grapevine-', 'Yale-',  'Georgetown-', 'Jack-Howe', 'Nano-', 'New-York-', 'Averill-', 'Mid-America-', 'Meadows-', 'Niles-', 'Trevian-', 'Westminster-', 'Greenhill-', 'Marist-', 'Nova-'], 
        "Nov/Dec 24": ['Minneapple-', 'longhorn-', 'Peach-', 'Michigan-', 'Badgerland-', 'ucla', 'Swing-', 'Glenbrooks-', 'Blue-', 'series-1', 'holiday-', 'costa-', 'Chung-', 'Bison-', 'Katy-Taylor', 'Princeton-', 'Paradigm-', 'Isidore-' ]
    }

# Extracts ZIP file to specific directory
def unzip_file(zip_path, extract_to):

    # Check if ZIP file exists in path
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"The file {zip_path} is not a valid ZIP archive.")
    
    # Extract contents of zipf
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)
    print(f"Extracted {zip_path} to {extract_to}")



# Get paragraphs from docx file
def get_paragraphs(docx_file):

    # Return exception if file not found
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The file {docx_file} does not exist.")
    try:

        # Return stripped paragraphs in array
        document = Document(docx_file)
        return [p.text.strip() for p in document.paragraphs if p.text.strip()]
    except Exception as e:
        raise RuntimeError(f"Error reading {docx_file}: {str(e)}")

# Get paragraphs with styling
def get_styled_paragraphs(docx_file):

    # Return exception if file not found
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The file {docx_file} does not exist.")
    try:
        document = Document(docx_file)
        styled_paragraphs = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                styled_text = ""
                for run in paragraph.runs:

                    # Bold Text
                    run_text = run.text
                    if run.bold:
                        run_text = f"<b>{run_text}</b>"

                        # Underlined Text
                    if run.underline:
                        run_text = f"<u>{run_text}</u>"

                        # Highlighted Text
                    if run.font.highlight_color:
                        run_text = f"<mark>{run_text}</mark>"
                    styled_text += run_text
                styled_paragraphs.append(styled_text)
        return styled_paragraphs
    except Exception as e:
        raise RuntimeError(f"Error reading {docx_file}: {str(e)}")
    
# Define url pattern
def contains_url(text):
    url_pattern = re.compile(r'http[s]?://\S+')
    return url_pattern.search(text) is not None

# Validate Card Structure
def is_card_valid(paragraphs, index):

    # Check that card is in valid index
    if not (0 <= index - 1 < len(paragraphs) and 0 <= index + 1 < len(paragraphs)):
        return False
    
    # Check that citation paragraph contains url 
    if not contains_url(paragraphs[index]):
        return False
    
    # Extract all paragrpahs after citation to next tagline and define it as evidence 
    j = index + 2
    while j < len(paragraphs) and not contains_url(paragraphs[j]):
        j += 1
    if j - 1 <= index + 1:
        return False
    
    # Retrurn tagline, citation and evidence
    return {
        "tagline": paragraphs[index - 1],
        "citation": paragraphs[index],
        "evidence": paragraphs[index + 1:j - 1]
    }

# Get side from filename
def extract_side(filepath):
    filename = os.path.basename(filepath).lower()
    if 'con' in filename or 'neg' in filename:
        return 'Neg'
    elif 'pro' in filename or 'aff' in filename:
        return 'Aff'
    else:
        print(f"Error: Side not found in filename '{filename}'")
        return None

# Determine topic based on tournament name
def determine_topic(filename):
    # Sep/Oct Topic
    for tournament in TOURNAMENTS["Sep/Oct 24"]:
        if tournament in filename.lower():
            return 'Sep/Oct 24'
   
    # Nov/Dec Topic
    for tournament in TOURNAMENTS["Nov/Dec 24"]:
        if tournament in filename.lower():
            return 'Nov/Dec 24'

    return None

# Cut cards
def cut_cards(paragraphs, styled_paragraphs, side, event, topic):
    cards = [] # Initalize card lsit
    unique_cards = set()
    evidence_set = 2024

    for i in range(len(paragraphs)):
        card_data = is_card_valid(paragraphs, i)
        if card_data:
            tagline = card_data["tagline"]
            citation = card_data["citation"]

            # Skip undefined topics, sides, or debate types
            if not all([side, event, topic]):
                continue

            styled_filtered_evidence = [
                styled_paragraphs[paragraphs.index(para)]
                for para in card_data["evidence"]
                if para in paragraphs
            ]

            cards.append({
                "tagline": tagline,
                "citation": citation,
                "evidence": styled_filtered_evidence,
                "side": side,
                "event": event.upper(),
                "topic": topic,
                "evidence_set": evidence_set
            })

    return cards

# Process Cards by Batch
def process_batch(docx_files, category, event):
    all_cards = [] # Initalize empty list of cards

    # Get paragraphs and styled_paragraphs from each docx file
    for docx_file in docx_files:
        try:
            print(f"Processing: {docx_file}")
            paragraphs = get_paragraphs(docx_file)
            if not paragraphs:
                print(f"Skipping empty file: {docx_file}")
                continue
            styled_paragraphs = get_styled_paragraphs(docx_file)

            # Check if side exists
            side = extract_side(docx_file)
            if side:
                side = side.capitalize() # Capitalize if side exists
            else:
                print(f"Warning: Side could not be determined for {docx_file}")
                continue  # Skip card if side does not exist
            
            # ONLY IF EVENT IF POLICY SET TOPIC TO 2024
            if category == "CX":
                topic = "2024"

            # Check if topic exists
            else:
                topic = determine_topic(docx_file.lower())
                if topic:
                    topic = topic.strip()  # Strip text
                else:
                    print(f"Warning: Topic could not be determined for {docx_file}")
                    continue  # Skip card if topic does not exist
            # Cut cards with side, event and topic
            cards = cut_cards(paragraphs, styled_paragraphs, side, event, topic)
            all_cards.extend(cards) # Append new card fields onto pre-existing tagline, citation and evidence field

            # Print amount of valid cards ine ach docx file
            print(f"Valid cards in {docx_file}: {len(cards)}")
        
        except Exception as e:
            print(f"Error processing {docx_file}: {e}")
    return all_cards

def find_docx_files(root_folders):
    docx_files = [] # Initalize empty list of docx_files
    all_tournaments = sum(TOURNAMENTS.values(), []) # all_tournaments in dict TOURNAMENTS
    for root_folder in root_folders:

        # Check if file exists in directory
        if not os.path.exists(root_folder):
            print(f"Error: Folder not found - {root_folder}")
            continue # Skip file if directory not found

        # Append all docx files onto list docx_files
        for dirpath, _, filenames in os.walk(root_folder):
            for file in filenames:
                if file.endswith('.docx') and any(tournament in file.lower() for tournament in all_tournaments):
                    docx_files.append(os.path.join(dirpath, file))

                    # Print total number of files found
    print(f"Found {len(docx_files)} .docx files across all folders.")
    return docx_files

def main():

    # Path to folder(s)
    root_folders = {
        "CX": [
            r'C:\Users\senth\DebateVault\hspolicy24-all-2024-12-24.zip'
        ]
    }

    for category, folders in root_folders.items():
        print(f"Processing category: {category}")  # Print file being processed
        
        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            for folder in folders:
                if folder.lower().endswith('.zip'):
                    try:
                        unzip_file(folder, temp_dir)
                    except Exception as e:
                        print(f"Error extracting {folder}: {e}")
                        continue
                else:
                    # If not a ZIP file, assume it's a directory
                    temp_dir = folder 

            # Search for .docx files within extraqcted files
            docx_files = find_docx_files([temp_dir])
            cards = process_batch(docx_files, category, event=category)
            print(f"Processed {len(cards)} cards for category {category}.")  # Print number of cards found
            
            output_file = 'raw_policy_cards.json' # OUTPUT FILE PATH
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(cards, f, ensure_ascii=False, indent=4)
            print(f"Cards saved to {output_file}")  # Confirm  if card has been added onto output_file

    print("All files processed successfully.")

if __name__ == "__main__":
    main()
