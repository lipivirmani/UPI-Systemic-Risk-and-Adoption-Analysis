import pandas as pd

# Load dataset
print("Loading Bank Performance Dataset...")
df = pd.read_csv(r'd:\Papers\Lipi\datasets\Raw Datasets\upi_bank_performance_master.csv')

# Clean Bank Names (strip whitespace, lowercase for matching)
df['Remitter Bank Clean'] = df['Remitter Bank'].str.strip().str.lower()

# Define Public vs Private lists based on major Indian banks
public_banks = [
    'state bank of india', 'punjab national bank', 'bank of baroda', 
    'bank of india', 'union bank of india', 'canara bank', 
    'central bank of india', 'indian bank', 'bank of maharashtra', 
    'uco bank', 'indian overseas bank', 'punjab and sind bank',
    'idbi bank limited' # Quasi-public
]

private_banks = [
    'hdfc bank', 'icici bank', 'axis bank', 'kotak mahindra bank', 
    'indusind bank', 'idfc first bank', 'yes bank', 'federal bank', 
    'bandhan bank', 'karnataka bank', 'karur vysya bank', 
    'south indian bank', 'city union bank', 'rbl', 'dcb bank',
    'standard chartered', 'citi bank', 'dbs bank'
]

# Function to categorize
def categorize_bank(bank_name):
    if bank_name in public_banks:
        return 'Public Sector'
    elif bank_name in private_banks:
        return 'Private Sector'
    else:
        return 'Other/Cooperative'

df['Bank_Type'] = df['Remitter Bank Clean'].apply(categorize_bank)

# The TD% and BD% are in raw decimal format (e.g., 0.0021 = 0.21%). 
# Let's convert them to actual Percentages (0 to 100) to make the ML models and graphs easier to read.
df['TD_Percent'] = df['TD%'] * 100
df['BD_Percent'] = df['BD%'] * 100
df['Approved_Percent'] = df['Approved%'] * 100

# Save cleaned data
output_path = r'd:\Papers\Lipi\data\banks\cleaned_bank_data.csv'
df.to_csv(output_path, index=False)
print(f"Cleaned dataset saved to {output_path}")

print("\nBank Categorization Breakdown:")
print(df['Bank_Type'].value_counts())
