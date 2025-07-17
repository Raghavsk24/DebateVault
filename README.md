# DebateVault

**DebateVault** is a full-stack, single-page, high-speed search engine that allows debaters to search, filter, and copy over 600,000 cards (competitive debate evidence) from 2014–2025, sourced from OpenCaseList and DebateSum. DebateVault is updated weekly with new cards from OpenCaseList on-season. 


## Features

- Search 600K+ cardsusing FastAPI backend with paginated JSON API
- Filter cards by side (AFF or NEG), event (LD, PF or CX), topic and year (2014-2024)
- Directly copy cards onto clipboard and download original case file from OpenCaseList
- High-Speed search with infinite scrolling, cards ranked by relevance and duplication count (how manny other cards existed in the original datset with the same tagline)



## How to Run the Project

### Prerequisites
- Python 3.x
- Virtual Environment (venv)
- VSCode
  

### Installation Steps
1. **Clone the repository**:
    ```bash
    git clone https://github.com/Raghavsk24/DebateVault.git
    cd DebateVault
    ```
    
2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv

    # For Mac or Linux:
    source venv/bin/activate

    # For Windows:
    venv\Scripts\activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the FastAPI server using `uvicorn`**:
    ```bash
    uvicorn backend.main:app --reload
    ```
    
5. **Open the app** in your browser at:
    ```
    http://127.0.0.1:8000/
    ```

### Card Processing Pipeline

#### Bulk Download from OpenCaselist (PF / LD / CX)
  
  OpenCaselist allows you to bulk-download full cases from tournaments in `.docx` and `.pdf` formats.
  
  **Steps to process these:**
  
  1. Download tournament files from OpenCaselist into the `data/raw/` folder.
  2. Run the card extractor:
      ```bash
      python backend/extract_cards.py \
          --input_dir data/raw \
          --output_dir data/processed \
          --event PF  # or LD or CX
      ```
  3. Clean and filter those extracted cards:
      ```bash
      python backend/filter_cards.py \
          --input_csv data/processed/raw_cards.csv \
          --output_csv data/final/processed_cards.json
      ```
  
  You can repeat this for any other tournament set by adjusting the input files and `--event` flag.

  
  #### 2. Hugging Face Dataset (`Yusuf5/OpenCaselist`)
  
  The DebateSUm OpenCaselist dataset contains pre-tokenized cards from multiple debate events. You can filter and load these cards directly for use in DebateVault.
  
  **Steps to use the dataset:**
  
  1. Install the `datasets` library (if not already):
      ```bash
      pip install datasets
      ```
  
  2. Load the dataset and export it to a CSV or JSON:
      ```python
      from datasets import load_dataset
      import pandas as pd
  
      dataset = load_dataset("Yusuf5/OpenCaselist", split="train")
      df = pd.DataFrame(dataset)
      df.to_csv("data/processed/hf_opencaselist.csv", index=False)
      ```
  
  3. Run the filter script on the exported file:
      ```bash
      python backend/filter_cards.py \
          --input_csv data/processed/DebateSum_cards.csv \
          --output_csv data/final/filtered_DebateSum_cards.json
      ```
