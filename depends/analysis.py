"""
Author: Zulkernain Tasin
Institution: Vilnius University Business School
Project: Financial Assistant (FINASS)
Version: 1.0
Description:
    This Projects different account (defined: Bank, Savings, Loan, Cash and Others)
    and visualize their balances.

Note:
    This version was submitted and demonstrated during the academic exam session.
    All features reflect Version 1 functionality.
"""


import pandas as pd
import matplotlib.pyplot as plt
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.width', None)

def analyze_account_groups_monthly(csv_file, account_groups):
    """
    Analyze and plot monthly financial data grouped by account category (Bank, Savings, Cash, Loan, Other).
    
    Treats:
    - Income: +
    - Expense: -
    - Transfer In: +
    - Transfer Out: -
    
    Parameters:
        csv_file (str): Path to the CSV file.
        account_groups (dict): Mapping of account names to group labels.
    """

    # Load CSV
    df = pd.read_csv(csv_file)
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
    
    # Ensure we have account groups
    if account_groups is None:
        print("⚠️ No account groupings found. Please load account groups first.")
        return
    #account_groups = {'Ammu': 'Loan', 'Bolt': 'Other', 'Cash': 'Cash', 'Ethos 24': 'Loan', 'Fleetfox': 'Other', 'Golam Rabbi': 'Loan', 'Neste Fuel': 'Other', 'Revolut': 'Bank','RevolutSaving ':'Savings', 'Sourov': 'Loan', 'Swedbank': 'Bank', 'Swedbank Saving': 'Savings', 'Wise': 'Bank', 'Wolt': 'Other'}
    # Map each account to its group
    df['AccountGroup'] = df['Accounts'].map(account_groups)

    #print(df['Accounts'].unique())
    #print(df['AccountGroup'])
    # print(account_groups)
    
    # Create new columns for types of financial flow
    df['Income'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'income' else 0, axis=1)
    df['Expense'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'expense' else 0, axis=1)
    df['TransferIn'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'transfer-in' else 0, axis=1)
    df['TransferOut'] = df.apply(lambda row: row['EUR'] if row['Income/Expense'] == 'transfer-out' else 0, axis=1)

    # Calculate net flow per row
    df['Net'] = df['Income'] - df['Expense'] + df['TransferIn'] - df['TransferOut']
    
    # Group by Month and AccountGroup
    grouped = df.groupby(['Month', 'AccountGroup']).agg({
        'Income': 'sum',
        'Expense': 'sum',
        'TransferIn': 'sum',
        'TransferOut': 'sum',
        'Net': 'sum'
    }).reset_index()
    
    #print(grouped)

    # Calculate running total (cumulative net) for each group
    all_group_dfs = []

    for group in grouped['AccountGroup'].unique():
        group_df = grouped[grouped['AccountGroup'] == group].copy()
        group_df.sort_values('Month', inplace=True)
        group_df['Total'] = group_df['Net'].cumsum()
        all_group_dfs.append(group_df)
    
    # Debug
    """
    target_group = 'Cash'

    for gdf in all_group_dfs:
        group = gdf['AccountGroup'].iloc[0]
        if target_group.strip().lower() in group.strip().lower():
            print(f"\n🔍 Data for group: {group}")
            print(gdf)
    """

    # Plot
    plt.figure(figsize=(12, 8))

    for gdf in all_group_dfs:
        group = gdf['AccountGroup'].iloc[0]
        # if(group=='Loan'): continue #ignoring Loan Profile
        #plt.plot(gdf['Month'], gdf['Income'], label=f'{group} Income', marker='o')
        #plt.plot(gdf['Month'], gdf['Expense'], label=f'{group} Expense', marker='o')
        #plt.plot(gdf['Month'], gdf['TransferIn'], label=f'{group} Transfer In', linestyle='dotted')
        #plt.plot(gdf['Month'], gdf['TransferOut'], label=f'{group} Transfer Out', linestyle='dotted')
        #plt.plot(gdf['Month'], gdf['Net'], label=f'{group} Net', linestyle='--', linewidth=2)
        plt.plot(gdf['Month'], gdf['Total'], label=f'{group} Running Total', linewidth=2)
        for col in ['Total']:
            for i, value in enumerate(gdf[col]):
                if abs(value) > 1e-1:  # Skip near-zero values
                    x = gdf['Month'].iloc[i]
                    y = value
                    plt.text(x, y, f'{value:,.0f}', fontsize=8, ha='center', va='bottom', rotation=0)

    # 👇 Combine all group DataFrames
    combined_df = pd.concat(all_group_dfs) #No Group ignored
    # Particular Group Ignored
    # combined_df = pd.concat([gdf for gdf in all_group_dfs if gdf['AccountGroup'].iloc[0] != 'Loan'])


    # 👇 Sum Total per Month across all groups
    total_assets = combined_df.groupby('Month')['Total'].sum().reset_index()

    # 👇 Plot the total asset line
    plt.plot(
        total_assets['Month'], 
        total_assets['Total'], 
        label='💰 Total Assets', 
        linestyle='--', 
        color='black', 
        linewidth=3, 
        marker='o'
    )

    # Annotate total asset values
    for i, value in enumerate(total_assets['Total']):
        x = total_assets['Month'].iloc[i]
        y = value
        if abs(value) > 1e-1:
            plt.text(x, y, f'{value:,.0f}', fontsize=9, ha='center', va='bottom', color='black', fontweight='bold')

    plt.title("Monthly Financial Summary by Account Group (with Transfers)")
    plt.xlabel("Month")
    plt.ylabel("EUR")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return all_group_dfs