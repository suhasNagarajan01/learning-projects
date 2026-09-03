import math
import streamlit as st
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="Autonomous Function Calling Agent",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Autonomous Function Calling Agent")
st.caption("Gemini dynamically inspects, selects, and invokes local Python functions based on natural language prompts.")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key", type="password")
    selected_model = st.selectbox("Select Model", ["gemini-2.5-flash", "gemini-3.6-flash"])

if not api_key:
    st.info("Please enter your Gemini API key in the sidebar to proceed.", icon="🔑")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# ------------------------------------------------------------------------------
# 1. Tool Function Definitions (With Type Hints & Google-Style Docstrings)
# ------------------------------------------------------------------------------

def calculate_loan_emi(principal: float, annual_rate_pct: float, tenure_years: int) -> dict:
    """Calculates the Equated Monthly Installment (EMI) for a loan.

    Args:
        principal: The total loan principal amount (e.g., 500000.0).
        annual_rate_pct: Annual interest rate percentage (e.g., 8.5 for 8.5%).
        tenure_years: Loan duration in years (e.g., 15).

    Returns:
        dict: Containing monthly EMI amount, total interest payable, and total payment amount.
    """
    monthly_rate = (annual_rate_pct / 100) / 12
    total_months = tenure_years * 12

    if monthly_rate == 0:
        emi = principal / total_months
    else:
        emi = (principal * monthly_rate * math.pow(1 + monthly_rate, total_months)) / (
            math.pow(1 + monthly_rate, total_months) - 1
        )

    total_payment = emi * total_months
    total_interest = total_payment - principal

    return {
        "monthly_emi": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payment": round(total_payment, 2),
        "tenure_months": total_months,
    }


def get_stock_metrics(ticker: str) -> dict:
    """Fetches key financial metrics and current valuation for a given stock ticker symbol.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'RELIANCE').

    Returns:
        dict: Stock market metrics including current price, P/E ratio, and 52-week range.
    """
    # Deterministic mock data for tool execution demonstration
    mock_market_data = {
        "AAPL": {"price": 224.50, "pe_ratio": 33.2, "52_week_high": 237.23, "currency": "USD"},
        "GOOGL": {"price": 178.35, "pe_ratio": 24.1, "52_week_high": 191.75, "currency": "USD"},
        "RELIANCE": {"price": 2980.00, "pe_ratio": 27.8, "52_week_high": 3217.90, "currency": "INR"},
    }

    symbol = ticker.upper().strip()
    if symbol in mock_market_data:
        data = mock_market_data[symbol]
        data["ticker"] = symbol
        return data
    else:
        return {
            "ticker": symbol,
            "price": 150.00,
            "pe_ratio": 20.0,
            "52_week_high": 165.00,
            "currency": "USD",
            "note": "Mock fallback values generated for unrecognized ticker.",
        }


# Dispatch Registry
TOOL_REGISTRY = {
    "calculate_loan_emi": calculate_loan_emi,
    "get_stock_metrics": get_stock_metrics,
}

# ------------------------------------------------------------------------------
# 2. UI & Execution Flow
# ------------------------------------------------------------------------------

user_query = st.text_input(
    "Ask a question requiring math or stock metrics:",
    value="Calculate the monthly EMI for a loan of $500,000 at an interest rate of 8.5% per annum for 15 years."
)

if st.button("Submit Query", type="primary"):
    with st.spinner("Processing with function calling agent..."):
        try:
            # Step A: First Model Call - Model determines if tool call is needed
            st.write("### 🔍 Step 1: Querying Gemini with Tool Declarations")
            response = client.models.generate_content(
                model=selected_model,
                contents=user_query,
                config=types.GenerateContentConfig(
                    tools=[calculate_loan_emi, get_stock_metrics]
                ),
            )

            # Step B: Inspect model's response for function call requests
            if response.function_calls:
                tool_call = response.function_calls[0]
                function_name = tool_call.name
                function_args = dict(tool_call.args)

                st.info(f"**Function Requested by Model:** `{function_name}`")
                st.json({"extracted_arguments": function_args})

                # Step C: Deterministic Local Dispatching
                if function_name in TOOL_REGISTRY:
                    st.write("### ⚙️ Step 2: Local Deterministic Function Execution")
                    tool_function = TOOL_REGISTRY[function_name]
                    tool_result = tool_function(**function_args)

                    st.success("Local execution completed successfully.")
                    st.json({"local_execution_result": tool_result})

                    # Step D: Second Model Call - Return function output to Gemini for natural synthesis
                    st.write("### 🤖 Step 3: Returning Tool Output to Gemini for Final Response")

                    # Construct conversation history including the function response part
                    chat_history = [
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=user_query)]
                        ),
                        response.candidates[0].content,  # Model's function call request
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_function_response(
                                    name=function_name,
                                    response={"result": tool_result}
                                )
                            ]
                        )
                    ]

                    final_response = client.models.generate_content(
                        model=selected_model,
                        contents=chat_history,
                        config=types.GenerateContentConfig(
                            tools=[calculate_loan_emi, get_stock_metrics]
                        ),
                    )

                    st.subheader("Final Output")
                    st.markdown(final_response.text)

                else:
                    st.error(f"Error: Function `{function_name}` requested by model is not in local registry.")

            else:
                # Direct response if Gemini answered without requiring function execution
                st.subheader("Final Output (No Function Call Required)")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Execution Error: {e}")