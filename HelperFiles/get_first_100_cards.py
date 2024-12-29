import ijson
from tqdm import tqdm
import json
import decimal

# Define input and output file paths
input_file = r'C:\Users\senth\DebateVault\Dataset_Cards\valid_dataset_cards.json'  
output_file = r'C:\Users\senth\DebateVault\Dataset_Cards\first_100_dataset_cards.json'  

# Extract the first 100 objects from a large JSON file using streaming
def extract_first_n_objects(json_path, n):
    extracted_objects = []
    try:
        with open(json_path, 'r', encoding='utf-8') as f_in:
            parser = ijson.items(f_in, 'item')  # Stream items from the top-level JSON array
            for i, item in tqdm(enumerate(parser), desc="Extracting Objects"):
                if i >= n:
                    break
                extracted_objects.append(item)
    except FileNotFoundError:
        print(f"Error: The file '{json_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred while extracting objects: {e}")
    return extracted_objects

# Write a list of JSON objects to a file
def write_json(obj_list, output_path):
    def custom_encoder(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)  # Convert Decimal to float
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(obj_list, f_out, indent=4, ensure_ascii=False, default=custom_encoder)  # Use custom encoder
        print(f"Successfully wrote {len(obj_list)} objects to '{output_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred while writing to the output file: {e}")

def main():
    # Extract the first 100 objects from the JSON input file
    print(f"Starting extraction of the first 100 objects from '{input_file}'...")
    first_100_objects = extract_first_n_objects(input_file, 100)
    
    if not first_100_objects:
        print("No objects were extracted. Please check the input file.")
        return
    
    # Write the extracted objects to the output JSON file
    print(f"Writing the extracted objects to '{output_file}'...")
    write_json(first_100_objects, output_file)
    
    print(f"\nProcessing complete. Extracted {len(first_100_objects)} objects to '{output_file}'.")

if __name__ == "__main__":
    main()
