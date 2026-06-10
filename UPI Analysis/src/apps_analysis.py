import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\apps\analysis_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass
sys.stdout = Logger()

print("Loading App Data...")
df = pd.read_csv(r'd:\Papers\Lipi\datasets\Raw Datasets\master_upi_apps.csv')

# Data Cleaning
print("Cleaning data...")
# Format like 01/04/22
df['Snapshot_Month'] = pd.to_datetime(df['Snapshot_Month'], format='%d/%m/%y')
df['Total_Volume_Mn'] = pd.to_numeric(df['Total_Volume_Mn'].astype(str).str.replace(',', ''), errors='coerce')
df['Total_Value_Cr'] = pd.to_numeric(df['Total_Value_Cr'].astype(str).str.replace(',', ''), errors='coerce')
df = df.dropna()

# Normalize App Names
df['App_Name'] = df['App_Name'].str.strip()
df['App_Name'] = df['App_Name'].replace({'Phone Pe': 'PhonePe', 'Paytm Payments Bank App': 'Paytm'})

# 1. Overall App ATS Analysis
print("\n--- APP ATS ANALYSIS ---")
app_totals = df.groupby('App_Name').agg({'Total_Volume_Mn': 'sum', 'Total_Value_Cr': 'sum'}).reset_index()
app_totals['ATS'] = (app_totals['Total_Value_Cr'] / app_totals['Total_Volume_Mn']) * 10
# Filter for apps with at least 5 Mn total volume over the period to remove noise
app_totals = app_totals[app_totals['Total_Volume_Mn'] > 5].sort_values(by='ATS', ascending=True)

print("Top 10 Apps by Lowest ATS (The Micro-Transaction Drivers):")
for _, row in app_totals.head(10).iterrows():
    print(f"  * {row['App_Name']}: Rs.{row['ATS']:.0f}")

print("\nTop 5 Apps by Highest ATS (The High-Value Niche):")
for _, row in app_totals.tail(5).sort_values(by='ATS', ascending=False).iterrows():
    print(f"  * {row['App_Name']}: Rs.{row['ATS']:.0f}")

# Plot ATS Comparison for selected major apps vs niche apps
major_apps = ['PhonePe', 'Google Pay', 'Paytm Payments Bank App', 'Cred', 'BHIM', 'Amazon Pay']
plot_df = app_totals[app_totals['App_Name'].isin(major_apps)].sort_values('ATS')
plt.figure(figsize=(10, 6))
sns.barplot(data=plot_df, x='App_Name', y='ATS', palette='coolwarm')
plt.title('Average Ticket Size (ATS) by UPI App')
plt.ylabel('ATS (Rs.)')
plt.xlabel('App Name')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\apps\app_ats_comparison.png')
plt.close()

# 2. Market Share & Duopoly Analysis over time
monthly_totals = df.groupby('Snapshot_Month')['Total_Volume_Mn'].sum().reset_index()
monthly_totals.rename(columns={'Total_Volume_Mn': 'Network_Volume'}, inplace=True)
df = df.merge(monthly_totals, on='Snapshot_Month')
df['Market_Share_Pct'] = (df['Total_Volume_Mn'] / df['Network_Volume']) * 100

# Duopoly = PhonePe + Google Pay
duopoly_df = df[df['App_Name'].isin(['PhonePe', 'Google Pay'])].groupby('Snapshot_Month')['Market_Share_Pct'].sum().reset_index()

plt.figure(figsize=(10, 6))
plt.plot(duopoly_df['Snapshot_Month'], duopoly_df['Market_Share_Pct'], marker='o', color='red', linewidth=2)
plt.title('UPI Duopoly Volume Market Share (PhonePe + Google Pay)')
plt.ylabel('Combined Market Share (%)')
plt.xlabel('Date')
plt.grid(True)
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\apps\duopoly_market_share.png')
plt.close()

# 3. Herfindahl-Hirschman Index (HHI)
df['Market_Share_Squared'] = df['Market_Share_Pct'] ** 2
hhi_df = df.groupby('Snapshot_Month')['Market_Share_Squared'].sum().reset_index()
hhi_df.rename(columns={'Market_Share_Squared': 'HHI'}, inplace=True)

plt.figure(figsize=(10, 6))
plt.plot(hhi_df['Snapshot_Month'], hhi_df['HHI'], marker='o', color='purple', linewidth=2)
plt.axhline(y=2500, color='r', linestyle='--', label='High Concentration Threshold (2500)')
plt.title('Herfindahl-Hirschman Index (HHI) for UPI Apps')
plt.ylabel('HHI Score')
plt.xlabel('Date')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\apps\hhi_trend.png')
plt.close()

print("\n--- MONOPOLY ANALYSIS ---")
latest_month = hhi_df['Snapshot_Month'].max()
latest_hhi = hhi_df[hhi_df['Snapshot_Month'] == latest_month]['HHI'].values[0]
latest_duopoly = duopoly_df[duopoly_df['Snapshot_Month'] == latest_month]['Market_Share_Pct'].values[0]

print(f"As of {latest_month.strftime('%Y-%m')}:")
print(f"HHI Index: {latest_hhi:.1f} (US DOJ Threshold for High Concentration is 2500)")
print(f"Duopoly (PhonePe + GPay) Volume Market Share: {latest_duopoly:.1f}%")

df.to_csv(r'd:\Papers\Lipi\data\apps\cleaned_apps_data.csv', index=False)
print("\nPhase 3 complete! Outputs saved to modular folders.")
