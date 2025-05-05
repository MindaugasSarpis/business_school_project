import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import socket

# My All Load data
@st.cache_data
def load_data():
    return pd.read_csv("Europe_GDP.csv")

data = load_data()

# Page configuration
st.set_page_config(
    page_title="Europe GDP Dashboard",
    page_icon="📊",
    layout="wide"
)

# Webpage Sidebar filters
st.sidebar.title("Filters")
country_options = data.columns.drop('Year').tolist()
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    country_options,
    default=["Finland", "Norway", "Germany"]
)

year_range = st.sidebar.slider(
    "Year Range",
    min_value=int(data['Year'].min()),
    max_value=int(data['Year'].max()),
    value=(2000, 2020)
)

# Main things and content of my project
st.title("Europe GDP Analysis")
st.markdown(f"*Running on {socket.gethostbyname(socket.gethostname())}*")

if not selected_countries:
    st.warning("Please select at least one country")
    st.stop()

# Filter My Project Data in web page
filtered_data = data[
    (data['Year'] >= year_range[0]) & 
    (data['Year'] <= year_range[1])
][['Year'] + selected_countries]

# Calculate metrics for all EUropean GDP
metrics = {}
for country in selected_countries:
    metrics[country] = {
        'current': filtered_data[country].iloc[-1],
        'growth': filtered_data[country].pct_change().iloc[-1] * 100,
        'max': filtered_data[country].max(),
        'min': filtered_data[country].min()
    }

# Metrics cards statistics
cols = st.columns(len(selected_countries))
for idx, country in enumerate(selected_countries):
    cols[idx].metric(
        label=country,
        value=f"${metrics[country]['current']:,.0f}",
        delta=f"{metrics[country]['growth']:.1f}% YoY"
    )
style_metric_cards()

# Main charts (will show in Dashboard)
tab1, tab2, tab3 = st.tabs(["GDP Trend", "Growth Rate", "Top Countries"])

with tab1:
    fig = px.line(
        filtered_data, 
        x='Year', 
        y=selected_countries,
        title='GDP Over Time (USD)',
        labels={'value': 'GDP', 'variable': 'Country'}
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    growth_data = filtered_data.set_index('Year').pct_change() * 100
    fig_growth = px.line(
        growth_data,
        title='Annual GDP Growth Rate (%)',
        labels={'value': 'Growth %', 'variable': 'Country'}
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with tab3:
    year = st.selectbox("Select Year for Ranking", filtered_data['Year'].unique())
    top_n = st.slider("Number of Countries", 3, 10, 5)
    
    ranked = data[data['Year'] == year].drop(columns='Year').T
    ranked.columns = ['GDP']
    ranked = ranked.sort_values('GDP', ascending=False).head(top_n)
    
    fig_rank = px.bar(
        ranked,
        x=ranked.index,
        y='GDP',
        title=f"Top {top_n} Economies in {year}"
    )
    st.plotly_chart(fig_rank, use_container_width=True)

# Correlation matrix(Here all correlation will be shown)
st.subheader("GDP Correlation Matrix")
corr_matrix = filtered_data[selected_countries].corr()
fig_corr = px.imshow(
    corr_matrix,
    text_auto=True,
    title="How GDP Trends Correlate"
)
st.plotly_chart(fig_corr, use_container_width=True)

# Data Download System(will be download CSV file)
st.download_button(
    "📥 Download Filtered Data",
    filtered_data.to_csv(index=False),
    "europe_gdp_filtered.csv"
)

# Displaying credit message of my Project 
st.markdown("""
    <hr>
    <p style="text-align: center;">
        <strong>This project is made by Mashrur Alam</strong><br>
        Vilnius University, DeepTech Entrepreneurship<br>
            Thanks a lot Dr. Mindaugas Sarpis
    </p>
    <hr>
""", unsafe_allow_html=True)

#The End, Thanks a lot
