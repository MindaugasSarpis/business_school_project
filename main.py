"""
Author: Zulkernain Tasin
Institution: Vilnius University Business School
Project: Financial Assistant (FINASS)
Version: 1.0
Description:
    This program is developed as part of the Financial Assistant (FINASS) project
    to help visualize and analyze personal financial data.
    It includes monthly summaries, categorization by account groups,
    and graphical representation of cash flows (including income, expenses, and transfers).

    Also a demo to predict saving goals

Note:
    This version was submitted and demonstrated during the academic exam session.
    All features reflect Version 1 functionality.
"""

print("Financial Assistant V1.0")

import os
import depends

# Defining Environment and Importing Panda
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.2f}'.format

# Importing Custom Functions
from depends.groups import load_account_groups 
from depends.analysis import analyze_account_groups_monthly

from FinAss import finAss 
from depends.predict import predict_savings

# Defining input Files
GROUP_FILE = 'depends/account_groups.txt'
CSV_FILE = 'depends/PerFinData.csv'

# Load Accounts and Groups
account_groups = load_account_groups(CSV_FILE,GROUP_FILE)
# Analyze and plot monthly data by account group
all_group_dfs = analyze_account_groups_monthly(CSV_FILE,account_groups)

# Plotting brift view of Income Expense Net and Balance
finAss(CSV_FILE)
print(all_group_dfs)
# Future Prediction 
predict_savings(CSV_FILE,'Savings') # Need to work on this part to predict all of the accounts in the CSV after grouping 