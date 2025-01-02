from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
from elasticsearch import Elasticsearch
from fastapi.staticfiles import StaticFiles
import json

# Define stop words
STOP_WORDS = {
    "about", "above", "across", "after", "against", "along", "amid", "among",
    "around", "as", "at", "before", "behind", "below", "beneath", "beside",
    "between", "beyond", "but", "by", "concerning", "despite", "down", "during",
    "except", "for", "from", "in", "inside", "into", "like", "near", "of",
    "off", "on", "onto", "out", "outside", "over", "past", "since", "through",
    "throughout", "till", "to", "toward", "under", "underneath", "until",
    "up", "upon", "with", "within", "without"
}

app = FastAPI()

# Elasticsearch Cloud connection
es = Elasticsearch(
    hosts=["https://852bdb4c2a854ef9923a92a913f7ef1a.us-west-1.aws.found.io:443"],
    basic_auth=("elastic", "V6gvgwaVLMA5zf4K8Ef8drZA")  # Replace with your credentials
)

# Mount static files
app.mount("/static", StaticFiles(directory=r"C:\Users\senth\DebateVault\static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r") as file:
        return HTMLResponse(content=file.read())

def remove_stop_words(query: str) -> str:
    """
    Remove filler words and prepositions from the search query.
    Ignores case and returns a filtered query string.
    """
    words = query.split()
    filtered_words = [word for word in words if word.lower() not in STOP_WORDS]
    return " ".join(filtered_words)

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
    try:
        from_index = (page - 1) * size
        query = {"bool": {"must": [], "should": []}}

        apply_min_score = False

        # Preprocess search query to remove stop words if search is provided
        if search and search.strip():
            exact_query = search.strip()
            fuzzy_query = remove_stop_words(exact_query)

            # Prioritize exact matches
            query["bool"]["should"].append({
                "multi_match": {
                    "query": exact_query,
                    "fields": [
                        "tagline^50",
                        "evidence^10",
                        "citation^1"
                    ],
                    "type": "phrase",
                    "boost": 100
                }
            })

            # Fallback fuzzy search
            query["bool"]["should"].append({
                "multi_match": {
                    "query": fuzzy_query,
                    "fields": [
                        "tagline^50",
                        "evidence^10",
                        "citation^1"
                    ],
                    "fuzziness": "AUTO"
                }
            })

            apply_min_score = True

        # Apply filters using term queries for exact matches on keyword fields
        if side:
            query["bool"]["must"].append({
                "term": {
                    "side": side
                }
            })

        if topic:
            query["bool"]["must"].append({
                "term": {
                    "topic": topic
                    
                }
            })


        if event:
            query["bool"]["must"].append({
                "term": {
                    "event": event
                }
            })

        if evidence_set:
            query["bool"]["must"].append({
                "term": {
                    "evidence_set": evidence_set
                }
            })

        # Construct the final Elasticsearch query
        search_query = {
            "from": from_index,
            "size": size,
            "query": query
        }

        # Only set min_score if the user entered a search query
        if apply_min_score:
            search_query["min_score"] = 5.0

        # Log the query for debugging
        print("Elasticsearch Query:", json.dumps(search_query, indent=2))

        # Perform the Elasticsearch search
        results = es.search(index="cards_index", body=search_query)
        cards = [hit["_source"] for hit in results["hits"]["hits"]]
        total = results["hits"]["total"]["value"]

        # Return results to the frontend
        return {"cards": cards, "total": total, "page": page, "size": size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cards: {e}")
