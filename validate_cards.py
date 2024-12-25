import json
import re
import os
from tqdm import tqdm

# Function to highlight evidence
def highlight_evidence(card):
    for i, evidence in enumerate(card.get('evidence', [])):
        if '<mark>' not in evidence:  # If there's no marked text
            # Highlight bolded or underlined text
            highlighted_text = re.sub(r'<b>(.*?)</b>', r'<mark>\1</mark>', evidence)
            highlighted_text = re.sub(r'<u>(.*?)</u>', r'<mark>\1</mark>', highlighted_text)
            card['evidence'][i] = highlighted_text

# Validation function for each card
def validate_card(card):
    try:
        # Define terms and patterns
        url_pattern = re.compile(r'https?://\S+')
        debate_terms = ['AC', 'NC', 'CP', 'contention', 'Contention', 'C1', 'C2', 'C3', 'C4', 'C5']

        # Extract fields
        tagline = card.get('tagline', "")
        citation = card.get('citation', "")
        evidence = " ".join(card.get('evidence', []))

        # Exclude the card if '¶' is present in any of the specified fields
        if '¶' in tagline or '¶' in citation or '¶' in evidence:
            return False

        # Check that tagline is between 6 and 150 words
        if not (6 <= len(tagline.split()) <= 150):
            return False

        # Validate citation
        if not url_pattern.search(citation):  # Check that citation has a URL
            return False
        if len(citation.split()) <= 5:  # Check that citation has >5 words
            return False
        if any(term in citation.lower() for term in debate_terms):  # Check for invalid terms
            return False

        # Validate evidence
        if len(card.get('evidence', [])) > 15:  # Reject evidence with more than 15 strings in array
            return False
        total_words = len(evidence.split())
        if total_words > 3000 or total_words <= 20:  # Ensure evidence is within word limits
            return False
        if url_pattern.search(evidence):  # Check URL is not in evidence
            return False
        if any(term in evidence.lower() for term in debate_terms):
            return False

        # Validate side
        side = str(card.get('side', ""))
        if side not in ['Aff', 'Neg']:
            return False

        # Validate topic
        topic = str(card.get('topic', ""))
        if topic not in ['Sep/Oct 24', 'Nov/Dec 24', "Jan 24", "Jan/Feb 24", '2024']:
            return False

        return True

    except Exception as e:
        print(f"Error validating card: {e}")
        return False

def main():
    input_file = r'C:\Users\senth\DebateVault\raw_policy_cards.json'
    output_file = r'C:\Users\senth\Debate GPT\cards\validated_cards.json'

    try:
        # Validate input file existence
        if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
            print(f"Error: Input file '{input_file}' does not exist or is empty.")
            return

        # Count total cards for progress bar
        with open(input_file, 'r', encoding='utf-8') as f:
            total_cards = len(json.load(f))

        # Load cards from input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            new_cards = json.load(f)
            if not isinstance(new_cards, list):
                print(f"Error: Input JSON is not a valid list.")
                return

        # Validate new cards with progress bar
        valid_cards = []
        with tqdm(total=total_cards, desc="Validating Cards", unit="card") as pbar:
            for card in new_cards:
                if validate_card(card):
                    valid_cards.append(card)
                pbar.update(1)

        # Save the validated cards to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(valid_cards, f, ensure_ascii=False, indent=4)

        print(f"Validation complete. {len(valid_cards)} cards validated and saved to '{output_file}'.")

    except FileNotFoundError:
        print(f"File {input_file} not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing cards: {e}")

if __name__ == '__main__':
    main()
