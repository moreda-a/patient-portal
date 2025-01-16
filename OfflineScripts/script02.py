import json
import pandas as pd

# Define the file path to the JSON file
file_path = r"c:\Users\Mohammadreza_D\Desktop\RAG\Aetna_Test_Data_Fixed.json"

# Load the JSON data
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

# Process the data and create a list of dictionaries with the relevant fields
output = []
for entry in data:
    resource_type = entry.get("resourceType", "Unknown")
    date = extract_date(entry)
    output.append({"id": entry.get("id", "No ID"), "resourceType": resource_type, "date": date})

# Convert the processed data to a DataFrame
df = pd.DataFrame(output)

# Save the DataFrame to a CSV file
output_csv_path = r"c:\Users\Mohammadreza_D\Desktop\RAG\resource_types_with_dates.csv"
df.to_csv(output_csv_path, index=False)
print(f"Data with dates saved to {output_csv_path}")
