import pandas as pd
import numpy as np

print("Loading Merchant_Combined.xlsx...")
df = pd.read_excel(r'd:\Papers\Lipi\datasets\Raw Datasets\Merchant_Combined.xlsx')

# Clean numeric columns (they might contain commas or non-numeric strings)
print("Cleaning data...")
df['volume_mn'] = df['volume_mn'].astype(str).replace({',': ''}, regex=True)
df['volume_mn'] = pd.to_numeric(df['volume_mn'], errors='coerce')

df['value_cr'] = df['value_cr'].astype(str).replace({',': ''}, regex=True)
df['value_cr'] = pd.to_numeric(df['value_cr'], errors='coerce')

# Drop rows with missing values in critical columns
df = df.dropna(subset=['category', 'volume_mn', 'value_cr'])

# Aggregate by Category to get total volume, value, and true ATS
print("Aggregating by category...")
grouped = df.groupby('category').agg({
    'volume_mn': 'sum',
    'value_cr': 'sum'
}).reset_index()

# Calculate ATS
grouped['ATS'] = (grouped['value_cr'] / grouped['volume_mn']) * 10

# Filter out anomalies (e.g., categories with practically zero volume across 4 years)
# Let's say a minimum of 1 Million total volume to be considered a real category
grouped = grouped[grouped['volume_mn'] >= 1.0]

# Drop any potential NaN or Infinity ATS
grouped = grouped.replace([np.inf, -np.inf], np.nan).dropna(subset=['ATS'])

# Save to cleaned CSV
output_path = r'd:\Papers\Lipi\data\merchant\cleaned_merchant_data.csv'
grouped.to_csv(output_path, index=False)
print(f"Cleaned data saved to {output_path}")
print(f"Total valid categories found: {len(grouped)}")
