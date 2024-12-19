import os
import json
import re
from docx import Document
from alive_progress import alive_bar
import hashlib
from bs4 import BeautifulSoup
import pypandoc


def convert_to_html(filepath):
    """Convert a .docx file to HTML using pypandoc."""
    try:
        return pypandoc.convert_file(filepath, 'html')
    except Exception as e:
        raise RuntimeError(f"Error converting {filepath} to HTML: {e}")


def parse_html(html_content):
    """Parse HTML content to extract potential cards."""
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]


def extract_styled_text(html_content):
    """Extract styled (bold, underlined, marked) text from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    styled_text = []
    for tag in soup.find_all(['b', 'u', 'mark']):
        styled_text.append(tag.get_text(strip=True))
    return styled_text


def contains_url(text):
    """Check if a paragraph contains a URL."""
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.search(text) is not None


def extract_cards(filepath, topic, side, debate_type):
    """Extract debate cards from a .docx file."""
    try:
        html_content = convert_to_html(filepath)
        paragraphs = parse_html(html_content)
        styled_texts = extract_styled_text(html_content)

        cards = []
        unique_cards = set()

        with alive_bar(len(paragraphs), title=f"Processing {os.path.basename(filepath)}") as bar:
            for i, paragraph in enumerate(paragraphs):
                bar()
                if contains_url(paragraph):
                    tagline = paragraphs[i - 1] if i - 1 >= 0 else None
                    evidence_start = i + 1
                    evidence_end = evidence_start

                    while evidence_end < len(paragraphs) and not contains_url(paragraphs[evidence_end]):
                        evidence_end += 1

                    evidence = paragraphs[evidence_start:evidence_end]

                    # Validate card
                    if tagline and evidence:
                        card_identifier = hashlib.sha256((tagline + paragraph).encode('utf-8')).hexdigest()
                        if card_identifier not in unique_cards:
                            unique_cards.add(card_identifier)
                            cards.append({
                                "tagline": tagline,
                                "citation": paragraph,
                                "evidence": evidence,
                                "side": side,
                                "debate_type": debate_type,
                                "topic": topic,
                                "styled_text": styled_texts
                            })

        return cards
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        return []


def save_cards(cards, output_file):
    """Save extracted cards to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=4)


def main():
    input_file = input("Enter the path to the .docx file: ").strip()
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist.")
        return

    topic = input("Enter the topic (e.g., 'Nov/Dec 24'): ").strip()
    side = input("Enter the side (e.g., 'Aff' or 'Neg'): ").strip().capitalize()
    debate_type = input("Enter the debate type (e.g., 'LD', 'PF', 'Policy'): ").strip().upper()

    if side not in ["Aff", "Neg"]:
        print("Error: Invalid side. Please enter 'Aff' or 'Neg'.")
        return

    print(f"Processing file: {input_file}...")
    cards = extract_cards(input_file, topic, side, debate_type)
    print(f"Extracted {len(cards)} cards.")

    output_file = os.path.join(os.path.dirname(input_file), 'extracted_cards.json')
    save_cards(cards, output_file)
    print(f"Cards saved to {output_file}")


if __name__ == "__main__":
    main()
