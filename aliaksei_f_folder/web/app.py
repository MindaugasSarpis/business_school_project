from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_cors import CORS
import os
import sys
import csv
import json
from pathlib import Path
from werkzeug.utils import secure_filename
import pandas as pd

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.parser import parse_apple_report, save_to_csv, process_files
from scripts.config import GAME_MAPPING, DEFAULT_GAME_NAME
from scripts.rates import EXCHANGE_RATES, LAST_UPDATED

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).parent.parent

# Configuration
UPLOAD_FOLDER = str(PROJECT_ROOT / 'data' / 'input')
ALLOWED_EXTENSIONS = {'txt'}
OUTPUT_FOLDER = str(PROJECT_ROOT / 'data' / 'output')
CONFIG_FILE = str(PROJECT_ROOT / 'scripts' / 'config.py')
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, 'combined_output.csv')

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_output_data():
    """Read and return data from the output CSV file."""
    if not os.path.exists(OUTPUT_FILE):
        return None
    
    data = []
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def read_config():
    """Read the current configuration from config.py."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract GAME_MAPPING
            game_mapping = {}
            mapping_start = content.find('GAME_MAPPING = {')
            if mapping_start != -1:
                mapping_end = content.find('}', mapping_start) + 1
                mapping_str = content[mapping_start:mapping_end]
                # Parse the dictionary using eval (safe in this context as we control the file)
                try:
                    game_mapping = eval(mapping_str.split('=', 1)[1].strip())
                except:
                    pass
            
            # Extract DEFAULT_GAME_NAME
            default_game = "Race Mobile Game"
            default_start = content.find('DEFAULT_GAME_NAME =')
            if default_start != -1:
                default_end = content.find('\n', default_start)
                default_str = content[default_start:default_end]
                try:
                    default_game = eval(default_str.split('=', 1)[1].strip().split('#')[0])
                except:
                    pass
            
            return game_mapping, default_game
    except Exception as e:
        print(f"Error reading config: {str(e)}")
        return {}, "Race Mobile Game"

def write_config(game_mapping, default_game):
    """Write the configuration back to config.py."""
    try:
        config_content = f"""GAME_MAPPING = {{
"""
        for key, value in game_mapping.items():
            config_content += f'    "{key}": "{value}",\n'
        config_content += f"""}}

DEFAULT_GAME_NAME = "{default_game}"  # All other SKUs belong to {default_game}
"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(config_content)
        return True
    except Exception as e:
        print(f"Error writing config: {str(e)}")
        return False

def get_currencies_from_data(data):
    currencies = set()
    for row in data:
        if '(' in row['Name']:
            currency = row['Name'].split('(')[1].strip(')')
            currencies.add(currency)
    return currencies

def convert_to_eur(data, rates):
    # Dictionary to store aggregated amounts by game name and period
    aggregated_data = {}
    
    for row in data:
        if '(' in row['Name']:
            game_name, currency = row['Name'].split('(')
            game_name = game_name.strip()
            currency = currency.strip(')')
            period = row['Period']
            
            if currency in rates:
                converted_amount = float(row['Sum']) * rates[currency]
                
                # Create a key for the game and period
                key = (game_name, period)
                
                # Add or update the aggregated amount
                if key in aggregated_data:
                    aggregated_data[key] += converted_amount
                else:
                    aggregated_data[key] = converted_amount
    
    # Convert the aggregated data back to a list format
    converted_data = []
    for (game_name, period), amount in aggregated_data.items():
        converted_data.append({
            'Period': period,
            'Name': game_name,
            'Sum': round(amount, 2)  # Round to 2 decimal places
        })
    
    return converted_data

@app.route('/')
def dashboard():
    output_data = get_output_data()
    if not output_data:
        return render_template('dashboard.html', output_data=None)
    
    # Check if we have all required exchange rates
    currencies = get_currencies_from_data(output_data)
    rates = EXCHANGE_RATES
    
    missing_currencies = [c for c in currencies if c not in rates]
    if missing_currencies:
        # Show the table with original data, but indicate missing rates
        return render_template('dashboard.html', 
                            output_data=output_data,
                            missing_currencies=missing_currencies)
    
    # Convert all amounts to EUR
    converted_data = convert_to_eur(output_data, rates)
    return render_template('dashboard.html', 
                        output_data=converted_data,
                        missing_currencies=None)

@app.route('/input-files')
def input_files():
    """Page for managing input files."""
    input_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.txt')]
    return render_template('input_files.html', input_files=input_files)

@app.route('/config')
def config():
    """Configuration management page."""
    game_mapping, default_game = read_config()
    return render_template('config.html', 
                         game_mapping=game_mapping,
                         default_game=default_game)

@app.route('/update-config', methods=['POST'])
def update_config():
    """Update the configuration."""
    game_mapping = {}
    for key, value in request.form.items():
        if key.startswith('game_'):
            game_id = key[5:]  # Remove 'game_' prefix
            game_mapping[game_id] = value
    
    default_game = request.form.get('default_game', 'Race Mobile Game')
    
    if write_config(game_mapping, default_game):
        flash('Configuration updated successfully')
    else:
        flash('Error updating configuration')
    
    return redirect(url_for('config'))

@app.route('/delete-file/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete a specific input file."""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'File {filename} deleted successfully')
    return redirect(url_for('input_files'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    if 'files[]' not in request.files:
        flash('No file part')
        return redirect(url_for('input_files'))
    
    files = request.files.getlist('files[]')
    if not files or not files[0].filename:
        flash('No selected file')
        return redirect(url_for('input_files'))
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            flash(f'File {filename} uploaded successfully')
    
    return redirect(url_for('input_files'))

@app.route('/process-files', methods=['POST'])
def process_files_route():
    """Process all input files and generate new output."""
    success, processed_files = process_files(UPLOAD_FOLDER, OUTPUT_FILE)
    if success:
        flash(f'Successfully processed files: {", ".join(processed_files)}')
    else:
        flash('No valid data was processed from existing files')
    return redirect(url_for('dashboard'))

@app.route('/download')
def download_file():
    """Download the output CSV file."""
    return send_file(OUTPUT_FILE, as_attachment=True)

@app.route('/exchange-rates')
def exchange_rates():
    # Get current rates
    rates = EXCHANGE_RATES
    
    # Get all possible currencies from the output file if it exists
    currencies = set()
    output_data = get_output_data()
    if output_data:
        currencies = get_currencies_from_data(output_data)
    
    # Add any currencies that are in the rates but not in current data
    currencies.update(set(rates.keys()))
    
    # Remove EUR from the list since we don't need its exchange rate
    currencies.discard('EUR')
    
    return render_template('exchange_rates.html', 
                         currencies=sorted(list(currencies)), 
                         rates=rates)

@app.route('/update-exchange-rates', methods=['POST'])
def update_exchange_rates():
    rates = {}
    for key, value in request.form.items():
        if key.startswith('rate_'):
            currency = key.replace('rate_', '')
            try:
                # Convert to float and round to 5 decimal places
                rate = round(float(value.replace(',', '.')), 5)
                rates[currency] = rate
            except ValueError:
                flash(f"Invalid exchange rate format for {currency}. Please use numbers with up to 5 decimal places.", "error")
                return redirect(url_for('exchange_rates'))
    
    # Update rates in the file
    rates_content = '''"""
Exchange rates configuration.
Rates are stored as a dictionary where keys are currency codes and values are the exchange rate to EUR.
Example: 1 USD = 0.92 EUR means USD: 0.92
"""

# Exchange rates relative to EUR (1 EUR = X Currency)
EXCHANGE_RATES = {
'''
    for currency, rate in rates.items():
        rates_content += f'    "{currency}": {rate},  # 1 {currency} = {rate} EUR\n'
    rates_content += '''}

# Last update timestamp
LAST_UPDATED = "''' + pd.Timestamp.now().isoformat() + '''"
'''
    
    with open(PROJECT_ROOT / 'scripts' / 'rates.py', 'w') as f:
        f.write(rates_content)
    
    flash("Exchange rates updated successfully!", "success")
    return redirect(url_for('dashboard')) 