import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor

from utils.spike_labels import spike_labels
from utils.date_mappings import weekday_map, month_map

st.set_page_config(layout="wide")

# Decorator with cache so we only upload data once
@st.cache_data
def load_data():
    df = pd.read_csv('data/merged_data.csv', parse_dates=['datetime'], index_col='datetime')
    return df
merged_df = load_data()

# We will need datafile in daily level + cleaning
daily_data = merged_df.resample('D').agg({
    'bicycles': 'sum',
    'tavg': 'mean',
    'prcp': 'mean',
    'wspd': 'mean',
    'pres': 'mean'
})
daily_data['prcp'] = daily_data['prcp'].fillna(0)

# ~~~ Navigation
menu = st.sidebar.radio("Menu", ["Trends", "Weather", "Prediction"])

# ~~~ Filters
DEFAULT_DATE_RANGE = [merged_df.index.min().date(), merged_df.index.max().date()]
DEFAULT_SEASON = "All"
DEFAULT_TIME_OF_DAY = "All"
if "filters_initialized" not in st.session_state:
    st.session_state["date_range"] = DEFAULT_DATE_RANGE
    st.session_state["season"] = DEFAULT_SEASON
    st.session_state["time_of_day"] = DEFAULT_TIME_OF_DAY
    st.session_state["filters_initialized"] = True

st.title("Bike Traffic Dashboard")
st.subheader(f"Currently viewing: {menu}")

col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    date_range = st.date_input(
        "Select Date Range",
        value=st.session_state["date_range"]
    )
    st.session_state["date_range"] = date_range
with col2:
    season = st.selectbox(
        "Select Season",
        ["All", "Spring", "Summer", "Autumn", "Winter"],
        index=["All", "Spring", "Summer", "Autumn", "Winter"].index(st.session_state["season"])
    )
    st.session_state["season"] = season
with col3:
    time_of_day = st.selectbox(
        "Select Time of Day",
        ["All", "Night", "Morning", "Day", "Evening"],
        index=["All", "Night", "Morning", "Day", "Evening"].index(st.session_state["time_of_day"])
    )
    st.session_state["time_of_day"] = time_of_day

start_date, end_date = st.session_state["date_range"]
season = st.session_state["season"]
time_of_day = st.session_state["time_of_day"]

# Need to use (introduce) filtered datafile after filers been applied
filtered_df = merged_df.loc[
    (merged_df.index.date >= start_date) &
    (merged_df.index.date <= end_date)
]
if season != "All":
    season_months = {
        'Spring': [3, 4, 5],
        'Summer': [6, 7, 8],
        'Autumn': [9, 10, 11],
        'Winter': [12, 1, 2]
    }
    filtered_df = filtered_df[filtered_df.index.month.isin(season_months[season])]
if time_of_day != "All":
    time_of_day_ranges = {
        "Night": (0, 6),
        "Morning": (6, 12),
        "Day": (12, 18),
        "Evening": (18, 24)
    }
    start_hour, end_hour = time_of_day_ranges[time_of_day]
    filtered_df = filtered_df[
        (filtered_df.index.hour >= start_hour) &
        (filtered_df.index.hour < end_hour)
    ]
    
# ||| TRENDS TAB |||
if menu == "Trends":

    if not filtered_df.empty:            # No data test
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_bikes = int(filtered_df['bicycles'].sum())
            st.metric(label="🚲 Total Number of Bikes", value=f"{total_bikes:,}")

        with col2:
            number_of_days = (filtered_df.index.max() - filtered_df.index.min()).days + 1
            daily_average_bikes = total_bikes / number_of_days if number_of_days > 0 else 0
            st.metric(label="📅 Daily Average", value=f"{int(daily_average_bikes):,}")

        with col3:
            number_of_hours = len(filtered_df)
            hourly_average_bikes = total_bikes / number_of_hours
            st.metric(label="⏰ Hourly Average", value=f"{hourly_average_bikes:.1f}")

        st.subheader("Busiest Moments")
        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown("### Top 10 Busiest Calendar Hours")
            top10_hours = filtered_df['bicycles'].sort_values(ascending=False).head(10).astype(int)
            st.dataframe(
                top10_hours.reset_index().rename(
                    columns={"datetime": "Date + Hour", "bicycles": "Number of Bikes"}
                ),
                use_container_width=True,
                hide_index=True
            )

        with col5:
            st.markdown("### Top 10 Busiest Calendar Days")
            daily_bikes = filtered_df['bicycles'].resample('D').sum()
            top10_days = daily_bikes.sort_values(ascending=False).head(10).astype(int)
            top10_days.index = top10_days.index.date
            st.dataframe(
                top10_days.reset_index().rename(
                    columns={"index": "Date", "bicycles": "Number of Bikes"}
                ),
                use_container_width=True,
                hide_index=True
            )

        with col6:
            st.markdown("### Most Popular Day of Month")

            day_avg = daily_bikes.groupby(daily_bikes.index.day).mean()
            fig_day = px.bar(
                x=day_avg.index,
                y=day_avg.values,
                labels={'x': 'Day of Month', 'y': 'Average Number of Bikes'},
                title="Average Daily Bikes by Day of Month"
            )
            st.plotly_chart(fig_day, use_container_width=True)

        st.subheader("Hourly, Weekly and Monthly Patterns")
        col7, col8, col9 = st.columns(3)

        with col7:
            st.markdown("### Most Popular Hour of the Day")
            hourly_avg = filtered_df.groupby(filtered_df.index.hour)['bicycles'].mean()
            fig_hourly = px.bar(
                x=hourly_avg.index,
                y=hourly_avg.values,
                labels={'x': 'Hour of Day', 'y': 'Average Number of Bikes'},
                title="Average Bikes by Hour"
            )
            fig_hourly.update_layout(xaxis=dict(tickmode='linear'))
            st.plotly_chart(fig_hourly, use_container_width=True)

        with col8:
            st.markdown("### Most Popular Weekday")
            weekday_avg = daily_bikes.groupby(daily_bikes.index.weekday).mean()
            weekday_avg.index = weekday_avg.index.map(weekday_map)
            fig_weekday = px.bar(
                x=weekday_avg.index,
                y=weekday_avg.values,
                labels={'x': 'Day of Week', 'y': 'Average Number of Bikes'},
                title="Average Bikes by Day of Week"
            )
            st.plotly_chart(fig_weekday, use_container_width=True)

        with col9:
            st.markdown("### Most Popular Month")
            filtered_df['month'] = filtered_df.index.month
            year_month_sum = filtered_df.groupby(['year', 'month'])['bicycles'].sum()
            month_avg_across_years = year_month_sum.groupby('month').mean()
            month_avg_across_years.index = month_avg_across_years.index.map(month_map)
            fig_month = px.bar(
                x=month_avg_across_years.index,
                y=month_avg_across_years.values,
                labels={'x': 'Month', 'y': 'Average Total Bikes'},
                title="Average Bikes by Month"
            )
            st.plotly_chart(fig_month, use_container_width=True)

        st.subheader("Weekly Heatmap")
        pivot_table = filtered_df.pivot_table(
            index=filtered_df.index.weekday,
            columns=filtered_df.index.hour,
            values='bicycles',
            aggfunc='mean'
        )
        pivot_table.index = pivot_table.index.map(weekday_map) # Heatmap is a pivot table
        fig_heatmap = px.imshow(
            pivot_table,
            labels=dict(x="Hour of Day", y="Day of Week", color="Average Bikes"),
            title="Heatmap of Average Bikes (Weekdays vs Hours)"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)


        st.subheader("Daily Dynamics & Spike Analysis")
        # Rolling means and spikes
        rolling_mean = daily_bikes.rolling(window=30).mean()
        rolling_std = daily_bikes.rolling(window=30).std()
        threshold = rolling_mean + 2.5 * rolling_std
        spikes = daily_bikes[daily_bikes > threshold]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_bikes.index,
            y=daily_bikes.values,
            mode='lines',
            name='Daily Counts',
            line=dict(color='lightblue')
        ))
        fig.add_trace(go.Scatter(
            x=rolling_mean.index,
            y=rolling_mean.values,
            mode='lines',
            name='30-Day Moving Average',
            line=dict(color='red')
        ))
        fig.add_trace(go.Scatter(
            x=spikes.index,
            y=spikes.values,
            mode='markers',
            name='Detected Spikes',
            marker=dict(color='purple', size=8, symbol='circle'),
            text=[spike_labels.get(date.strftime('%Y-%m-%d'), "") for date in spikes.index],
            hovertemplate='%{x}<br>Bikes: %{y}<br>%{text}'
        ))
        fig.update_layout(
            title="Bike Counts with Detected Spikes",
            xaxis_title="Date",
            yaxis_title="Number of Bikes",
            legend_title="Legend",
            hovermode="closest",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ No data matches your filters. Try adjusting them.", icon="⚡")


# ||| WEATHER TAB |||
if menu == "Weather":
    st.subheader("Temperature")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Average Daily")
        st.metric("Average Daily", f"{filtered_df['tavg'].mean():.1f}°C")

    with col2:
        st.markdown("#### Dynamics")
        # Resample daily averages and sums
        daily_temp = filtered_df['tavg'].resample('D').mean()
        daily_temp = daily_temp.fillna(method='ffill')
        daily_bikes = filtered_df['bicycles'].resample('D').sum()
        temp_rolling = daily_temp.rolling(window=30).mean()
        bikes_rolling = daily_bikes.rolling(window=30).mean()

        fig = go.Figure()
        # Left Y-axis
        fig.add_trace(go.Scatter(
            x=daily_temp.index,
            y=daily_temp,
            name="Temperature (°C)",
            line=dict(color='red', width=1),
            yaxis="y1"
        ))
        fig.add_trace(go.Scatter(
            x=temp_rolling.index,
            y=temp_rolling,
            name="30d Avg Temp (°C)",
            line=dict(color='darkred', width=2),
            yaxis="y1"
        ))
        # Right Y-axis
        fig.add_trace(go.Scatter(
            x=daily_bikes.index,
            y=daily_bikes,
            name="Daily Bikes",
            line=dict(color='blue', width=1),
            yaxis="y2"
        ))
        fig.add_trace(go.Scatter(
            x=bikes_rolling.index,
            y=bikes_rolling,
            name="30d Avg Bikes",
            line=dict(color='darkblue', width=2),
            yaxis="y2"
        ))
        # Final iteration
        fig.update_layout(
            title="Daily Temperature and Bike Counts (with 30d Moving Averages)",
            xaxis_title="Date",
            yaxis=dict(
                title="Temperature (°C)",
                tickfont=dict(color="red")
            ),
            yaxis2=dict(
                title="Bike Counts",
                tickfont=dict(color="blue"),
                overlaying="y",
                side="right"
            ),
            hovermode="x unified",
            height=650
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.markdown("#### Correlation")
        
        valid_data = pd.concat([daily_temp, daily_bikes], axis=1).dropna()
        temp_values = valid_data['tavg']
        bike_values = valid_data['bicycles']
        correlation = temp_values.corr(bike_values)
    
        # Fitting 4th-degree polynomial
        coeffs = np.polyfit(temp_values, bike_values, 4)
        x_fit = np.linspace(temp_values.min(), temp_values.max(), 500)
        y_fit = np.polyval(coeffs, x_fit)
        equation = f"y = {coeffs[0]:.2e}x⁴ + {coeffs[1]:.2e}x³ + {coeffs[2]:.2e}x² + {coeffs[3]:.2e}x + {coeffs[4]:.2f}"
    
        # Plotting
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=temp_values,
            y=bike_values,
            mode='markers',
            name='Daily Data',
            marker=dict(color='blue', opacity=0.5)
        ))
        fig.add_trace(go.Scatter(
            x=x_fit,
            y=y_fit,
            mode='lines',
            name=f"4th Degree Polynomial (r={correlation:.2f})",
            line=dict(color='red')
        ))
        fig.update_layout(
            title="Temperature vs. Bike Counts with 4th Degree Polynomial Fit",
            xaxis_title="Average Daily Temperature (°C)",
            yaxis_title="Total Daily Bikes",
            hovermode="closest",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Regression equation: {equation}")


    st.subheader("Precipitation")
    col4, col5, col6 = st.columns(3)

    with col4:
        filtered_daily = filtered_df.resample('D').agg({'prcp': 'mean'}).fillna(0)
        avg_precip = filtered_daily['prcp'].mean()
        st.metric("Average Daily Precipitation (mm)", f"{avg_precip:.2f}")

    with col5:
        st.markdown("#### Dynamics")
        filtered_daily = filtered_df.resample('D').agg({'prcp': 'mean', 'bicycles': 'sum'}).fillna(0)
        filtered_daily['prcp_30d'] = filtered_daily['prcp'].rolling(window=30).mean()
        filtered_daily['bicycles_30d'] = filtered_daily['bicycles'].rolling(window=30).mean()
        
        fig_precip_dynamics = go.Figure()
        fig_precip_dynamics.add_trace(go.Scatter(x=filtered_daily.index, y=filtered_daily['prcp'], mode='lines', name='Daily Precipitation (mm)', line=dict(color='lightgreen')))
        fig_precip_dynamics.add_trace(go.Scatter(x=filtered_daily.index, y=filtered_daily['prcp_30d'], mode='lines', name='30d Avg Precipitation (mm)', line=dict(color='green')))
        fig_precip_dynamics.add_trace(go.Scatter(x=filtered_daily.index, y=filtered_daily['bicycles'], mode='lines', name='Daily Bikes', line=dict(color='lightblue'), yaxis='y2'))
        fig_precip_dynamics.add_trace(go.Scatter(x=filtered_daily.index, y=filtered_daily['bicycles_30d'], mode='lines', name='30d Avg Bikes', line=dict(color='blue'), yaxis='y2'))
        fig_precip_dynamics.update_layout(
            title="Daily Precipitation and Bikes (with 30d Moving Averages)",
            xaxis_title="Date",
            yaxis=dict(title="Precipitation (mm)"),
            yaxis2=dict(title="Bike Counts", overlaying='y', side='right'),
            height=650
        )
        st.plotly_chart(fig_precip_dynamics, use_container_width=True)

    with col6:
        st.markdown("#### Correlation")
        filtered_daily = filtered_df.resample('D').agg({'prcp': 'mean', 'bicycles': 'sum'}).fillna(0) 
        x = filtered_daily['prcp']
        y = filtered_daily['bicycles']
        correlation = x.corr(y)
    
        coeffs = np.polyfit(x, y, 4)
        x_sorted = np.sort(x)
        y_poly = np.polyval(coeffs, x_sorted)
        equation = f"y = {coeffs[0]:.2f}x⁴ + {coeffs[1]:.2f}x³ + {coeffs[2]:.2f}x² + {coeffs[3]:.2f}x + {coeffs[4]:.2f}"
        
        fig_precip_corr = go.Figure()
        fig_precip_corr.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Daily Data', marker=dict(color='blue', opacity=0.5)))
        fig_precip_corr.add_trace(go.Scatter(x=x_sorted, y=y_poly, mode='lines', name=f'4th Degree Polynomial (r={correlation:.2f})', line=dict(color='red')))
        fig_precip_corr.update_layout(
            title="Precipitation vs. Bike Counts with 4th Degree Polynomial Fit",
            xaxis_title="Daily Precipitation (mm)",
            yaxis_title="Total Daily Bikes",
            height=600
        )
        st.plotly_chart(fig_precip_corr, use_container_width=True)
        st.caption(f"Regression equation: {equation}")

      # Row 3
    st.subheader("Wind speed")
    col7, col8, col9 = st.columns(3)
    with col7:
        st.markdown("#### Average Daily")
        filtered_daily = filtered_df.resample('D').agg({'wspd': 'mean'}).fillna(0)
        avg_wind = filtered_daily['wspd'].mean()
        st.metric("Average Daily Wind Speed (km/h)", f"{avg_wind:.2f}")
        
    with col8:
        st.markdown("#### Dynamics")
        daily_data = filtered_df.resample('D').agg({'wspd': 'mean', 'bicycles': 'sum'})
        daily_data['wspd_30d'] = daily_data['wspd'].rolling(window=30).mean()
        daily_data['bicycles_30d'] = daily_data['bicycles'].rolling(window=30).mean()
        
        fig_wind_dynamics = go.Figure()
        fig_wind_dynamics.add_trace(go.Scatter(x=daily_data.index, y=daily_data['wspd'], mode='lines', name='Daily Wind Speed (km/h)', line=dict(color='lightgreen')))
        fig_wind_dynamics.add_trace(go.Scatter(x=daily_data.index, y=daily_data['wspd_30d'], mode='lines', name='30d Avg Wind Speed (km/h)', line=dict(color='green')))
        fig_wind_dynamics.add_trace(go.Scatter(x=daily_data.index, y=daily_data['bicycles'], mode='lines', name='Daily Bikes', line=dict(color='lightblue'), yaxis='y2'))
        fig_wind_dynamics.add_trace(go.Scatter(x=daily_data.index, y=daily_data['bicycles_30d'], mode='lines', name='30d Avg Bikes', line=dict(color='blue'), yaxis='y2'))
        fig_wind_dynamics.update_layout(
            title="Daily Wind Speed and Bikes (with 30d Moving Averages)",
            xaxis_title="Date",
            yaxis=dict(title="Wind Speed (km/h)"),
            yaxis2=dict(title="Bike Counts", overlaying='y', side='right'),
            height=650
        )
        st.plotly_chart(fig_wind_dynamics, use_container_width=True)

    with col9:
        # Prepare daily data
        daily_wspd = filtered_df['wspd'].resample('D').mean()
        daily_bikes = filtered_df['bicycles'].resample('D').sum()
        valid_data = pd.concat([daily_wspd, daily_bikes], axis=1).dropna()
        wspd_values = valid_data['wspd'].values.reshape(-1, 1)
        bike_values = valid_data['bicycles'].values
        
        # Using linear regression model here, others seemed as an unecessary overkill
        model = LinearRegression()
        model.fit(wspd_values, bike_values)
        y_pred = model.predict(wspd_values)
        r = np.corrcoef(wspd_values.flatten(), bike_values)[0, 1] # Pearson correlation coefficient 𝑟
        slope = model.coef_[0]
        intercept = model.intercept_
        equation = f"y = {slope:.2f}x + {intercept:.2f}"
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=wspd_values.flatten(),
            y=bike_values,
            mode='markers',
            name='Daily Data',
            marker=dict(color='blue', opacity=0.5)
        ))
        fig.add_trace(go.Scatter(
            x=wspd_values.flatten(),
            y=y_pred,
            mode='lines',
            name=f"Linear Regression (r={r:.2f})",
            line=dict(color='red')
        ))
        fig.update_layout(
            title="Wind Speed vs. Bike Counts with Linear Regression",
            xaxis_title="Daily Wind Speed (km/h)",
            yaxis_title="Total Daily Bikes",
            hovermode="closest",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"Regression equation: {equation}")

      # Row 4
    st.subheader("Air Pressure")
    col10, col11, col12 = st.columns(3)
    with col10:
        st.markdown("#### Average Daily")
        avg_pres = filtered_df['pres'].mean()
        st.metric("Average Daily Air Pressure (hPa)", f"{avg_pres:.2f}")
        
    with col11:
        st.markdown("#### Dynamics")
        daily_pressure = filtered_df['pres'].resample('D').mean().fillna(method='ffill')
        pressure_ma = daily_pressure.rolling(window=30).mean()
        bikes_ma = daily_bikes.rolling(window=30).mean()
    
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_pressure.index, y=daily_pressure, mode='lines', name='Daily Pressure (hPa)', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=pressure_ma.index, y=pressure_ma, mode='lines', name='30d Avg Pressure (hPa)', line=dict(color='green', width=3)))
        fig.add_trace(go.Scatter(x=daily_bikes.index, y=daily_bikes, mode='lines', name='Daily Bikes', line=dict(color='blue', width=1), yaxis='y2'))
        fig.add_trace(go.Scatter(x=bikes_ma.index, y=bikes_ma, mode='lines', name='30d Avg Bikes', line=dict(color='blue', width=3), yaxis='y2'))
        fig.update_layout(
        title="Daily Air Pressure and Bikes (with 30d Moving Averages)",
        xaxis_title="Date",
        yaxis=dict(title="Pressure (hPa)", side='left'),
        yaxis2=dict(title="Bike Counts", overlaying='y', side='right'),
        height=650,
        legend=dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        ),
    )
        st.plotly_chart(fig, use_container_width=True)

    with col12:
        st.markdown("#### Correlation")
        daily_pres = filtered_df['pres'].resample('D').mean()
        daily_bikes = filtered_df['bicycles'].resample('D').sum()
        valid_data = pd.concat([daily_pres, daily_bikes], axis=1).dropna()
        pres_values = valid_data['pres'].values.reshape(-1, 1)
        bike_values = valid_data['bicycles'].values
        
        model = LinearRegression()
        model.fit(pres_values, bike_values)
        y_pred = model.predict(pres_values)
        r = np.corrcoef(pres_values.flatten(), bike_values)[0, 1]
        slope = model.coef_[0]
        intercept = model.intercept_
        equation = f"y = {slope:.2f}x + {intercept:.2f}"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pres_values.flatten(),
            y=bike_values,
            mode='markers',
            name='Daily Data',
            marker=dict(color='blue', opacity=0.5)
        ))
        fig.add_trace(go.Scatter(
            x=pres_values.flatten(),
            y=y_pred,
            mode='lines',
            name=f"Linear Regression (r={r:.2f})",
            line=dict(color='red')
        ))
        fig.update_layout(
            title="Air Pressure vs. Bike Counts with Linear Regression",
            xaxis_title="Average Daily Air Pressure (hPa)",
            yaxis_title="Total Daily Bikes",
            hovermode="closest",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"Regression equation: {equation}")

# ||| PREDICTION TAB |||
elif menu == "Prediction":
    st.markdown("### Model Training Approaches")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### First training method")
        st.caption("Linear regression trained on daily average weather and weekday to predict bike counts. R² score is evaluated on a separate test set.")

        df_train = filtered_df.copy()
        df_train['weekday'] = df_train.index.weekday
        daily = df_train.resample('D').agg({
            'bicycles': 'sum',
            'tavg': 'mean',
            'prcp': 'sum',
            'wspd': 'mean',
            'pres': 'mean',
            'weekday': 'first'
        }).dropna()
        X = daily[['tavg', 'prcp', 'wspd', 'pres', 'weekday']]
        y = daily['bicycles']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
    
        st.write("**Coefficients:**")
        coeffs = pd.DataFrame({'Feature': X.columns, 'Coefficient': model.coef_})
        st.dataframe(coeffs, use_container_width=True)
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        st.metric("R² Score (test set)", f"{r2:.2f}")
            
    with col2:
        st.markdown("#### Second method (with squares)")
        st.caption("Linear regression with squared features to account for non-linear effects. R² score is evaluated on a separate test set.")
    
        X_squared = X.copy()
        for col in ['tavg', 'prcp', 'wspd', 'pres']:
            X_squared[f'{col}_squared'] = X[col] ** 2
        y = daily['bicycles']
        
        X_train, X_test, y_train, y_test = train_test_split(X_squared, y, test_size=0.2, random_state=42)
        model_sq = LinearRegression()
        model_sq.fit(X_train, y_train)
    
        st.write("**Coefficients:**")
        coeffs_sq = pd.DataFrame({'Feature': X_squared.columns, 'Coefficient': model_sq.coef_})
        st.dataframe(coeffs_sq, use_container_width=True)
        y_pred_sq = model_sq.predict(X_test)
        r2_sq = r2_score(y_test, y_pred_sq)
        st.metric("R² Score (test set)", f"{r2_sq:.2f}")

    with col3:
        st.markdown("#### Polynomial regression")
        st.caption("Polynomial regression (degree 3) using weather and weekday. R² score is evaluated on a separate test set.")
    
        poly = PolynomialFeatures(degree=3, include_bias=False)
        X_poly = poly.fit_transform(X)
        feature_names = poly.get_feature_names_out(X.columns)
    
        X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)
        model_poly = LinearRegression()
        model_poly.fit(X_train, y_train)
    
        st.write("**Coefficients:**")
        coeffs_poly = pd.DataFrame({
            'Feature': feature_names,
            'Coefficient': model_poly.coef_
        })
        st.dataframe(coeffs_poly, use_container_width=True)
        y_pred_poly = model_poly.predict(X_test)
        r2_poly = r2_score(y_test, y_pred_poly)
        st.metric("R² Score (test set)", f"{r2_poly:.2f}")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("#### Random Forest")
        st.caption("Random Forest regression using weather and weekday. R² score is evaluated on a separate test set.")

        df_rf = filtered_df.copy()
        df_rf['weekday'] = df_rf.index.weekday
        daily_rf = df_rf.resample('D').agg({
            'bicycles': 'sum',
            'tavg': 'mean',
            'prcp': 'sum',
            'wspd': 'mean',
            'pres': 'mean',
            'weekday': 'first'
        }).dropna()
        X_rf = daily_rf[['tavg', 'prcp', 'wspd', 'pres', 'weekday']]
        y_rf = daily_rf['bicycles']
    
        X_train_rf, X_test_rf, y_train_rf, y_test_rf = train_test_split(X_rf, y_rf, test_size=0.2, random_state=42)
        rf_model = RandomForestRegressor(random_state=42)
        rf_model.fit(X_train_rf, y_train_rf)
        y_pred_rf = rf_model.predict(X_test_rf)
        r2_rf = r2_score(y_test_rf, y_pred_rf)
        st.metric("R² Score (test set)", f"{r2_rf:.2f}")

    with col5:
        st.markdown("#### Feature Importances")
    
        importances = rf_model.feature_importances_
        importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances})
        importance_df = importance_df.sort_values(by="Importance", ascending=False)
    
        fig_importance = px.bar(importance_df, x='Importance', y='Feature', orientation='h', title="Feature Importances", height=600)
        st.plotly_chart(fig_importance, use_container_width=True)
    
    with col6:
        st.markdown("#### 4.3 Prediction vs Actual")

        # Scatterplot
        fig_pred_actual = go.Figure()
        fig_pred_actual.add_trace(go.Scatter(
            x=y_test_rf,
            y=y_pred_rf,
            mode='markers',
            marker=dict(color='blue', opacity=0.5),
            name='Predictions'
        ))
        fig_pred_actual.add_trace(go.Scatter(
            x=[y_test_rf.min(), y_test_rf.max()],
            y=[y_test_rf.min(), y_test_rf.max()],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Perfect Prediction'
        ))
        fig_pred_actual.update_layout(
            title="Actual vs. Predicted Bike Counts (Random Forest)",
            xaxis_title="Actual Bike Count",
            yaxis_title="Predicted Bike Count",
            height=600
        )
        st.plotly_chart(fig_pred_actual, use_container_width=True)

    # Doing future predcitions chart here
    st.markdown("### 4.4 Forecast: Future Predictions")
    
    # Use filtered_df (already based on filters)
    df_train = filtered_df.copy()
    df_train['weekday'] = df_train.index.weekday
    daily = df_train.resample('D').agg({
        'bicycles': 'sum',
        'tavg': 'mean',
        'prcp': 'sum',
        'wspd': 'mean',
        'pres': 'mean',
        'weekday': 'first'
    }).dropna()
    daily['tavg_sq'] = daily['tavg'] ** 2
    daily['prcp_sq'] = daily['prcp'] ** 2
    daily['wspd_sq'] = daily['wspd'] ** 2
    daily['pres_sq'] = daily['pres'] ** 2

    X_train = daily[['tavg', 'prcp', 'wspd', 'pres', 'weekday', 'tavg_sq', 'prcp_sq', 'wspd_sq', 'pres_sq']]
    y_train = daily['bicycles']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Here we add another set of future data for weather
    future_weather = pd.read_csv("data/weather_data2.csv", parse_dates=['date'])
    future_weather = future_weather.set_index('date')
    future_weather['weekday'] = future_weather.index.weekday
    future_weather = future_weather.fillna(0)
    future_weather['tavg_sq'] = future_weather['tavg'] ** 2
    future_weather['prcp_sq'] = future_weather['prcp'] ** 2
    future_weather['wspd_sq'] = future_weather['wspd'] ** 2
    future_weather['pres_sq'] = future_weather['pres'] ** 2
    
    future_weather['predicted_bikes'] = model.predict(future_weather[X_train.columns])
    future_weather['rolling_30d'] = future_weather['predicted_bikes'].rolling(30).mean()
    
    top10 = future_weather['predicted_bikes'].nlargest(10)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=future_weather.index, y=future_weather['predicted_bikes'], mode='lines', name='Predicted Daily Bikes'))
    fig.add_trace(go.Scatter(x=future_weather.index, y=future_weather['rolling_30d'], mode='lines', name='30d Moving Avg', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(
        x=top10.index,
        y=top10.values,
        mode='markers+text',
        name='Top 10 Peaks',
        marker=dict(size=10, color='red'),
        text=[date.strftime('%Y-%m-%d') for date in top10.index],
        textposition="top center",
        textfont=dict(size=10)
    ))     
    fig.update_layout(title="4.4 Future Bike Predictions (on-the-fly)", xaxis_title="Date", yaxis_title="Predicted Bikes", height=750)
    st.plotly_chart(fig, use_container_width=True)































