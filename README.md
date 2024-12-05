# DebateVault

- DebateVault is a web application based search engine for debate card and debate evidence


## Features

- **Vast Database:** Includes 1500 cards up to date with current resolutions as of December 2024.
- **Dynamic Filtering:** Filter cards by `Side` (Aff/Neg) or `Debate Type` (PF, LD, CX) or `Resolution` (Nov/Dec 24) .
- **Search:** Find specific cards with fuzzy search.
- **Copy Functionality:** Easily copy card text with styling maintained. 



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


