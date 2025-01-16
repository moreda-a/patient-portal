# Patient Portal - Flask RAG Application

This repository contains a Flask-based application for processing patient medical history data and generating summaries using OpenAI's GPT-4 API. The app utilizes the Retrieval-Augmented Generation (RAG) model architecture to analyze and summarize patient records.

---

## 1. RAG Model Architecture

### Overview
The Retrieval-Augmented Generation (RAG) architecture combines retrieval-based techniques with generative models to produce relevant and contextually rich outputs. The process for this project is as follows:

1. **Data Preprocessing:**
   - Extracts and decodes patient data (e.g., Conditions, Diagnostic Reports, and Lab Results) from uploaded JSON files.

2. **Data Retrieval:**
   - Truncates and organizes patient information to ensure relevant data is passed to the GPT-4 model.

3. **Generation:**
   - Queries OpenAI GPT-4 in a structured manner using specific prompts for:
     - Profile generation
     - Insights extraction
     - Summary creation
     - Anomaly detection

4. **Presentation:**
   - Displays patient summaries on a user-friendly web interface.

---

## 2. Steps for Replication

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Flask
- Git
- Render or any cloud deployment platform (optional)

### Clone the Repository
```bash
# Clone the repository
$ git clone https://github.com/your-username/patient-portal.git

# Navigate to the project directory
$ cd patient-portal
```

### Set Up a Virtual Environment
```bash
# Create a virtual environment
$ python -m venv venv

# Activate the virtual environment
# Windows
$ venv\Scripts\activate

# macOS/Linux
$ source venv/bin/activate
```

### Install Dependencies
```bash
# Install required libraries
$ pip install -r requirements.txt
```

### Add Environment Variables
Create a `.env` file in the root directory and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key
```

---

## 3. Deployment Instructions

### Local Deployment

1. **Run the Flask App:**
   ```bash
   $ python app.py
   ```

2. **Access the Web App:**
   Open a browser and navigate to `http://127.0.0.1:5000`.

### Cloud Deployment (Render Example)

#### Step 1: Push Code to GitHub
Ensure your code is in a GitHub repository.

#### Step 2: Create a New Render Web Service
1. Log in to your [Render](https://render.com/) account.
2. Select **New +** > **Web Service**.
3. Connect your GitHub repository.
4. Set the following build and runtime settings:
   - **Environment:** Python 3.x
   - **Start Command:** `gunicorn app:app`
5. Add the required environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key

6. Click **Deploy**.

#### Step 3: Access Your Deployed App
After deployment, Render will provide a public URL where your application is accessible.

---

## 4. File Structure
```
patient-portal/
├── app.py                # Main Flask application
├── templates/            # HTML templates for the web interface
│   ├── upload.html       # File upload page
│   ├── results.html      # Results display page
├── static/               # Static assets (e.g., CSS, images)
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── .env                  # Environment variables (not pushed to GitHub)
```

---

## 5. Example Outputs

### Input File (JSON Example):
```json
{
    "resourceType": "Patient",
    "id": "1234",
    "name": [{ "text": "John Doe" }],
    "birthDate": "1985-07-28",
    "conditions": [
        { "code": { "coding": [{ "display": "Diabetes Mellitus" }] } },
        { "code": { "coding": [{ "display": "Hypertension" }] } }
    ]
}
```

### Generated Summary:
```
Name: John Doe
Birth Date: 1985-07-28

Profile:
- Age: 38
- Gender: Male

Insights:
- Conditions: Diabetes Mellitus, Hypertension
- Diagnostic Reports: Lipid Panel

Summary:
- The patient has a history of diabetes and hypertension. No recent anomalies were detected.

Anomalies:
- Elevated cholesterol levels detected in the lipid panel.
```

---

## 6. Contributing
If you have suggestions or improvements, feel free to submit a pull request or open an issue.

---

## 7. License
This project is licensed under the MIT License. See the `LICENSE` file for details.
