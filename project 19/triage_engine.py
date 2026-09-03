import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, DEFAULT_MODEL

# Initialize the Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def classify_ticket(email_content: str) -> dict:
    """Analyzes customer email and returns structured JSON classification."""
    prompt = f"""
    Analyze the following incoming customer support email and output a JSON object strictly matching this schema:

    {{
      "department": "Billing & Finance" | "Technical Support" | "Security & Fraud" | "General Inquiry",
      "priority": "Critical" | "High" | "Medium" | "Low",
      "sentiment": "Angry" | "Frustrated" | "Neutral" | "Pleased",
      "sla_response_hours": 2 | 6 | 24 | 48,
      "reasoning": "Short justification of assigned department and urgency."
    }}

    Customer Email:
    "{email_content}"
    """

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    return json.loads(response.text)