from datasets import load_dataset
import orjson
from tqdm import tqdm

# Define output file path
output_file = "dataset_cards.jsonl"

# Define fields to extract
required_fields = ["tag", "fullcite", "fulltext", "markup", "tournament", "year", "event", "level"]

# Load dataset in streaming mode
dataset = load_dataset(
    "Hellisotherpeople/OpenCaseList-Deduplicated",
    split="train",
    streaming=True
)

# Define the batch size
batch_size = 5000 

# Open the output file in binary write mode
with open(output_file, "wb") as f_out:
    batch = [] # Initalize empty list to hold records
    for record in tqdm(dataset, desc="Processing Records"):

        # Only process records where level is 'hs'
        if record.get("level") != "hs":
            continue  
        
        # Extract required fields
        card = {field: record.get(field, None) for field in required_fields}
        
        # Serialize the card dictionary to JSON bytes using orjson
        json_line = orjson.dumps(card)
        
        # Append the serialized JSON to the batch
        batch.append(json_line)
        
        # Write the batch to the file when batch_size is reached
        if len(batch) >= batch_size:
            f_out.write(b'\n'.join(batch) + b'\n')
            batch = [] # Clear the batch for the next set of records
    
    # Write any remaining records in the batch to the file
    if batch:
        f_out.write(b'\n'.join(batch) + b'\n')
