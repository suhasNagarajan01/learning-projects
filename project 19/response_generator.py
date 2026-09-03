from google import genai
from config import GEMINI_API_KEY, DEFAULT_MODEL

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

COMPANY_POLICIES = """
Company Support Guidelines:
- Billing & Finance: Apologize for financial discrepancies. Unauthorized/duplicate charges are refunded within 3-5 business days.
- Technical Support: Acknowledge system errors (500/API bugs), inform customer that Tier-2 engineering is investigating, and offer workarounds if applicable.
- Security & Fraud: Urgent response. Confirm immediate account lock/reset, send identity verification steps, and reassure security protocol activation.
- General Inquiry: Provide clear, friendly answers about product features or existing options.
"""

def generate_response(email_content: str, triage_data: dict) -> str:
    """Drafts an empathetic, policy-grounded email response."""
    prompt = f"""
    You are an enterprise support representative. Draft a professional, empathetic, and actionable email reply.

    Policies & Guidelines:
    {COMPANY_POLICIES}

    Ticket Context:
    - Department: {triage_data.get('department')}
    - Urgency/Priority: {triage_data.get('priority')}
    - Customer Sentiment: {triage_data.get('sentiment')}

    Original Customer Inquiry:
    "{email_content}"

    Draft the email response now:
    """

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt
    )
    return response.text