"""
E-commerce Analytics Report Generator
Author: Rytis Bimbiras
"""

# ========== SECTION 1: CONFIGURATION ==========
# Import libraries with standard aliases
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import sys
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages

# Configure global settings
sns.set(style="whitegrid")  # Set consistent visual style
plt.rcParams['font.size'] = 10  # Base font size for all plots
DEBUG_MODE = True  # Set to False to disable debug prints

# ========== SECTION 2: DATA LOADING & VALIDATION ==========
def load_and_validate_data(filename):
    """
    Load and validate the input Excel file
    Returns DataFrame if successful, exits program otherwise
    """
    try:
        # Load data with strict dtype checking
        df = pd.read_excel(filename, engine='openpyxl')
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Validate required columns
        required_columns = {
            'order_id', 'date', 'shop', 'delivery_method',
            'payment_status', 'ordered_quantity', 'item_price'
        }
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
            
        if DEBUG_MODE:
            print("✅ Data loaded successfully")
            print(f"📊 Initial row count: {len(df)}")
            
        return df
        
    except Exception as e:
        print(f"❌ Critical error loading data: {str(e)}")
        sys.exit(1)

# ========== SECTION 3: DATA PROCESSING ==========
def process_data(raw_df):
    """
    Clean and transform raw data into analysis-ready format
    Returns processed DataFrame
    """
    try:
        # Create copy to avoid modifying original data
        df = raw_df.copy()
        
        # ------ DateTime Conversion ------
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if df['date'].isna().any():
            print("⚠️ Warning: Some dates could not be parsed")
            
        # ------ Time Period Calculations ------
        df['week'] = df['date'].dt.to_period('W').dt.start_time
        df['month'] = df['date'].dt.strftime('%Y-%m')  # More readable format
        
        # ------ Financial Calculations ------
        df['total_price'] = df['item_price'] * df['ordered_quantity']
        
        # ------ Address Parsing ------
        def extract_city(address):
            """Helper function to extract city from address string"""
            if pd.isna(address):
                return 'Unknown'
            match = re.search(r',\s*([^,]+),\s*LT-\d+', str(address))
            return match.group(1).strip() if match else 'Unknown'
            
        df['city'] = df['address'].apply(extract_city)
        
        if DEBUG_MODE:
            print("✅ Data processing completed")
            print(f"🌆 Cities detected: {df['city'].nunique()}")
            
        return df
        
    except Exception as e:
        print(f"❌ Data processing error: {str(e)}")
        sys.exit(1)

# ========== SECTION 4: BUSINESS ANALYTICS ==========
def calculate_metrics(clean_df):
    """
    Calculate key business metrics from cleaned data
    Returns dictionary of DataFrames with calculated metrics
    """
    metrics = {}
    
    try:
        # ------ Weekly Metrics ------
        weekly = clean_df.groupby('week').agg(
            revenue=('total_price', 'sum'),
            sales=('ordered_quantity', 'sum'),
            orders=('order_id', 'nunique')
        ).reset_index()
        weekly['avg_order_value'] = weekly['revenue'] / weekly['orders']
        metrics['weekly'] = weekly
        
        # ------ Monthly Metrics ------
        monthly = clean_df.groupby('month').agg(
            revenue=('total_price', 'sum'),
            sales=('ordered_quantity', 'sum'),
            orders=('order_id', 'nunique')
        ).reset_index()
        monthly['avg_order_value'] = monthly['revenue'] / monthly['orders']
        metrics['monthly'] = monthly
        
        # ------ Shop Performance ------
        metrics['shop_perf'] = clean_df.groupby('shop').agg(
            revenue=('total_price', 'sum'),
            sales=('ordered_quantity', 'sum'),
            orders=('order_id', 'nunique')
        ).reset_index()
        
        # ------ Payment vs Fulfillment ------
        # KEY DIFFERENCE: 
        # Payment Methods = how customers paid (credit card, cash, etc)
        # Fulfillment Status = order processing status (completed, pending, etc)
        metrics['payment_month'] = pd.crosstab(clean_df['month'], clean_df['payment_status'])
        metrics['fulfillment_month'] = pd.crosstab(clean_df['month'], clean_df['order_processed'])
        
        # ------ Customer Geography ------
        metrics['city_month'] = pd.crosstab(clean_df['month'], clean_df['city'])
        
        if DEBUG_MODE:
            print("✅ Metrics calculated")
            
        return metrics
        
    except Exception as e:
        print(f"❌ Metric calculation error: {str(e)}")
        sys.exit(1)

# ========== SECTION 5: VISUALIZATION ==========
def create_visualizations(metrics, output_file):
    """
    Generate professional visualizations and save to PDF
    """
    try:
        with PdfPages(output_file) as pdf:
            # ------ Helper Functions ------
            def style_plot(ax, title, ylabel, xlabel=None):
                """Standardize plot styling"""
                ax.set_title(title, pad=20)
                ax.set_ylabel(ylabel)
                if xlabel:
                    ax.set_xlabel(xlabel)
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                
            # ------ Revenue Analysis ------
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.lineplot(
                x=metrics['weekly']['week'], 
                y=metrics['weekly']['revenue'],
                marker='o',
                ax=ax
            )
            style_plot(ax, 'Weekly Revenue Trend', 'Revenue (€)', 'Week')
            pdf.savefig()
            plt.close()
            
            # ------ Payment vs Fulfillment Comparison ------
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Payment Methods
            metrics['payment_month'].plot(kind='bar', stacked=True, ax=ax1, cmap='Pastel1')
            style_plot(ax1, 'Payment Methods per Month', 'Number of Orders')
            
            # Fulfillment Status
            metrics['fulfillment_month'].plot(kind='bar', stacked=True, ax=ax2, cmap='Set2')
            style_plot(ax2, 'Order Fulfillment Status per Month', 'Number of Orders')
            
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            
            # ------ Additional Recommended Visualizations ------
            # (Add more plots as needed following same pattern)
            
        if DEBUG_MODE:
            print(f"✅ Report saved to {output_file}")
            
    except Exception as e:
        print(f"❌ Visualization error: {str(e)}")
        sys.exit(1)

# ========== SECTION 6: MAIN EXECUTION ==========
if __name__ == "__main__":
    print("=== E-commerce Analytics Report Generator ===")
    
    # Step 1: Load Data
    raw_data = load_and_validate_data('orders.xlsx')
    
    # Step 2: Process Data
    clean_data = process_data(raw_data)
    
    # Step 3: Calculate Metrics
    business_metrics = calculate_metrics(clean_data)
    
    # Step 4: Generate Report
    create_visualizations(business_metrics, 'enhanced_eshop_report.pdf')
    
    print("=== Analysis Complete ===")
