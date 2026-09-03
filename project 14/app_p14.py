import streamlit as st
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="Autonomous Multi-Tool ReAct Agent Loop",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Autonomous Multi-Tool ReAct Agent Loop")
st.caption("Chain multiple tools autonomously across sequential reasoning steps using Gemini.")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key", type="password")
    selected_model = st.selectbox("Select Model", ["gemini-3.6-flash", "gemini-2.5-pro"])
    max_turns = st.slider("Max Loop Iterations", min_value=1, max_value=10, value=5)

if not api_key:
    st.info("Please enter your Gemini API key in the sidebar to proceed.", icon="🔑")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# ------------------------------------------------------------------------------
# 1. Tool Function Definitions
# ------------------------------------------------------------------------------

def get_crypto_price(symbol: str) -> dict:
    """Fetches the current market price for a given cryptocurrency ticker symbol.

    Args:
        symbol: The cryptocurrency ticker or name (e.g., 'BTC', 'ETH', 'SOL').

    Returns:
        dict: Cryptocurrency current price in USD and 24h change percentage.
    """
    mock_crypto_db = {
        "BTC": {"symbol": "BTC", "name": "Bitcoin", "price_usd": 65000.00, "24h_change_pct": 2.5},
        "ETH": {"symbol": "ETH", "name": "Ethereum", "price_usd": 3500.00, "24h_change_pct": -1.2},
        "SOL": {"symbol": "SOL", "name": "Solana", "price_usd": 145.00, "24h_change_pct": 5.8},
    }
    
    ticker = symbol.upper().strip()
    if ticker in mock_crypto_db:
        return mock_crypto_db[ticker]
    else:
        return {
            "symbol": ticker,
            "name": ticker,
            "price_usd": 100.00,
            "24h_change_pct": 0.0,
            "note": "Fallback value for unrecognized ticker."
        }


def calculate_crypto_roi(
    initial_investment_usd: float,
    entry_price_usd: float,
    current_price_usd: float
) -> dict:
    """Calculates the return on investment (ROI), net profit/loss, and target token count for a crypto trade.

    Args:
        initial_investment_usd: Total initial capital invested in USD (e.g., 5000.0).
        entry_price_usd: Purchase price per token in USD (e.g., 50000.0).
        current_price_usd: Current market price per token in USD (e.g., 65000.0).

    Returns:
        dict: Total tokens purchased, current total value, net profit in USD, and ROI percentage.
    """
    if entry_price_usd <= 0:
        return {"error": "Entry price must be greater than 0."}

    tokens_acquired = initial_investment_usd / entry_price_usd
    current_value_usd = tokens_acquired * current_price_usd
    net_profit_usd = current_value_usd - initial_investment_usd
    roi_percentage = (net_profit_usd / initial_investment_usd) * 100.0

    return {
        "initial_investment_usd": round(initial_investment_usd, 2),
        "tokens_acquired": round(tokens_acquired, 6),
        "entry_price_usd": round(entry_price_usd, 2),
        "current_price_usd": round(current_price_usd, 2),
        "current_value_usd": round(current_value_usd, 2),
        "net_profit_usd": round(net_profit_usd, 2),
        "roi_percentage": round(roi_percentage, 2),
    }

# Local Tool Execution Registry
TOOL_REGISTRY = {
    "get_crypto_price": get_crypto_price,
    "calculate_crypto_roi": calculate_crypto_roi,
}

# Declarations list for model config
TOOLS_LIST = [get_crypto_price, calculate_crypto_roi]

# ------------------------------------------------------------------------------
# 2. ReAct Agent Loop
# ------------------------------------------------------------------------------

default_query = (
    "I invested $10,000 in Bitcoin when it was at $50,000. "
    "Check the current price of BTC using your tool, calculate my profit and ROI, "
    "and give me a full breakdown."
)

user_query = st.text_area("Compound Query:", value=default_query, height=100)

if st.button("Run ReAct Loop", type="primary"):
    # Conversation buffer initialization
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_query)]
        )
    ]

    # Status log container for ReAct trace
    with st.status("🚀 Running Autonomous ReAct Loop...", expanded=True) as status:
        iteration = 0
        final_answer = None

        while iteration < max_turns:
            iteration += 1
            st.write(f"### 📍 Iteration {iteration}")

            # Query Gemini model with tool definitions
            response = client.models.generate_content(
                model=selected_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=TOOLS_LIST,
                    system_instruction=(
                        "You are an autonomous ReAct financial agent. "
                        "When given a task, decide whether to call tools or provide a final answer. "
                        "Execute tools sequentially as needed to gather information and complete calculations."
                    )
                )
            )

            # Append model candidate response to message history
            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)

            # Check if Gemini requested function call(s)
            if response.function_calls:
                for tool_call in response.function_calls:
                    fn_name = tool_call.name
                    fn_args = dict(tool_call.args)

                    st.markdown(f"**Thought:** Requesting tool `{fn_name}`")
                    st.json(fn_args)

                    # Execute function locally
                    if fn_name in TOOL_REGISTRY:
                        tool_fn = TOOL_REGISTRY[fn_name]
                        result = tool_fn(**fn_args)

                        st.markdown(f"**Action Result (`{fn_name}`):**")
                        st.json(result)

                        # Pack local function result into standard tool response content
                        contents.append(
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_function_response(
                                        name=fn_name,
                                        response={"result": result}
                                    )
                                ]
                            )
                        )
                    else:
                        st.error(f"Error: Function `{fn_name}` not in local registry.")
                        break
            else:
                # No function call requested -> Loop terminal state reached
                final_answer = response.text
                st.markdown("**Thought:** Task complete. Formulating final answer.")
                status.update(label=f"✅ ReAct Loop completed in {iteration} steps!", state="complete")
                break

        if not final_answer and iteration >= max_turns:
            status.update(label="⚠️ Maximum loop iterations reached.", state="error")

    # Display Final Answer
    if final_answer:
        st.subheader("📊 Final Answer")
        st.markdown(final_answer)