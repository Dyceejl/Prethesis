import pandas as pd
import numpy as np

# Load the dataset
data = pd.read_csv("C:/MIMIC-Extract/data/antibiotics_time_to_event_fixed.csv")
print(f"Original dataset shape: {data.shape}")

# Identify negative time rows
negative_time = data[data["time"] < 0]
print(f"\nNumber of rows with negative time: {len(negative_time)}")
print("Sample of negative time rows:")
print(negative_time[["time", "status", "surv_30d"]].head(10))

# Remove rows with negative time
data_clean = data[data["time"] >= 0].copy()
print(f"\nCleaned dataset shape: {data_clean.shape}")

# Validate
print("\nTime distribution (cleaned):")
print(data_clean["time"].describe())
print("\nStatus distribution (cleaned):")
print(data_clean["status"].value_counts())
print("\nSurv_30d distribution (cleaned):")
print(data_clean["surv_30d"].value_counts())
print(f"Surv_30d prevalence: {data_clean['surv_30d'].mean():.2%}")

# Check for invalid values
print("\nInvalid time values (outside 0–30):")
print(data_clean[(data_clean["time"] < 0) | (data_clean["time"] > 30)][["time", "status"]])
print("\nInvalid status values (not 0 or 1):")
print(data_clean[~data_clean["status"].isin([0, 1])][["time", "status"]])

# Save cleaned dataset
save_path = "C:/MIMIC-Extract/data/antibiotics_time_to_event_cleaned.csv"
data_clean.to_csv(save_path, index=False)
print(f"\nCleaned dataset saved to: {save_path}")

# Verify saved dataset
loaded_data = pd.read_csv(save_path)
print(f"\nLoaded dataset shape: {loaded_data.shape}")
print("Loaded columns:", loaded_data.columns.tolist())
print("Missing values in loaded dataset:\n", loaded_data.isna().sum())