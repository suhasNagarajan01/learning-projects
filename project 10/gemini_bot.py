import json
import os
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """
You are an expert tutor. Given a topic, your job is to:
1. Provide a concise, clear 2-paragraph concept overview.
2. Generate a 3-question multiple-choice quiz based on the overview.

You MUST respond strictly in valid JSON format matching this schema:
{
    "overview": "Paragraph 1...\\n\\nParagraph 2...",
    "quiz": [
        {
            "id": 1,
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Why Option A is correct."
        }
    ]
}
"""


class StudyBuddyBot:

    def __init__(
        self, api_key: str = None, model_name: str = "gemini-3.6-flash"
    ):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

        self.config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
            response_mime_type="application/json",
        )

    def generate_study_material(self, topic: str) -> dict:
        if not topic or not topic.strip():
            return {"error": "Please provide a valid topic."}

        prompt = f"Create a study guide and 3-question quiz for the topic: {topic}"

        try:
            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt, config=self.config
            )

            # Parse strict JSON response
            parsed_data = json.loads(response.text)
            return parsed_data

        except json.JSONDecodeError:
            return {
                "error": "Failed to parse structured JSON from Gemini response."
            }
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}