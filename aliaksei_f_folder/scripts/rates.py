"""
Exchange rates configuration.
Rates are stored as a dictionary where keys are currency codes and values are the exchange rate to EUR.
Example: 1 USD = 0.92 EUR means USD: 0.92
"""

# Exchange rates relative to EUR (1 EUR = X Currency)
EXCHANGE_RATES = {
    "AUD": 0.57734,  # 1 AUD = 0.57734 EUR
    "CAD": 0.64188,  # 1 CAD = 0.64188 EUR
    "EUR": 1.0,  # 1 EUR = 1.0 EUR
    "GBP": 1.19312,  # 1 GBP = 1.19312 EUR
    "USD": 0.91549,  # 1 USD = 0.91549 EUR
}

# Last update timestamp
LAST_UPDATED = "2025-04-22T15:06:35.482289"
