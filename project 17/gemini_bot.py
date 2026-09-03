import os
from google import genai
from google.genai import types

# Initialize the Gemini client
# Ensure GEMINI_API_KEY is set in your environment variables or Streamlit secrets
client = genai.Client(api_key="AQ.Ab8RN6JfKqaUumj_mWi2FLSA4z_AaMhaJlVOR6t1a4XF4J5YQw")

DATABASE_SCHEMA = """
Table: students
Columns:
- roll_no INTEGER PRIMARY KEY
- name TEXT NOT NULL
- department TEXT NOT NULL (e.g., "Computer Science", "Data Science", "Electronics", "Mechanical")
- course TEXT NOT NULL
- marks REAL NOT NULL (0.0 to 100.0)
- grade TEXT NOT NULL ('A', 'B', 'C', 'D')
"""

def text_to_sql_bot(user_prompt: str):
    """
    Takes natural language text, applies database schema rules,
    and returns a tuple of (sql_query, explanation_rules).
    """
    system_instruction = f"""
    You are an expert SQLite text-to-SQL assistant for a University Academic Records system.
    
    ### Database Schema Rules:
    {DATABASE_SCHEMA}
    
    ### Instructions:
    1. Convert the user's natural language request into a valid SQLite query targeting the `students` table.
    2. Provide a clear, step-by-step explanation and set of rules explaining how and why the SQL query was constructed this way based on the schema.
    3. Output your response strictly in the following format:
    
    [SQL]
    -- Your SQL query here (just the raw query or single line statement)
    
    [EXPLANATION]
    -- Your rule-based explanation here
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.7-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1, # Low temperature for precise code generation
            ),
        )
        
        content = response.text
        
        # Parse output fields safely
        sql_query = "SELECT * FROM students;"
        explanation = "No explanation provided."
        
        if "[SQL]" in content and "[EXPLANATION]" in content:
            parts = content.split("[EXPLANATION]")
            sql_part = parts[0].replace("[SQL]", "").strip()
            explanation = parts[1].strip()
            
            # Clean up markdown code blocks if Gemini includes them
            sql_query = sql_part.replace("```sql", "").replace("```", "").strip()
        else:
            sql_query = content.strip()
            
        return sql_query, explanation
        
    except Exception as e:
        return "", f"Error generating response from Gemini: {e}"