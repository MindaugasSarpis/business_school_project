# Student Depression Analysis Dashboard

An interactive dashboard for analyzing student depression data, providing comprehensive visualizations and statistical insights.

## Features

- Interactive data exploration
- Multiple visualization types:
  - Histograms
  - Box plots
  - Correlation heatmaps
  - Distribution plots
- Statistical summaries
- Real-time updates
- Modern, responsive design

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository or download the source code

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Required Packages

- pandas==2.1.0
- plotly==5.17.0
- dash==2.13.0
- dash-bootstrap-components==1.4.2

## Usage

1. Place your CSV data file in the same directory as the script
2. Run the dashboard:
```bash
python depression_analysis.py
```
3. Open your web browser and navigate to:
```
http://127.0.0.1:8050/
```

## Dashboard Components

### 1. Dataset Overview
- Total number of students
- Number of features
- List of all columns

### 2. Feature Selection
- Dropdown menu to select features for analysis
- Real-time updates of all visualizations

### 3. Statistical Analysis
- Mean, median, standard deviation
- Minimum and maximum values
- Distribution analysis

### 4. Visualizations
- Histograms for numeric data
- Box plots for numeric data
- Correlation heatmap (excluding ID columns)
- Detailed distribution plots

## Data Requirements

The dashboard expects a CSV file with the following characteristics:
- UTF-8 encoding
- Numeric and categorical columns
- No special formatting requirements

## Customization

You can customize the dashboard by:
1. Modifying the color scheme in the `colors` dictionary
2. Adjusting the layout in the `app.layout` section
3. Adding new visualizations in the callbacks

## Troubleshooting

Common issues and solutions:

1. **Module not found error**
   - Ensure all required packages are installed
   - Run `pip install -r requirements.txt`

2. **File not found error**
   - Check if the CSV file is in the correct directory
   - Verify the file name matches the one in the code

3. **Visualization errors**
   - Ensure data types are correct
   - Check for missing or invalid data

## Contributing

Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests

## License

This project is open source and available under the MIT License.
