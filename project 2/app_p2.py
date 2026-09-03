import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Gemini Q&A Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Question-Answering Assistant")
st.write("Transform your static page into a live AI assistant powered by **Gemini 3.6 Flash**.")

# --- 1. SIDEBAR: API KEY MANAGEMENT ---
st.sidebar.header("Authentication")
api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    placeholder="Paste your key here...",
    help="Your API key is processed securely in this session and never saved."
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Tip:** You can obtain a free development API key from [Google AI Studio](https://aistudio.google.com/)."
)

# --- 2. MAIN INTERFACE: MULTI-LINE QUESTION BOX ---
st.markdown("### Ask a Question")
question = st.text_area(
    "Enter your prompt below:",
    value="Why is the sky blue?",
    height=120,
    placeholder="Ask anything..."
)

# --- 3. SUBMISSION & STREAMING RESPONSE ---
if st.button("Generate Answer", type="primary"):
    if not api_key:
        st.warning("⚠️ Please provide your Gemini API key in the sidebar to proceed.")
    elif not question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        # 4. ERROR HANDLING & CLIENT INITIALIZATION
        try:
            # Initialize the Google GenAI client with the user-provided key
            client = genai.Client(api_key=api_key)
            
            st.markdown("### Answer:")
            
            # Create a generator function to yield streaming text chunks
            def response_generator():
                response = client.models.generate_content_stream(
                    model="gemini-3.6-flash",
                    contents=question
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            # Stream the text incrementally to the UI using Streamlit's native streaming utility
            st.write_stream(response_generator())
            
        except Exception as e:
            st.error(f"❌ An error occurred during generation: {e}")