import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
import os
import sys

os.makedirs(r'd:\Papers\Lipi\models\with_festive', exist_ok=True)
os.makedirs(r'd:\Papers\Lipi\logs\with_festive', exist_ok=True)

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\with_festive\training_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass

sys.stdout = Logger()

# 1. Load Preprocessed Data
df = pd.read_csv(r'd:\Papers\Lipi\data\with_festive\preprocessed_upi_data_v2.csv', parse_dates=['Date'], index_col='Date')
df = df.sort_index()

# 2. Train/Test Split
train_size = len(df) - 10
train, test = df.iloc[:train_size].copy(), df.iloc[train_size:].copy()

def evaluate_model(y_true, y_pred, model_name):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    print(f"[{model_name}] RMSE: {rmse:.2f} | MAE: {mae:.2f}")
    return rmse, mae

# -----------------------------------------------------------------------------
# Base Model (No Festivals)
# -----------------------------------------------------------------------------
print("\n--- Training Base XGBoost Model ---")
base_features = ['ATS_Divergence_Lag_1', 'ATS_Divergence_Lag_2', 'ATS_Divergence_Lag_3',
                 'ATS_P2P_Lag_1', 'ATS_P2M_Lag_1', 'Internet_Subscribers_Mn_Scaled']

X_train_base, y_train = train[base_features], train['ATS_Divergence']
X_test_base, y_test = test[base_features], test['ATS_Divergence']

base_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42)
base_model.fit(X_train_base, y_train)
base_preds = base_model.predict(X_test_base)
base_rmse, base_mae = evaluate_model(y_test, base_preds, "XGBoost Base")

# -----------------------------------------------------------------------------
# Model V2 (With Festivals)
# -----------------------------------------------------------------------------
print("\n--- Training Model V2 (With Festivals) ---")
v2_features = base_features + ['Is_Diwali', 'Is_Holi', 'Is_Eid', 'Is_Christmas_NewYear', 'Is_Navratri_Dussehra']

X_train_v2 = train[v2_features]
X_test_v2 = test[v2_features]

v2_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42)
v2_model.fit(X_train_v2, y_train)
v2_preds = v2_model.predict(X_test_v2)
v2_rmse, v2_mae = evaluate_model(y_test, v2_preds, "XGBoost V2 (Festivals)")

# -----------------------------------------------------------------------------
# Plotting Comparison
# -----------------------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(test.index, test['ATS_Divergence'], label='Actual Divergence', color='blue', linewidth=2)
plt.plot(test.index, base_preds, label='Base Model Forecast', color='orange', linestyle='--')
plt.plot(test.index, v2_preds, label='V2 (Festivals) Forecast', color='red', linestyle=':')

plt.title('ATS Divergence: Base Model vs V2 (Festivals)')
plt.ylabel('ATS Divergence (₹)')
plt.xlabel('Date')
plt.legend()
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\models\with_festive\v2_comparison.png')
plt.close()

# Feature Importance for V2
xgb.plot_importance(v2_model, importance_type='weight', title='V2 Feature Importance (Including Festivals)')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\models\with_festive\v2_feature_importance.png')
plt.close()

print("\nModel V2 Evaluation Completed! Plots saved in d:\\Papers\\Lipi\\models\with_festive")
