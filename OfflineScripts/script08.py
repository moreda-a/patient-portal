import json
import base64
import pandas as pd
import openai
from transformers import pipeline

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


# Function to decode Base64 presentedForm data
def decode_presented_form(presented_form):
    decoded_texts = []
    for form in presented_form:
        if "data" in form:
            base64_data = form["data"]
            try:
                decoded_text = base64.b64decode(base64_data).decode("utf-8")
                decoded_texts.append(decoded_text)
            except Exception as e:
                decoded_texts.append(f"Error decoding data: {str(e)}")
        else:
            decoded_texts.append("No data available")
    return " | ".join(decoded_texts)


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
            presented_form = entry.get("presentedForm", [])
            decoded_notes = decode_presented_form(presented_form)
            
            diagnostic_reports.append({
                "id": entry.get("id"),
                #"status": entry.get("status", "Unknown"),
                "date": entry.get("effectiveDateTime", "No date available"),
                "code": coding.get("display"),#entry.get("code", {}).get("text", "Unknown"),
                "performer": ", ".join([perf.get("display", "Unknown") for perf in entry.get("performer", [])]),
                "decoded_notes": decoded_notes,
                "result": ", ".join([r.get("display", "Unknown") for r in entry.get("result", [])]),
                "result_references": [r.get("reference", "Unknown") for r in entry.get("result", [])]

            })
    elif resource_type == "Observation":
        observations[entry.get("id")] = str(entry.get("valueQuantity", {}).get("value", "Unknown")  # Extract valueQuantity value
        or entry.get("valueString", "Unknown")  # Fallback to valueString
        )

# Link observations to diagnostic reports
for report in diagnostic_reports:
    linked_results = []
    for ref in report.get("result_references", []):
        observation_id = ref.split("/")[-1] if isinstance(ref, str) else "Unknown"
        linked_results.append(observations.get(observation_id, "Unknown"))
    
    # Save linked observations
    report["detailedResults"] = ", ".join(linked_results)


# Convert data to DataFrames
patients_df = pd.DataFrame(patients)
conditions_df = pd.DataFrame(conditions)
diagnostic_reports_df = pd.DataFrame(diagnostic_reports)

# Save to CSV
patients_csv_path = "c:/Users/Mohammadreza_D/Desktop/RAG/patients.csv"
conditions_csv_path = "c:/Users/Mohammadreza_D/Desktop/RAG/updated_conditions.csv"
diagnostic_reports_csv_path = "c:/Users/Mohammadreza_D/Desktop/RAG/updated_diagnostic_reports.csv"

patients_df.to_csv(patients_csv_path, index=False)
conditions_df.to_csv(conditions_csv_path, index=False)
diagnostic_reports_df.to_csv(diagnostic_reports_csv_path, index=False)

print(f"Patients data saved to {patients_csv_path}")
print(f"Conditions data saved to {conditions_csv_path}")
print(f"Diagnostic reports data saved to {diagnostic_reports_csv_path}")


patient_data = []

for patient in patients:
    patient_id = patient["id"]
    
    # Find related conditions and diagnostic reports
    patient_conditions = [c for c in conditions]#if c.get("id") == patient_id]
    patient_reports = [r for r in diagnostic_reports]# if r.get("id") == patient_id]
    
    patient_data.append({
        "name": patient["name"],
        "birthDate": patient["birthDate"],
        "conditions": patient_conditions,
        "diagnosticReports": patient_reports
    })

#print(patient_data)

'''
# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Generate a summary for each patient
for patient in patient_data:
    prompt = f"""
    Summarize the health information for the following patient:
    Name: {patient['name']}
    Birth Date: {patient['birthDate']}
    Conditions: {', '.join([c['code'] for c in patient['conditions']])}
    Diagnostic Reports: {', '.join([r['code'] for r in patient['diagnosticReports']])}
    """
    
    # Use ChatCompletion API with GPT model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model you want to use
        messages=[
            {"role": "system", "content": "You are a medical assistant generating health summaries."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    
    # Extract the response content
    print(f"Summary for {patient['name']}:\n", response['choices'][0]['message']['content'].strip())
'''
# Initialize a summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Generate a summary for each patient
for patient in patient_data:
    # Construct the input text with a clear structure
    input_text = f"""
    Patient Summary:
    Name: {patient['name']}
    Birth Date: {patient['birthDate']}
    
    Conditions:
    {', '.join([c['code'] for c in patient['conditions']])}
    
    Diagnostic Reports:
    {', '.join([r['code'] for r in patient['diagnosticReports']])}
    """
    
    # Generate a summary using the local model
    summary = summarizer(input_text, max_length=100, min_length=50, do_sample=False)
    
    # Extract the summarized text
    summarized_text = summary[0]['summary_text']
    
    # Post-process to ensure the summary ends with a complete sentence
    if not summarized_text.endswith('.'):
        summarized_text += '.'
    
    # Print the final summary
    print(f"Summary for {patient['name']}:\n", summarized_text)