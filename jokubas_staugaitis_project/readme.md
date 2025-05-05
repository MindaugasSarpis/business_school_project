# Truck Accident Report Generator

## Overview

The Truck Accident Report Generator is a Python application that processes truck accident data from Excel files and generates comprehensive PDF reports. The application provides:

- Data visualization through charts and tables
- Daily accident summaries
- Monthly comparison statistics
- Driver accident leaderboards
- Email functionality to send reports directly from the application

## Features

- **User-friendly GUI** built with Tkinter
- **Excel data processing** with pandas
- **Professional PDF reports** with ReportLab
- **Data visualization** with Matplotlib and Seaborn
- **Email integration** via Outlook
- **Preview functionality** to view generated charts
- **Progress tracking** during report generation

## System Requirements

- Windows OS (for Outlook email functionality)
- Python 3.7+
- Required Python packages (listed in Installation)

## Installation

1. Clone or download the repository
2. Install required dependencies:
   ```
   pip install pandas matplotlib seaborn numpy reportlab pywin32 pillow openpyxl
   ```

## Usage

### 1. Launch the Application
Run the script:
```
python report_generator.py
```

### 2. Select Excel File
- Click "Browse Excel File" to select your input Excel file
- The Excel file must contain these columns:
  - Truck type
  - Licence plate number
  - Driver
  - Date
  - Fault
  - Type
  - Description

### 3. Generate Report
- Click "Generate Report" to process the data and create a PDF
- The report will be saved to your Documents folder with today's date

### 4. View Report
- Click "Preview Report" to see chart visualizations
- Click "Open PDF" in the preview to view the full report

### 5. Email Report (Optional)
- Click "Send Email" to open the email dialog
- Enter recipient(s), subject, and message
- Click "Send Email" to send via Outlook

## Report Contents

The generated PDF report includes:

1. **Daily Summary Statistics**
   - Accident count by driver fault
   - Accident count by truck type

2. **New Accidents Today**
   - Detailed table of today's accidents

3. **Monthly Comparison**
   - Current month vs. previous months average
   - Daily trend for last 30 days

4. **Driver Leaderboards**
   - Top 20 drivers by total accidents
   - Top 5 drivers for current month
