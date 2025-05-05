import csv
import os
from datetime import datetime
from collections import defaultdict
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.config import GAME_MAPPING, DEFAULT_GAME_NAME

def extract_period(file_path):
    """
    Extracts the Start Date and End Date from the Apple report file.
    Returns the period in YYYY-MM-DD_YYYY-MM-DD format.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    start_date, end_date = None, None

    for line in lines:
        if line.lower().startswith("start date"):
            raw_start_date = line.split("\t")[1].strip()
            start_date = datetime.strptime(raw_start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        elif line.lower().startswith("end date"):
            raw_end_date = line.split("\t")[1].strip()
            end_date = datetime.strptime(raw_end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        if start_date and end_date:
            break

    if not start_date or not end_date:
        raise ValueError(f"Could not extract start and end dates from {file_path}")

    return f"{start_date}_{end_date}"

def parse_apple_report(file_path):
    """
    Parses an Apple report file by manually handling misaligned rows.
    """
    revenue_data = defaultdict(float)
    period = extract_period(file_path)

    print(f"\n=== Processing Report: {file_path} ===")

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Identify the header row dynamically
    header_row = None
    for i, line in enumerate(lines):
        columns = line.strip().split("\t")
        if "SKU" in columns and "Extended Partner Share" in columns and "Partner Share Currency" in columns:
            header_row = i
            break

    if header_row is None:
        print(f"❌ ERROR: Could not find a valid table header in {file_path}")
        raise ValueError(f"Could not find a valid table header in {file_path}")

    print(f"✅ Found table header at line {header_row + 1}")

    header = lines[header_row].strip().split("\t")
    header = [col.lower() for col in header]  # Normalize column names

    # Identify column indexes
    try:
        sku_idx = header.index("sku")
        revenue_idx = header.index("extended partner share")
        currency_idx = header.index("partner share currency")
    except ValueError as e:
        print(f"❌ ERROR: Missing required columns in {file_path}: {e}")
        raise ValueError(f"Missing required columns in {file_path}: {e}")

    # Process each line after the header until "Country of Sale" appears
    for line_num, line in enumerate(lines[header_row + 1:], start=header_row + 2):
        if "country of sale" in line.lower():  # Stop processing beyond valid data
            print(f"🚨 Stopping processing at Line {line_num}: Found 'Country of Sale'")
            break

        columns = line.strip().split("\t")

        # Ensure row has enough columns before processing
        if len(columns) <= max(sku_idx, revenue_idx, currency_idx):
            print(f"⚠️ Skipping row at Line {line_num}: Not enough columns. Extracted: {columns}")
            continue

        sku = columns[sku_idx].strip()
        revenue_value = columns[revenue_idx].strip()
        currency = columns[currency_idx].strip().upper()

        # Ensure that SKU, revenue, and currency exist before processing
        if not sku or not revenue_value or not currency:
            print(f"⚠️ Skipping row {line_num} in {file_path}: Missing SKU, Revenue, or Currency. Extracted: {columns}")
            continue

        # Convert revenue to a number
        try:
            revenue = float(revenue_value)
        except ValueError:
            print(f"⚠️ Skipping row at Line {line_num} in {file_path}: Invalid revenue format ('{revenue_value}'). Extracted: {columns}")
            continue

        # Determine the game name based on SKU
        game_name = DEFAULT_GAME_NAME
        for prefix, name in GAME_MAPPING.items():
            if sku.startswith(prefix):
                game_name = name
                break

        # Group revenue by game and currency
        key = (period, f"{game_name} ({currency})")
        revenue_data[key] += revenue

    return revenue_data

def save_to_csv(all_data, output_file):
    """
    Saves parsed data into a CSV file, sorted first by report period (oldest first),
    then alphabetically by game name.
    """
    output_dir = os.path.dirname(output_file)

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Sort first by period (oldest first), then by game name alphabetically
    sorted_data = sorted(all_data.items(), key=lambda x: (datetime.strptime(x[0][0].split("_")[0], "%Y-%m-%d"), x[0][1]))

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Period", "Name", "Sum"])  # CSV headers

        for (period, game_currency), total in sorted_data:
            writer.writerow([period, game_currency, round(total, 2)])

def process_files(input_folder: str, output_file: str) -> Tuple[bool, List[str]]:
    """
    Process all .txt files in the input folder and save results to output file.
    Returns (success, list of processed files)
    """
    all_data = {}
    processed_files = []
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_folder, filename)
            try:
                report_data = parse_apple_report(file_path)
                # Merge data into all_data
                for key, value in report_data.items():
                    all_data[key] = all_data.get(key, 0) + value
                processed_files.append(filename)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
    
    if all_data:
        save_to_csv(all_data, output_file)
        return True, processed_files
    return False, processed_files