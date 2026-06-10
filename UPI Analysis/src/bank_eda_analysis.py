import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\banks\eda_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass
sys.stdout = Logger()

print("Loading cleaned bank data...")
df = pd.read_csv(r'd:\Papers\Lipi\data\banks\cleaned_bank_data.csv')

# Drop Cooperative/Other banks for the core Public vs Private analysis, as they handle negligible volume
core_banks = df[df['Bank_Type'] != 'Other/Cooperative']

print("\n--- HISTORICAL FAILURE RATES (PUBLIC VS PRIVATE) ---")
type_stats = core_banks.groupby('Bank_Type')[['TD_Percent', 'BD_Percent']].mean().reset_index()
print(type_stats)

plt.figure(figsize=(8, 5))
sns.barplot(data=type_stats, x='Bank_Type', y='TD_Percent', palette='Set2')
plt.title('Average Technical Decline Rate (Server Crashes) by Bank Sector')
plt.ylabel('Average Technical Decline (TD%)')
plt.xlabel('Bank Sector')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\banks\public_vs_private_td.png')
plt.close()

print("\n--- TOP MOST STRESSED BANKS (BY TECHNICAL DECLINE) ---")
# Group by bank to find average TD% and Volume across the dataset
bank_stress = core_banks.groupby('Remitter Bank')[['TD_Percent', 'Total Volume']].mean().reset_index()
# Filter for banks that actually have significant volume to avoid small-sample noise
bank_stress = bank_stress[bank_stress['Total Volume'] > 5000].sort_values(by='TD_Percent', ascending=False)
print(bank_stress.head(5))

plt.figure(figsize=(10, 6))
sns.barplot(data=bank_stress.head(10), x='Remitter Bank', y='TD_Percent', palette='Reds_r')
plt.title('Top 10 Most Stressed Major Banks (Highest Server Crash Rates)')
plt.ylabel('Average Technical Decline (TD%)')
plt.xlabel('Bank')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\banks\top_stressed_banks.png')
plt.close()

print("\n--- VOLUME VS SERVER CRASH CORRELATION ---")
plt.figure(figsize=(10, 6))
sns.scatterplot(data=core_banks, x='Total Volume', y='TD_Percent', hue='Bank_Type', palette='Set1', alpha=0.6, s=60)
plt.title('Infrastructure Stress: Transaction Volume vs Technical Declines')
plt.xlabel('Total Transaction Volume (Log Scale)')
plt.ylabel('Technical Decline Rate (TD%)')
plt.xscale('log') # Log scale because SBI volume dwarfs everyone else
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\banks\volume_vs_td_scatter.png')
plt.close()

print("\nHistorical EDA complete! Charts saved to eda/banks/")
