import os
from docx import Document
import re
import csv

# Define URL Pattern
url_pattern = re.compile(r'http[s]?://\S+')

# Get list of paragraphs from docx file
def get_paragraphs(docx_file):
    
    # Check if docx file exists
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The file {docx_file} does not exist.")
    
    # Get paragraph as every newline in docx file
    try:
        document = Document(docx_file)
        return [p.text.strip() for p in document.paragraphs if p.text.strip()]
    except Exception as e:
        raise RuntimeError(f"Error reading {docx_file}: {str(e)}")


# Get styled paragrpahs from docx file
def get_styled_paragraphs(docx_file):
    
    # Check docx file exists
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The file {docx_file} does not exist.")
    
    # Get paragraphs as every newline in docx file
    try:
        document = Document(docx_file)
        styled_paragraphs = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                styled_text = ""
                for run in paragraph.runs:
                    run_text = run.text
                    
                    # Bold 
                    if run.bold:
                        run_text = f"<b>{run_text}</b>"
                        
                    # Underline
                    if run.underline:
                        run_text = f"<u>{run_text}</u>"
                        
                    # Highlight
                    if run.font.highlight_color:
                        run_text = f"<mark>{run_text}</mark>"
    
                    styled_text += run_text
                styled_paragraphs.append(styled_text)
        return styled_paragraphs
    except Exception as e:
        raise RuntimeError(f"Error reading {docx_file}: {str(e)}")

# Check if paragraphs is a valid card
def is_card_valid(paragraphs, index):
    
    # Check paragrpah is in valid index
    if not (0 <= index - 1 < len(paragraphs) and 0 <= index + 1 < len(paragraphs)):
        return False

    # Check that citation paragraphs contains url
    if not url_pattern.search(paragraphs[index]):
        return False
    
    # Define evidence text to start after citation and go to next tagline
    j = index + 2
    while j < len(paragraphs) and not url_pattern.search(paragraphs[j]):
        j += 1
    if j - 1 <= index + 1: # Ensure evidence text is in valid index
        return False

    return {
        "tagline": paragraphs[index - 1], 
        "citation": paragraphs[index], 
        "evidence": paragraphs[index + 1:j - 1]
    }

# Extract side (Aff or Neg) from filename
def extract_side(filepath):
    
    # Get Filename
    filename = os.path.basename(filepath).lower()
    
    if 'aff' in filename:
        return 'Aff'
    elif 'neg' in filename:
        return 'Neg'
    else:
        return 'Error: Side not found'

# Extract cards from docx file
def cut_cards(paragraphs, styled_paragraphs, side, debate_type, topic):
    
    # Initalize empty list of cards
    cards = []
    
    # Extract tagline, citation and evidence and append to cards list
    for i in range(len(paragraphs)):
        card_data = is_card_valid(paragraphs, i)
        if card_data:
            tagline = card_data["tagline"]
            citation = card_data["citation"]
            evidence_text = " ".join(card_data["evidence"])
            styled_filtered_evidence = [
                styled_paragraphs[paragraphs.index(para)]
                for para in card_data["evidence"]
                if para in paragraphs
            ]
            cards.append([tagline, citation, " ".join(styled_filtered_evidence), side, debate_type, topic])
    return cards

# Count amount of docx files in OpenCaseList Download
def find_docx_files(root_folder):
    
    # Initalize empty list to hold docx files
    docx_files = []
    
    # List of tournament names
    tournaments = ['minneapple', 'peach', 'badgerland', 'ucla', 'swing', 'glenbrooks']
    
    # Search for files that end with '.docx' and append them to list
    for dirpath, _, filenames in os.walk(root_folder):
        for file in filenames:
            if file.endswith('.docx'):
                 if any(tournament in file.lower() for tournament in tournaments):
                        docx_files.append(os.path.join(dirpath, file))
    
    # Print amount of docx files in folder
    print(f"Found {len(docx_files)} .docx files in {root_folder}.")
    return docx_files

# Load extracted cards onto csv
def process_batch(docx_files, output_csv):
    
    # Initalize empty list to hold all cards
    all_cards = []
    
    # Extract cards and side from each file
    for docx_file in docx_files:
        try:
            print(f"Processing: {docx_file}")
            paragraphs = get_paragraphs(docx_file)
            if not paragraphs:
                print(f"Skipping empty file: {docx_file}")
                continue
            styled_paragraphs = get_styled_paragraphs(docx_file) 
            side = extract_side(docx_file) # Side
            cards = cut_cards(paragraphs, styled_paragraphs, side, 'LD', 'Nov/Dec 24')
            all_cards.extend(cards)
            print(f"Valid cards in {docx_file}: {len(cards)}")
        except Exception as e:
            print(f"Error processing {docx_file}: {e}")
            
    # Load extracted cards onto csv
    try:
        with open(output_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(all_cards)
    except Exception as e:
        print(f"Error writing to {output_csv}: {e}")

# Process cards by batch size of 100
def main(root_folder, output_csv, batch_size=100,):
    print("Searching for .docx files...")
    docx_files = find_docx_files(root_folder)
    if not docx_files:
        print("No .docx files found in the directory structure.")
        return

    
    # Check if the output file exists; if not, create it with headers
    if not os.path.exists(output_csv):
        with open(output_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Tagline', 'Citation', 'Evidence', 'Side', 'Debate_Type', 'Topic'])
    
    # Process files and append to the existing output CSV
    for i in range(0, len(docx_files), batch_size):
        batch = docx_files[i:i + batch_size]
        print(f"\nProcessing batch {i // batch_size + 1}/{(len(docx_files) - 1) // batch_size + 1}...")
        process_batch(batch, output_csv)
    print("All files processed successfully.")


root_folder = r'C:\Users\senth\Debate GPT\OpenCaseList Downloads'
output_csv = r'C:\Users\senth\Debate GPT\Cards\Raw_Cards.csv'

main(root_folder, output_csv)
