# researcher.py
import os
from groq import Groq
from duckduckgo_search import DDGS
from config import DEFAULT_MODEL

def perform_web_search(query: str, max_results: int = 5):
    """Queries live web sources using DuckDuckGo search."""
    snippets = []
    sources = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            for r in results:
                snippets.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}")
                sources.append(r.get('href'))
    except Exception as e:
        snippets.append(f"Search warning: Could not fetch live web results ({e}). Relying on model intelligence.")
        sources.append("Internal Knowledge Base")
    return "\n\n".join(snippets), sources

def gather_market_intelligence(topic: str, api_key: str = None):
    """
    Autonomous research agent that fetches live web snippets and synthesizes
    factual market intelligence using Groq.
    """
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError("Groq API Key is missing. Please provide it in the sidebar or environment variables.")
    
    client = Groq(api_key=key)
    
    # 1. Fetch live web content
    search_query = f"{topic} market trends analysis statistics 2025 2026"
    raw_snippets, sources = perform_web_search(search_query)
    
    # 2. Synthesize using Groq
    prompt = f"""
    You are an expert market research analyst. Based on the following live web search snippets and your extensive knowledge, synthesize comprehensive factual intelligence regarding: "{topic}".
    
    Web Search Findings:
    {raw_snippets}
    
    Provide a detailed analytical synthesis including key metrics, market drivers, challenges, and future outlook. Ensure factual accuracy.
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are an elite research assistant specializing in market intelligence."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    return response.choices[0].message.content, sources