import json
import re
import pandas as pd
import os

# Function to normalize quotes
def normalize_quotes(text):
    return text.replace('‘', "'").replace('’', "'")

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

        # Normalize fields
        card['tagline'] = normalize_quotes(str(card['tagline']))
        card['citation'] = normalize_quotes(str(card['citation']))
        card['evidence'] = [normalize_quotes(str(e)) for e in card.get('evidence', [])]

        # Reject cards with more than 15 evidence strings
        if len(card['evidence']) > 15:
            return False

        # Check that tagline is between 6 and 150 words
        tagline = card['tagline']
        if not (6 <= len(tagline.split()) <= 150):
            return False

        # Validate citation
        citation = card['citation']
        if not url_pattern.search(citation):  # Check that citation has a URL
            return False
        if len(citation.split()) <= 5:  # Check that citation has >5 words
            return False
        if any(term in citation.lower() for term in debate_terms):  # Check for invalid terms
            return False

        # Validate evidence
        evidence = " ".join(card.get('evidence', []))
        total_words = len(evidence.split())
        if total_words > 3000:  # Ensure evidence <3000 words
            return False
        if total_words <= 20:  # Ensure evidence >20 words
            return False
        if url_pattern.search(evidence):  # Check URL is not in evidence
            return False
        if any(term in evidence.lower() for term in debate_terms):
            return False

        # Highlight bolded or underlined text if no marked text exists
        if not any('<mark>' in e for e in card.get('evidence', [])):
            highlight_evidence(card)

        # Validate side
        side = str(card['side'])
        if side not in ['Aff', 'Neg']:
            return False

        # Validate topic
        topic = str(card['topic'])
        if topic not in ['Sep/Oct 24', 'Nov/Dec 24', "Jan 24", "Jan/Feb 24", '2024']:
            return False

        return True
    except Exception as e:
        print(f"Error validating card: {e}")
        return False

# Remove duplicates based on tagline, citation, or evidence
def remove_duplicates(cards):
    if not cards:
        return []  # Return an empty list if no cards are provided
    df = pd.DataFrame(cards)
    df = df.drop_duplicates(subset=['tagline', 'citation'], keep='first')
    df = df.drop_duplicates(subset=['evidence'], keep='first', inplace=False)
    return df.to_dict(orient='records')

# Main function to validate, filter, and append cards
def main():
    input_file = r'C:\Users\senth\Debate GPT\cards\temp_cards.json'
    output_file = r'C:\Users\senth\Debate GPT\cards\validated_cards.json'

    try:
        # Load cards from input JSON file
        if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
            print(f"Error: Input file '{input_file}' does not exist or is empty.")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            new_cards = json.load(f)
            if not isinstance(new_cards, list):
                print(f"Error: Input JSON is not a valid list.")
                return

        # Validate new cards
        valid_cards = [card for card in new_cards if validate_card(card)]

        # Remove duplicates from the new cards
        unique_new_cards = remove_duplicates(valid_cards)

        # Load existing validated cards if output file exists and is not empty
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_cards = json.load(f)
        else:
            existing_cards = []

        # Combine existing and new validated cards, then remove duplicates
        all_cards = existing_cards + unique_new_cards
        all_unique_cards = remove_duplicates(all_cards)

        # Save the combined cards back to validated_cards.json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_unique_cards, f, ensure_ascii=False, indent=4)

        print(f"Validation complete. {len(unique_new_cards)} new cards appended.")
        print(f"Total unique cards in '{output_file}': {len(all_unique_cards)}")

    except FileNotFoundError:
        print(f"File {input_file} not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing cards: {e}")

if __name__ == '__main__':
    main()
