import os
import streamlit as st
import pandas as pd
import numpy as np
from google import genai
from omdb_utils import fetch_omdb_details

# --- Page Setup ---
st.set_page_config(page_title="Vector Geometry Movie Recommender", layout="wide")

st.title("🎬 Smart Recommender Agent (Vector Geometry)")
st.caption("Powered by pure NumPy Cosine Similarity & Gemini Reasoning")

# --- Local File & API Configuration ---
LOCAL_CSV_PATH = "movies.csv"

with st.sidebar:
    st.header("🔑 API Credentials & Data")
    omdb_api_key = st.text_input("OMDB API Key", type="password", help="Optional: Required for plot, cast, and year metadata")
    gemini_api_key = st.text_input("Gemini API Key", type="password", help="Required for AI recommendation reasoning")
    
    if os.path.exists(LOCAL_CSV_PATH):
        st.success(f"Loaded local dataset: `{LOCAL_CSV_PATH}`")
        dataset_source = LOCAL_CSV_PATH
    else:
        dataset_source = st.file_uploader("Upload Movies CSV (225 films)", type=["csv"])

# Columns that are NOT genre vectors
EXCLUDED_COLS = ['id', 'title', 'language']

def compute_cosine_similarity(df, genre_cols, weighted_filters):
    """
    Constructs user vector (u) and dataset matrix (V) directly from CSV binary genre columns.
    Computes Cosine Similarity: dot(u, v) / (norm(u) * norm(v))
    """
    u = np.zeros(len(genre_cols))
    genre_to_idx = {col: i for i, col in enumerate(genre_cols)}
    
    for genre, weight in weighted_filters.items():
        if genre in genre_to_idx:
            u[genre_to_idx[genre]] = weight
            
    norm_u = np.linalg.norm(u)
    if norm_u == 0:
        return np.zeros(len(df))
        
    V = df[genre_cols].apply(pd.to_numeric, errors='coerce').fillna(0).to_numpy()
    
    dot_products = np.dot(V, u)
    norm_V = np.linalg.norm(V, axis=1)
    
    similarity_scores = np.zeros(len(df))
    valid_indices = (norm_V > 0)
    similarity_scores[valid_indices] = dot_products[valid_indices] / (norm_V[valid_indices] * norm_u)
    
    return similarity_scores

# --- Main Execution ---
if dataset_source is not None:
    df = pd.read_csv(dataset_source)
    
    title_col = next((c for c in df.columns if c.lower() in ['title', 'film', 'name']), df.columns[1])
    genre_cols = [c for c in df.columns if c.lower() not in EXCLUDED_COLS]
    
    st.subheader("🎯 Configure Weighted Genre Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        main_filters = st.multiselect("Main Genres (Weight: 1.0)", options=genre_cols, help="Highest weight impact")
    with col2:
        sub_options = [g for g in genre_cols if g not in main_filters]
        sub_filters = st.multiselect("Sub Genres (Weight: 0.5)", options=sub_options, help="Medium weight impact")
    with col3:
        opt_options = [g for g in genre_cols if g not in main_filters and g not in sub_filters]
        optional_filters = st.multiselect("Optional Genres (Weight: 0.25)", options=opt_options, help="Minor tie-breaker impact")

    selected_weighted_filters = {}
    for g in main_filters: selected_weighted_filters[g] = 1.0
    for g in sub_filters: selected_weighted_filters[g] = 0.5
    for g in optional_filters: selected_weighted_filters[g] = 0.25

    if st.button("🚀 Calculate Vector Similarities & Recommend Top 15"):
        if not selected_weighted_filters:
            st.warning("Please select at least one genre filter across Main, Sub, or Optional sections.")
        else:
            with st.spinner("Computing NumPy vector cosine similarity..."):
                scores = compute_cosine_similarity(df, genre_cols, selected_weighted_filters)
                df['similarity_score'] = scores
                top_15_df = df.sort_values(by='similarity_score', ascending=False).head(15)
                
            st.subheader("🍿 Top 15 Recommended Movies")
            
            recommendations_data = []
            
            with st.spinner("Fetching metadata..."):
                for _, row in top_15_df.iterrows():
                    raw_title = str(row[title_col])
                    sim_pct = round(row['similarity_score'] * 100, 1)
                    
                    omdb_info = fetch_omdb_details(raw_title, omdb_api_key)
                    omdb_info['similarity_pct'] = sim_pct
                    recommendations_data.append(omdb_info)
                    
                    # Native Streamlit layout container
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 5])
                        with c1:
                            st.metric(label="Match", value=f"{sim_pct}%")
                        with c2:
                            st.subheader(omdb_info.get("Title", raw_title))
                            st.caption(f"**Year:** {omdb_info.get('Year', 'N/A')} | **Genre:** {omdb_info.get('Genre', 'N/A')}")
                            if omdb_info.get('Actors') and omdb_info.get('Actors') != 'N/A':
                                st.markdown(f"**Cast:** {omdb_info['Actors']}")
                            st.markdown(f"**Plot:** {omdb_info.get('Plot', 'N/A')}")

            # --- Gemini Reasoning Section ---
            st.markdown("---")
            st.subheader("🤖 Gemini AI Recommendation Reasoning")
            
            if gemini_api_key:
                with st.spinner("Generating AI analysis of vector match results..."):
                    movie_summary_list = [
                        f"- {m['Title']} ({m['Year']}): {m['similarity_pct']}% match | Genre: {m['Genre']}"
                        for m in recommendations_data[:5]
                    ]
                    
                    prompt = f"""
                    Act as an expert film critic and AI recommendation engineer.
                    
                    The user specified the following genre preference vector constraints:
                    - Main Genre Filters (Weight 1.0): {main_filters if main_filters else 'None'}
                    - Sub Genre Filters (Weight 0.5): {sub_filters if sub_filters else 'None'}
                    - Optional Genre Filters (Weight 0.25): {optional_filters if optional_filters else 'None'}
                    
                    The pure NumPy vector cosine similarity algorithm calculated these top movie matches:
                    {chr(10).join(movie_summary_list)}
                    
                    Provide a concise, 2-3 paragraph explanation detailing WHY these top recommendations logically and mathematically satisfy the user's preference vectors.
                    """
                    
                    try:
                        client = genai.Client(api_key=gemini_api_key)
                        response = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=prompt,
                        )
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Error generating Gemini reasoning: {e}")
            else:
                st.info("💡 Enter a Gemini API Key in the sidebar to generate AI explanation/reasoning for these recommendations.")

else:
    st.info("👈 Please ensure 'movies.csv' exists in the folder or upload your CSV dataset in the sidebar to begin.")