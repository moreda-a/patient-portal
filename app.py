import os
import json
import base64
import pandas as pd
from openai import OpenAI
from flask import Flask, request, render_template, jsonify

# Flask App Initialization
app = Flask(__name__)
key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=key)


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

def truncate_data(data, max_items):
    """Truncate the list of data to a specified maximum number of items."""
    return data[:max_items]

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
                "name": " ".join(entry.get("name", [{}])[0].get("given", []) + [entry.get("name", [{}])[0].get("family", "")]),
                "birthDate": entry.get("birthDate", "Unknown"),
                "gender": entry.get("gender"),
                "address": entry.get("address", [{}])[0].get("text"),
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
                "result_references": [r.get("reference", "Unknown") for r in entry.get("result", [])]
            })
        elif resource_type == "Observation":
            observations[entry.get("id")] = str(entry.get("valueQuantity", {}).get("value", "Unknown")  # Extract valueQuantity value
            or entry.get("valueString", "Unknown")  # Fallback to valueString
            )


    for report in diagnostic_reports:
        linked_results = []
        for ref in report.get("result_references", []):
            observation_id = ref.split("/")[-1] if isinstance(ref, str) else "Unknown"
            linked_results.append(observations.get(observation_id, "Unknown"))
        
        # Save linked observations
        report["detailedResults"] = ", ".join(linked_results)

    # Link conditions and reports to patients
    patient_data = []
    for patient in patients:
        patient_id = patient["id"]
        patient_conditions = [
            {"code": c["code"], "date": c["date"]}
            for c in conditions
        ]
        patient_reports = [
            {"code": r["code"], "date": r["date"], "notes": r["decoded_notes"], "lab results": r["result"], "detailedResults":r["detailedResults"]}
            for r in diagnostic_reports
        ]
        patient_data.append({
            "name": patient["name"],
            "birthDate": patient["birthDate"],
            "gender":patient["gender"],
            "address": patient["address"],
            "conditions": patient_conditions,
            "diagnosticReports": patient_reports
        })
    
    return patient_data

def generate_summary(patient):
    def safe_api_call(prompt, system_content, max_tokens):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in API call: {str(e)}")
            return "No data available."

    # Profile
    profile_prompt = f"Talk layperson and easy to understand. Generate the profile information for this patient very short just name birthday and gender or age or address(Don't say that you are AI, that you don't know, or that reports are incomplete. Only state what you know.): Name: {patient['name']} Birth Date: {patient['birthDate']} gender: {patient['gender']},address: {patient['address']} "
    profile_text = safe_api_call(profile_prompt, "You are a medical assistant providing profile details.", 150)

    # Insights
    truncated_conditions = truncate_data(patient["conditions"], 40)
    truncated_reports = truncate_data(patient["diagnosticReports"], 40)
    insights_prompt = f"Talk layperson and easy to understand. Summarize the insights for this patient(Don't say that you are AI, that you don't know, or that reports are incomplete. Only state what you know): Conditions: {', '.join([c['code'] for c in truncated_conditions])} Diagnostic Reports: {', '.join([r['code'] for r in truncated_reports])}"
    insights_text = safe_api_call(insights_prompt, "You are a medical assistant summarizing health insights.", 500)

    # Summary
    summary_prompt = f"Talk layperson and easy to understand. Provide a high-level summary for this patient(Don't say that you are AI, that you don't know, or that reports are incomplete. Only state what you know): Conditions: {', '.join([c['code'] for c in truncated_conditions])} Diagnostic Notes: {', '.join([r['notes'] for r in truncated_reports])}"
    summary_text = safe_api_call(summary_prompt, "You are a medical assistant generating a summary.", 500)

    # Anomalies
    anomalies_prompt = f"Talk layperson and easy to understand. Identify any anomalies or concerning findings (small number) (Don't say that you are AI, that you don't know, or that reports are incomplete. Only state what you know): Lab Tests: {', '.join([r['lab results'] for r in truncated_reports])} Lab Results: {', '.join([r['detailedResults'] for r in truncated_reports])}"
    anomalies_text = safe_api_call(anomalies_prompt, "You are a medical assistant identifying anomalies(if any).", 200)

    return {
        "Profile": profile_text,
        "Insights": insights_text,
        "Summary": summary_text,
        "Anomalies": anomalies_text,
    }

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
            results.append({"name": patient["name"], **summary})
        return render_template("results.html", results=results)
    except Exception as e:
        return f"Error processing file: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)