import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import os

# Create directory for EDA plots
os.makedirs(r'd:\Papers\Lipi\eda\without_festive', exist_ok=True)

# 1. Load the dataset
df = pd.read_csv(r'd:\Papers\Lipi\datasets\master_upi_dataset.csv')

# 2. Preprocessing
# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
df.sort_values('Date', inplace=True)
df.set_index('Date', inplace=True)

# Filter for Jan 2022 onwards (where P2P/P2M split is available)
df_filtered = df[df.index >= '2022-01-01'].copy()

# Handle potential missing values or empty strings in ATS columns by re-calculating them
# P2P_Value_Cr, P2P_Volume_Mn, P2M_Value_Cr, P2M_Volume_Mn
# Ensure they are numeric
cols_to_numeric = ['P2P_Value_Cr', 'P2P_Volume_Mn', 'P2M_Value_Cr', 'P2M_Volume_Mn', 'Total_Value_Cr', 'Total_Volume_Mn', 'Internet_Subscribers_Mn']
for col in cols_to_numeric:
    df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')

# Drop any rows with NaN in critical columns (e.g., if Jan/Feb 2026 lack internet subscribers, we can ffill)
df_filtered.ffill(inplace=True)

# Compute ATS variables (in Rupees: Value is in Crores, Volume in Millions -> (Value * 10^7) / (Volume * 10^6) = Value/Volume * 10)
# Actually, Value in Cr = 10,000,000 Rs. Volume in Mn = 1,000,000. So ATS = (Value * 10,000,000) / (Volume * 1,000,000) = (Value / Volume) * 10
df_filtered['ATS_Overall'] = (df_filtered['Total_Value_Cr'] / df_filtered['Total_Volume_Mn']) * 10
df_filtered['ATS_P2P'] = (df_filtered['P2P_Value_Cr'] / df_filtered['P2P_Volume_Mn']) * 10
df_filtered['ATS_P2M'] = (df_filtered['P2M_Value_Cr'] / df_filtered['P2M_Volume_Mn']) * 10
df_filtered['ATS_Divergence'] = df_filtered['ATS_P2P'] - df_filtered['ATS_P2M']

print(f"Data shape after filtering (Jan 2022+): {df_filtered.shape}")
print(f"Missing values:\n{df_filtered.isnull().sum().max()}") # Should be 0 after ffill

# 3. Create Lag Features
# We want lags for our ATS metrics to use in XGBoost
for col in ['ATS_P2P', 'ATS_P2M', 'ATS_Overall']:
    for lag in [1, 2, 3]:
        df_filtered[f'{col}_Lag_{lag}'] = df_filtered[col].shift(lag)

# Drop rows with NaN caused by lagging (drops first 3 rows)
df_model = df_filtered.dropna().copy()
print(f"Data shape after dropping lag NAs: {df_model.shape}")

# 4. Scaling
# Scale non-target numerical features (e.g., Internet Subscribers)
scaler = MinMaxScaler()
df_model['Internet_Subscribers_Mn_Scaled'] = scaler.fit_transform(df_model[['Internet_Subscribers_Mn']])

# 5. EDA and Plotting
sns.set_theme(style="whitegrid")

# Plot 1: The ATS Trend (The Core Research Question)
plt.figure(figsize=(12, 6))
plt.plot(df_model.index, df_model['ATS_P2P'], label='P2P ATS', color='blue', linewidth=2)
plt.plot(df_model.index, df_model['ATS_P2M'], label='P2M ATS', color='green', linewidth=2)
plt.plot(df_model.index, df_model['ATS_Overall'], label='Overall ATS', color='black', linestyle='--')
plt.title('UPI Average Ticket Size (ATS) Trend (2022-2026)')
plt.ylabel('Ticket Size (₹)')
plt.xlabel('Date')
plt.legend()
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\without_festive\ats_trend.png')
plt.close()

# Plot 2: ATS Divergence Gap
plt.figure(figsize=(10, 5))
plt.fill_between(df_model.index, 0, df_model['ATS_Divergence'], color='purple', alpha=0.3)
plt.plot(df_model.index, df_model['ATS_Divergence'], color='purple', linewidth=2)
plt.title('ATS Divergence (Gap between P2P and P2M Ticket Size)')
plt.ylabel('Divergence in ₹')
plt.xlabel('Date')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\without_festive\ats_divergence.png')
plt.close()

# Plot 3: Correlation Heatmap
# Select columns of interest for correlation
corr_cols = ['ATS_Overall', 'ATS_P2P', 'ATS_P2M', 'ATS_Divergence', 
             'Internet_Subscribers_Mn', 'Total_Volume_Mn', 'P2M_Volume_Share_Pct']
corr_matrix = df_model[corr_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title('Correlation Matrix of Core Variables')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\without_festive\correlation_matrix.png')
plt.close()

# Save the preprocessed dataset for ML models
df_model.to_csv(r'd:\Papers\Lipi\data\without_festive\preprocessed_upi_data.csv')
print("Preprocessing and EDA completed. Plots saved to d:\Papers\Lipi\eda\without_festive")
print("Preprocessed data saved to d:\Papers\Lipi\data\without_festive\preprocessed_upi_data.csv")

# Print top correlations with ATS_Divergence
print("\nTop Correlations with ATS_Divergence:")
print(corr_matrix['ATS_Divergence'].sort_values(ascending=False))
