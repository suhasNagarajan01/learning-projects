import os
import streamlit as st
from google import genai
from google.genai import types
import config
from config import API_KEY
# Page configuration
st.set_page_config(
    page_title="Persona Translator - Project 3", page_icon="🎭", layout="centered"
)

# Initialize GenAI Client
# Safely fetch API key from environment variables or Streamlit secrets
api_key = API_KEY
if not api_key and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key) if api_key else None

st.title("🎭 Prompt Engineering & Persona Translator")
st.markdown(
    "Transform complex academic and financial concepts into specific vernaculars using dynamic **System Instructions**."
)

# Persona Mapping Dictionary
PERSONA_PROMPTS = {
    "ELI5 (Explain Like I'm 5)": (
        "You are a kind, patient preschool teacher. Explain complex topics using "
        "extremely simple analogies involving toys, candy, or playground games. "
        "Keep language elementary and warm."
    ),
    "Ranked Gamer": (
        "You are an intense esports player. Explain everything through competitive "
        "gaming metrics, mechanics, and slang (e.g., buffs, nerfs, meta builds, "
        "RNG, grinding, skill issue, tier lists)."
    ),
    "Gen Z Slang": (
        "You are a chronically online Gen Z teen. Break down concepts using "
        "heavy internet slang and current expressions (e.g., 'no cap', 'main character "
        "energy', 'it's giving...', 'era', 'cooked')."
    ),
    "Victorian Aristocrat": (
        "You are a dramatic 19th-century noble. Explain the prompt with immense "
        "formality, archaic vocabulary, and theatrical grandeur."
    ),
}

# UI Layout Inputs
topic = st.text_input(
    "Enter an academic topic:",
    placeholder="e.g., Inflation, Quantum Entanglement, Supply Chain",
)
selected_persona = st.selectbox(
    "Select Persona Vernacular:", list(PERSONA_PROMPTS.keys())
)

# Execution Trigger
if st.button("Translate Concept 🚀", type="primary"):
  if not topic.strip():
    st.warning("⚠️ Please provide a topic first!")
  elif not client:
    st.error(
        "❌ Gemini API key missing. Please set GEMINI_API_KEY in your environment"
        " or Streamlit secrets."
    )
  else:
    with st.spinner(f"Translating '{topic}' into {selected_persona}..."):
      try:
        # Retrieve persona instruction from dictionary
        system_instruction = PERSONA_PROMPTS[selected_persona]
        user_prompt = f"Explain the concept of: {topic}"

        # Generate response using modern Google GenAI SDK
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8,  # Higher temperature enhances persona creativity
            ),
        )

        st.subheader("✨ Translated Output")
        st.markdown(response.text)

      except Exception as e:
        st.error(f"An error occurred: {e}")