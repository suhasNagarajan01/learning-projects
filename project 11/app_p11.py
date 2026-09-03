import os
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Project 11: Chatbot with Memory",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Conversational Chatbot with Memory")

# 2. Sidebar - Configuration & Clear Memory Button
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Enter your API key or set it in your environment variables."
    )
    
    st.markdown("---")
    
    # Sidebar Clear Memory Button
    if st.button("🗑️ Clear Chat Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 3. Initialize Persistent Chat Memory in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Past Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle Chat Input and Gemini API Interaction
if prompt := st.chat_input("Type your message here..."):
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar to proceed.")
        st.stop()

    # Display user's message immediately in UI
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to persistent session state memory
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare historical context for the API call
    # Formats messages to match the expected Content schema
    formatted_contents = [
        types.Content(
            role=msg["role"],
            parts=[types.Part.from_text(text=msg["content"])]
        )
        for msg in st.session_state.messages
    ]

    # Initialize client and generate response with full conversation context
    try:
        client = genai.Client(api_key=api_key)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=formatted_contents
                )
                
                assistant_reply = response.text
                st.markdown(assistant_reply)

        # Store assistant response into persistent session state memory
        st.session_state.messages.append({"role": "model", "content": assistant_reply})

    except Exception as e:
        st.error(f"An error occurred while generating a response: {e}")