import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots
import geonamescache

# Load and prepare data
df = pd.read_csv('ev_charging_stations.csv')
df = df.dropna(subset=['Latitude', 'Longitude'])
df = df[df['Latitude'].between(-90, 90) & df['Longitude'].between(-180, 180)]

# Prepare country data
city_coordinates_df = df[['Address', 'Latitude', 'Longitude']].copy()
city_coordinates_df['City'] = city_coordinates_df['Address'].apply(lambda x: x.split(',')[1].strip())
gc = geonamescache.GeonamesCache()
cities = gc.get_cities()
city_to_country = {city['name']: city['countrycode'] for city in cities.values()}
city_coordinates_df['Country'] = city_coordinates_df['City'].map(city_to_country)
city_coordinates_df.dropna(subset=['Country'], inplace=True)
country_counts = city_coordinates_df['Country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']

# Load world map data
world = gpd.read_file(
    "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
)
world = world.merge(country_counts, left_on='iso_a2', right_on='Country', how='left')

# Prepare operator data
operator_counts = df['Station Operator'].value_counts().reset_index()
operator_counts.columns = ['Operator', 'Count']

# Prepare charger type&rating data
operator_charger_counts = df.groupby(["Station Operator", "Charger Type"]).size().unstack(fill_value=0)
rating_rank = df.groupby('Station Operator')['Reviews (Rating)'].mean().sort_values().reset_index()
rating_rank.columns = ['Operator', 'Rating']

# Create Dashboard (2 rows, 3 cols)
fig = make_subplots(
    rows=2, cols=3,
    specs=[
        [{"type": "choropleth", "colspan": 3}, None, None],
        [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]
    ],
    column_widths=[0.33, 0.33, 0.33],
    row_heights=[2.2, 2],
    subplot_titles=(
        "Charging Stations by Country", 
        "Market Share by Operator",
        "Customer Ratings by Operator",
        "Stations by Charger Type (Grouped)"
    )
)

# Choropleth map
fig.add_trace(
    go.Choropleth(
        geojson=world.geometry.__geo_interface__, # Geographical Boundary Data, turn from df to GeoJSON
        locations=world.index, 
        z=world['Count'],
        colorscale='ylgn',
        hoverinfo='text',
        hovertext = (world['name'] + '<br>Stations: ' + world['Count'].astype(str).str.replace('.0', '')),
        marker_line_color='gray',
        showscale=True,
        colorbar=dict(
            title="Number of Stations",
            x=0.80,
            y=0.80,
            len=0.4,
            thickness=15
        )
    ),
    row=1, col=1
)

# Market share bar chart
fig.add_trace(
    go.Bar(
        x=operator_counts['Operator'],
        y=operator_counts['Count'],
        marker_color='#2c8769',
        name="Market Share",
        text=operator_counts['Count'],  #Show value on the top
        textposition='auto',
        showlegend=False
    ),
    row=2, col=1
)

# Ratings bar chart
fig.add_trace(
    go.Bar(
        y=rating_rank['Operator'],
        x=rating_rank['Rating'],
        orientation='h', #Horizontal bar chart
        marker_color='#88B371',
        name="Ratings",
        showlegend=False
    ),
    row=2, col=2
)

# Grouped bar chart for charger type by operator
charger_colors = {
    "DC": '#FCFED2',
    "AC Level 1": '#B3D295',
    "AC Level 2": '#005430'
}

# Add grouped bar traces with custom colors and cleaned legend
for charger_type in operator_charger_counts.columns:
    fig.add_trace(
        go.Bar(
            x=operator_charger_counts.index,
            y=operator_charger_counts[charger_type],
            name=charger_type,
            marker_color=charger_colors.get(charger_type, "gray"),
            hovertemplate='Operator: %{x}<br>Count: %{y}<br>Type: ' + charger_type + '<extra></extra>',
            showlegend=True 
        ),
        row=2, col=3
    )

# Layout
fig.update_layout(
    height=750, #dashboard
    width=1200,
    legend=dict(x=0.75, y=0.45),
    margin=dict(t=100, b=0, l=30, r=30),
    title_text="Global EV Charging Stations Dashboard",
    title_x=0.5,
    title_y=0.98,
    title_font=dict(size=30),
    barmode='group',
    geo=dict(
        projection_scale=1, #map
        center=dict(lat=0, lon=0),
        fitbounds="locations", 
        domain=dict(x=[0, 1], y=[0.6, 1]),
        showcountries=True,
        countrycolor='gray',
        showcoastlines=True,
        coastlinecolor='black',
        showocean=True,
        oceancolor='lightblue'
    )
)
fig.update_yaxes(range=[800, 1100], row=2, col=1) #Set value range for bar charts
fig.update_xaxes(range=[3.9, 4.1], row=2, col=2)
fig.update_yaxes(range=[0, 400], row=2, col=3)

# Save and show
fig.write_html("ev_dashboard.html", auto_open=True)

