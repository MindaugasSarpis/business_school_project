import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import r2_score, mean_absolute_error

# Load and preprocess data
orders = pd.read_excel("orders.xlsx")
orders['date'] = pd.to_datetime(orders['date'])
orders['weekday'] = orders['date'].dt.day_name()

# Create daily revenue data
daily_data = orders.groupby(['date', 'weekday'])['item_price'].sum().reset_index()

# Feature engineering
def create_features(df):
    df = df.copy()
    if 'date' in df.columns:
        df['day_of_month'] = df['date'].dt.day
        df['week_of_year'] = df['date'].dt.isocalendar().week
    df['is_weekend'] = df['weekday'].isin(['Saturday', 'Sunday']).astype(int)
    
    # Cyclical encoding for weekdays
    day_order = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 
                'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    df['weekday_encoded'] = df['weekday'].map(day_order)
    df['weekday_sin'] = np.sin(2 * np.pi * df['weekday_encoded']/7)
    df['weekday_cos'] = np.cos(2 * np.pi * df['weekday_encoded']/7)
    
    return df

daily_data = create_features(daily_data)

# Prepare data
X = daily_data.drop(columns=['date', 'item_price', 'weekday'])
y = daily_data['item_price']

# Time-series cross-validation
tscv = TimeSeriesSplit(n_splits=5)

# Model with hyperparameter grid
model = GradientBoostingRegressor(random_state=42)
param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.05],
    'max_depth': [3, 5],
    'subsample': [0.8, 1.0],
    'min_samples_split': [2, 5]
}

# Grid search with time-series validation
grid_search = GridSearchCV(model, param_grid, cv=tscv, 
                          scoring='r2', n_jobs=-1)
grid_search.fit(X, y)

# Best model
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X)

# Evaluation
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Training R²: {r2_score(y, y_pred):.3f}")
print(f"MAE: {mean_absolute_error(y, y_pred):.2f}")

# Budget allocation logic
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
           'Friday', 'Saturday', 'Sunday']

# Create prediction matrix with dummy date
prediction_data = pd.DataFrame({
    'weekday': weekdays,
    'date': pd.date_range(start='2025-01-01', periods=7)  # dummy dates
})

X_pred = create_features(prediction_data).fillna(0)
X_pred = X_pred[X.columns]  # Keep only features used in training

predicted_revenues = best_model.predict(X_pred)

budget_allocation = pd.DataFrame({
    'weekday': weekdays,
    'predicted_revenue': predicted_revenues
})

total_pred = budget_allocation['predicted_revenue'].abs().sum()
budget_allocation['budget_percent'] = (budget_allocation['predicted_revenue'].abs() 
                                      / total_pred * 100).round(1)

print("\nOptimized Marketing Budget Allocation:")
print(budget_allocation[['weekday', 'budget_percent']]
      .sort_values('budget_percent', ascending=False))
