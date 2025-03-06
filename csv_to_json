import csv
import json
import argparse

def csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            data.append(row)

    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

parser = argparse.ArgumentParser()
parser.add_argument("--input_csv", required=True, help="Path to the input CSV file")
parser.add_argument("--output_json", required=True, help="Path to the output JSON file")
args = parser.parse_args()

input_csv = args.input_csv
output_json = args.output_json

csv_to_json(input_csv, output_json)
