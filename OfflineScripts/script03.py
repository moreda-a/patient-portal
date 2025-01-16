import json

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
            "result": entry.get("result", [])
        })

print("Patients:", patients)
print("Conditions:", conditions)
print("Diagnostic Reports:", diagnostic_reports)
