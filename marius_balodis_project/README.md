# 🚲 Bike Traffic Analysis Dashboard

## Author's experience

**Author:** Marius Balodis

**Experience:**
- Experienced with BI tools, ML concepts, data analysis & vizualization
- Low level coding experience with C++, read a lot of code formats like json, xml, html
- Little to none experience with Python

## Project description

This is a data analysis project for Vilnius University Business School Master's course "Data Science and Artificial Intelligence". 

Final product of this project is an interactive Streamlit app dashboard that analyzes bicycle traffic paterns in Vilnius, Žvejų g. throughout period from 2019-01-01 to 2023-04-23. Dashboard contains analysis of events and trends, bike traffic correlation with weather as well as traffic numbers forecast for period from 2023-04-23 to 2025-04-29. 

Sources of data includes [Meteostat archive](https://meteostat.net/en/place/lt/vilnius?s=26730&t=2023-04-23/2025-04-29) and [bicycle traffic data from VDA](https://atviri-duomenys.stat.gov.lt/datasets/LTdata::%C5%BEvej%C5%B3-g-dvira%C4%8Di%C5%B3-sraut%C5%B3-duomenys/explore?showTable=true) as [CC BY 4.0 INTERNATIONAL LICENCE](https://creativecommons.org/licenses/by/4.0/)

## 🚀 Run the App

1. Clone this repo** or download the project files to your local machine.

2. Navigate to the project directory in your terminal:
    ```
    cd your-project-folder-name
    ```

3. Create and activate a virtual environment (recommended):
#### For Windows:
```
    python -m venv venv
    venv\Scripts\activate
```
#### For macOS/Linux:
```
    python3 -m venv venv
    source venv/bin/activate
```

4. Install the dependencies listed in requirements.txt:
```
        pip install -r requirements.txt
```

5. (OPTIONAL) Launch [Jupyter environment lab](https://jupyter.org/)
```
        pip install jupyterlab

        jupyter lab
```
7. Launch the Streamlit app:
```
        streamlit run app.py
```
   
*The app will open in your default web browser. If not, follow the terminal link (usually http://localhost:8501).*



## Dashboard Features

### 1. Trends
- Interactive filters: by date range, season, and time of day
- KPI metrics for total and average bike counts
- Time series charts with 30-day moving averages
- Weekly heatmap of bike activity
- Most popular hours with bar charts and top-10 peaks

### 2. Weather
- Correlation between weather conditions and bike usage
- KPIs and plots for:
  - Temperature
  - Precipitation
  - Wind Speed
  - Air Pressure
- Polynomial and linear regression models with equations
- All weather features filtered by the same controls as in Trends tab

### 3. Prediction
- Four different ML models (Linear Regression, Polynomial Regression, Random Forest)
- Coefficient and R² score tables for each
- Feature importances and predicted vs actual scatter plots
- Future forecasts calculated on-the-fly
- Top predicted peaks highlighted dynamically

## Technologies

- Python 3.10+
- Jupyter for coding
- [Streamlit](https://streamlit.io/)
- pandas, numpy
- plotly, matplotlib
- scikit-learn

## Project Structure

```
├── data/
│ ├── merged_data.csv # Main dataset (weather + bike counts)
│ ├── source_data.csv # Raw bikes dataset
│ ├── bike_data_cleaned.csv # Had to clean the raw dataset
│ ├── weather_data.csv # Raw weather dataset from 2019-01-01 to 2023-04-23
│ ├── weather_data2.csv # Raw weather dataset from 2023-04-23 to 2025-04-29
│ └── future_predictions.csv # precomputed predictions from 02_analysis.ipynb (not used for streamlit app)
├── notebooks/
│ ├── 01_data_cleaning.ipynb # Prepared CSVs
│ └── 02_analysis.ipynb # Used as testing env to test majority of Streamlit app building blocks
├── venv/ # Just a virtual environment directory
├── utils/
│ ├── date_mappings.py # index.weekday join and index.month join as functions
│ └── spike_labels.py # Just a dictionary of pre-determined spikes for "TRENDS" tab
├── app.py # Main Streamlit app
├── requirements.txt
└── README.md
```