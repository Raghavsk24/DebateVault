import os
import json
import re
from docx import Document


def get_paragraphs(docx_file):
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The file {docx_file} does not exist.")
    try:
        document = Document(docx_file)
        return [p.text.strip() for p in document.paragraphs if p.text.strip()]
    except Exception as e:
        raise RuntimeError(f"Error reading {docx_file}: {str(e)}")

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
    

def contains_url(text):
    url_pattern = re.compile(r'http[s]?://\S+')
    return url_pattern.search(text) is not None

def is_card_valid(paragraphs, index):
    if not (0 <= index - 1 < len(paragraphs) and 0 <= index + 1 < len(paragraphs)):
        return False
    if not contains_url(paragraphs[index]):
        return False
    j = index + 2
    while j < len(paragraphs) and not contains_url(paragraphs[j]):
        j += 1
    if j - 1 <= index + 1:
        return False
    return {
        "tagline": paragraphs[index - 1],
        "citation": paragraphs[index],
        "evidence": paragraphs[index + 1:j - 1]
    }

def extract_side(filepath):
    filename = os.path.basename(filepath).lower()
    if 'con' in filename or 'neg' in filename:
        return 'Neg'
    elif 'pro' in filename or 'aff' in filename:
        return 'Aff'
    else:
        print(f"Error: Side not found in filename '{filename}'")
        return None

def determine_topic(filename):
    tournament_Nov_Dec= ['minneapple', 'peach', 'badgerland', 'ucla', 'swing', 'glenbrooks', 'blue', 'digital']
    tournament_Sep_Oct = ['loyola', 'uk', 'grapevine', 'yale', 'georgetown', 'howe', 'nano', 'york', 'averill']

    for tournament in tournament_Nov_Dec:
        if tournament in filename:
            return 'Nov/Dec 24'

    for tournament in tournament_Sep_Oct:
        if tournament in filename:
            return 'Sep/Oct 24'

    return None

def cut_cards(paragraphs, styled_paragraphs, side, debate_type, topic):
    cards = []
    unique_cards = set()

    for i in range(len(paragraphs)):
        card_data = is_card_valid(paragraphs, i)
        if card_data:
            tagline = card_data["tagline"]
            citation = card_data["citation"]

            # Skip undefined topics, sides, or debate types
            if not all([side, debate_type, topic]):
                continue

            # Check for duplicates using tagline and citation
            card_identifier = (tagline, citation)
            if card_identifier in unique_cards:
                continue
            unique_cards.add(card_identifier)

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
                "debate_type": debate_type.upper(),
                "topic": topic
            })

    return cards

def process_batch(docx_files, category, debate_type):
    all_cards = []
    for docx_file in docx_files:
        try:
            print(f"Processing: {docx_file}")
            paragraphs = get_paragraphs(docx_file)
            if not paragraphs:
                print(f"Skipping empty file: {docx_file}")
                continue
            styled_paragraphs = get_styled_paragraphs(docx_file)
            side = extract_side(docx_file).capitalize()
            topic = determine_topic(docx_file.lower()).strip()
            cards = cut_cards(paragraphs, styled_paragraphs, side, debate_type, topic)
            all_cards.extend(cards)
            print(f"Valid cards in {docx_file}: {len(cards)}")
        except Exception as e:
            print(f"Error processing {docx_file}: {e}")
    return all_cards

def find_docx_files(root_folders):
    docx_files = []
    tournaments = ['minneapple', 'peach', 'badgerland', 'ucla', 'swing', 'glenbrooks', 'blue', 'digital',
                   'loyola', 'uk', 'grapevine', 'yale', 'georgetown', 'howe', 'nano', 'york', 'averill']
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

def main():
    root_folders = {
        "PF": [
            r'C:\Users\senth\Debate GPT\WikiDownloads\hspolicy24-all-2024-12-17'
        ]
    }

    for category, folders in root_folders.items():
        print(f"Processing category: {category}")
        docx_files = find_docx_files(folders)
        cards = process_batch(docx_files, category, debate_type=category)
        print(f"Processed {len(cards)} cards for category {category}.")
        output_file = r'C:\Users\senth\Debate GPT\cards\temp_cards.json'
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cards, f, ensure_ascii=False, indent=4)
        print(f"Cards saved to {output_file}")


    print("All files processed successfully.")

if __name__ == "__main__":
    main()
