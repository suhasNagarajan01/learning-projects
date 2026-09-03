import math
import re
from collections import Counter
import streamlit as st
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="In-Memory RAG & Knowledge Base Agent",
    page_icon="📚",
    layout="wide"
)

st.title("📚 In-Memory RAG & Knowledge Base Agent")
st.caption("Perform strict Retrieval-Augmented Generation on custom text/policy files to prevent AI hallucinations.")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key", type="password")
    selected_model = st.selectbox("Select Model", ["gemini-3.6-flash", "gemini-3.6-pro"])
    chunk_size = st.slider("Chunk Size (words)", min_value=50, max_value=300, value=100, step=25)
    top_k = st.slider("Top K Chunks to Retrieve", min_value=1, max_value=5, value=3)

if not api_key:
    st.info("Please enter your Gemini API key in the sidebar to proceed.", icon="🔑")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# ------------------------------------------------------------------------------
# 1. Chunking & In-Memory Retrieval Utilities
# ------------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    """Tokenizes string into lowercase alphanumeric words."""
    return re.findall(r'\w+', text.lower())

def chunk_text(text: str, chunk_word_size: int = 100, overlap: int = 20) -> list[dict]:
    """Splits plain text into overlapping chunks of word counts.

    Returns:
        List of dicts containing chunk_id, text, and word metadata.
    """
    words = text.split()
    chunks = []
    i = 0
    chunk_id = 1
    
    while i < len(words):
        chunk_words = words[i:i + chunk_word_size]
        chunk_str = " ".join(chunk_words)
        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_str,
            "word_count": len(chunk_words)
        })
        chunk_id += 1
        i += (chunk_word_size - overlap)
        if i >= len(words) - overlap:
            break
            
    return chunks

def compute_tf_idf_cosine_similarity(query: str, chunks: list[dict]) -> list[tuple[dict, float]]:
    """Calculates TF-IDF cosine similarity scores between a query and text chunks."""
    query_tokens = tokenize(query)
    if not query_tokens or not chunks:
        return []

    # Calculate Term Frequencies for chunks and query
    chunk_tfs = [Counter(tokenize(c["text"])) for c in chunks]
    query_tf = Counter(query_tokens)

    # Calculate Inverse Document Frequencies across all chunks
    num_docs = len(chunks)
    all_words = set(query_tokens)
    idfs = {}
    for word in all_words:
        doc_count = sum(1 for tf in chunk_tfs if word in tf)
        idfs[word] = math.log((num_docs + 1) / (doc_count + 1)) + 1

    # Vectorize Query
    query_vector = {word: count * idfs[word] for word, count in query_tf.items()}
    query_norm = math.sqrt(sum(v ** 2 for v in query_vector.values()))

    scores = []
    for idx, chunk in enumerate(chunks):
        tf = chunk_tfs[idx]
        chunk_vector = {word: count * idfs[word] for word, count in tf.items() if word in idfs}
        
        # Dot product
        dot_product = sum(query_vector[w] * chunk_vector.get(w, 0.0) for w in query_vector)
        
        chunk_norm = math.sqrt(sum(v ** 2 for v in chunk_vector.values()))
        
        similarity = 0.0
        if query_norm > 0 and chunk_norm > 0:
            similarity = dot_product / (query_norm * chunk_norm)
            
        scores.append((chunk, round(similarity, 4)))

    # Sort descending by score
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

# ------------------------------------------------------------------------------
# 2. UI & Knowledge Base Upload Section
# ------------------------------------------------------------------------------

default_policy_doc = """Acme Corp Refund & Cancellation Policy (Revised 2026)

1. General Refund Eligibility
Customers can request a full refund for digital products within 14 calendar days of purchase if total usage is under 2 hours. Physical products must be returned unopened in original packaging within 30 days to qualify for a refund.

2. Non-Refundable Items
Custom enterprise setups, annual subscription renewals beyond 78 hours from charge time, and discounted clearout items are non-refundable under any circumstance.

3. SLA and Uptime Credits
If service uptime drops below 99.5\% in any calendar month, Enterprise tier clients receive a 15% account credit toward their next billing cycle. Downtime due to scheduled maintenance communicated 48 hours in advance does not count toward SLA violations.

4. Customer Support Hours
Our primary tier support is available Monday to Friday from 8 AM to 6 PM EST. Priority enterprise tickets are answered 24/7 with a guaranteed initial response within 15 minutes."""

uploaded_file = st.file_uploader("Upload a TXT document to index:", type=["txt"])

if uploaded_file:
    raw_document = uploaded_file.getvalue().decode("utf-8")
else:
    raw_document = st.text_area("Or edit sample Knowledge Base policy text directly:", value=default_policy_doc, height=200)

if raw_document:
    # Chunk document in memory
    doc_chunks = chunk_text(raw_document, chunk_word_size=chunk_size)
    st.success(f"Knowledge Base indexed into {len(doc_chunks)} chunks.")

    with st.expander("🔍 View In-Memory Indexed Chunks"):
        for c in doc_chunks:
            st.markdown(f"**Chunk #{c['chunk_id']}** (`{c['word_count']}` words)")
            st.caption(c['text'])
            st.divider()

    # ------------------------------------------------------------------------------
    # 3. Query & Grounded Execution
    # ------------------------------------------------------------------------------

    st.subheader("Query Knowledge Base")
    user_query = st.text_input(
        "Ask a policy question:",
        value="What is the refund rule for digital products?"
    )

    if st.button("Run RAG Query", type="primary"):
        # Retrieve relevant chunks
        scored_chunks = compute_tf_idf_cosine_similarity(user_query, doc_chunks)
        top_chunks = scored_chunks[:top_k]

        st.write("### 📍 Step 1: Retrieved Chunks (Cosine Similarity)")
        retrieved_context_str = ""
        
        for item, score in top_chunks:
            st.markdown(f"- **Chunk #{item['chunk_id']}** (Similarity Score: `{score}`)")
            st.caption(f'"{item["text"]}"')
            retrieved_context_str += f"[Chunk #{item['chunk_id']}]:\n{item['text']}\n\n"

        # Construct Hallucination-Prevention System Prompt
        system_instruction = (
            "You are a strict grounded QA assistant. Answer questions using ONLY the provided text context chunks. "
            "If the answer cannot be explicitly derived from the provided context chunks, "
            "you MUST reply exact phrase: 'Not found in knowledge base.' "
            "Do NOT use external knowledge, speculate, or infer information not directly stated. "
            "Always cite the Chunk ID number [e.g., Chunk #1] when referencing facts in your answer."
        )

        user_prompt = (
            f"CONTEXT CHUNKS:\n{retrieved_context_str}\n"
            f"USER QUERY:\n{user_query}"
        )

        # Call Gemini Model
        with st.spinner("Generating grounded answer with Gemini..."):
            try:
                response = client.models.generate_content(
                    model=selected_model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.0  # Zero temperature for deterministic grounded extraction
                    )
                )

                st.write("### 🤖 Step 2: Grounded Answer")
                if "Not found in knowledge base" in response.text:
                    st.warning(response.text)
                else:
                    st.success(response.text)

            except Exception as e:
                st.error(f"Error querying model: {e}")