import pandas as pd

try:
    df = pd.read_csv('student-mat.csv', sep=';')
    print(df.head())
    print(df.shape)
except FileNotFoundError:
    print("Error: 'student-mat.csv' not found. Please ensure the file exists in the current directory.")
    df = None

import matplotlib.pyplot as plt
import seaborn as sns

# 1. Distribution of Final Grades
plt.figure(figsize=(8, 6))
sns.histplot(df['G3'], kde=True, color='skyblue')
plt.title('Distribution of Final Grades (G3)')
plt.xlabel('Final Grade (G3)')
plt.ylabel('Frequency')
plt.show()

# 2. Average Final Grade across Categories
categorical_features = ['school', 'sex', 'address', 'famsize', 'Pstatus', 'Mjob', 'Fjob', 'reason', 'guardian']
plt.figure(figsize=(15, 20))
for i, col in enumerate(categorical_features):
    plt.subplot(5, 2, i + 1)
    df.groupby(col)['G3'].mean().plot(kind='bar', color='skyblue')
    plt.title(f'Average G3 by {col}')
    plt.ylabel('Average G3')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
plt.show()