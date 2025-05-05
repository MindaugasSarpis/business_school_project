# Strava Activity Data Analysis

This project explores personal activity data exported from the Strava app. The main objective was to analyze trends and behavior over time using Python and Jupyter Notebook.

## Context

Initially, the Strava app itself did not provide the depth of insights I was looking for. This sparked the idea to extract raw `.csv` data and use Python with data visualization and machine learning tools to explore it further. One long-term goal is to eventually link this analysis to an LLM system for personalized training feedback.

## Dataset Source

- **Exported from:** Strava
- **Rows:** 1,393 (and growing regularly)
- **File:** `strava_activities.csv`

## Key Steps

### Data Cleaning and Parsing
- Initial conversion of `start_date` failed for most rows due to mixed formats.
- Solved using `dateutil.parser` to robustly parse all date entries.

### Feature Engineering
- Extracted year, month, weekday for time-based insights.

### Visual Analysis
- Activities by weekday
- Activity count over time
- Moving time vs. distance scatterplot
- Monthly total distance
- Linear trend using regression

---

> Created as part of the DeepTech Entrepreneurship program at Vilnius University Business School.
