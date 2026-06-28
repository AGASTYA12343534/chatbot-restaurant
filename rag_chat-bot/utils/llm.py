import os
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()
# Configure Gemini with your API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)

def generate_content(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Content generation failed: {e}")