import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('Europe_GDP.csv')
comparison_data = data[['Year', 'Finland', 'Norway']]

print("GDP Comparison (in USD):")
print(comparison_data)

plt.figure(figsize=(10, 6))
plt.plot(comparison_data['Year'], comparison_data['Finland'], label='Finland', color='blue')
plt.plot(comparison_data['Year'], comparison_data['Norway'], label='Norway', color='red')
plt.title('GDP Comparison: Finland vs. Norway (1960-2023)')
plt.xlabel('Year')
plt.ylabel('GDP (in USD)')
plt.legend()
plt.grid(True)
plt.show()