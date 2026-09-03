import os
import sys
import traceback
from typing import Dict, Any, Tuple
from google import genai

# Initialize the Gemini Client (automatically pulls GEMINI_API_KEY from environment)
client = genai.Client(api_key="AQ.Ab8RN6Ie3wT6gopaj6z9DCs2BpnoBdWEg22Su_zxbarC7L8zAQ")

# ---------------------------------------------------------------------------
# 1. SANDBOX EXECUTION ENGINE
# ---------------------------------------------------------------------------

def run_in_sandbox(code_str: str, test_str: str) -> Tuple[bool, str]:
    """
    Executes generated code alongside hidden test assertions in a restricted
    namespace, capturing stdout and tracebacks.
    """
    sandbox_globals: Dict[str, Any] = {
        "__builtins__": __builtins__,
    }
    sandbox_locals: Dict[str, Any] = {}

    try:
        # Combine generated code with test assertions
        full_script = f"{code_str}\n\n# --- HIDDEN TESTS ---\n{test_str}"
        
        # Execute in sandbox environment
        exec(full_script, sandbox_globals, sandbox_locals)
        return True, "All tests passed successfully."

    except Exception:
        # Trap full traceback including AssertionErrors and IndexErrors
        error_msg = traceback.format_exc()
        return False, error_msg
# ---------------------------------------------------------------------------
# 2. AUTONOMOUS REPAIR LOOP
# ---------------------------------------------------------------------------

def autonomous_tdd_agent(prompt_spec: str, hidden_tests: str, max_attempts: int = 3) -> str:
    """
    Recursive TDD repair loop that writes, tests, and heals code based on
    sandboxed tracebacks.
    """
    attempt = 1
    code = ""
    error_log = ""

    print("==================================================")
    print("🚀 Starting Autonomous TDD Agent")
    print("==================================================")

    while attempt <= max_attempts:
        print(f"\n--- [Turn {attempt}/{max_attempts}] Generating / Repairing Code ---")

        if attempt == 1:
            prompt = f"""
You are an expert Python developer working in a TDD pipeline.
Task: Write a Python function based on this specification:
"{prompt_spec}"

Requirements:
- Output ONLY valid, executable Python code enclosed in ```python ``` blocks.
- Do NOT include test code or explanations.
- Ensure edge cases (such as empty lists or out-of-range indices) are handled gracefully.
"""
        else:
            prompt = f"""
Your previous implementation FAILED hidden tests.

--- BROKEN CODE ---
```python
{code}
```
--- EXECUTION TRACEBACK ---
{error_log}

Task:
Fix the error identified in the traceback above. Ensure edge cases like empty inputs, boundary indices, or negative values are properly handled.
Output ONLY valid, executable Python code in ```python ``` blocks.
"""

        # Call API using google-genai Client format
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        raw_text = response.text

        # Extract clean code block from Markdown formatting
        if "```python" in raw_text:
            code = raw_text.split("```python")[1].split("```")[0].strip()
        elif "```" in raw_text:
            code = raw_text.split("```")[1].split("```")[0].strip()
        else:
            code = raw_text.strip()

        print(f"Generated Code (Attempt {attempt}):\n{code}")

        # Run generated code against hidden assertions in sandbox
        passed, output = run_in_sandbox(code, hidden_tests)

        if passed:
            print(f"\n✅ [Turn {attempt}] SUCCESS: Code passed all assertions!")
            return code
        else:
            print(f"\n❌ [Turn {attempt}] FAILED: Intercepted Error\n")
            print(output.strip())
            error_log = output
            attempt += 1

    print(f"\n❌ Agent reached max repair attempts ({max_attempts}) without passing tests.")
    return code


# ---------------------------------------------------------------------------
# 3. TASK SPECIFICATION & HIDDEN TESTS
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    TASK_SPEC = """
    Write a function `get_third_element(lst)` that returns the third element 
    of a list. If the list is shorter than 3 items, return None.
    """

    HIDDEN_TEST_SUITE = """
# Test 1: Standard case
assert get_third_element([10, 20, 30, 40]) == 30, "Failed standard 4-element list"

# Test 2: Edge case - Exactly 3 elements
assert get_third_element(['a', 'b', 'c']) == 'c', "Failed 3-element list"

# Test 3: Edge case - Less than 3 elements
assert get_third_element([1, 2]) is None, "Failed 2-element list edge case"

# Test 4: Edge case - Empty list
assert get_third_element([]) is None, "Failed empty list edge case"
"""

    final_code = autonomous_tdd_agent(TASK_SPEC, HIDDEN_TEST_SUITE)
    
    print("\n==================================================")
    print("FINAL DELIVERED CODE:")
    print("==================================================")
    print(final_code)