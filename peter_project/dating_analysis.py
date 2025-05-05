import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better visualizations
sns.set_theme(style="whitegrid")

# Read the dataset
df = pd.read_csv('dating_dataset.csv')
print("Original dataset shape:", df.shape)
print("\nColumns in the dataset:", df.columns.tolist())

# Basic cleaning specific to this dataset
def clean_dating_data(df):
    df = df.copy()
    
    # Convert interests from string to list
    df['Interests'] = df['Interests'].apply(eval)
    
    # Convert numeric columns
    numeric_cols = ['Height', 'Age']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean categorical columns
    categorical_cols = ['Gender', 'Looking For', 'Children', 'Education Level', 'Occupation', 'Frequency of Usage']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].str.strip()
    
    # Remove any rows with missing values
    df = df.dropna()
    
    return df

# Clean the data
df_clean = clean_dating_data(df)
print("\nCleaned dataset shape:", df_clean.shape)

# Analysis and Visualization
def analyze_dating_data(df):
    # 1. Gender Distribution
    plt.figure(figsize=(12, 8))
    sns.countplot(data=df, x='Gender')
    plt.title('Gender Distribution')
    plt.savefig('gender_distribution.png')
    plt.close()
    
    # 2. Relationship Goals Distribution
    plt.figure(figsize=(12, 8))
    sns.countplot(data=df, x='Looking For')
    plt.xticks(rotation=45)
    plt.title('Relationship Goals Distribution')
    plt.tight_layout()
    plt.savefig('relationship_goals.png')
    plt.close()
    
    # 3. Height Distribution by Gender
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=df, x='Gender', y='Height')
    plt.title('Height Distribution by Gender')
    plt.savefig('height_by_gender.png')
    plt.close()
    
    # 4. Most Common Interests
    all_interests = [interest for interests_list in df['Interests'] for interest in interests_list]
    interest_counts = pd.Series(all_interests).value_counts()
    
    plt.figure(figsize=(12, 8))
    interest_counts.head(10).plot(kind='bar')
    plt.title('Top 10 Most Common Interests')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('top_interests.png')
    plt.close()
    
    # 5. Education Level Distribution
    plt.figure(figsize=(12, 8))
    sns.countplot(data=df, x='Education Level')
    plt.xticks(rotation=45)
    plt.title('Education Level Distribution')
    plt.tight_layout()
    plt.savefig('education_distribution.png')
    plt.close()
    
    # Print some statistical insights
    print("\nDataset Insights:")
    print(f"Total number of users: {len(df)}")
    print(f"\nGender distribution:\n{df['Gender'].value_counts(normalize=True).round(3) * 100}%")
    print(f"\nMost popular relationship goal: {df['Looking For'].mode()[0]}")
    print(f"\nMost common occupation: {df['Occupation'].mode()[0]}")
    print(f"\nAverage height: {df['Height'].mean():.2f}")
    print(f"\nMost popular interest: {interest_counts.index[0]}")
    print(f"\nMost common education level: {df['Education Level'].mode()[0]}")
    print(f"\nAge statistics:")
    print(df['Age'].describe())

# Run the analysis
analyze_dating_data(df_clean)
print("\nAnalysis complete! Check the generated PNG files for visualizations.")
