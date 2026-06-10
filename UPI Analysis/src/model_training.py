import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.api import VAR
import xgboost as xgb
import os
import sys

os.makedirs(r'd:\Papers\Lipi\models\without_festive', exist_ok=True)
os.makedirs(r'd:\Papers\Lipi\logs\without_festive', exist_ok=True)

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(r'd:\Papers\Lipi\logs\without_festive\training_log.txt', 'w')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass

sys.stdout = Logger()

# 1. Load Preprocessed Data
df = pd.read_csv(r'd:\Papers\Lipi\data\without_festive\preprocessed_upi_data.csv', parse_dates=['Date'], index_col='Date')
df = df.sort_index()

for lag in [1, 2, 3]:
    df[f'ATS_Divergence_Lag_{lag}'] = df['ATS_Divergence'].shift(lag)
df = df.dropna()

# 2. Train/Test Split (Walk-Forward Validation)
# Total rows = 48 (after dropping lag NaNs). Let's use first 38 for training, last 10 for testing.
train_size = len(df) - 10
train, test = df.iloc[:train_size].copy(), df.iloc[train_size:].copy()

print(f"Train size: {len(train)}, Test size: {len(test)}")

def evaluate_model(y_true, y_pred, model_name):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    print(f"[{model_name}] RMSE: {rmse:.2f} | MAE: {mae:.2f}")
    return rmse, mae

# -----------------------------------------------------------------------------
# MODEL 1: SARIMAX (Univariate Baseline for ATS Divergence)
# -----------------------------------------------------------------------------
print("\n--- Training SARIMAX Baseline ---")
sarima_model = SARIMAX(train['ATS_Divergence'], order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
sarima_fit = sarima_model.fit(disp=False)
sarima_preds = sarima_fit.forecast(steps=len(test))
sarima_rmse, sarima_mae = evaluate_model(test['ATS_Divergence'], sarima_preds, "SARIMAX (Baseline)")

# -----------------------------------------------------------------------------
# MODEL 2: VAR (Vector Autoregression for P2P vs P2M Divergence)
# -----------------------------------------------------------------------------
print("\n--- Training VAR (Joint P2P & P2M Model) ---")
# VAR requires stationary data, but we'll run it directly on ATS levels to capture the system dynamics 
# or diff it if needed. Given small sample, we fit directly to levels to forecast divergence.
var_data = train[['ATS_P2P', 'ATS_P2M']]
var_model = VAR(var_data)
# Fit with maxlags = 1
var_fit = var_model.fit(maxlags=1)

# Forecast
lag_order = var_fit.k_ar
forecast_input = var_data.values[-lag_order:]
var_forecast = var_fit.forecast(y=forecast_input, steps=len(test))

# Reconstruct Divergence: P2P forecast (col 0) - P2M forecast (col 1)
var_divergence_preds = var_forecast[:, 0] - var_forecast[:, 1]
var_rmse, var_mae = evaluate_model(test['ATS_Divergence'], var_divergence_preds, "VAR")

# -----------------------------------------------------------------------------
# MODEL 3: XGBoost (Tree-based model with Lags)
# -----------------------------------------------------------------------------
print("\n--- Training XGBoost ---")
features = ['ATS_Divergence_Lag_1', 'ATS_Divergence_Lag_2', 'ATS_Divergence_Lag_3',
            'ATS_P2P_Lag_1', 'ATS_P2M_Lag_1', 'Internet_Subscribers_Mn_Scaled',
            'Is_Diwali', 'Is_Holi', 'Is_Eid', 'Is_Christmas_NewYear', 'Is_Navratri_Dussehra']

X_train, y_train = train[features], train['ATS_Divergence']
X_test, y_test = test[features], test['ATS_Divergence']

xgb_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42)
xgb_model.fit(X_train, y_train)
xgb_preds = xgb_model.predict(X_test)
xgb_rmse, xgb_mae = evaluate_model(y_test, xgb_preds, "XGBoost")

# -----------------------------------------------------------------------------
# Plotting the Results
# -----------------------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(train.index, train['ATS_Divergence'], label='Train Actual', color='black')
plt.plot(test.index, test['ATS_Divergence'], label='Test Actual', color='blue', linewidth=2)
plt.plot(test.index, sarima_preds, label='SARIMAX Forecast', color='orange', linestyle='--')
plt.plot(test.index, var_divergence_preds, label='VAR Forecast', color='green', linestyle='--')
plt.plot(test.index, xgb_preds, label='XGBoost Forecast', color='red', linestyle='--')

plt.title('ATS Divergence: Forecast Models Comparison')
plt.ylabel('ATS Divergence (₹)')
plt.xlabel('Date')
plt.legend()
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\models\without_festive\forecast_comparison.png')
plt.close()

# Feature Importance for XGBoost
xgb.plot_importance(xgb_model, importance_type='weight', title='XGBoost Feature Importance')
plt.tight_layout()
plt.savefig(r'd:\Papers\Lipi\models\without_festive\xgboost_feature_importance.png')
plt.close()

print("\nModel Evaluation Completed! Plots saved in d:\\Papers\\Lipi\\models\without_festive")
