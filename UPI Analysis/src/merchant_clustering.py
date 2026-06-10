import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import sys

os.makedirs(r'd:\Papers\Lipi\eda\merchant', exist_ok=True)
os.makedirs(r'd:\Papers\Lipi\models\merchant', exist_ok=True)
os.makedirs(r'd:\Papers\Lipi\logs\merchant', exist_ok=True)

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\merchant\clustering_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass
sys.stdout = Logger()

# 1. Load Data
print("Loading preprocessed merchant data...")
df = pd.read_csv(r'd:\Papers\Lipi\data\merchant\cleaned_merchant_data.csv')

# 2. Scale Features
features = ['volume_mn', 'ATS']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

# 3. Elbow Method
wcss = []
K_range = range(1, 10)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(K_range, wcss, marker='o', linestyle='--')
plt.title('Elbow Method For Optimal K')
plt.xlabel('Number of Clusters')
plt.ylabel('WCSS (Within-Cluster Sum of Squares)')
plt.grid(True)
plt.savefig(r'd:\Papers\Lipi\eda\merchant\elbow_plot.png')
plt.close()

print("Elbow plot generated. Proceeding with K=3 clusters based on economic theory (Micro, Standard, High-Value).")

# 4. Run K-Means with K=3
k_optimal = 3
kmeans = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# 5. Visualize Clusters
plt.figure(figsize=(10, 6))
# We use log scale because financial transaction volume often has extreme outliers (e.g., Groceries dwarfs everything else)
sns.scatterplot(data=df, x='ATS', y='volume_mn', hue='Cluster', palette='viridis', s=100, alpha=0.8)
plt.title('UPI Merchant Categories: ATS vs Total Volume')
plt.xlabel('Average Ticket Size (₹) - Log Scale')
plt.ylabel('Total Volume (Millions) - Log Scale')
plt.yscale('log') 
plt.xscale('log') 
plt.legend(title='Economic Cluster')
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\models\merchant\ats_vs_volume_clusters.png')
plt.close()

# 6. Analyze and Log Results
print("\n--- K-MEANS CLUSTER ANALYSIS ---")
for i in range(k_optimal):
    cluster_data = df[df['Cluster'] == i]
    avg_ats = cluster_data['ATS'].mean()
    total_vol = cluster_data['volume_mn'].sum()
    print(f"\nCluster {i} Summary:")
    print(f"- Number of Categories in Cluster: {len(cluster_data)}")
    print(f"- Average ATS of Cluster: Rs.{avg_ats:.2f}")
    print(f"- Total Historical Volume: {total_vol:,.0f} Million")
    
    # Sort by volume to find the dominators
    top_categories = cluster_data.sort_values(by='volume_mn', ascending=False).head(5)
    print("- Top 5 Categories Driving this Cluster:")
    for _, row in top_categories.iterrows():
        print(f"  * {row['category']} (ATS: Rs.{row['ATS']:.0f}, Vol: {row['volume_mn']:,.0f} Mn)")

df.to_csv(r'd:\Papers\Lipi\data\merchant\merchant_clusters.csv', index=False)
print("\nClustering complete! All outputs saved to modular folders.")
