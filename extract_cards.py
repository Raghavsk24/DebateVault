import os
from docx import Document
import re
import csv

# Define URL Pattern
url_pattern = re.compile(r'http[s]?://\S+')

# Get list of paragraphs from docx file
def get_paragraphs(docx_file):
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The file {docx_file} does not exist.")
    try:
        document = Document(docx_file)
        return [p.text.strip() for p in document.paragraphs if p.text.strip()]
    except Exception as e:
        raise RuntimeError(f"Error reading {docx_file}: {str(e)}")

# Get styled paragraphs from docx file
def get_styled_paragraphs(docx_file):
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The file {docx_file} does not exist.")
    try:
        document = Document(docx_file)
        styled_paragraphs = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                styled_text = ""
                for run in paragraph.runs:
                    run_text = run.text
                    if run.bold:
                        run_text = f"<b>{run_text}</b>"
                    if run.underline:
                        run_text = f"<u>{run_text}</u>"
                    if run.font.highlight_color:
                        run_text = f"<mark>{run_text}</mark>"
                    styled_text += run_text
                styled_paragraphs.append(styled_text)
        return styled_paragraphs
    except Exception as e:
        raise RuntimeError(f"Error reading {docx_file}: {str(e)}")

# Check if paragraphs is a valid card
def is_card_valid(paragraphs, index):
    if not (0 <= index - 1 < len(paragraphs) and 0 <= index + 1 < len(paragraphs)):
        return False
    if not url_pattern.search(paragraphs[index]):
        return False
    j = index + 2
    while j < len(paragraphs) and not url_pattern.search(paragraphs[j]):
        j += 1
    if j - 1 <= index + 1:
        return False
    return {
        "tagline": paragraphs[index - 1],
        "citation": paragraphs[index],
        "evidence": paragraphs[index + 1:j - 1]
    }

def extract_side(filepath):
    """
    Extracts the side (Aff or Neg) from the filename based on patterns like 'Pro' or 'Con'.
    """
    filename = os.path.basename(filepath).lower()

    # Check for 'pro' or 'con' in the filename
    if 'con' in filename:
        return 'Neg'
    elif 'pro' in filename:
        return 'Aff'
    else:
        print(f"Error: Side not found in filename '{filename}'")
        return 'Error: Side not found'


# Extract cards from docx file
def cut_cards(paragraphs, styled_paragraphs, side, debate_type, topic):
    cards = []
    for i in range(len(paragraphs)):
        card_data = is_card_valid(paragraphs, i)
        if card_data:
            tagline = card_data["tagline"]
            citation = card_data["citation"]
            styled_filtered_evidence = [
                styled_paragraphs[paragraphs.index(para)]
                for para in card_data["evidence"]
                if para in paragraphs
            ]
            cards.append([tagline, citation, " ".join(styled_filtered_evidence), side, debate_type, topic])
    return cards

# Find docx files
def find_docx_files(root_folders):
    docx_files = []
    tournaments = ['minneapple', 'peach', 'badgerland', 'ucla', 'swing', 'glenbrooks', 'blue']
    for root_folder in root_folders:
        if not os.path.exists(root_folder):
            print(f"Error: Folder not found - {root_folder}")
            continue
        for dirpath, _, filenames in os.walk(root_folder):
            for file in filenames:
                if file.endswith('.docx') and any(tournament in file.lower() for tournament in tournaments):
                    docx_files.append(os.path.join(dirpath, file))
    print(f"Found {len(docx_files)} .docx files across all folders.")
    return docx_files

# Process batch of docx files
def process_batch(docx_files, output_csv):
    all_cards = []
    for docx_file in docx_files:
        try:
            print(f"Processing: {docx_file}")
            paragraphs = get_paragraphs(docx_file)
            if not paragraphs:
                print(f"Skipping empty file: {docx_file}")
                continue
            styled_paragraphs = get_styled_paragraphs(docx_file)
            side = extract_side(docx_file)
            cards = cut_cards(paragraphs, styled_paragraphs, side, 'PF', 'Nov/Dec 24')
            all_cards.extend(cards)
            print(f"Valid cards in {docx_file}: {len(cards)}")
        except Exception as e:
            print(f"Error processing {docx_file}: {e}")
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Tagline', 'Citation', 'Evidence', 'Side', 'Debate_Type', 'Topic'])
            writer.writerows(all_cards)
    except Exception as e:
        print(f"Error writing to {output_csv}: {e}")

# Main function
def main(root_folders, output_csv, batch_size=100):
    print("Searching for .docx files...")
    docx_files = find_docx_files(root_folders)
    if not docx_files:
        print("No .docx files found in the specified directories.")
        return
    for i in range(0, len(docx_files), batch_size):
        batch = docx_files[i:i + batch_size]
        print(f"\nProcessing batch {i // batch_size + 1}/{(len(docx_files) - 1) // batch_size + 1}...")
        process_batch(batch, output_csv)
    print("All files processed successfully.")

# File paths
root_folders = [
    r'C:\Users\senth\Debate GPT\OpenCaseList Downloads1',
    r'C:\Users\senth\Debate GPT\OpenCaseList Downloads2',
    r'C:\Users\senth\Debate GPT\OpenCaseList Downloads3',
    r'C:\Users\senth\Debate GPT\OpenCaseList Downloads4'
]
output_csv = r'C:\Users\senth\Debate GPT\Cards\Raw_Cards.csv'

main(root_folders, output_csv)
