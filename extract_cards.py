import os
import json
import pandas as pd
from docx import Document
import fitz
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Global list of tournament keywords (Sep/Oct, Nov/Dec, Jan/Feb) for quick file filtering
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
    'series-2', 'milo', 'series-3'
]

def get_file_extension(file_path):
    """
    Return the file extension ('pdf' or 'docx' or 'unknown').
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return 'pdf'
    elif ext == '.docx':
        return 'docx'
    else:
        return 'unknown'


def parse_docx(docx_file):
    """
    Return two lists: plain_paragraphs and styled_paragraphs for a given DOCX file.
    """
    document = Document(docx_file)
    plain_paragraphs = []
    styled_paragraphs = []

    for p in document.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        plain_paragraphs.append(text)

        # Build styled text
        styled_text = ""
        for run in p.runs:
            run_text = run.text
            if run.bold:
                run_text = f"<b>{run_text}</b>"
            if run.underline:
                run_text = f"<u>{run_text}</u>"
            if run.font.highlight_color:
                run_text = f"<mark>{run_text}</mark>"
            styled_text += run_text

        styled_paragraphs.append(styled_text)

    return plain_paragraphs, styled_paragraphs


def parse_pdf(pdf_file):
    """
    Return two lists: plain_paragraphs and styled_paragraphs for a given PDF file.
    Uses fitz (PyMuPDF) to extract both plain text and basic bold styling in one pass.
    """
    doc = fitz.open(pdf_file)
    plain_paragraphs = []
    styled_paragraphs = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # text block
                plain_spans = []
                styled_spans = []

                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        # Plain text
                        plain_spans.append(span["text"])

                        # Minimal styled text (bold detection via font name)
                        span_text = span["text"]
                        if "Bold" in span["font"]:
                            span_text = f"<b>{span_text}</b>"
                        styled_spans.append(span_text)

                    # Separate lines with a newline if desired
                    plain_spans.append("\n")
                    styled_spans.append("\n")

                paragraph_plain = "".join(plain_spans).strip()
                paragraph_styled = "".join(styled_spans).strip()
                if paragraph_plain:
                    plain_paragraphs.append(paragraph_plain)
                    styled_paragraphs.append(paragraph_styled)

    return plain_paragraphs, styled_paragraphs


def extract_side(filepath):
    """
    Attempt to detect AFF/NEG side from the filename.
    """
    filename = os.path.basename(filepath).lower()
    if '-con-' in filename or '-neg-' in filename:
        return 'Neg'
    elif '-pro-' in filename or '-aff-' in filename:
        return 'Aff'
    else:
        return None


def determine_topic(filename):
    """
    Attempt to detect the topic based on known tournament strings.
    Customize this as needed for your own naming conventions.
    """
    filename = filename.lower()

    # Examples of how you might parse out the topic. Adjust as needed:
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


def cut_card(paragraphs, styled_paragraphs, file_path, side=None, topic=None):
    """
    Given lists of plain and styled paragraphs, plus optional side/topic info,
    extract "cards" (tagline + citation + evidence) using simple logic:
    - If a paragraph contains 'https', we treat that as the citation.
    - The immediately preceding paragraph is the tagline.
    - All following paragraphs (until the next 'https') is the evidence block.
    """
    cards = []
    i = 0
    while i < len(paragraphs):
        if 'https' in paragraphs[i]:
            tagline_index = i - 1
            tagline = paragraphs[tagline_index] if tagline_index >= 0 else None
            styled_tagline = styled_paragraphs[tagline_index] if tagline_index >= 0 else None

            citation = paragraphs[i]
            styled_citation = styled_paragraphs[i]

            evidence = []
            styled_evidence = []
            j = i + 1

            # Accumulate evidence until next 'https' or end
            while j < len(paragraphs) and 'https' not in paragraphs[j]:
                evidence.append(paragraphs[j])
                styled_evidence.append(styled_paragraphs[j])
                j += 1

            if evidence and tagline:
                debate_type = 'LD'  # Hard-coded in your logic
                card = {
                    'tagline': tagline,
                    'citation': citation,
                    'evidence': evidence,
                    'side': side,
                    'debate_type': debate_type,
                    'topic': topic,
                    'file_path': file_path,
                    'marked_tagline': styled_tagline,
                    'marked_citation': styled_citation,
                    'marked_evidence': styled_evidence
                }
                cards.append(card)

            i = j  # jump past evidence
        else:
            i += 1
    return cards


def find_files(root_folders):
    """
    Find all .docx/.pdf files in the given folders whose filenames
    contain any known tournament keywords (for speed).
    """
    files_found = []
    for root_folder in root_folders:
        for dirpath, _, filenames in os.walk(root_folder):
            for file in filenames:
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.docx', '.pdf'] and any(t in file.lower() for t in ALL_TOURNAMENTS):
                    files_found.append(os.path.join(dirpath, file))

    print(f"Found {len(files_found)} files (.docx or .pdf) across all folders.")
    return files_found


def process_file(file):
    """
    Main wrapper to parse a file (DOCX or PDF) in one pass, detect side/topic,
    then cut the cards.
    """
    try:
        file_type = get_file_extension(file)
        if file_type == 'docx':
            paragraphs, styled_paragraphs = parse_docx(file)
        elif file_type == 'pdf':
            paragraphs, styled_paragraphs = parse_pdf(file)
        else:
            return []

        # Quick safety check
        if not paragraphs or not styled_paragraphs or len(paragraphs) != len(styled_paragraphs):
            return []

        # Extract side and topic once, not per card
        side = extract_side(file)
        topic = determine_topic(file)

        # Cut the cards
        return cut_card(paragraphs, styled_paragraphs, file, side=side, topic=topic)

    except Exception as e:
        print(f"Error processing {file}: {e}")
        return []


def process_batch_parallel(files, max_workers=8):
    """
    Process a list of files in parallel using a ProcessPoolExecutor.
    Returns a list of all "cards" found across the batch.
    """
    all_cards = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, file): file for file in files}
        for future in tqdm(as_completed(futures), total=len(futures),
                           desc="Processing files", unit="file"):
            result = future.result()
            if result:
                all_cards.extend(result)
    return all_cards


# ------------------- Main Execution -------------------
if __name__ == "__main__":
    # Set the root folder(s) where your DOCX/PDF files are stored.
    root_folders = ["/workspaces/DebateVault/hsld24_all_cards"]

    # Set the output folder for CSV files.
    output_folder = "/workspaces/DebateVault/output"
    os.makedirs(output_folder, exist_ok=True)

    # Find all matching files.
    all_files = find_files(root_folders)

    # (Optional) Load a checkpoint here if needed; otherwise, set processed_files to empty.
    processed_files = set()

    # Filter out files already processed.
    unprocessed_files = [f for f in all_files if f not in processed_files]
    print(f"Total files to process: {len(unprocessed_files)}")

    # Split the list of unprocessed files into N batches (tweak as needed).
    num_batches = 100
    batch_size = max(1, len(unprocessed_files) // num_batches)
    batches = [unprocessed_files[i:i + batch_size]
               for i in range(0, len(unprocessed_files), batch_size)]
    print(f"Created {len(batches)} batches.")

    # Specify the starting batch (e.g., 1 to process from the beginning).
    start_batch = 23

    # Process each batch starting from the specified start_batch.
    for batch_num, batch_files in enumerate(batches, start=1):
        if batch_num < start_batch:
            print(f"Skipping batch {batch_num} as it's already processed.")
            processed_files.update(batch_files)
            continue

        print(f"\nProcessing batch {batch_num} with {len(batch_files)} files...")
        # Adjust max_workers based on your environment (e.g., 4, 8, etc.)
        cards = process_batch_parallel(batch_files, max_workers=4)
        if not cards:
            print(f"No cards found in batch {batch_num}.")
        else:
            df_cards = pd.DataFrame(cards)
            output_csv = os.path.join(output_folder, f"cards_batch_{batch_num}.csv")
            df_cards.to_csv(output_csv, index=False, encoding="utf-8")
            print(f"Batch {batch_num}: Saved {len(df_cards)} cards to {output_csv}")

        # Update checkpoint in memory (or write to a file if needed).
        processed_files.update(batch_files)

    print("All batches processed successfully.")
