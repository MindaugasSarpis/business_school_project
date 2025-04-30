# 🚦 Traffic Analyzer LT — Traffic Incident Analysis for Lithuania (2023)

## 📋 About the Project

**Traffic Analyzer LT** is a Python-based web application that downloads and analyzes traffic incidents involving humans in **Lithuania (year 2023)**.  
It provides interactive insights and statistics based on real accident data and presents visualizations and aggregated reports.

---

## ✅ Key Features

- **Data Analysis**:
  - Analyzes traffic incidents based on **car types**, **intoxicated drivers**, **deaths**, and **injuries**.
  - Aggregates and visualizes accident data over time and by various categories.
- **Interactive Map**:

  - Displays accidents on a map with pins for each incident location.
  - Allows zooming, panning, and detailed location view.

- **Aggregated Reports**:
  - Provides precomputed data in JSON format for easy access to stats and insights.
  - Includes data about car types, intoxicated drivers, accidents per month, and more.

---

## 🛠️ Installation

### Prerequisites

Ensure you have the following installed:

- **Docker** (to run the application in a containerized environment)
- **Python** (for local development or custom runs)
- **Node.js** (for the frontend build process)

### Clone the repository

```bash
git clone https://github.com/your-repo/traffic-analyzer-lt.git
cd traffic-analyzer-lt
```

### Run application

Starting backend may take up to 5 minutes to get the data and aggregate it

```bash
docker-compose up
```
