import os
import pandas as pd

# ACCOUNT NAME CAN NOT START OR END WITH BLANK SPACE

def load_account_groups(csv_file='PerFinData.csv', group_file='account_groups.txt'):
    """
    Loads account groupings from a file, or prompts the user to create them if not found.
    
    Parameters:
        csv_file (str): Path to the input CSV file.
        group_file (str): Path to the account group mapping text file.

    Returns:
        dict: A dictionary mapping accounts to their group.
    """
    group_options = {
        '1': 'Bank',
        '2': 'Savings',
        '3': 'Cash',
        '4': 'Loan',
        '5': 'Other'
    }

    # Load from file if it exists
    if os.path.exists(group_file):
        with open(group_file, 'r') as f:
            lines = f.readlines()
        return {line.split('=>')[0].strip(): line.split('=>')[1].strip() for line in lines}

    # File not found, prompt user to assign groups
    df = pd.read_csv(csv_file)
    unique_accounts = sorted(df['Accounts'].dropna().unique())

    print("\nGrouping Options:")
    for key, value in group_options.items():
        print(f"  {key}: {value}")

    account_groups = {}
    for i, acc in enumerate(unique_accounts, 1):
        while True:
            choice = input(f"{i}. {acc}: Enter group number (1-5, 0 to Exit): ").strip()
            if choice == '0':
                return 
            elif choice in group_options:
                account_groups[acc] = group_options[choice]
                break
            else:
                print("Invalid input. Please enter a number between 1 and 5.")

    # Save to file
    with open(group_file, 'w') as f:
        for acc, grp in account_groups.items():
            f.write(f"{acc} => {grp}\n")

    print(f"\n✅ Saved account groups to '{group_file}'")
    return account_groups
