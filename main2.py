from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import json
import os

# --------------- STOP WORDS ---------------
STOP_WORDS = {
    "about", "above", "across", "after", "against", "along", "amid", "among",
    "around", "as", "at", "before", "behind", "below", "beneath", "beside",
    "between", "beyond", "but", "by", "concerning", "despite", "down", "during",
    "except", "for", "from", "in", "inside", "into", "like", "near", "of",
    "off", "on", "onto", "out", "outside", "over", "past", "since", "through",
    "throughout", "till", "to", "toward", "under", "underneath", "until",
    "up", "upon", "with", "within", "without"
}

# --------------- FASTAPI APP ---------------
app = FastAPI()

# Mount static files (for serving index.html, CSS, JS, etc.)
app.mount("/static", StaticFiles(directory=r"C:\Users\senth\DebateVault\static"), name="static")

# --------------- LOAD CARDS (IN-MEMORY) ---------------
# Adjust "cards_index.json" to the path where you store all 6000 cards.
DATA_FILE = r"C:\Users\senth\DebateVault\valid_Jan-Feb_LD_cards.json"
if not os.path.exists(DATA_FILE):
    raise RuntimeError(f"Data file not found: {DATA_FILE}")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    ALL_CARDS = json.load(f)  # ALL_CARDS is now a list of dicts (each dict = one card)


# --------------- HELPER FUNCTIONS ---------------
def remove_stop_words(query: str) -> str:
    """
    Remove filler words and prepositions from the search query.
    Ignores case and returns a filtered query string.
    """
    words = query.split()
    filtered_words = [word for word in words if word.lower() not in STOP_WORDS]
    return " ".join(filtered_words)

def compute_score(card: dict, search_tokens: list[str]) -> float:
    """
    Very simple scoring approach:
    - +50 points if a token is in 'tagline'
    - +10 points if in 'evidence'
    - +1 point if in 'citation'
    We sum across all tokens. If no search provided, score = 0.
    """
    score = 0.0
    
    tagline_text = card.get("tagline", "").lower()
    evidence_text = " ".join(card.get("evidence", [])).lower()  # evidence is typically a list
    citation_text = card.get("citation", "").lower()

    for token in search_tokens:
        # Substring check; you can refine by tokenizing or using regex, etc.
        if token in tagline_text:
            score += 50.0
        if token in evidence_text:
            score += 10.0
        if token in citation_text:
            score += 1.0

    return score


# --------------- ROUTES ---------------
@app.get("/", response_class=HTMLResponse)
def root():
    """
    Serve index.html from the static directory.
    """
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    else:
        return HTMLResponse("<h1>index.html not found</h1>", status_code=404)


@app.get("/data")
def get_data(
    side: Optional[str] = None,
    topic: Optional[str] = None,
    event: Optional[str] = None,
    evidence_set: Optional[str] = None,
    search: Optional[str] = None,
    size: int = 50,
    page: int = 1
):
    """
    In-memory search across ALL_CARDS.
    - Optional filters for side, topic, event, evidence_set
    - 'search' query with naive substring matching + scoring
    - Paginated with ?size=&page=
    """
    try:
        # 1) Filter by side, topic, event, evidence_set if provided
        filtered_cards = []
        for card in ALL_CARDS:
            if side and card.get("side", "").lower() != side.lower():
                continue
            if topic and card.get("topic", "").lower() != topic.lower():
                continue
            if event and card.get("event", "").lower() != event.lower():
                continue
            if evidence_set and str(card.get("evidence_set", "")).lower() != evidence_set.lower():
                continue
            # If all checks passed, this card is included
            filtered_cards.append(card)

        # 2) If there's a search query, do scoring
        if search and search.strip():
            # Remove stop words
            cleaned_search = remove_stop_words(search.strip().lower())
            search_tokens = cleaned_search.split()
            
            # Score each card
            scored_results = []
            for card in filtered_cards:
                score = compute_score(card, search_tokens)
                scored_results.append((score, card))

            # We mimic the 'min_score=5.0' from your ES code
            # Keep only cards with score >= 5.0 (adjust if you prefer)
            final_results = [(s, c) for (s, c) in scored_results if s >= 5.0]

            # Sort by descending score
            final_results.sort(key=lambda x: x[0], reverse=True)

            # Unpack cards after sorting
            filtered_cards = [c for (s, c) in final_results]
        else:
            # If no search query, keep them in the original order
            pass

        # 3) Pagination
        from_index = (page - 1) * size
        to_index = from_index + size
        total = len(filtered_cards)
        paginated_cards = filtered_cards[from_index:to_index]

        # 4) Return results
        return {
            "cards": paginated_cards,
            "total": total,
            "page": page,
            "size": size
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cards: {e}")
