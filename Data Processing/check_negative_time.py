import pandas as pd
import numpy as np

# Load the dataset with time and status
data = pd.read_csv("C:/MIMIC-Extract/data/antibiotics_time_to_event.csv")

# Load MIMIC-III tables to get timestamps
icustays = pd.read_csv("C:/MIMIC-III/mimic-iii-clinical-database-1.4/data/ICUSTAYS.csv", parse_dates=["INTIME", "OUTTIME"])
patients = pd.read_csv("C:/MIMIC-III/mimic-iii-clinical-database-1.4/data/PATIENTS.csv", parse_dates=["DOD"])
admissions = pd.read_csv("C:/MIMIC-III/mimic-iii-clinical-database-1.4/data/ADMISSIONS.csv", parse_dates=["DISCHTIME"])

# Merge to get timestamps
mimic_data = icustays.merge(
    patients[["SUBJECT_ID", "DOD"]],
    on="SUBJECT_ID",
    how="left"
).merge(
    admissions[["SUBJECT_ID", "HADM_ID", "DISCHTIME"]],
    on=["SUBJECT_ID", "HADM_ID"],
    how="left"
)

# Merge with dataset
data_with_timestamps = data.merge(
    mimic_data[["SUBJECT_ID", "HADM_ID", "ICUSTAY_ID", "INTIME", "OUTTIME", "DOD", "DISCHTIME"]],
    left_on=["subject_id", "hadm_id", "icustay_id"],
    right_on=["SUBJECT_ID", "HADM_ID", "ICUSTAY_ID"],
    how="inner"
)

# Inspect rows with negative time
negative_time = data_with_timestamps[data_with_timestamps["time"] < 0]
print(f"Number of rows with negative time: {len(negative_time)}")
print("\nSample of negative time rows:")
print(negative_time[["time", "status", "INTIME", "OUTTIME", "DOD", "DISCHTIME"]].head(10))

# Calculate days to death for verification
negative_time["days_to_death"] = (negative_time["DOD"] - negative_time["INTIME"]).dt.total_seconds() / (24 * 60 * 60)
print("\nDays to death for negative time rows:")
print(negative_time[["time", "days_to_death", "INTIME", "DOD"]].head(10))