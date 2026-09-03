# app_p10.py
import streamlit as st
import os
from google import genai
from google.genai import types

# Initialize Gemini Client (ensure GEMINI_API_KEY is in your environment or st.secrets)
client = genai.Client(api_key="API_KEY")


st.title("Visual AI Vision Inspector & OCR Agent")
st.write("Upload an image or take a picture to extract structured data and insights.")

# Task 2: Input selection
input_method = st.radio("Choose Input Method:", ["File Upload", "Camera Input"])

uploaded_file = None
if input_method == "File Upload":
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
else:
    uploaded_file = st.camera_input("Take a picture")

# Task 4: Extraction modes
extraction_mode = st.selectbox(
    "Select Extraction Mode:",
    [
        "Extract Bill Items as Table",
        "Explain Architecture Diagram",
        "Handwriting OCR"
    ]
)

# Single button call handles both success and empty input states
if st.button("Process Image"):
    if uploaded_file is not None:
        # Task 3: Extract raw bytes & construct image part
        raw_bytes = uploaded_file.getvalue()
        mime_type = uploaded_file.type
        
        image_part = types.Part.from_bytes(data=raw_bytes, mime_type=mime_type)
        
        # Select prompt based on mode
        if extraction_mode == "Extract Bill Items as Table":
            prompt = """
            Analyze this receipt or bill. Extract all line items and return a clean, 
            itemized markdown table. The table must include columns for Item Name, 
            Price, and Tax breakdown. Do not include any extra text outside the table.
            """
        elif extraction_mode == "Explain Architecture Diagram":
            prompt = """
            Analyze this architecture diagram. Explain its primary components, 
            how they interact, the overall data flow, and the system's likely purpose.
            """
        else:
            prompt = """
            Perform OCR on this image. Extract all handwritten text exactly as it 
            is written, preserving the original formatting and line breaks as much as possible.
            """

        with st.spinner("Processing image with Gemini..."):
            try:
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[image_part, prompt]
                )
                
                st.subheader("Results")
                # Task 5: Render output
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an image or take a picture first.")