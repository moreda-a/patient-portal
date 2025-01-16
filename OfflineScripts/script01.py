import json
import pandas as pd

# Define the file path to the uploaded JSON file
file_path = r"c:\Users\Mohammadreza_D\Desktop\RAG\Aetna_Test_Data_Fixed.json"

# Open the file and process it
output = []
with open(file_path, 'r') as file:
    data = json.load(file)
    for entry in data:
        resource_type = entry.get("resourceType", "Unknown")
        output.append({"id": entry.get("id", "No ID"), "resourceType": resource_type})

# Create a DataFrame
df = pd.DataFrame(output)

# Save the DataFrame to a CSV file
df.to_csv("resource_types.csv", index=False)
print("Data saved to resource_types.csv")