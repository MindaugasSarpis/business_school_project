import pandas as pd
import numpy as np

def clean_data(df):
    """
    Perform common data cleaning operations on a pandas DataFrame
    """
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    
    # 2. Handle missing values
    df['numeric_col'] = df['numeric_col'].fillna(df['numeric_col'].mean())  # Fill with mean
    df['categorical_col'] = df['categorical_col'].fillna('Unknown')  # Fill with default value
    
    # 3. Remove whitespace from string columns
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].str.strip()
    
    # 4. Convert to proper data types
    df['date_col'] = pd.to_datetime(df['date_col'], errors='coerce')
    df['numeric_col'] = pd.to_numeric(df['numeric_col'], errors='coerce')
    
    # 5. Handle outliers using IQR method
    Q1 = df['numeric_col'].quantile(0.25)
    Q3 = df['numeric_col'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df['numeric_col'] < (Q1 - 1.5 * IQR)) | (df['numeric_col'] > (Q3 + 1.5 * IQR)))]
    
    # 6. Standardize text case in categorical columns
    df['categorical_col'] = df['categorical_col'].str.lower()
    
    return df

if __name__ == "__main__":
    # Create sample data
    data = {
        'numeric_col': [1, 2, np.nan, 4, 100, 6, 7, 8],
        'categorical_col': ['A ', ' B', 'C', np.nan, 'A', 'B ', ' C ', 'A'],
        'date_col': ['2025-01-01', '2025-01-02', 'invalid_date', '2025-01-04',
                     '2025-01-05', '2025-01-06', '2025-01-07', '2025-01-01']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    print("Original Data:")
    print(df)
    print("\nShape before cleaning:", df.shape)
    
    # Clean the data
    cleaned_df = clean_data(df)
    print("\nCleaned Data:")
    print(cleaned_df)
    print("\nShape after cleaning:", cleaned_df.shape)
