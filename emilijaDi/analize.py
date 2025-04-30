import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import os

# Load the data
data = pd.read_csv('data.csv')

# Calculate statistics
total_sales = data['Sales'].sum()
mean_sales = data['Sales'].mean()
median_sales = data['Sales'].median()
std_sales = data['Sales'].std()

# Group data for visualizations
region_sales = data.groupby('Region')['Sales'].sum().reset_index()
product_sales = data.groupby('Product')['Sales'].sum().reset_index()

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Sales Data Analysis Dashboard", style={'textAlign': 'center'}),
    
    # Statistics Section
    html.Div([
        html.H3("Key Statistics"),
        html.P(f"Total Sales: ${total_sales:,.2f}"),
        html.P(f"Mean Sales: ${mean_sales:,.2f}"),
        html.P(f"Median Sales: ${median_sales:,.2f}"),
        html.P(f"Standard Deviation of Sales: ${std_sales:,.2f}"),
    ], style={'border': '2px solid #ddd', 'padding': '10px', 'margin': '10px'}),
    
    # Bar Chart: Sales by Region
    html.Div([
        html.H3("Sales by Region"),
        dcc.Graph(
            id='region-bar-chart',
            figure=px.bar(region_sales, x='Region', y='Sales', title='Total Sales by Region')
        )
    ], style={'border': '2px solid #ddd', 'padding': '10px', 'margin': '10px'}),
    
    # Pie Chart: Sales Distribution by Product
    html.Div([
        html.H3("Sales Distribution by Product"),
        dcc.Graph(
            id='product-pie-chart',
            figure=px.pie(product_sales, values='Sales', names='Product', title='Sales Distribution by Product')
        )
    ], style={'border': '2px solid #ddd', 'padding': '10px', 'margin': '10px'}),
    
    # Map: Sales by Region
    html.Div([
        html.H3("Sales by Region (Map)"),
        dcc.Graph(
            id='region-map',
            figure=px.choropleth(region_sales, locations='Region', locationmode='USA-states', 
                                  color='Sales', scope="usa", title='Sales by Region (USA)')
        )
    ], style={'border': '2px solid #ddd', 'padding': '10px', 'margin': '10px'})
])

# Open the browser manually
os.system("start http://127.0.0.1:8050/")  # For Windows
# os.system("open http://127.0.0.1:8050/")  # For macOS
# os.system("xdg-open http://127.0.0.1:8050/")  # For Linux

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)