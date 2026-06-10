import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\statewise\clustering_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass
sys.stdout = Logger()

print("Loading cleaned statewise data for clustering...")
df = pd.read_csv(r'd:\Papers\Lipi\data\statewise\cleaned_statewise_data.csv')

# Drop UNCLASSIFIED
df = df[~df['state'].str.contains('UNCLASSIFIED', na=False)]

# 1. Scale Features
features = ['volume_mn', 'ATS']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

# 2. Elbow Method (We'll assume K=3 is theoretically sound for Mature/Emerging/Laggard)
wcss = []
K_range = range(1, 10)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(K_range, wcss, marker='o', linestyle='--')
plt.title('Elbow Method For State Maturity Clusters')
plt.xlabel('Number of Clusters')
plt.ylabel('WCSS')
plt.grid(True)
plt.savefig(r'd:\Papers\Lipi\eda\statewise\elbow_plot.png')
plt.close()

# 3. Fit K-Means with K=3
k_optimal = 3
kmeans = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# 4. Visualizing Clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='ATS', y='volume_mn', hue='Cluster', palette='viridis', s=100, alpha=0.8)
plt.title('Statewise Maturity: ATS vs Total Volume')
plt.xlabel('Average Ticket Size (Rs.)')
plt.ylabel('Total Volume (Millions) - Log Scale')
plt.yscale('log')
plt.grid(True, which="both", ls="--", alpha=0.3)

# Annotate some top states
for idx, row in df.sort_values(by='volume_mn', ascending=False).head(5).iterrows():
    plt.annotate(row['state'], (row['ATS'], row['volume_mn']), xytext=(5, 5), textcoords='offset points')

plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\models\statewise\state_clusters.png')
plt.close()

# 5. Analysis Readout
print("\n--- K-MEANS STATE CLUSTER ANALYSIS ---")
for i in range(k_optimal):
    cluster_data = df[df['Cluster'] == i]
    avg_ats = cluster_data['ATS'].mean()
    total_vol = cluster_data['volume_mn'].sum()
    print(f"\nCluster {i} Summary:")
    print(f"- Number of States: {len(cluster_data)}")
    print(f"- Average ATS of Cluster: Rs.{avg_ats:.2f}")
    print(f"- Total Historical Volume: {total_vol:,.0f} Mn")
    
    print("- Sample States in this Cluster:")
    top_sample = cluster_data.sort_values(by='volume_mn', ascending=False).head(4)
    for _, row in top_sample.iterrows():
        print(f"  * {row['state']} (ATS: Rs.{row['ATS']:.0f}, Vol: {row['volume_mn']:,.0f} Mn)")

df.to_csv(r'd:\Papers\Lipi\data\statewise\statewise_clusters.csv', index=False)
print("\nClustering complete! Outputs saved to modular folders.")
