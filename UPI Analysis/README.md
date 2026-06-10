# UPI Systemic Risk Analysis — Research Paper

> **Beneath the Trillion-Transaction Milestone: A Machine Learning Investigation of Systemic Risk in India's UPI Ecosystem**

A five-phase empirical study applying machine learning to publicly available NPCI data to investigate structural risks hidden beneath UPI's aggregate transaction growth.

---

## 📊 Interactive Dashboard

A Power BI dashboard visualizing all key findings is available here:  🔗 [View Dashboard](https://1drv.ms/b/c/ede69e97616e578e/IQCjq0XNx7CbQLJjLll3d866ARDMjM0egM2kNFADGHcBVvw)


---

## 🗂️ Project Structure

```
UPI Analysis/
├── data/                        # Processed datasets (by domain)
│   ├── apps/                    # TPAP market share data
│   ├── banks/                   # Bank technical decline data
│   ├── merchant/                # Merchant category data
│   ├── statewise/               # State-level UPI data
│   ├── with_festive/            # ATS data with festival markers
│   └── without_festive/         # ATS data (base)
│
├── src/                         # All Python analysis scripts
│   ├── model_training.py        # Phase 1: XGBoost ATS forecasting (V1)
│   ├── model_training_v2.py     # Phase 1: XGBoost + festival ablation (V2)
│   ├── merchant_clustering.py   # Phase 2: K-Means merchant clustering
│   ├── apps_analysis.py         # Phase 3: HHI + TPAP market concentration
│   ├── bank_stress_model.py     # Phase 4: Linear vs Random Forest stress test
│   ├── statewise_clustering.py  # Phase 5: State maturity K-Means clustering
│   ├── eda_preprocessing.py     # EDA preprocessing (ATS divergence)
│   ├── bank_preprocessing.py    # EDA preprocessing (banks)
│   ├── merchant_preprocessing.py# EDA preprocessing (merchants)
│   └── statewise_preprocessing.py # EDA preprocessing (states)
│
├── eda/                         # Generated EDA figures
│   ├── apps/                    # App market charts (HHI, share, ATS)
│   ├── banks/                   # Bank TD% charts
│   ├── merchant/                # Elbow plot
│   └── statewise/               # Geographic charts
│
├── models/                      # Generated model output figures
│   ├── with_festive/            # V1 vs V2 comparison + feature importance
│   ├── banks/                   # Random Forest feature importance
│   ├── merchant/                # Cluster scatter plot
│   └── statewise/               # State cluster scatter plot
│
├── paper/
│   └── research_paper.html      # Full paper (HTML, print-ready)
│
└── UPI Dashboard.pdf            # Exported Power BI dashboard (PDF)
```

---
## 🎯 Key Findings

- UPI exhibits structural divergence between P2P and P2M transaction behavior.
- Merchant transactions have evolved into a micro-payment dominated ecosystem.
- The TPAP market exhibits high concentration (HHI = 3,383.7), indicating duopoly characteristics.
- Banking stress patterns demonstrate non-linear tipping-point behavior.
- Geographic clustering reveals uneven digital payment maturity across states.

--- 
## 🔬 Five Analytical Phases

| Phase | Method | Hypothesis | Verdict |
|-------|--------|------------|---------|
| 1. ATS Divergence Forecasting | SARIMAX vs XGBoost + Ablation | H1: Non-linear, structural | ✅ Confirmed |
| 2. Merchant Clustering | K-Means (K=3) | H2: Micro-Utility dominance | ✅ Confirmed |
| 3. App Market Concentration | Herfindahl-Hirschman Index | H3: Formal duopoly (HHI > 2500) | ✅ Confirmed (HHI = 3,383.7) |
| 4. Bank Stress Testing | Linear Regression vs Random Forest | H4: Non-linear tipping-point failure | ✅ Confirmed (R² = –0.007) |
| 5. Geographic Maturity Mapping | K-Means (K=3) on states/UTs | — | Rural nationalization of stress |

---

## 📦 Data Source

All data sourced from official NPCI public statistics:  
🔗 [https://www.npci.org.in/product/bhim/product-statistics](https://www.npci.org.in/product/bhim/product-statistics)

**Coverage:** April 2022 – March 2026

---

## ⚙️ Requirements

```bash
pip install pandas numpy scikit-learn xgboost statsmodels matplotlib seaborn
```

---

## 👥 Author

Lipi Virmani

---

## 📜 License

This repository is for academic research purposes. Please cite appropriately if using any part of this work.
