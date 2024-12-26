import os
import json
import re
import zipfile
import tempfile
from docx import Document
from tqdm import tqdm
import logging

# Define TOURNAMENTS Dictionary
TOURNAMENTS = {
    "Sep/Oct 24": [
        'loyola-', 'opener-', 'grapevine-', 'yale-', 'georgetown-day',
        'jack-howe', 'nano-nagle', 'new-york', 'tim-averill', 'mid-america-',
        'meadows-', 'niles-', 'trevian-', 'westminster-', 'greenhill-',
        'marist-', 'nova-'
    ],
    "Nov/Dec 24": [
        'minneapple-', 'longhorn-', 'peach-', 'michigan-', 'badgerland-',
        'ucla-', 'swing-', 'glenbrooks-', 'blue', 'series-1-',
        'holiday-classic-', 'costa-', 'chung-', 'bison-', 'katy-taylor-',
        'princeton-', 'paradigm-', 'isidore-'
    ],
    "Jan/Feb 24": [
        'john-', 'strake-'
    ]
}

# Precompile the URL regex pattern for efficiency
URL_PATTERN = re.compile(r'http[s]?://\S+')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Extract ZIP File to specified directory
def unzip_file(zip_path, extract_to):

    # Log Error if ZIP File does not exist
    if not zipfile.is_zipfile(zip_path):
        logger.error(f"The file {zip_path} is not a valid ZIP archive.")
        return
    
    # Extract zipf contents
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)
    logger.info(f"Extracted {zip_path} to {extract_to}")


# Extract stripped paragraphs from .docx file
def get_paragraphs(docx_file):

    # Check if file exists
    if not os.path.exists(docx_file):
        logger.error(f"The file {docx_file} does not exist.")
        return []
    try:
        document = Document(docx_file)
        return [p.text.strip() for p in document.paragraphs if p.text.strip()] # Return stripped paragraphs in file in an array
    except Exception as e:
        logger.error(f"Error reading {docx_file}: {e}")
        return []

# Extract paragraphs with styling (bold, underline, highlight) from .docx file
def get_styled_paragraphs(docx_file):
    """
    Extracts paragraphs with styling (bold, underline, highlight) from a .docx file.
    """
    if not os.path.exists(docx_file):
        logger.error(f"The file {docx_file} does not exist.")
        return []
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
        logger.error(f"Error reading {docx_file}: {e}")
        return []

# Check if text contains url
def contains_url(text):
    return URL_PATTERN.search(text) is not None

# Validate Card Structure
def is_card_valid(paragraphs, index):

    # Check that card is in valid indicie
    if not (0 <= index - 1 < len(paragraphs) and 0 <= index + 1 < len(paragraphs)):
        return False
    
    # Check that citation paragraph contains url
    if not contains_url(paragraphs[index]):
        return False
    
    # Extract evidence paragraphs
    j = index + 2
    while j < len(paragraphs) and not contains_url(paragraphs[j]):
        j += 1
    if j - 1 <= index + 1:
        return False
    
    # Return tagline, citation and evidence
    return {
        "tagline": paragraphs[index - 1],
        "citation": paragraphs[index],
        "evidence": paragraphs[index + 1:j - 1]
    }

# Determine side from filename
def extract_side(filepath):
    filename = os.path.basename(filepath).lower()
    if 'con' in filename or 'neg' in filename:
        return 'Neg'
    elif 'pro' in filename or 'aff' in filename:
        return 'Aff'
    else:
        logger.warning(f"Side not found in filename '{filename}'")
        return None

# Determine topic from tournament
def determine_topic(filename):
    filename = filename.lower()
    for topic, tournaments in TOURNAMENTS.items():
        for tournament in tournaments:
            if tournament in filename:
                logger.info(f"Matched {tournament} in {filename} -> {topic}")
                return topic
    logger.warning(f"No topic match for {filename}")
    return None

# Extract valid cards from paragraphs
def cut_cards(paragraphs, styled_paragraphs, side, event, topic):
    cards = []
    evidence_set = 2024 # Set evidence to 2024
    
    # Get tagline, citation and evidence lists
    for i in range(1, len(paragraphs) - 1):
        card_data = is_card_valid(paragraphs, i)
        if card_data:
            tagline = card_data["tagline"]
            citation = card_data["citation"]
            evidence_paragraphs = card_data["evidence"]
            

            if not all([side, event, topic]):
                continue  # Skip if any essential field is missing
            
            # map evidence paragraphs to styled paragraphs
            evidence_indices = range(i + 1, i + 1 + len(evidence_paragraphs))
            styled_filtered_evidence = [
                styled_paragraphs[j]
                for j in evidence_indices
                if j < len(styled_paragraphs)
            ]
            
            # Append fields to card
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

# Find all files within directory
def find_docx_files(root_folders):
    docx_files = [] # Initalize empty list 
    all_tournaments = set(sum(TOURNAMENTS.values(), []))  # Get all tournaments from global TOURNAMENTS dictionary

    # Get files with specified tournaments only 
    for root_folder in root_folders:
        if not os.path.exists(root_folder):
            logger.error(f"Folder not found - {root_folder}")
            continue
        for dirpath, _, filenames in os.walk(root_folder):
            for file in filenames:
                if file.lower().endswith('.docx'):
                    if any(tournament in file.lower() for tournament in all_tournaments):
                        docx_files.append(os.path.join(dirpath, file))
    logger.info(f"Found {len(docx_files)} .docx files across all folders.")
    return docx_files

# Process .docx file and extract cards
def process_docx_file(docx_file):
    try:
        logger.info(f"Processing: {docx_file}")
        paragraphs = get_paragraphs(docx_file) # Get paragraphs
        if not paragraphs:
            logger.warning(f"Skipping empty file: {docx_file}")
            return []
        styled_paragraphs = get_styled_paragraphs(docx_file) # Get Styled Paragraphs
        side = extract_side(docx_file)

        # Drop cards with invalid side
        if not side:
            logger.warning(f"Skipping file due to undefined side: {docx_file}")
            return []
        
        filename = os.path.basename(docx_file)
        event = "PF" # Set event to PF
        
        # Set policyc ards to topic 2024
        if event.upper() == "CX":
            topic = "2024"

        # Determine topic for LD & PF based on dictioanry
        else:
            topic = determine_topic(filename)
            if not topic:
                logger.warning(f"Skipping file due to undefined topic: {docx_file}")
                return []
        # Cut and return cards
        cards = cut_cards(paragraphs, styled_paragraphs, side, event, topic)
        logger.info(f"Valid cards in {docx_file}: {len(cards)}")
        return cards

    except Exception as e:
        logger.error(f"Error processing {docx_file}: {e}")
        return []

# Process cards by batch
def process_batch(docx_files, category, event):
    all_cards = []
    for docx_file in tqdm(docx_files, desc=f"Processing {category} files", unit="file"):
        cards = process_docx_file(docx_file)
        all_cards.extend(cards)
    return all_cards

def main():
    root_folders = {
        "PF": [r'C:\Users\senth\DebateVault\hspf24-weekly-2024-12-24.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-12-17.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-11-26.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-11-19.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-11-12.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-11-05.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-10-29.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-10-22.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-10-08.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-10-01.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-09-24.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-09-17.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-09-10.zip',
               r'C:\Users\senth\DebateVault\hspf24-weekly-2024-09-03.zip'
        ]

    }

    output_file = 'raw_PF_cards.json' # Define output file
    all_extracted_cards = []

    for category, folders in root_folders.items():
        logger.info(f"Processing category: {category}")
        with tempfile.TemporaryDirectory() as temp_dir:
            for folder in folders:
                if folder.lower().endswith('.zip'):
                    try:
                        unzip_file(folder, temp_dir)
                    except Exception as e:
                        logger.error(f"Error extracting {folder}: {e}")
                        continue
                else:
                    temp_dir = folder  # If it's not a ZIP File, assume it's a directory

            # Find .docx files within extracted or specified directories
            docx_files = find_docx_files([temp_dir])
            if not docx_files:
                logger.warning(f"No .docx files found for category {category}.")
                continue

            # Process .docx files sequentially
            cards = process_batch(docx_files, category, event=category)
            logger.info(f"Processed {len(cards)} cards for category {category}.")
            all_extracted_cards.extend(cards)

    # Save all extracted cards to a JSON file
    if all_extracted_cards:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_extracted_cards, f, ensure_ascii=False, indent=4)
        logger.info(f"Cards saved to {output_file}")
    else:
        logger.warning("No cards were extracted.")

    logger.info("All files processed successfully.")

if __name__ == "__main__":
    main()
