# Sales Analysis for App Store In-Game Purchases

## Summary
A Python tool which converts raw reports into structured, currency-normalized summaries with visual insights.

## Problem

Game developers working with Apple App Store often use built-in analytics to monitor in-game sales. While these tools offer convenient summaries, they have limitations in precision and customization. For those looking to gain more control and insight, working with raw transaction data provides a valuable alternative. 

App Store Connect allows developers to download raw transaction-level reports in TXT format. However, these files are hard to work with. Each report may contain thousands of entries, lacks a structured format, and includes extraneous header and footer information. Additionally, transactions come in various currencies, making financial aggregation impossible without conversion. The primary goal is to process this data into structured summaries that are accurate and insightful.

## Data Analysis Process

Between January and March 2025, original reports were downloaded from App Store Connect. Due to confidentiality requirements, synthetic reports were generated to replicate the structure and patterns of the real data.

A Python application was developed to automate data cleaning, analysis, and visualization. The table below outlines the main tasks handled by the tool:

| **Function**            | **Details**                                                                                                                                     |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **Data Cleaning**       | Strips out irrelevant headers and footers, converts all financial values into numeric format, and parses each row into a clean CSV structure.   |
| **Data Analysis**       | Groups transactions by game, converts all sales amounts into EUR using exchange rates, and calculates total monthly revenue per game.            |
| **Data Visualization**  | Generates pie and bar charts to show sales distribution across games, and line charts to visualize revenue trends over time.                     |

## Machine Learning

To evaluate whether machine learning could add value, a prototype was created in Google Colab using K-Means clustering on transaction features. Results showed weak clustering and limited insight, suggesting that richer or labeled data would be needed for more meaningful outcomes. Therefore, machine learning features were not added to the main application.

Full details and evaluation can be found in the notebook:  
[Google Colab Notebook](https://colab.research.google.com/drive/1KqGK1F7its-IMZS85Wdz5pffzifwR6ga?usp=sharing)

## Key Insights

This project demonstrated that raw TXT reports from App Store Connect can be transformed into accurate and insightful sales summaries. Currency conversion is critical for financial aggregation, and even basic visualizations reveal valuable trends. While machine learning was explored, the dataset's structure and content limited its effectiveness. Still, this approach provides a solid foundation for more advanced analytics in the future.

## Next Steps

Future improvements may include adding support for reports from other platforms (Google Play, Amazon App Store, etc.), introducing more flexible filters for dates, countries, or SKUs, and acquiring a richer dataset that would make machine learning models more effective. Automating the monthly report processing pipeline would also make the tool more useful.