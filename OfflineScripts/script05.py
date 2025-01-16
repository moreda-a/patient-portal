import json
import pandas as pd

# Load JSON data
file_path = "c:/Users/Mohammadreza_D/Desktop/RAG/Aetna_Test_Data_Fixed.json"
with open(file_path, 'r') as file:
    data = json.load(file)


# Define a function to extract the date/time for each entry
def extract_date(item):
    # Prioritize relevant date fields over lastUpdated
    return (
        item.get("recordedDate") or
        item.get("effectiveDateTime") or
        item.get("issued") or
        item.get("period", {}).get("start") or
        item.get("meta", {}).get("lastUpdated") or
        "No Date Available"
)

# Function to decode medical codes (example with dictionaries)
def decode_medical_code(system, code):
    if system == "http://snomed.info/sct":
        # Example SNOMED codes (you can expand this or integrate with an API)
        snomed_dict = {
            "10509002": "Acute bronchitis (disorder)",
            "386661006": "Fever"
        }
        return snomed_dict.get(code, "Unknown SNOMED code")
    elif system == "http://loinc.org":
        # Example LOINC codes
        loinc_dict = {
            "72109-2": "Alcohol Use Disorder Identification Test",
            "59041-4": "Cholesterol in Serum or Plasma"
        }
        return loinc_dict.get(code, "Unknown LOINC code")
    return "Unknown system"

# Extract relevant fields
patients = []
conditions = []
diagnostic_reports = []
observations = {}

# Process the data
for entry in data:
    resource_type = entry.get("resourceType", "Unknown")
    
    if resource_type == "Patient":
        patients.append({
            "id": entry.get("id"),
            "name": entry.get("name", [{}])[0].get("text", "Unknown"),
            "birthDate": entry.get("birthDate", "Unknown")
        })
    elif resource_type == "Condition":
        for coding in entry.get("code", {}).get("coding", []):
            conditions.append({
                "id": entry.get("id"),
                "code": coding.get("display"),#decode_medical_code(coding.get("system"), coding.get("code")),
                "date": extract_date(entry)
            })
    elif resource_type == "DiagnosticReport":
        for coding in entry.get("code", {}).get("coding", []):
            diagnostic_reports.append({
                "id": entry.get("id"),
                "code": decode_medical_code(coding.get("system"), coding.get("code")),
                "date": entry.get("effectiveDateTime", "Unknown"),
                "result": ", ".join([r.get("display", "Unknown") for r in entry.get("result", [])])
            })
    elif resource_type == "Observation":
        observations[entry.get("id")] = entry.get("valueString", "Unknown")

# Link observations to diagnostic reports
for report in diagnostic_reports:
    linked_results = []
    for res in report.get("result", []):
        # Handle both dictionary and string formats
        if isinstance(res, dict) and "reference" in res:
            observation_id = res["reference"].split("/")[-1]  # Extract the ID
        elif isinstance(res, str):
            observation_id = res.split("/")[-1]  # Assume it's already a string
        else:
            observation_id = "Unknown"
        
        # Look up the observation by ID
        linked_results.append(observations.get(observation_id, "Unknown"))
    
    report["detailedResults"] = ", ".join(linked_results)


# Convert data to DataFrames
patients_df = pd.DataFrame(patients)
conditions_df = pd.DataFrame(conditions)
diagnostic_reports_df = pd.DataFrame(diagnostic_reports)

# Save to CSV
patients_csv_path = "patients.csv"
conditions_csv_path = "updated_conditions.csv"
diagnostic_reports_csv_path = "updated_diagnostic_reports.csv"

patients_df.to_csv(patients_csv_path, index=False)
conditions_df.to_csv(conditions_csv_path, index=False)
diagnostic_reports_df.to_csv(diagnostic_reports_csv_path, index=False)

print(f"Patients data saved to {patients_csv_path}")
print(f"Conditions data saved to {conditions_csv_path}")
print(f"Diagnostic reports data saved to {diagnostic_reports_csv_path}")
