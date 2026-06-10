import pandas as pd
import numpy as np
import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\statewise\preprocessing_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass
sys.stdout = Logger()

print("Loading Statewise dataset...")
df = pd.read_excel(r'd:\Papers\Lipi\datasets\Raw Datasets\Statewise_Combined.xlsx')

print("Cleaning data...")
# Clean State names
df['state'] = df['state'].astype(str).str.strip().str.upper()

# Fix potential duplicates or misspellings
df['state'] = df['state'].replace({
    'UTTARPRADESH': 'UTTAR PRADESH',
    'JAMMU & KASHMIR': 'JAMMU AND KASHMIR',
    'ANDAMAN & NICOBAR': 'ANDAMAN AND NICOBAR',
    'NAN': np.nan,
    'NONE': np.nan
})
df = df.dropna(subset=['state'])

# Clean numeric values
df['volume_mn'] = df['volume_mn'].astype(str).replace({',': ''}, regex=True)
df['volume_mn'] = pd.to_numeric(df['volume_mn'], errors='coerce')

df['value_cr'] = df['value_cr'].astype(str).replace({',': ''}, regex=True)
df['value_cr'] = pd.to_numeric(df['value_cr'], errors='coerce')

df = df.dropna(subset=['volume_mn', 'value_cr'])

# Group by State to find overall historical totals
grouped = df.groupby('state').agg({
    'volume_mn': 'sum',
    'value_cr': 'sum'
}).reset_index()

# Calculate True ATS
grouped['ATS'] = (grouped['value_cr'] / grouped['volume_mn']) * 10
grouped = grouped.dropna(subset=['ATS'])

# Filter out edge cases (e.g., Union territories with < 1 million total historical volume)
grouped = grouped[grouped['volume_mn'] > 1.0]
grouped = grouped.sort_values('volume_mn', ascending=False)

output_path = r'd:\Papers\Lipi\data\statewise\cleaned_statewise_data.csv'
grouped.to_csv(output_path, index=False)
print(f"Cleaned dataset saved to {output_path}")

print(f"\nTotal valid states identified: {len(grouped)}")
print("\nTop 5 States by Volume:")
print(grouped.head(5)[['state', 'volume_mn']])
