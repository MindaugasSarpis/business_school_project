import os
import sys

# Add the scripts directory to the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.parser import parse_apple_report, save_to_csv
from scripts.config import GAME_MAPPING, DEFAULT_GAME_NAME
from web.app import app

INPUT_FOLDER = "data/input/"
OUTPUT_FILE = "data/output/combined_output.csv"

def process_files():
    all_data = {}

    # Iterate over all .txt files in the input folder
    for file_name in os.listdir(INPUT_FOLDER):
        if file_name.endswith(".txt"):  # Process only TXT files
            file_path = os.path.join(INPUT_FOLDER, file_name)
            print(f"Processing {file_name}...")
            report_data = parse_apple_report(file_path)

            # Merge data into all_data
            for key, value in report_data.items():
                all_data[key] = all_data.get(key, 0) + value

    # Save all parsed data into a single CSV file
    save_to_csv(all_data, OUTPUT_FILE)
    print(f"All reports have been processed and saved to {OUTPUT_FILE}")

def main():
    # Process any existing files
    process_files()
    
    # Start the Flask web server
    print("Starting web server...")
    app.run(host='0.0.0.0', port=5001, debug=True)

if __name__ == "__main__":
    main()