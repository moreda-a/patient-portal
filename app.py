import os
import json
import base64
import pandas as pd
import openai
from flask import Flask, request, render_template, jsonify

# Flask App Initialization
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")

# Function Definitions (from your script)
def extract_date(item):
    """Extract the date/time for a given resource."""
    return (
        item.get("recordedDate") or
        item.get("effectiveDateTime") or
        item.get("issued") or
        item.get("period", {}).get("start") or
        item.get("meta", {}).get("lastUpdated") or
        "No Date Available"
    )

def decode_presented_form(presented_form):
    """Decode Base64 presented form data."""
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

def process_json(file):
    """Process the uploaded JSON file and extract patient data."""
    data = json.load(file)
    patients = []
    conditions = []
    diagnostic_reports = []
    observations = {}

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
                    "code": coding.get("display"),
                    "date": extract_date(entry)
                })
        elif resource_type == "DiagnosticReport":
            presented_form = entry.get("presentedForm", [])
            decoded_notes = decode_presented_form(presented_form)

            diagnostic_reports.append({
                "id": entry.get("id"),
                "date": entry.get("effectiveDateTime", "No date available"),
                "code": ", ".join(
                    [coding.get("display", "Unknown") for coding in entry.get("code", {}).get("coding", [])]
                ),
                "decoded_notes": decoded_notes,
                "result": ", ".join([r.get("display", "Unknown") for r in entry.get("result", [])]),
            })

    # Link conditions and reports to patients
    patient_data = []
    for patient in patients:
        patient_id = patient["id"]
        patient_conditions = [
            {"code": c["code"], "date": c["date"]}
            for c in conditions
        ]
        patient_reports = [
            {"code": r["code"], "date": r["date"], "notes": r["decoded_notes"], "lab results": r["result"]}
            for r in diagnostic_reports
        ]
        patient_data.append({
            "name": patient["name"],
            "birthDate": patient["birthDate"],
            "conditions": patient_conditions,
            "diagnosticReports": patient_reports
        })
    
    return patient_data

def generate_summary(patient):
    """Generate a summary using OpenAI API."""
    prompt = f"""
    Summarize the health information for the following patient:
    Name: {patient['name']}
    Birth Date: {patient['birthDate']}
    Conditions: {', '.join([c['code'] for c in patient['conditions']])}
    Diagnostic Reports: {', '.join([r['code'] for r in patient['diagnosticReports']])}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a medical assistant generating health summaries."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5,
    )
    return response["choices"][0]["message"]["content"].strip()

# Flask Routes
@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400
    
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    try:
        patient_data = process_json(file)
        results = []
        for patient in patient_data:
            summary = generate_summary(patient)
            results.append({"name": patient["name"], "summary": summary})
        
        return render_template("results.html", results=results)
    except Exception as e:
        return f"Error processing file: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)