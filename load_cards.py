from elasticsearch import Elasticsearch
import json

# Update Elastic Cloud Connection
ES_CLOUD_HOST = "https://852bdb4c2a854ef9923a92a913f7ef1a.us-west-1.aws.found.io:443"
USERNAME = "elastic"
PASSWORD = "V6gvgwaVLMA5zf4K8Ef8drZA"
CARD_FILE_PATH = r"C:\Users\senth\DebateVault\all_valid_cards.json"
INDEX_NAME = "cards_index"

# Deletes specified index and creates a new one
def recreate_index(es, index_name=INDEX_NAME):

    # Index Mapping
    mapping = {
        "mappings": {
            "properties": {
                "side": {"type": "keyword"},
                "topic": {"type": "keyword"},
                "event": {"type": "keyword"},
                "tagline": {"type": "text"},
                "citation": {"type": "text"},
                "evidence": {"type": "text"},
                "evidence_set": {"type": "integer"}
            }
        }
    }

    # If cards_index exists it is deleted and then recreated
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Deleted existing index: {index_name}")
    
    es.indices.create(index=index_name, body=mapping)
    print(f"Created new index: {index_name}")

# Load data from json file to elasticsearch
def load_data_to_elasticsearch(es, index_name=INDEX_NAME, file_path=CARD_FILE_PATH):

    # Read json file contents
    with open(file_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
    
    # Index card and print it onto terminal
    for i, card in enumerate(cards, start=1):
        es.index(index=index_name, document=card)
        print(f"Indexed card {i}/{len(cards)}")

if __name__ == "__main__":
    es = Elasticsearch(
        hosts=[ES_CLOUD_HOST],
        basic_auth=(USERNAME, PASSWORD)
    )
    recreate_index(es)
    load_data_to_elasticsearch(es)
