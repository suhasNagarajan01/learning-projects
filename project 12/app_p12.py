import streamlit as st
from google import genai
from google.genai import types

# Page setup
st.set_page_config(
    page_title="Multimodal Document & Code Inspector",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Multimodal Document & Code Inspector")
st.caption("Inspect Python scripts, PDFs, and text files directly in memory using Gemini.")

# Sidebar API key configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key", type="password")
    selected_model = st.selectbox(
        "Select Model",
        ["gemini-2.5-flash", "gemini-3.6-flash"]
    )

if not api_key:
    st.info("Please enter your Gemini API key in the sidebar to proceed.", icon="🔑")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# File Uploader
uploaded_file = st.file_uploader(
    "Upload a Python script (.py), PDF document (.pdf), or Text file (.txt)",
    type=["py", "pdf", "txt"]
)

if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "text/plain"

    # Display file details
    st.success(f"Loaded `{uploaded_file.name}` ({len(file_bytes)} bytes)")

    # Code/Text preview
    if mime_type in ["text/x-python", "text/plain"] or uploaded_file.name.endswith(".py"):
        with st.expander("📄 View File Content", expanded=False):
            st.code(file_bytes.decode("utf-8"), language="python" if uploaded_file.name.endswith(".py") else None)

    st.divider()

    # Pre-built audit prompts
    action = st.radio(
        "Choose Inspection Mode:",
        ["🐛 Audit Bugs & Security Issues", "🏗️ Summarize Architecture & Structure", "💬 Custom Query"]
    )

    user_prompt = ""
    if action == "🐛 Audit Bugs & Security Issues":
        user_prompt = (
            "Perform a rigorous line-by-line audit of the attached file. "
            "Identify all bugs, logic errors, syntax mistakes, or potential security risks. "
            "For every issue found, specify:\n"
            "1. Exact line number(s)\n"
            "2. Description of the error\n"
            "3. Corrected code snippet and explanation of the fix."
        )
    elif action == "🏗️ Summarize Architecture & Structure":
        user_prompt = (
            "Analyze the attached file and provide a high-level architectural overview. "
            "Detail key classes, core functions, data flow, external dependencies, "
            "and primary responsibilities."
        )
    else:
        user_prompt = st.text_area("Enter your prompt for the file:", "Explain what this file does step-by-step.")

    if st.button("Run Inspection", type="primary"):
        with st.spinner("Analyzing document with Gemini..."):
            try:
                # Build multimodal Part directly from memory byte buffer
                document_part = types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type
                )

                # Send both in-memory byte buffer part and text prompt to Gemini
                response = client.models.generate_content(
                    model=selected_model,
                    contents=[document_part, user_prompt]
                )

                st.subheader("Inspection Results")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Error inspecting file: {e}")