import pandas as pd

def read_file(file_name):
    print('File read successfully')
    return pd.read_csv(file_name)

def clean_data(file):
    return read_file(file)