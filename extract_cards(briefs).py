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

# Check if paragraphs form a valid card
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

# Extract cards from docx file
def cut_cards(paragraphs, styled_paragraphs, side, debate_type, topic):
    cards = []
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

# Process a single docx file
def process_file(docx_file, output_csv, debate_type='LD', topic='Nov/Dec 24'):
    try:
        print(f"Processing: {docx_file}")
        paragraphs = get_paragraphs(docx_file)
        if not paragraphs:
            print(f"Skipping empty file: {docx_file}")
            return
        styled_paragraphs = get_styled_paragraphs(docx_file)
        cards = cut_cards(paragraphs, styled_paragraphs, 'NEG', debate_type, topic)
        print(f"Valid cards in {docx_file}: {len(cards)}")
        with open(output_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(cards)
    except Exception as e:
        print(f"Error processing {docx_file}: {e}")

# Main function to process individual files
def main(file_paths, output_csv):
    print("Processing files...")
    if not os.path.exists(output_csv):
        with open(output_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Tagline', 'Citation', 'Evidence', 'Side', 'Debate_Type', 'Topic'])
    for docx_file in file_paths:
        process_file(docx_file, output_csv)
    print("All files processed successfully.")

# Example usage
file_paths = [
    r'your_input_path'  
]
output_csv = r'C:\Users\senth\Debate GPT\Cards\Raw_Cards.csv'

main(file_paths, output_csv)
