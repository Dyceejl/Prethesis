import pandas as pd
from datetime import timedelta
import numpy as np

# Load MIMIC-III tables
# Use uppercase column names as per MIMIC-III conventions
icustays = pd.read_csv(
    "C:/MIMIC-III/mimic-iii-clinical-database-1.4/data/ICUSTAYS.csv",
    parse_dates=["INTIME", "OUTTIME"]
)
patients = pd.read_csv(
    "C:/MIMIC-III/mimic-iii-clinical-database-1.4/data/PATIENTS.csv",
    parse_dates=["DOD"]
)
admissions = pd.read_csv(
    "C:/MIMIC-III/mimic-iii-clinical-database-1.4/data/ADMISSIONS.csv",
    parse_dates=["DISCHTIME"]
)

# Load your revised subset
subset = pd.read_csv("C:/MIMIC-Extract/data/ref_anti_with_ids.csv")
print(f"Original subset size: {len(subset)}")
print("Subset columns:", subset.columns.tolist())

# Merge tables
mimic_data = icustays.merge(
    patients[["SUBJECT_ID", "DOD"]],
    on="SUBJECT_ID",
    how="left"
).merge(
    admissions[["SUBJECT_ID", "HADM_ID", "DISCHTIME"]],
    on=["SUBJECT_ID", "HADM_ID"],
    how="left"
)

# Merge with subset
data = subset.merge(
    mimic_data[["SUBJECT_ID", "HADM_ID", "ICUSTAY_ID", "INTIME", "OUTTIME", "DOD", "DISCHTIME"]],
    left_on=["subject_id", "hadm_id", "icustay_id"],
    right_on=["SUBJECT_ID", "HADM_ID", "ICUSTAY_ID"],
    how="inner"
)
print(f"Size after merge: {len(data)}")

# Calculate survival time and status
def calculate_time_status(row):
    admit_time = row["INTIME"]
    death_time = row["DOD"]
    discharge_time = row["OUTTIME"]

    # Survival time (days)
    if pd.notnull(death_time):
        days_to_death = (death_time - admit_time).days
        if days_to_death <= 30:
            return days_to_death, 1  # Died within 30 days
        else:
            return 30, 0  # Survived past 30 days (censored)
    else:
        # No death recorded, use discharge time or 30 days
        days_to_discharge = (discharge_time - admit_time).days
        return min(days_to_discharge, 30), 0  # Censored

# Apply calculation
data[["time", "status"]] = data.apply(calculate_time_status, axis=1, result_type="expand")

# Validate surv_30d
data["surv_30d_check"] = (data["time"] == 30) & (data["status"] == 0)
if not (data["surv_30d"] == data["surv_30d_check"]).all():
    print("Warning: surv_30d does not align with time/status for some rows")
    print(data[data["surv_30d"] != data["surv_30d_check"]][["surv_30d", "time", "status"]])

# Reapply complete cases
vars_anti_updated = [
    "subject_id", "hadm_id", "icustay_id",
    "time", "status", "has_antibiotic", "surv_30d",
    "age", "sepsis_icd9", "White blood cell count_mean",
    "Temperature_mean", "Oxygen saturation_mean", "Creatinine_mean",
    "Respiratory rate_mean", "admission_type", "first_careunit"
]
data = data[vars_anti_updated].dropna()
print(f"Final sample size after dropna: {len(data)}")

# Check missingness
print("Missingness:\n", data.isnull().sum())

# Save output
save_path = "C:/MIMIC-Extract/data/antibiotics_time_to_event.csv"
data.to_csv(save_path, index=False)
print(f"Time-to-event data saved to: {save_path}")

# Verify saved dataset
loaded_data = pd.read_csv(save_path)
print(f"\nLoaded dataset shape: {loaded_data.shape}")
print("Loaded columns:", loaded_data.columns.tolist())
print("Missing values in loaded dataset:\n", loaded_data.isna().sum())