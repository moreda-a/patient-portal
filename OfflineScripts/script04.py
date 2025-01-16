import json
import pandas as pd

# Load JSON data
file_path = "c:/Users/Mohammadreza_D/Desktop/RAG/Aetna_Test_Data_Fixed.json"
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract relevant fields
patients = []
conditions = []
diagnostic_reports = []

for entry in data:
    resource_type = entry.get("resourceType", "Unknown")
    
    if resource_type == "Patient":
        patients.append({
            "id": entry.get("id"),
            "name": entry.get("name", [{}])[0].get("text", "Unknown"),
            "birthDate": entry.get("birthDate", "Unknown")
        })
    elif resource_type == "Condition":
        conditions.append({
            "id": entry.get("id"),
            "code": entry.get("code", {}).get("text", "Unknown"),
            "date": entry.get("recordedDate", "Unknown")
        })
    elif resource_type == "DiagnosticReport":
        diagnostic_reports.append({
            "id": entry.get("id"),
            "code": entry.get("code", {}).get("text", "Unknown"),
            "date": entry.get("effectiveDateTime", "Unknown"),
            "result": ", ".join([r.get("display", "Unknown") for r in entry.get("result", [])])
        })

# Save each extracted resource to a CSV
patients_df = pd.DataFrame(patients)
conditions_df = pd.DataFrame(conditions)
diagnostic_reports_df = pd.DataFrame(diagnostic_reports)

patients_csv_path = "patients.csv"
conditions_csv_path = "conditions.csv"
diagnostic_reports_csv_path = "diagnostic_reports.csv"

patients_df.to_csv(patients_csv_path, index=False)
conditions_df.to_csv(conditions_csv_path, index=False)
diagnostic_reports_df.to_csv(diagnostic_reports_csv_path, index=False)

print(f"Patients data saved to {patients_csv_path}")
print(f"Conditions data saved to {conditions_csv_path}")
print(f"Diagnostic reports data saved to {diagnostic_reports_csv_path}")
