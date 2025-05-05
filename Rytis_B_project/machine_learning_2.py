# Customer Segmentation using RFM Analysis and K-means Clustering
# This program groups customers based on their buying behavior

# Import the tools we need
import pandas as pd                                  # For data handling
import matplotlib.pyplot as plt                      # For creating charts
from sklearn.preprocessing import StandardScaler     # For standardizing our data
from sklearn.cluster import KMeans                   # For clustering
from sklearn.metrics import silhouette_score         # For evaluating clusters
import seaborn as sns                                # For better visualizations

# STEP 1: Load and prepare the data
print("Loading the sales data...")
orders = pd.read_excel('orders.xlsx')
print(f"Loaded {len(orders)} order records from {len(orders['client'].unique())} unique customers.")

# Calculate the total amount spent for each order line
orders['total_spent'] = orders['item_price'] * orders['ordered_quantity']

# STEP 2: Calculate RFM metrics
print("\nCalculating customer shopping behavior metrics...")
# RFM stands for Recency, Frequency, Monetary
# - Recency: How recently did the customer purchase?
# - Frequency: How often does the customer purchase?
# - Monetary: How much does the customer spend?

# Group data by customer
customer_rfm = orders.groupby('client').agg({
    'date': lambda x: (pd.to_datetime(orders['date'].max()) - pd.to_datetime(x.max())).days,  # Days since last purchase
    'order_id': 'nunique',                                                                    # Number of orders
    'total_spent': 'sum'                                                                      # Total amount spent
}).reset_index()

# Rename columns for clarity
customer_rfm.columns = ['Customer', 'Recency', 'Frequency', 'Monetary']

# Show the first few rows
print("\nHere's what the customer data looks like:")
print(customer_rfm.head())

# STEP 3: Standardize the data
print("\nStandardizing the data (making all metrics comparable)...")
# We need to standardize because the metrics are on different scales
# (e.g., days vs. number of orders vs. euros)
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(customer_rfm[['Recency', 'Frequency', 'Monetary']])

# STEP 4: Find the optimal number of clusters
print("\nFinding the best number of customer groups...")
# The silhouette score helps us determine how well-separated the clusters are
silhouette_scores = []
cluster_range = range(2, 6)  # Try 2-5 clusters

for k in cluster_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    cluster_labels = kmeans.fit_predict(rfm_scaled)
    silhouette_avg = silhouette_score(rfm_scaled, cluster_labels)
    silhouette_scores.append(silhouette_avg)
    print(f"With {k} clusters, the silhouette score is {silhouette_avg:.3f}")

# STEP 5: Visualize the silhouette scores
plt.figure(figsize=(8, 5))
plt.plot(cluster_range, silhouette_scores, marker='o', linestyle='-')
plt.title('Silhouette Score for Different Numbers of Clusters')
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Score (higher is better)')
plt.grid(True)
plt.show()

# Find the best number of clusters
best_k = cluster_range[silhouette_scores.index(max(silhouette_scores))]
print(f"\nThe best number of customer groups is {best_k}, with a silhouette score of {max(silhouette_scores):.3f}")

# STEP 6: Apply K-means clustering with the optimal number of clusters
print(f"\nGrouping customers into {best_k} segments...")
kmeans = KMeans(n_clusters=best_k, random_state=42)
customer_rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# STEP 7: Analyze the clusters
print("\nAnalyzing the customer segments...")
cluster_summary = customer_rfm.groupby('Cluster').agg({
    'Customer': 'count',
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean'
}).reset_index()

cluster_summary.columns = ['Segment', 'Number of Customers', 'Days Since Last Purchase', 
                          'Number of Orders', 'Total Spent (€)']

# Sort by monetary value (highest spending segment first)
cluster_summary = cluster_summary.sort_values('Total Spent (€)', ascending=False)

# Print the segment summary
print("\nCustomer Segment Summary:")
print(cluster_summary)

# STEP 8: Visualize the customer segments
print("\nCreating a visual representation of the customer segments...")
plt.figure(figsize=(10, 8))

# Create a scatter plot
scatter = plt.scatter(
    customer_rfm['Recency'],                       # X-axis: Days since last purchase
    customer_rfm['Monetary'],                      # Y-axis: Total spent
    s=customer_rfm['Frequency'] * 50 + 50,         # Size: Number of orders
    c=customer_rfm['Cluster'],                     # Color: Cluster
    cmap='viridis',                                # Color map
    alpha=0.7                                      # Transparency
)

# Add labels and title
plt.title('Customer Segments Based on Shopping Behavior', fontsize=15)
plt.xlabel('Days Since Last Purchase (lower is better)', fontsize=12)
plt.ylabel('Total Amount Spent (€)', fontsize=12)

# Add a legend for the clusters
plt.colorbar(scatter, label='Customer Segment')

# Show the plot
plt.tight_layout()
plt.show()

# STEP 9: Provide business insights for each segment
print("\nBusiness Insights and Recommendations:")

# Calculate the average values for reference
avg_recency = cluster_summary['Days Since Last Purchase'].mean()
avg_frequency = cluster_summary['Number of Orders'].mean()
avg_monetary = cluster_summary['Total Spent (€)'].mean()

# For each segment, provide insights
for index, row in cluster_summary.iterrows():
    segment = row['Segment']
    count = row['Number of Customers']
    recency = row['Days Since Last Purchase']
    frequency = row['Number of Orders']
    monetary = row['Total Spent (€)']
    
    print(f"\nSEGMENT {segment}: {count} customers")
    print(f"  Average Days Since Last Purchase: {recency:.1f}")
    print(f"  Average Number of Orders: {frequency:.1f}")
    print(f"  Average Total Spent: €{monetary:.2f}")
    
    # Define segment characteristics and recommendations
    characteristics = []
    if recency < avg_recency:
        characteristics.append("recent shoppers")
    else:
        characteristics.append("not recent shoppers")
        
    if frequency > avg_frequency:
        characteristics.append("frequent buyers")
    else:
        characteristics.append("infrequent buyers")
        
    if monetary > avg_monetary:
        characteristics.append("high spenders")
    else:
        characteristics.append("low spenders")
    
    print(f"  Characteristics: These customers are {', '.join(characteristics)}.")
    
    # Provide specific recommendations based on segment characteristics
    if recency < avg_recency and frequency > avg_frequency and monetary > avg_monetary:
        print("  RECOMMENDATION: These are your VIP customers! Focus on:")
        print("  • Exclusive rewards and loyalty programs")
        print("  • Premium product offers")
        print("  • Personal thank-you messages")
    elif recency < avg_recency and frequency > avg_frequency:
        print("  RECOMMENDATION: These are your loyal customers. Focus on:")
        print("  • Upselling to premium products")
        print("  • Value-added services")
        print("  • Loyalty rewards")
    elif recency < avg_recency and monetary > avg_monetary:
        print("  RECOMMENDATION: These are big spenders who don't buy often. Focus on:")
        print("  • Regular communication")
        print("  • Early access to new products")
        print("  • Special events or offers")
    elif frequency > avg_frequency and monetary > avg_monetary:
        print("  RECOMMENDATION: These are valuable customers who haven't purchased recently. Focus on:")
        print("  • Re-engagement campaigns")
        print("  • Special comeback offers")
        print("  • New product announcements")
    elif recency < avg_recency:
        print("  RECOMMENDATION: These are recent but not frequent or high-value customers. Focus on:")
        print("  • Second purchase promotions")
        print("  • Product recommendations")
        print("  • Educational content")
    elif frequency > avg_frequency:
        print("  RECOMMENDATION: These are frequent but low-spending customers. Focus on:")
        print("  • Upselling and cross-selling")
        print("  • Bundle offers")
        print("  • Premium product trials")
    elif monetary > avg_monetary:
        print("  RECOMMENDATION: These are high-spending but infrequent and not recent customers. Focus on:")
        print("  • Re-engagement campaigns")
        print("  • Understanding purchase triggers")
        print("  • Personal outreach")
    else:
        print("  RECOMMENDATION: These are low-value, inactive customers. Focus on:")
        print("  • Reactivation campaigns")
        print("  • Surveys to understand dissatisfaction")
        print("  • Consider reducing marketing investment if no response")

print("\nAnalysis complete! You now have actionable insights into your customer segments.")
