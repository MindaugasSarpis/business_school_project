import pandas as pd
import streamlit as st
import plotly.express as px
import socket
import io

# Starting with this for Streamlite and Page configuration(without in this position it was not running properly)
st.set_page_config(
    page_title="Academic Expenditure Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load the csv file into the project
@st.cache_data
def load_data():
    df = pd.read_csv("academic_expenditure_01_22.csv")
    df = df.melt(id_vars='department_name', var_name='Year', value_name='Expenditure')
    df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
    df['Expenditure'] = pd.to_numeric(df['Expenditure'], errors='coerce')
    return df

data = load_data()

# Sidebar Filters
st.sidebar.title("🔹 Filters")
departments = data['department_name'].unique().tolist()
selected_departments = st.sidebar.multiselect(
    "Select Departments",
    options=sorted(departments),
    default=departments[:5],
    help="Search and select departments to view their expenditure data"
)

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(data['Year'].min()),
    max_value=int(data['Year'].max()),
    value=(2001, 2021)
)

# Main Title and Storytelling Introduction
st.title("🎓 Academic Department Expenditure Analysis")
st.markdown(f"*Running on {socket.gethostbyname(socket.gethostname())}*")

with st.container():
    st.markdown("### 🧾 About This Dashboard")
    st.markdown("""
        Welcome to the **Academic Expenditure Dashboard**.  
        This interactive tool lets you explore how various academic departments allocated their funds over the years.  
        Use the filters on the left to dive into departments and time periods.  
        Discover patterns, track growth, and identify top spenders — all at a glance! 🌟
    """)

st.markdown("---")

# Filter Data Based on Selections
filtered_data = data[
    (data['department_name'].isin(selected_departments)) &
    (data['Year'].between(year_range[0], year_range[1]))
]

# Debuging: Show filtered data
st.write("✅ Filtered data preview:")
st.dataframe(filtered_data.head())
st.write("Filtered data shape:", filtered_data.shape)

if filtered_data.empty:
    st.warning("⚠️ No data available for selected filters. Please adjust filters.")
    st.stop()

# Metrics Summary
st.subheader("📊 Summary KPIs")
total_spent = filtered_data['Expenditure'].sum()
avg_spent = filtered_data['Expenditure'].mean()
latest_year = filtered_data['Year'].max()
top_department = filtered_data.groupby("department_name")["Expenditure"].sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Expenditure", f"${total_spent:,.0f}")
col2.metric("📈 Average Expenditure", f"${avg_spent:,.0f}")
col3.metric("📅 Latest Year", latest_year)

st.info(f"🏅 **Top Spending Department** so far: `{top_department}`")

st.markdown("---")
st.markdown("### 📈 Visual Insights")

# Tabs for Visualization
tab1, tab2, tab3, tab4 = st.tabs(["Expenditure Trend", "Growth Rate", "Top Departments", "Raw Data"])

# Set color palette
color_palette = px.colors.qualitative.Set2

# Tab 1: Trend analysis of data
with tab1:
    fig_trend = px.line(
        filtered_data,
        x='Year',
        y='Expenditure',
        color='department_name',
        markers=True,
        color_discrete_sequence=color_palette,
        title="Annual Department Expenditure Over Time"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Tab 2: Year Over Year (YoY) Growth
with tab2:
    growth_df = filtered_data.sort_values(['department_name', 'Year'])
    growth_df['YoY Growth (%)'] = growth_df.groupby('department_name')['Expenditure'].pct_change() * 100
    fig_growth = px.line(
        growth_df.dropna(),
        x='Year',
        y='YoY Growth (%)',
        color='department_name',
        color_discrete_sequence=color_palette,
        title="Year-over-Year Expenditure Growth (%)"
    )
    fig_growth.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_growth, use_container_width=True)

# Tab 3: Top Departments(According to the expense)
with tab3:
    top_n = st.slider("Select Top N Departments", 3, 10, 5)
    top_total = filtered_data.groupby('department_name')['Expenditure'].sum().sort_values(ascending=False).head(top_n)
    fig_top = px.bar(
        top_total,
        x=top_total.index,
        y=top_total.values,
        labels={'x': 'Department', 'y': 'Total Expenditure'},
        title=f"Top {top_n} Departments by Total Expenditure",
        color_discrete_sequence=['#636EFA']
    )
    st.plotly_chart(fig_top, use_container_width=True)

# Tab 4: Raw Data showing Tab
with tab4:
    with st.expander("🔍 View Raw Data"):
        st.dataframe(filtered_data.sort_values(by=["Year", "department_name"]))

# Percentage Contribution Section
st.markdown("---")
st.markdown("### 🧮 Percentage Contribution by Department")

contribution_df = filtered_data.groupby('department_name')['Expenditure'].sum().reset_index()
contribution_df['Percentage'] = (contribution_df['Expenditure'] / contribution_df['Expenditure'].sum()) * 100

fig_pie = px.pie(
    contribution_df,
    values='Percentage',
    names='department_name',
    title="Share of Total Expenditure (%)",
    hole=0.4  # donut-style
)
fig_pie.update_traces(textinfo='percent+label')

st.plotly_chart(fig_pie, use_container_width=True)

# Optional Tab for showing percentage table(It will be hidden)
with st.expander("📋 View Percentage Table"):
    st.dataframe(contribution_df.sort_values(by="Percentage", ascending=False).style.format({"Expenditure": "${:,.0f}", "Percentage": "{:.2f}%"}))


# Download buttons and options(CSV and Excel)
excel_buffer = io.BytesIO()
filtered_data.to_excel(excel_buffer, index=False, engine='xlsxwriter')
excel_buffer.seek(0)

st.download_button(
    label="📥 Download as Excel",
    data=excel_buffer,
    file_name="filtered_academic_expenditure.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.download_button(
    label="📥 Download as CSV",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_academic_expenditure.csv",
    mime="text/csv"
)

# Footer note of this project (Name and university)
st.markdown(""" 
    <hr>
    <p style="text-align: center; font-size:14px;">
        <strong>Made by Rahat Sultana</strong><br>
        MSc DeepTech Entrepreneurship | Vilnius University
    </p>
    <hr>
""", unsafe_allow_html=True)

#The End. Thanks a lot!