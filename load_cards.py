from elasticsearch import Elasticsearch
import json

# Update Elasticsearch connection details
ES_HOST = "https://localhost:9200"
CA_CERTS_PATH = r"C:/Users/senth/Downloads/elasticsearch-8.17.0-windows-x86_64/elasticsearch-8.17.0/config/certs/http_ca.crt"
USERNAME = "elastic"
PASSWORD = "eSI4Mouej*keLZeEngvm"
CARD_FILE_PATH = r"C:\Users\senth\Debate GPT\cards\validated_cards.json"
INDEX_NAME = "cards_index"

def recreate_index(es, index_name=INDEX_NAME):
    """
    Deletes the specified index if it exists and recreates it with the correct mapping.
    """
    mapping = {
        "mappings": {
            "properties": {
                "side": {"type": "keyword"},
                "topic": {"type": "keyword"},
                "debate_type": {"type": "keyword"},
                "tagline": {"type": "text"},
                "citation": {"type": "text"},
                "evidence": {"type": "text"}
            }
        }
    }

    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Deleted existing index: {index_name}")
    
    es.indices.create(index=index_name, body=mapping)
    print(f"Created new index: {index_name}")

def load_data_to_elasticsearch(es, index_name=INDEX_NAME, file_path=CARD_FILE_PATH):
    """
    Loads data from JSON file into Elasticsearch index.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
    
    for i, card in enumerate(cards, start=1):
        es.index(index=index_name, document=card)
        print(f"Indexed card {i}/{len(cards)}")

if __name__ == "__main__":
    es = Elasticsearch(
        hosts=[ES_HOST],
        ca_certs=CA_CERTS_PATH,
        basic_auth=(USERNAME, PASSWORD)
    )
    recreate_index(es)
    load_data_to_elasticsearch(es)
