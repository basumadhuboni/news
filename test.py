import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load the API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ API key not found in .env file.")
    exit()

# Configure the API
genai.configure(api_key=api_key)

try:
    # Use a lightweight flash model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    response = model.generate_content("Say 'Hello from Gemini Flash!'")
    print("✅ API is working! Response:")
    print(response.text)

except Exception as e:
    print("❌ Error occurred. Check your API key, model name, or quota limits.")
    print(f"Details: {e}")
