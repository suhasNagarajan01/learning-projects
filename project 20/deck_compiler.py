# deck_compiler.py
import json
import os
from groq import Groq
from config import DEFAULT_MODEL

def generate_slide_schema(research_text: str, topic: str, api_key: str = None) -> dict:
    """
    Takes raw research and generates a strict 5-slide JSON schema using Groq JSON mode.
    """
    key = api_key or os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=key)
    
    prompt = f"""
    You are an expert executive presentation designer. Convert the following research intelligence on "{topic}" into a strict JSON schema for a 5-slide executive presentation.
    
    Research Intelligence:
    {research_text}
    
    Return ONLY a valid JSON object matching this exact structure:
    {{
      "presentation_title": "Title of Presentation",
      "subtitle": "Subtitle or Subheading",
      "slides": [
        {{
          "slide_number": 1,
          "title": "Executive Summary",
          "bullet_points": ["Point 1", "Point 2", "Point 3"],
          "key_takeaway": "Main highlight of this slide"
        }},
        {{
          "slide_number": 2,
          "title": "Market Overview & Landscape",
          "bullet_points": ["Point 1", "Point 2", "Point 3"],
          "key_takeaway": "Main highlight of this slide"
        }},
        {{
          "slide_number": 3,
          "title": "Key Trends & Growth Drivers",
          "bullet_points": ["Point 1", "Point 2", "Point 3"],
          "key_takeaway": "Main highlight of this slide"
        }},
        {{
          "slide_number": 4,
          "title": "Challenges & Risk Analysis",
          "bullet_points": ["Point 1", "Point 2", "Point 3"],
          "key_takeaway": "Main highlight of this slide"
        }},
        {{
          "slide_number": 5,
          "title": "Strategic Recommendations",
          "bullet_points": ["Point 1", "Point 2", "Point 3"],
          "key_takeaway": "Main highlight of this slide"
        }}
      ]
    }}
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional deck generator. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )
    
    return json.loads(response.choices[0].message.content)

def compile_to_html(deck_data: dict, sources: list) -> str:
    """
    Compiles the 5-slide JSON schema into an interactive standalone HTML presentation file.
    """
    slides_html = ""
    for slide in deck_data.get("slides", []):
        bullets = "".join([f"<li>{bp}</li>" for bp in slide.get("bullet_points", [])])
        slides_html += f"""
        <div class="slide">
            <div class="slide-header">
                <span class="slide-num">Slide {slide.get('slide_number')} of 5</span>
                <h2>{slide.get('title')}</h2>
            </div>
            <div class="slide-body">
                <ul>{bullets}</ul>
                <div class="key-takeaway">
                    <strong>Key Takeaway:</strong> {slide.get('key_takeaway')}
                </div>
            </div>
        </div>
        """
        
    sources_html = "".join([f'<li><a href="{src}" target="_blank">{src}</a></li>' for src in sources])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{deck_data.get('presentation_title', 'Executive Presentation')}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #0e1117;
                color: #fafafa;
                margin: 0;
                padding: 40px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .deck-container {{ width: 100%; max-width: 900px; }}
            .cover {{
                text-align: center;
                padding: 60px 20px;
                background: linear-gradient(135deg, #1f2937, #111827);
                border-radius: 12px;
                border: 1px solid #374151;
                margin-bottom: 30px;
            }}
            .cover h1 {{ font-size: 2.5em; margin-bottom: 10px; color: #f3f4f6; }}
            .cover p {{ font-size: 1.2em; color: #9ca3af; }}
            .slide {{
                background: #1f2937;
                border-radius: 12px;
                border: 1px solid #374151;
                padding: 40px;
                margin-bottom: 30px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            }}
            .slide-header {{ border-bottom: 1px solid #374151; padding-bottom: 15px; margin-bottom: 25px; }}
            .slide-num {{ font-size: 0.85em; color: #3b82f6; text-transform: uppercase; font-weight: 700; }}
            .slide-header h2 {{ margin: 5px 0 0 0; font-size: 1.8em; color: #ffffff; }}
            .slide-body ul {{ line-height: 1.6; font-size: 1.1em; color: #d1d5db; margin-bottom: 25px; }}
            .slide-body li {{ margin-bottom: 10px; }}
            .key-takeaway {{
                background: rgba(59, 130, 246, 0.1);
                border-left: 4px solid #3b82f6;
                padding: 15px;
                border-radius: 0 8px 8px 0;
                color: #93c5fd;
                font-size: 1.05em;
            }}
            .sources-section {{
                background: #111827;
                padding: 25px;
                border-radius: 12px;
                border: 1px solid #374151;
                width: 100%;
                max-width: 900px;
            }}
            .sources-section h3 {{ margin-top: 0; color: #f3f4f6; }}
            .sources-section ul {{ padding-left: 20px; color: #9ca3af; word-break: break-all; }}
            .sources-section a {{ color: #60a5fa; text-decoration: none; }}
            .sources-section a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="deck-container">
            <div class="cover">
                <h1>{deck_data.get('presentation_title')}</h1>
                <p>{deck_data.get('subtitle')}</p>
            </div>
            {slides_html}
            <div class="sources-section">
                <h3>Research Citations & Live Sources</h3>
                <ul>{sources_html}</ul>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content