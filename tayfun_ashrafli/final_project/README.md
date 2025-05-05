<p align="center">
  <a href="#-project-overview">Overview</a> •
  <a href="#-repository-structure">Structure</a> •
  <a href="#%EF%B8%8F-quickstart">Quickstart</a> •
  <a href="#%F0%9F%93%88-results">Results</a> •
  <a href="#%F0%9F%94%A7-next-steps">Next Steps</a> •
  <a href="#%F0%9F%93%84-license">License</a>
</p>

---

## Smoke‑Aware City Forecasting
Wildfire smoke significantly elevates fine particulate matter (PM₂.₅) levels, posing health risks to Reno residents. This project builds a simple forecasting pipeline to predict tomorrow’s average PM₂.₅ concentration using today’s satellite fire hotspot counts and yesterday’s PM₂.₅ readings. A reliable 24‑hour ahead forecast enables public health agencies and individuals to make informed decisions about outdoor activities.

---

## 🔍 Project Overview

Wildfire smoke is Reno’s major air-quality threat, driving dangerous PM₂.₅ spikes.  
This repo demonstrates a simple, end-to-end workflow:

1. **Ingest** hourly PM₂.₅ via OpenAQ v3 API (2015–2025)  
2. **Download** daily MODIS fire-pixel counts (2021–2025)  
3. **Explore** data with line plots & boxplots  
4. **Baseline**: “tomorrow = yesterday” → MAE ≈ 3.91 µg/m³  
5. **Model**: Random Forest (fire pixels + yesterday’s PM₂.₅) → MAE ≈ 1.72 µg/m³  

---

## 📂 Repository Structure

```text
smoke-aware-city/
├── data/                   # Raw & processed CSVs
│   ├── pm25_Reno_2024-07-01.csv
│   └── fires_Reno_2025.csv
├── notebooks/              # Jupyter notebooks
│   ├── 01_download.ipynb   # Data ingestion
│   ├── 02_eda.ipynb        # EDA plots
│   ├── 03_baseline.ipynb   # Baseline MAE
│   └── 05_model.ipynb      # Random Forest model
├── figures/                # Exported chart images
├── environment.yml         # Conda environment spec
├── README.md               # This file
└── LICENSE                 # MIT License
```
---

🚀 Quickstart


1. Clone the repository

git clone https://github.com/<your-username>/smoke-aware-city.git

cd smoke-aware-city

2. Create the environment


Using Conda:

conda env create -f environment.yml | conda activate smoke-aware-env

Or with venv + pip:

python -m venv .venv | source .venv/bin/activate  # Linux/macOS  | .venv\Scripts\activate    # Windows

pip install -r requirements.txt


---


3. Ingest data


Open notebooks/01_download.ipynb and run all cells to download PM₂.₅ and fire-pixel data.

Inspect data/ to verify that CSV files appear.

---

4. Explore and model


Sequentially run the EDA, baseline, and model notebooks:

notebooks/02_eda.ipynb

notebooks/03_baseline.ipynb

notebooks/05_model.ipynb

Each notebook prints metrics and displays key plots.


---


📈 Results
Baseline MAE (yesterday → tomorrow): 3.91 µg/m³

Random Forest MAE (with fire-pixels + previous PM₂.₅): 1.72 µg/m³

These results illustrate that satellite-detected fire activity is a strong predictor of next-day PM₂.₅.
