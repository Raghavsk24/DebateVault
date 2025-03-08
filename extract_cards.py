import os
import json
import argparse
import pandas as pd
from docx import Document
import fitz
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Global list of tournaments
ALL_TOURNAMENTS = [

    # Sep/Oct tournaments
    'loyola', 'opener', 'grapevine', 'niles', 'knight', 'scottsdale', 'washburn', 'greenhill',
    'yale', 'stephen', 'lindale', 'america', 'georgetown', 'bvsw', 'marist', 'howe', 'nova',
    'delores', 'tennent', 'westminster', 'york', 'trevian', 'averill', 'kansas', 'heart', 'iowa',
    # Nov/Dec tournaments
    'blue', 'kckcc', 'quarry', 'michigan', 'hockaday', 'minneapple', 'peach', 'badgerland',
    'dragon', 'katy', 'stampede', 'ucla', 'swing', 'glenbrooks', 'longhorn', 'princeton',
    'series-1', 'mamaroneck', 'alta-silver', 'alief', 'costa', 'cypress', 'wphs', 'holiday-classic',
    'paradigm', 'isidore-newman', 'chapel-hill',
    # Jan/Feb tournaments
    'blake', 'college-prep', 'strake-jesuit', 'billy-tate', 'churchill', 'hdshc', 'samford',
    'peninsula', 'harvard-westlake', 'cavalier', 'rebel-speech', 'mount-vernon', 'cougar-classic',
    'jean-ward', 'camp-cabot', 'columbia', 'pennsbury', 'unlv', 'foley', 'jasper', 'regatta',
    'marshall-spalter', 'bellaire', 'three-rivers', 'pennsylvania-liberty', 'newman-smith', 'langham',
    'stanford', 'harvard-national', 'bingham-bids', 'berkeley', 'chisholm', 'john-marshall',
    'series-2', 'milo', 'series-3',
    # March/April tournaments
    'debate-coaches', 'of-champions'
]

# Return file extension
def get_file_extension(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return 'pdf'
    elif ext == '.docx':
        return 'docx'
    else:
        return 'unknown'

# Return list of plain paragraphs and marked_pararaphs from DOCX file
def parse_docx(docx_file):
    document = Document(docx_file)
    plain_paragraphs = []
    marked_paragraphs = []

    for p in document.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        plain_paragraphs.append(text)

        # Build marked_paragraphs
        marked_text = ""
        for run in p.runs:
            run_text = run.text
            if run.bold:
                run_text = f"<b>{run_text}</b>"
            if run.underline:
                run_text = f"<u>{run_text}</u>"
            if run.font.highlight_color:
                run_text = f"<mark>{run_text}</mark>"
            marked_text += run_text

        marked_paragraphs.append(marked_text)

    return plain_paragraphs, marked_paragraphs

# Return list of plain paragraphs and marked_pararaphs from the PDF file
def parse_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    plain_paragraphs = []
    marked_paragraphs = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:
                plain_spans = []
                marked_spans = []

                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        
                        # Plain text
                        plain_spans.append(span["text"])

                        # Minimal marked text
                        span_text = span["text"]
                        if "Bold" in span["font"]:
                            span_text = f"<b>{span_text}</b>"
                        marked_spans.append(span_text)

                    # Separate lines with a newline if desired
                    plain_spans.append("\n")
                    marked_spans.append("\n")

                paragraph_plain = "".join(plain_spans).strip()
                paragraph_marked = "".join(marked_spans).strip()
                if paragraph_plain:
                    plain_paragraphs.append(paragraph_plain)
                    marked_paragraphs.append(paragraph_marked)

    return plain_paragraphs, marked_paragraphs

# Get Side from file path (AFF or NEG) 
def extract_side(filepath):
    filename = os.path.basename(filepath).lower()
    if '-con-' in filename or '-neg-' in filename: # con if event is 'PF' and NEG if event is 'LD' or 'CX'
        return 'Neg'
    elif '-pro-' in filename or '-aff-' in filename: # pro if event is 'PF' and AFF if event is 'LD' or 'CX'
        return 'Aff'
    else:
        return None

# Detect topic based on tournament name
def determine_topic(filename):
    filename = filename.lower()

    tournaments_sep_oct = [
        'loyola-invitational', 'hendrickson-tfatoc', 'niles-township', 'season-opener',
        'grapevine-classic', 'falls-knight', 'washburn-rural-debate', 'greenhill-fall-classic',
        'yale-invitational', 'stephen-stewart', 'lindale-tfa', 'mid-america', 'georgetown-day-school',
        'bvsw', 'marist-ivy', 'jack-howe', 'nova-titan', 'delores-taylor', 'nano-nagle',
        'william-tennent', 'westminster', 'new-york-city-invitational', 'trevian-invitational',
        'tim-averill', 'kansas-city-invitational', 'heart-of-texas', 'iowa-caucus'
    ]
    tournaments_nov_dec = [
        'blue-key', 'kckcc', 'quarry-lane', 'of-michigan', 'hockaday-school', 'minneapple',
        'peach-state', 'badgerland-chung', 'debate-dragon', 'katy-taylor', 'bison-stampede',
        'ucla', 'cat-swing', 'glenbrooks-speech', 'longhorn-classic', 'princeton-classic',
        'series-1', 'mamaroneck', 'alta-silver', 'alief', 'la-costa', 'cypress-', 'wphs',
        'holiday-classic', 'paradigm-', 'isidore-newman', 'chapel-hill'
    ]
    tournaments_jan_feb = [
        'blake-', 'college-prep', 'strake-jesuit', 'billy-tate', 'churchill-', 'hdshc',
        'samford-', 'peninsula-', 'harvard-westlake', 'cavalier-', 'rebel-speech',
        'mount-vernon', 'cougar-classic', 'jean-ward', 'camp-cabot', 'columbia-',
        'pennsbury-falcon', 'unlv', 'martin-luther', 'barkely-forum', 'jasper-howl', 'regatta',
        'marshall-spalter', 'bellaire', 'three-rivers', 'pennsylvania-liberty', 'newman-smith',
        'langham', 'stanford', 'harvard-national', 'bingham-bids', 'berkeley-', 'chisholm-',
        'john-marshall', 'series-2', 'milo-', 'series-3'
    ]

    for t in tournaments_sep_oct:
        if t in filename:
            return 'Sep/Oct 24'
    for t in tournaments_nov_dec:
        if t in filename:
            return 'Nov/Dec 24'
    for t in tournaments_jan_feb:
        if t in filename:
            return 'Jan/Feb 25'
    return None

# Cut cards with tagline, citation, evidence, fil path, side, topic and event
def cut_card(paragraphs, marked_paragraphs, file_path, side=None, topic=None, event=None):
    cards = []
    i = 0
    while i < len(paragraphs):
        if 'https' in paragraphs[i]:
            # Tagline
            tagline_index = i - 1
            tagline = paragraphs[tagline_index] if tagline_index >= 0 else None

            # Citation
            citation = paragraphs[i]

            # Evidence
            evidence = []
            j = i + 1
            while j < len(paragraphs) and 'https' not in paragraphs[j]:
                evidence.append(marked_paragraphs[j])
                j += 1

            if tagline and citation and evidence:
                card = {
                    'tagline': tagline,
                    'citation': citation,
                    'evidence': evidence,
                    'side': side,
                    'event': event,
                    'topic': topic,
                    'file_path': file_path,
                }
                cards.append(card)
            i = j  # jump past evidence
        else:
            i += 1
    return cards

# Get all PDF and DOCX Files from directory
def find_files(root_folders):
    files_found = []
    for root_folder in root_folders:
        for dirpath, _, filenames in os.walk(root_folder):
            for file in filenames:
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.docx', '.pdf'] and any(t in file.lower() for t in ALL_TOURNAMENTS):
                    files_found.append(os.path.join(dirpath, file))

    print(f"Found {len(files_found)} files (.docx or .pdf) across all folders.")
    return files_found

# Process files in one pass
def process_file(file, event=None):
    try:
        file_type = get_file_extension(file)
        if file_type == 'docx':
            paragraphs, marked_paragraphs = parse_docx(file)
        elif file_type == 'pdf':
            paragraphs, marked_paragraphs = parse_pdf(file)
        else:
            return []

        # Check that plain_paragraphs = marked_paragraphs
        if not paragraphs or not marked_paragraphs or len(paragraphs) != len(marked_paragraphs):
            return []

        # Extract side and topic once per file
        side = extract_side(file)
        topic = determine_topic(file)

        # Cut Card
        return cut_card(paragraphs, marked_paragraphs, file, side=side, topic=topic, event=event)

    except Exception as e:
        print(f"Error processing {file}: {e}")
        return []

# Process files in batches and parallel using ParallelPoolExecutor
def process_batch_parallel(files, event, max_workers=8):
    all_cards = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, file, event): file for file in files}
        for future in tqdm(as_completed(futures), total=len(futures),
                           desc="Processing files", unit="file"):
            result = future.result()
            if result:
                all_cards.extend(result)
    return all_cards



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process DOCX and PDF Files for debate cards.")
    parser.add_argument("--input_dir", required=True, help="Path to the input directory with cards")
    parser.add_argument("--output_dir", required=True, help="Path to the output directory")
    parser.add_argument("--event", required=True, help="Enter event category of all cards (e.g PF, LD, or CX)")
    args = parser.parse_args()

    # Set input and output folder
    input_folder = args.input_dir
    output_folder = args.output_dir
    os.makedirs(output_folder, exist_ok=True)

    # Set event
    event = args.event

    # Find all matching files.
    all_files = find_files([input_folder])

    # Load checkpoint
    processed_files = set()

    # Filter out files already processed.
    unprocessed_files = [f for f in all_files if f not in processed_files]
    print(f"Total files to process: {len(unprocessed_files)}")

    # Split the list of unprocessed files into N batches.
    num_batches = 100
    batch_size = max(1, len(unprocessed_files) // num_batches)
    batches = [unprocessed_files[i:i + batch_size]
               for i in range(0, len(unprocessed_files), batch_size)]
    print(f"Created {len(batches)} batches.")

    # Specify the starting batch 
    start_batch =1

    # Process each batch starting from the specified start_batch.
    for batch_num, batch_files in enumerate(batches, start=1):
        if batch_num < start_batch:
            print(f"Skipping batch {batch_num} as it's already processed.")
            processed_files.update(batch_files)
            continue

        print(f"\nProcessing batch {batch_num} with {len(batch_files)} files...")
        cards = process_batch_parallel(batch_files, event, max_workers=4)
        if not cards:
            print(f"No cards found in batch {batch_num}.")
        else:
            df_cards = pd.DataFrame(cards)
            output_csv = os.path.join(output_folder, f"cards_batch_{batch_num}.csv")
            df_cards.to_csv(output_csv, index=False, encoding="utf-8")
            print(f"Batch {batch_num}: Saved {len(df_cards)} cards to {output_csv}")

        # Update checkpoint in memory 
        processed_files.update(batch_files)

    print("All batches processed successfully.")
