import openai

# Step 1: Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Step 2: Define a simple prompt
prompt = "Write a short story about a brave knight who saves a village from a dragon."

# Step 3: Call the ChatGPT API
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Specify the model (e.g., gpt-3.5-turbo or gpt-4)
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=200,  # Limit the response length
    temperature=0.7  # Adjust creativity (0.0 = precise, 1.0 = creative)
)

# Step 4: Extract and print the response
print("ChatGPT response:")
print(response["choices"][0]["message"]["content"])