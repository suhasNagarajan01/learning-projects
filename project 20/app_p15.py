# app_p15.py
import streamlit as st
import json
from researcher import gather_market_intelligence
from deck_compiler import generate_slide_schema, compile_to_html

st.set_page_config(
    page_title="Autonomous Research & Executive Slide Deck Generator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Autonomous Research & Executive Slide Deck Generator")
st.markdown("Powered by **Groq API** (`llama-3.3-70b-versatile`) & Live Web Grounding")

with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Enter Groq API Key", type="password", value="")
    st.markdown("---")
    st.markdown("### Instructions")
    st.markdown("1. Enter your Groq API Key.\n2. Type any industry or research topic.\n3. Run the autonomous agent.\n4. Preview slides and download presentation.")

topic_input = st.text_input("🎯 Enter Industry, Technology, or Market Topic:", placeholder="e.g., Autonomous EV Fleets Market Outlook 2026")

if st.button("🚀 Run Autonomous Agent & Generate Deck", type="primary"):
    if not groq_api_key:
        st.error("Please enter a valid Groq API Key in the sidebar.")
    elif not topic_input:
        st.error("Please enter a research topic.")
    else:
        with st.status("🤖 Autonomous Agent Executing...", expanded=True) as status:
            st.write("🌍 Step 1: Querying live web sources...")
            try:
                research_text, sources = gather_market_intelligence(topic_input, api_key=groq_api_key)
                st.write(f"✅ Found {len(sources)} web sources and synthesized market intelligence.")
                
                st.write("📊 Step 2: Structuring 5-slide executive JSON schema...")
                deck_schema = generate_slide_schema(research_text, topic_input, api_key=groq_api_key)
                st.write("✅ JSON schema successfully compiled.")
                
                st.write("🎨 Step 3: Compiling interactive presentation...")
                html_deck = compile_to_html(deck_schema, sources)
                st.write("✅ Standalone HTML deck generated!")
                
                status.update(label="✨ Autonomous Generation Complete!", state="complete", expanded=False)
                
                # Cache to session state
                st.session_state['deck_schema'] = deck_schema
                st.session_state['html_deck'] = html_deck
                st.session_state['sources'] = sources
                st.session_state['research_text'] = research_text
            except Exception as e:
                status.update(label="❌ Generation Failed", state="error", expanded=True)
                st.error(f"An error occurred: {e}")

# Display results if available in session state
if 'deck_schema' in st.session_state:
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Executive Presentation Preview")
        deck = st.session_state['deck_schema']
        
        st.markdown(f"### 🏷️ Title: {deck.get('presentation_title')}")
        st.markdown(f"*{deck.get('subtitle')}*")
        
        for slide in deck.get('slides', []):
            with st.expander(f"Slide {slide.get('slide_number')}: {slide.get('title')}", expanded=(slide.get('slide_number')==1)):
                for bp in slide.get('bullet_points', []):
                    st.markdown(f"- {bp}")
                st.info(f"**Key Takeaway:** {slide.get('key_takeaway')}")
                
    with col2:
        st.subheader("📥 Download Presentation")
        st.markdown("Download your standalone interactive HTML deck ready to present or share.")
        
        st.download_button(
            label="💾 Download HTML Deck",
            data=st.session_state['html_deck'],
            file_name=f"{topic_input.replace(' ', '_').lower()}_executive_deck.html",
            mime="text/html",
            type="primary"
        )
        
        with st.expander("🔍 View Raw Research Intelligence"):
            st.write(st.session_state['research_text'])
            
        with st.expander("🔗 Live Sources"):
            for src in st.session_state['sources']:
                st.markdown(f"- [{src}]({src})")