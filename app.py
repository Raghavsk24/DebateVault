from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
from elasticsearch import Elasticsearch
from fastapi.staticfiles import StaticFiles
import json

STOP_WORDS = {
    "a", "about", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", 
    "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "another", 
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at", "back", "be", "became", 
    "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", 
    "besides", "between", "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", 
    "computer", "con", "could", "couldn't", "cry", "de", "describe", "detail", "did", "do", "done", "down", "due", 
    "during", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever", 
    "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", 
    "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", 
    "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", 
    "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "i", "ie", "if", "in", "inc", 
    "indeed", "into", "is", "it", "its", "it's", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", 
    "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", 
    "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", 
    "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", 
    "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves"
}


app = FastAPI()

# Elasticsearch connection
es = Elasticsearch(
    hosts=["https://localhost:9200"],
    ca_certs=r"C:/Users/senth/Downloads/elasticsearch-8.17.0-windows-x86_64/elasticsearch-8.17.0/config/certs/http_ca.crt",
    basic_auth=("elastic", "eSI4Mouej*keLZeEngvm")
)

app.mount("/static", StaticFiles(directory=r"C:\Users\senth\Debate GPT\static"), name="static")

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
    debate_type: Optional[str] = None,
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
                        "evidence.hbu^10",
                        "evidence.bu^1",
                        "citation^0.1"
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
                        "evidence.hbu^10",
                        "evidence.bu^1",
                        "citation^0.1"
                    ],
                    "fuzziness": "AUTO"
                }
            })

            apply_min_score = True

        # Apply filters
        if side:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": side,
                    "fields": ["side"],
                    "operator": "and"
                }
            })

        if topic:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": topic,
                    "fields": ["topic"],
                    "operator": "and"
                }
            })

        if debate_type:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": debate_type,
                    "fields": ["debate_type"],
                    "operator": "and"
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
