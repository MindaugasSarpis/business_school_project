# 🌍 Global EV Charging Stations Dashboard

This project visualizes global electric vehicle (EV) charging infrastructure using an interactive dashboard built with Python, Plotly, and GeoPandas. The dashboard includes geospatial and statistical insights into the distribution of charging stations, operator market share, charger types, and customer ratings.

## 📊 Dashboard Features

The generated dashboard (`ev_dashboard.html`) includes:

- **Choropleth Map** of EV charging stations by country
- **Bar Chart** showing station market share by operator
- **Horizontal Bar Chart** ranking operators by customer ratings
- **Grouped Bar Chart** of charger type distribution by operator

## 🧰 Tech Stack

- **Python 3.8+**
- **Pandas** – for data manipulation
- **GeoPandas** – for geospatial processing
- **Plotly** – for interactive visualizations
- **Geonamescache** – for city-to-country mapping

## 📁 Data Requirements

The script expects an input CSV file named `ev_charging_stations.csv` in the same directory. The file should include at least the following columns:

- `Address` (with city and country info)
- `Latitude`, `Longitude`
- `Station Operator`
- `Charger Type`
- `Reviews (Rating)`

# 🚀 How to Run
Install required packages:

pip install pandas  
pip install geopandas  
pip install plotly  
pip install geonamescache  
  
Place your dataset in the same directory as the script:
  
ev_charging_stations.csv
  
Run the script: python ev_dashboard.py    
The dashboard will automatically open in your default browser as ev_dashboard.html.

# 📌 Notes
The map uses live GeoJSON data from Natural Earth.

Only valid coordinates are used (Latitude between -90 and 90, Longitude between -180 and 180).

City-to-country matching is based on the second comma-separated component in the Address field. Ensure your address formatting supports this.

# 📄 License
This project is open-source and available under the MIT License.
