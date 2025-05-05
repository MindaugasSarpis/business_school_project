# Apple Report Parser

## Overview
This application processes Apple transaction reports in TXT format and provides a web-based dashboard for visualizing and managing the data. It aggregates revenue per game and currency, making it easy to analyze Apple App Store transaction data.

## Main Functionality
- Process Apple transaction reports in TXT format
- Aggregate revenue data by game and currency
- Generate consolidated CSV reports
- Interactive web dashboard for data visualization
- File management system for report uploads
- Real-time data updates and filtering capabilities

## System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- 100MB of free disk space
- Internet connection for initial setup

## Installation and Launch

1. **Clone the repository**
   ```sh
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create and activate virtual environment**
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Launch the application**
   ```sh
   python main.py
   ```

5. **Access the dashboard**
   Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```

## Web Interface Guide

### Dashboard
- The main dashboard shows aggregated revenue data by game and currency
- Data is automatically converted to EUR if exchange rates are available
- Missing exchange rates are highlighted for easy identification

### File Management
1. **Upload Files**
   - Click "Upload Files" in the navigation menu
   - Select one or more .txt files to upload
   - Files will be automatically processed

2. **Process Files**
   - Click "Process Files" to manually trigger processing
   - View processing status and results

3. **Delete Files**
   - Go to "Input Files" section
   - Select files to delete
   - Confirm deletion

### Configuration
1. **Game Mapping**
   - Access through "Configuration" menu
   - Map SKU prefixes to game names
   - Set default game name for unmapped SKUs

2. **Exchange Rates**
   - Access through "Exchange Rates" menu
   - View current exchange rates
   - Update rates as needed
   - Rates are used to convert all currencies to EUR

### Data Export
- Click "Download" to export the aggregated data as CSV
- The CSV file includes all processed data with EUR conversions