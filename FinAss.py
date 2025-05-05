"""
Author: Zulkernain Tasin
Institution: Vilnius University Business School
Project: Financial Assistant (FINASS)
Version: 1.0
Description:
    This function 

Note:
    This version was submitted and demonstrated during the academic exam session.
    All features reflect Version 1 functionality.
"""

import os
import depends

# Defining Environment and Importing Panda
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.2f}'.format

# Load and preprocess

def finAss(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    df['Period'] = pd.to_datetime(df['Period'], errors='coerce', dayfirst=True)
    df['Month'] = df['Period'].dt.to_period('M').astype(str)
    df['Income/Expense'] = (
        df['Income/Expense']
        .str.strip()
        .str.lower()
        .replace({
            'exp.': 'expense'
        })
    )
    df['EUR'] = pd.to_numeric(df['EUR'], errors='coerce')

    # Clean and list unique accounts
    accounts = df['Accounts'].dropna().unique()

    # Filter Swedbank-related accounts
    swed_accounts = accounts #['Swedbank']
    df_swed = df[df['Accounts'].isin(swed_accounts)]

    # Group by month and original income/expense/transfer-in/out type
    monthly_swed = (
        df_swed.groupby(['Month', 'Income/Expense'])['EUR']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Calculate Net manually
    income = monthly_swed.get('income', 0)+monthly_swed.get('transfer-in', 0)
    expense = monthly_swed.get('expense', 0)+monthly_swed.get('transfer-out', 0)
    monthly_swed['Net'] = income - expense

    monthly_swed['Balance'] = monthly_swed.get('Net',0).cumsum()

    #print(monthly_swed['Balance'])

    # Plot
    plt.figure(figsize=(12, 6))

    #for col in monthly_swed.columns[1:]:
    #    plt.plot(monthly_swed['Month'], monthly_swed[col], label=col.capitalize(), marker='o')

    plt.plot(monthly_swed['Month'], monthly_swed.get('income', 0), label='Income', marker='o')
    plt.plot(monthly_swed['Month'], monthly_swed.get('expense', 0), label='Expense', marker='o')
    plt.plot(monthly_swed['Month'], monthly_swed['Net'], label='Net', linestyle='--', marker='o')
    plt.plot(monthly_swed['Month'], monthly_swed['Balance'], label='Balance', linestyle='-', marker='o', linewidth=2)


    plt.title('Monthly Financial Overview (Swedbank & Swedbank Saving)')
    plt.xlabel('Month')
    plt.ylabel('EUR')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
