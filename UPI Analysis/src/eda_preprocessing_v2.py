import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import os

# Create directory for V2 EDA plots
os.makedirs(r'd:\Papers\Lipi\eda\with_festive', exist_ok=True)

# 1. Load the dataset
df = pd.read_csv(r'd:\Papers\Lipi\datasets\master_upi_dataset.csv')

# 2. Preprocessing
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
df.sort_values('Date', inplace=True)
df.set_index('Date', inplace=True)

# Filter for Jan 2022 onwards
df_filtered = df[df.index >= '2022-01-01'].copy()

cols_to_numeric = ['P2P_Value_Cr', 'P2P_Volume_Mn', 'P2M_Value_Cr', 'P2M_Volume_Mn', 'Total_Value_Cr', 'Total_Volume_Mn', 'Internet_Subscribers_Mn']
for col in cols_to_numeric:
    df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')

df_filtered.ffill(inplace=True)

# Compute ATS variables
df_filtered['ATS_Overall'] = (df_filtered['Total_Value_Cr'] / df_filtered['Total_Volume_Mn']) * 10
df_filtered['ATS_P2P'] = (df_filtered['P2P_Value_Cr'] / df_filtered['P2P_Volume_Mn']) * 10
df_filtered['ATS_P2M'] = (df_filtered['P2M_Value_Cr'] / df_filtered['P2M_Volume_Mn']) * 10
df_filtered['ATS_Divergence'] = df_filtered['ATS_P2P'] - df_filtered['ATS_P2M']

# 3. Create Lag Features
for col in ['ATS_P2P', 'ATS_P2M', 'ATS_Overall', 'ATS_Divergence']:
    for lag in [1, 2, 3]:
        df_filtered[f'{col}_Lag_{lag}'] = df_filtered[col].shift(lag)

df_model = df_filtered.dropna().copy()

# 4. Scaling
scaler = MinMaxScaler()
df_model['Internet_Subscribers_Mn_Scaled'] = scaler.fit_transform(df_model[['Internet_Subscribers_Mn']])

# 5. EDA for V2 (Focusing on Festivals)
festival_cols = ['Is_Diwali', 'Is_Holi', 'Is_Eid', 'Is_Christmas_NewYear', 'Is_Navratri_Dussehra']
corr_cols = ['ATS_Divergence', 'P2M_Volume_Share_Pct'] + festival_cols
corr_matrix = df_model[corr_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title('Correlation: ATS Divergence vs Festivals')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\eda\with_festive\festival_correlation_matrix.png')
plt.close()

# Save the preprocessed dataset for ML models
df_model.to_csv(r'd:\Papers\Lipi\data\with_festive\preprocessed_upi_data_v2.csv')
print("V2 Preprocessing and EDA completed. Plots saved to d:\\Papers\\Lipi\\eda\with_festive")
print("Preprocessed data saved to d:\\Papers\\Lipi\\datasets\\preprocessed_upi_data_v2.csv")
