"""
    For Testing Code
"""

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
