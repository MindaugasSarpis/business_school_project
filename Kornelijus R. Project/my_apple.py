import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Fetch Apple stock data
ticker = 'AAPL'
apple = yf.Ticker(ticker)
df = apple.history(period='1mo')

# Create figure
plt.figure(figsize=(10, 5))
plt.plot(df.index, df['Close'], marker='o', linestyle='-', color='blue', label='Closing Price')

# Customize chart
plt.xlabel('Date')
plt.ylabel('Stock Price (USD)')
plt.title('Apple (AAPL) Stock Performance - Last Month')
plt.legend()
plt.grid()

# Show plot
plt.show()