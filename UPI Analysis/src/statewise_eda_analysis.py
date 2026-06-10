import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\statewise\eda_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass
sys.stdout = Logger()

print("Loading cleaned statewise data...")
df = pd.read_csv(r'd:\Papers\Lipi\data\statewise\cleaned_statewise_data.csv')

# Drop UNCLASSIFIED garbage data
df = df[~df['state'].str.contains('UNCLASSIFIED', na=False)]

print("\n--- OPTION 1: THE URBAN VS RURAL ATS DIVIDE ---")
# Get top 15 states by volume to compare ATS
top_states = df.sort_values(by='volume_mn', ascending=False).head(15)

plt.figure(figsize=(12, 6))
sns.barplot(data=top_states, x='state', y='ATS', palette='coolwarm')
plt.title('Average Ticket Size (ATS) for Top 15 Highest Volume States')
plt.ylabel('Average Ticket Size (Rs.)')
plt.xlabel('State')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\statewise\state_ats_comparison.png')
plt.close()

print("ATS for Top 5 Volume States:")
print(top_states.head(5)[['state', 'volume_mn', 'ATS']])

print("\n--- OPTION 2: GEOGRAPHIC MONOPOLY ---")
total_network_volume = df['volume_mn'].sum()
top_4_volume = top_states.head(4)['volume_mn'].sum()
top_4_share = (top_4_volume / total_network_volume) * 100

print(f"Total Network Volume (Classified): {total_network_volume:,.0f} Mn")
print(f"Volume of Top 4 States: {top_4_volume:,.0f} Mn")
print(f"The Top 4 States control {top_4_share:.1f}% of the entire Indian UPI Network.")

# Pie Chart for Geographic Monopoly
labels = list(top_states.head(4)['state']) + ['Rest of India (All Other States & UTs)']
sizes = list(top_states.head(4)['volume_mn']) + [total_network_volume - top_4_volume]
explode = (0.1, 0.1, 0.1, 0.1, 0)

plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140, colors=sns.color_palette('Set2'))
plt.title('Geographic Monopoly: Volume Share of Top 4 States vs Rest of India')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\statewise\geographic_monopoly_pie.png')
plt.close()

print("\nEDA complete! Charts saved to eda/statewise/")
