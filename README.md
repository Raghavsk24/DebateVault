# DebateVault

- DebateVault is a web application based search engine for debate card and debate evidence


## Features

- **Vast Database:** Includes 1500 cards up to date with current resolutions as of December 2024.
- **Dynamic Filtering:** Filter cards by `Side` (Aff/Neg) or `Debate Type` (PF, LD, CX) or `Resolution` (Nov/Dec 24) .
- **Search:** Find specific cards with fuzzy search.
- **Copy Functionality:** Easily copy card text with styling maintained. 


## File Descriptions

### 1. `extract_cards.py`
This script is responsible for extracting cards for `.docx` files. It loops through case files form bulk downloads on OpenCaseList extracting cards based on mentions of a url (citation) in a paragraph. It then extracts the paragraph in the index behind it as a tagline and the paragraph in the index after it as evidence.

**Features:**
- Extracts `Tagline`, `Citation`, and `Evidence` from structured files.
- Identifies the `Side` (Aff/Neg) and `Debate Type` based on file naming conventions.
- Handles styled text (e.g., bold, underline, and highlight) for evidence.

**Output:** `Raw_Cards.csv` file containing unvalidated cards with the following columns:
- `Tagline`
- `Citation`
- `Evidence`
- `Side`
- `Debate_Type`
- `Topic`

---

### 2. `validate_cards.py`
This script validates the cards extracted by `extract_cards.py` and appends valid entries to `Valid_Cards.csv`. This script is responsible for checking if each component of the card (tagline, citation and evidence) are correct.

**Features:**
- Ensures `Tagline` length is between 6 and 50 words.
- Validates `Citation` for URLs 
- Filters out `Evidence` with less than 20 words or containing URLs/jargon.
- Removes duplicate cards 

**Output:** `Valid_Cards.csv` file containing sanitized and validated cards ready for use in the application.

---

### 3. `script.js`
This JavaScript file tunss the frontend functionality of DebateVault. It manages dynamic card fetching, infinite scrolling, filtering, and search.

**Features:**
- **Dynamic Fetching:** Fetches cards from the backend api in batches to improve performance.
- **Infinite Scrolling:** Loads more cards as the user scrolls down the page.
- **Search and Filtering:** Supports searching cards by keywords and filtering by `Side` and `Debate_Type`.
- **Copy Functionality:** Enables copying card content while preserving formatting.
- **Debounced Search:** Implements a debounce mechanism for efficient filtering.


## Installation

Follow these steps to set up DebateVault locally:

### Prerequisites

- Python 3.9+
- Node.js and npm (optional for frontend build tools)
- A running Elasticsearch or Meilisearch instance for card storage

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/debatevault.git
   cd debatevault

2. Set up the Virtual Environment:
   ```bash
   python -m venv venv
   # Linux/MacOS
   source venv/bin/activate
   # Windows
    venv\Scripts\activate

3. Install dependencies
   ```bash
   pip install -r requirements.txt

4. Start the backend server
    ```bash
    python app.py


