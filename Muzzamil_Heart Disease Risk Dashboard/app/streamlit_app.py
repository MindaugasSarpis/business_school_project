import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.prediction import predict_heart_risk  # Import the prediction function

# Set Streamlit page config for a wide layout and custom icon
st.set_page_config(page_title="Heart Disease Risk Dashboard", layout="wide", page_icon="❤️")

# Load CSS from a separate file
css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
with open(css_path, encoding='utf-8') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load HTML header from a separate file
html_path = os.path.join(os.path.dirname(__file__), 'header.html')
with open(html_path, encoding='utf-8') as f:
    st.markdown(f.read(), unsafe_allow_html=True)

# Load processed data
df = pd.read_csv('data/processed/heart_risk_processed.csv')

# --- Sidebar Filters ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/heart-with-pulse--v1.png", width=80)
    st.header("🔎 Filter Data")
    age_bins = [20, 30, 40, 50, 60, 70, 80, 90]
    df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins)
    age_group_options = df['AgeGroup'].cat.categories.astype(str).tolist()
    selected_age_groups = st.multiselect("Select Age Group(s):", age_group_options, default=age_group_options)
    gender_map = {0: "Female", 1: "Male"}
    gender_options = [0, 1]
    selected_genders = st.multiselect("Select Gender(s):", [gender_map[g] for g in gender_options], default=[gender_map[g] for g in gender_options])
    risk_factors = [
        'High_BP', 'High_Cholesterol', 'Diabetes', 'Smoking', 'Obesity',
        'Sedentary_Lifestyle', 'Family_History', 'Chronic_Stress',
        'Chest_Pain', 'Cold_Sweats_Nausea', 'Dizziness', 'Fatigue', 'Pain_Arms_Jaw_Back',
        'Palpitations', 'Shortness_of_Breath', 'Swelling'
    ]
    selected_risk_factors = []
    with st.expander("Risk Factors", expanded=False):
        for factor in risk_factors:
            if st.checkbox(f"Has {factor.replace('_', ' ')}", value=False, key=f"risk_{factor}"):
                selected_risk_factors.append(factor)

# --- Apply Filters ---
filtered_df = df[df['AgeGroup'].astype(str).isin(selected_age_groups)]
filtered_df = filtered_df[filtered_df['Gender'].map(gender_map).isin(selected_genders)]
for factor in selected_risk_factors:
    filtered_df = filtered_df[filtered_df[factor] == 1]

# --- Dashboard Layout ---
# Data Preview and Basic Stats side by side
st.markdown('<div class="dashboard-section">📋 Data Preview & Statistics</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#666; margin-bottom:1.2rem;">This section displays a preview of the filtered dataset and basic statistical summaries to help you understand the data distribution.</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1.5, 1])
with col1:
    with st.container():
        st.subheader("Data Preview")
        if filtered_df.empty:
            st.warning("No data to display. Please select at least one filter option in the sidebar.")
        else:
            st.dataframe(filtered_df.head())
with col2:
    with st.container():
        st.subheader("Basic Statistics")
        if filtered_df.empty:
            st.info("No statistics to show. Please select at least one filter option in the sidebar.")
        else:
            st.write(filtered_df.describe())

# Pie chart and Risk Factor Comparison side by side
st.markdown('<div class="dashboard-section">📊 Risk Overview</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#666; margin-bottom:1.2rem;">The pie chart shows the proportion of people at risk for heart disease, while the bar chart compares risk levels between those with and without specific risk factors.</div>', unsafe_allow_html=True)
col3, col4 = st.columns([1, 1.5])
with col3:
    with st.container():
        st.subheader("Heart Risk Prevalence")
        if filtered_df.empty or filtered_df['Heart_Risk'].nunique() == 0:
            st.info("No data available for Heart Risk Prevalence. Please select at least one filter option in the sidebar.")
        else:
            risk_counts = filtered_df['Heart_Risk'].value_counts().sort_index()
            labels_dict = {0: "No Risk", 1: "At Risk"}
            pie_labels = [labels_dict.get(idx, str(idx)) for idx in risk_counts.index]
            fig_pie, ax_pie = plt.subplots()
            ax_pie.pie(risk_counts, labels=pie_labels, autopct='%1.1f%%', colors=["#8fd9b6", "#ff9999"], startangle=90)
            ax_pie.axis('equal')
            st.pyplot(fig_pie)
with col4:
    with st.container():
        st.subheader("Risk Factor Comparison")
        if filtered_df.empty:
            st.info("No data available for Risk Factor Comparison. Please select at least one filter option in the sidebar.")
        else:
            risk_factor_percentages = []
            for factor in risk_factors:
                group_with = filtered_df[filtered_df[factor] == 1]
                group_without = filtered_df[filtered_df[factor] == 0]
                pct_with = group_with['Heart_Risk'].mean() * 100 if len(group_with) > 0 else np.nan
                pct_without = group_without['Heart_Risk'].mean() * 100 if len(group_without) > 0 else np.nan
                risk_factor_percentages.append({
                    "Risk Factor": factor.replace("_", " "),
                    "Has Factor": pct_with,
                    "No Factor": pct_without
                })
            rf_df = pd.DataFrame(risk_factor_percentages)
            fig_risk, ax_risk = plt.subplots(figsize=(8, 5))
            bar_width = 0.35
            index = np.arange(len(rf_df))
            ax_risk.bar(index, rf_df["Has Factor"], bar_width, label="Has Factor", color="#ff9999")
            ax_risk.bar(index + bar_width, rf_df["No Factor"], bar_width, label="No Factor", color="#8fd9b6")
            ax_risk.set_xlabel("Risk Factor")
            ax_risk.set_ylabel("% At Risk")
            ax_risk.set_title("Heart Disease Risk by Risk Factor Presence")
            ax_risk.set_xticks(index + bar_width / 2)
            ax_risk.set_xticklabels(rf_df["Risk Factor"], rotation=30, ha="right")
            ax_risk.legend()
            st.pyplot(fig_risk)

# Trends Over Age full width (compact chart)
st.markdown('<div class="dashboard-section">📈 Trends Over Age</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:1.08rem; color:#444; margin-bottom:1rem;">This chart shows how the probability of being at risk for heart disease changes with age in the filtered dataset.</div>', unsafe_allow_html=True)
with st.container():
    if filtered_df.empty:
        st.info("No data available for Trends Over Age. Please select at least one filter option in the sidebar.")
    else:
        age_risk = filtered_df.groupby('Age')['Heart_Risk'].mean() * 100
        if age_risk.empty:
            st.info("No age data available for trend analysis.")
        else:
            fig_trend, ax_trend = plt.subplots(figsize=(6, 3))
            ax_trend.plot(age_risk.index, age_risk.values, marker='o', markersize=3, color="#3366cc")
            ax_trend.set_xlabel("Age (years)")
            ax_trend.set_ylabel("% At Risk")
            ax_trend.set_title("Heart Disease Risk Trend Over Age")
            st.pyplot(fig_trend)

# Three charts in a row: Age Distribution, Gender, Age Group
st.markdown('<div class="dashboard-section">📊 Demographic Visualizations</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#666; margin-bottom:1.2rem;">These charts illustrate the age distribution, the breakdown of heart disease risk by gender, and how risk varies across different age groups.</div>', unsafe_allow_html=True)
col5, col6, col7 = st.columns(3)
with col5:
    with st.container():
        st.subheader("Age Distribution")
        if filtered_df.empty:
            st.info("No data available for Age Distribution. Please select at least one filter option in the sidebar.")
        else:
            fig, ax = plt.subplots()
            sns.histplot(filtered_df['Age'], bins=30, kde=True, ax=ax, color="#3366cc")
            ax.set_xlabel("Age (years)")
            ax.set_ylabel("Number of People")
            st.pyplot(fig)
with col6:
    with st.container():
        st.subheader("Heart Risk by Gender")
        if filtered_df.empty:
            st.info("No data available for Heart Disease Risk by Gender. Please select at least one filter option in the sidebar.")
        else:
            fig2, ax2 = plt.subplots()
            sns.countplot(x='Gender', hue='Heart_Risk', data=filtered_df, ax=ax2, palette="Set2")
            ax2.set_xlabel("Gender (0 = Female, 1 = Male)")
            ax2.set_ylabel("Number of People")
            ax2.legend(title="Heart Risk", labels=["No Risk", "At Risk"])
            st.pyplot(fig2)
with col7:
    with st.container():
        st.subheader("Heart Risk by Age Group")
        if filtered_df.empty:
            st.info("No data available for Heart Disease Risk by Age Group. Please select at least one filter option in the sidebar.")
        else:
            fig3, ax3 = plt.subplots()
            sns.countplot(x='AgeGroup', hue='Heart_Risk', data=filtered_df, ax=ax3, palette="Set1")
            ax3.set_xlabel("Age Group")
            ax3.set_ylabel("Number of People")
            ax3.legend(title="Heart Risk", labels=["No Risk", "At Risk"])
            st.pyplot(fig3)

# Top Risk Factors and Correlation Heatmap side by side
st.markdown('<div class="dashboard-section">🧬 Risk Factors & Correlations</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#666; margin-bottom:1.2rem;">The bar chart highlights the most common risk factors among at-risk individuals, and the heatmap reveals correlations between numerical variables in the dataset.</div>', unsafe_allow_html=True)
col8, col9 = st.columns(2)
with col8:
    with st.container():
        st.subheader("Top Risk Factors")
        if filtered_df.empty:
            st.info("No data available for Top Risk Factors. Please select at least one filter option in the sidebar.")
        else:
            risk_counts = filtered_df[filtered_df['Heart_Risk'] == 1][risk_factors].sum().sort_values(ascending=False)
            fig4, ax4 = plt.subplots()
            sns.barplot(x=risk_counts.values, y=risk_counts.index, ax=ax4, palette="Reds_r")
            ax4.set_xlabel("Number of At-Risk People")
            ax4.set_ylabel("Risk Factor")
            st.pyplot(fig4)
with col9:
    with st.container():
        st.subheader("Correlation Heatmap")
        if filtered_df.empty:
            st.info("No data available for Correlation Heatmap. Please select at least one filter option in the sidebar.")
        else:
            numeric_df = filtered_df.select_dtypes(include=['number'])
            fig5, ax5 = plt.subplots(figsize=(10, 8))
            corr = numeric_df.corr()
            sns.heatmap(corr, annot=False, cmap="coolwarm", ax=ax5)
            st.pyplot(fig5)

# --- Prediction Section ---
st.markdown('<div class="dashboard-section">🔮 Heart Disease Risk Prediction</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#666; margin-bottom:1.2rem;">Enter your details to predict the risk of heart disease.</div>', unsafe_allow_html=True)

age = st.number_input("Age", min_value=20, max_value=90, value=50)
gender = st.selectbox("Gender", options=["Female", "Male"])
risk_factors_input = {factor: st.checkbox(f"Has {factor.replace('_', ' ')}", value=False) for factor in risk_factors}

if st.button("Predict Risk"):
    risk_label = predict_heart_risk(age, gender, risk_factors_input)
    st.subheader("Prediction Result")
    st.write(f"The model predicts: **{risk_label}**")

st.info("✨ Tip: Use the sidebar to filter the data and see how the charts update dynamically!")