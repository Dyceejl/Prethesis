import pandas as pd
import numpy as np

# Load the time-to-event dataset
data = pd.read_csv("/data/antibiotics_time_to_event.csv")
print(f"Dataset shape: {data.shape}")
print("Columns:", data.columns.tolist())

# Check original surv_30d distribution
print("\nOriginal surv_30d distribution:")
print(data["surv_30d"].value_counts())
print(f"Original surv_30d prevalence: {data['surv_30d'].mean():.2%}")

# Fix surv_30d
data["surv_30d"] = ((data["time"] == 30) & (data["status"] == 0)).astype(int)
print("\nUpdated surv_30d distribution:")
print(data["surv_30d"].value_counts())
print(f"Updated surv_30d prevalence: {data['surv_30d'].mean():.2%}")

# Validate time and status
print("\nTime distribution:")
print(data["time"].describe())
print("\nStatus distribution:")
print(data["status"].value_counts())

# Check for invalid values
print("\nInvalid time values (outside 0–30):")
print(data[(data["time"] < 0) | (data["time"] > 30)][["time", "status"]])
print("\nInvalid status values (not 0 or 1):")
print(data[~data["status"].isin([0, 1])][["time", "status"]])

# Inspect mismatches (using original data for comparison)
data["surv_30d_check"] = ((data["time"] == 30) & (data["status"] == 0)).astype(int)
mismatches = data[data["surv_30d"] != data["surv_30d_check"]]
print(f"\nNumber of mismatched rows: {len(mismatches)}")
print("\nSample of mismatched rows:")
print(mismatches[["surv_30d", "time", "status"]].head(10))

# Save updated dataset
save_path = "/data/antibiotics_time_to_event_fixed.csv"
data.drop(columns=["surv_30d_check"]).to_csv(save_path, index=False)
print(f"\nUpdated dataset saved to: {save_path}")

# Verify saved dataset
loaded_data = pd.read_csv(save_path)
print(f"\nLoaded dataset shape: {loaded_data.shape}")
print("Loaded columns:", loaded_data.columns.tolist())
print("Missing values in loaded dataset:\n", loaded_data.isna().sum())