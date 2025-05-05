"""
Author: Zulkernain Tasin
Institution: Vilnius University Business School
Project: Financial Assistant (FINASS)
Version: 1.0
Description:
    Function takes an account type as input and predicts future balance according to the data

Note:
    This version was submitted and demonstrated during the academic exam session.
    All features reflect Version 1 functionality.
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
import numpy as np

# ----------------- CONFIGURATION -----------------

CSV_FILE = "depends/PerFinData.csv"

# Example grouping (customize as needed)
account_groups = {
    'RevolutSaving': 'Savings',
    'Swedbank Saving': 'Savings',
    'Swedbank': 'Bank',
    'Wise': 'Bank',
    'Cash': 'Cash',
    'Loan Provider': 'Loan',
    'Ethos 24': 'Loan',
    'Fleetfox': 'Other',
    'Wolt': 'Other',
    'Bolt': 'Other'
}

# ----------------- MAIN FUNCTION -----------------

def predict_savings(csv_file, group_name):
    # Load CSV
    df = pd.read_csv(csv_file)
    df['Period'] = pd.to_datetime(df['Period'], dayfirst=True, errors='coerce')
    df['Month'] = df['Period'].dt.to_period('M').astype(str)
    df['EUR'] = pd.to_numeric(df['EUR'], errors='coerce')
    
    # Standardize Income/Expense column
    df['Income/Expense'] = (
        df['Income/Expense']
        .str.strip()
        .str.lower()
        .replace({'exp.': 'expense'})
    )
    
    # Map account group
    df['AccountGroup'] = df['Accounts'].map(account_groups)

    # Filter only savings accounts
    df = df[df['AccountGroup'] == group_name]

    # Classify flows
    df['Income'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'income' else 0, axis=1)
    df['Expense'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'expense' else 0, axis=1)
    df['TransferIn'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'transfer-in' else 0, axis=1)
    df['TransferOut'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'transfer-out' else 0, axis=1)

    df['Net'] = df['Income'] - df['Expense'] + df['TransferIn'] - df['TransferOut']

    # Monthly aggregation
    monthly = df.groupby('Month').agg({
        'Income': 'sum',
        'Expense': 'sum',
        'Net': 'sum'
    }).reset_index()

    # Convert months to numerical order for regression
    monthly['MonthIndex'] = np.arange(len(monthly))
    
    # Prepare features and target
    X = monthly[['MonthIndex']]
    y = monthly['Net'].cumsum()  # total savings over time

    # Linear Regression
    model = LinearRegression()
    model.fit(X, y)

    # Predict next 6 months
    future_months = np.arange(len(monthly), len(monthly) + 6).reshape(-1, 1)
    predictions = model.predict(future_months)

    # Create forecast DataFrame
    future_df = pd.DataFrame({
        'MonthIndex': future_months.flatten(),
        'PredictedSavings': predictions
    })

    # Combine for plotting
    combined = pd.concat([
        monthly[['MonthIndex', 'Month']].assign(Savings=y),
        future_df.rename(columns={'PredictedSavings': 'Savings'}).assign(Month='Future')
    ])

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(combined['MonthIndex'], combined['Savings'], marker='o', label='Savings (Actual & Predicted)')
    plt.axvline(x=X['MonthIndex'].iloc[-1], color='gray', linestyle='--', label='Prediction Start')
    plt.title(f"Predicted Savings using Linear Regression ({group_name})")
    plt.xlabel("Month Index")
    plt.ylabel("Cumulative Savings (EUR)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ----------------- RUN -----------------

#predict_savings(CSV_FILE,'Cash')
