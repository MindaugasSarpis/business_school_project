
# 🎓 Academic Expenditure Dashboard

Welcome to the **Academic Expenditure Dashboard**, a Streamlit-based interactive tool for visualizing and analyzing academic department expenditure data over time.

<p align="center">
  <img src="https://img.shields.io/badge/streamlit-v1.32.0-brightgreen" />
  <img src="https://img.shields.io/badge/pandas-✓-blue" />
  <img src="https://img.shields.io/badge/plotly-✓-orange" />
  <img src="https://img.shields.io/badge/status-Active-success" />
</p>

---

## 📌 Project Overview

This dashboard enables users to:
- 📊 Explore yearly academic expenditures by department  
- 📈 Analyze trends and year-over-year growth  
- 🏅 Identify top spending departments  
- 📎 Download filtered data in CSV and Excel formats  

Use intuitive filters to dive deep into financial data across years and departments. Great for institutional research, financial planning, or academic administration.

---

## 🚀 Getting Started

### 1. Install Dependencies

Make sure computer has Python installed (preferably 3.8 or above).

```bash
pip install streamlit pandas plotly openpyxl xlsxwriter
```

### 2. Run the App

```bash
python -m streamlit run deep.py

```

Once launched, the dashboard will open in default web browser at:

```
http://localhost:8501
```

---

## 📁 File Structure

```bash
📂 academic-expenditure-dashboard/
│
├── app.py                        # Main Streamlit application
├── academic_expenditure_01_22.csv # Source dataset
├── README.md                     # Project overview and instructions
```

---

## 🧾 Features

- 🔍 **Dynamic Filtering**  
  Filter data by department and year range with interactive sidebar widgets.

- 📈 **Visual Analytics Tabs**  
  - Expenditure trends  
  - Year-over-year growth rates  
  - Top departments by total spend  
  - Raw data preview

- 🎯 **KPI Summary**  
  Quick stats like total, average, and latest year expenditures.

- 🥧 **Pie Chart**  
  Visualize each department's share of total expenditure.

- 📤 **Export Options**  
  Download filtered data as Excel or CSV.

---



## 🙋‍♀️ About the Author

**Rahat Sultana**  
📍 MSc DeepTech Entrepreneurship  
🏫 Vilnius University  
✉️ rahat.sultana.gsa@gmail.com

---

## 📄 License

This project does not have an official license.  
It is intended for **educational and non-commercial use only**.  
Please contact the author for permission if you wish to reuse or adapt this project for other purposes.
