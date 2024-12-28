from elasticsearch import Elasticsearch

# Set up the connection
es = Elasticsearch(
    "https://852bdb4c2a854ef9923a92a913f7ef1a.us-west-1.aws.found.io:443",
    basic_auth=("elastic", "V6gvgwaVLMA5zf4K8Ef8drZA")
)

# Test the connection
try:
    info = es.info()
    print("Cluster Info:", info)
except Exception as e:
    print("Connection failed:", e)
