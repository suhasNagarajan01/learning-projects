#this streamlit app should work as a ticket collector web app which takes user's email , type of ticket {ciritical ,tech based etc}
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Support Triage Dashboard",
    page_icon="🤖",
    layout="wide",
)


# 2. Initialize Session State
if "processed" not in st.session_state:
    st.session_state.processed = False
if "draft_text" not in st.session_state:
    st.session_state.draft_text = ""


# 3. Sidebar Configuration & Controls
st.sidebar.header("Triage Settings")
selected_model = st.sidebar.selectbox(
    "Target Model", ["gemini-3.6-flash", "gemini-1.5-pro"]
)
run_button = st.sidebar.button("Run Triage Pipeline", type="primary")


# 4. Main Header Area
st.title("🛡️ Autonomous Customer Support & Ticket Routing")
st.markdown(
    "Classify incoming inquiries, evaluate SLAs, and review drafted responses."
)

# Horizontal Rule
st.markdown("---")


# 5. Metrics Row (Displaying Triage Stats)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Tickets Processed", value="128", delta="+12")
with col2:
    st.metric(label="High Urgency / Critical", value="5", delta="-2")
with col3:
    st.metric(label="SLA Breached", value="0", delta="0")
with col4:
    st.metric(label="Avg Response Time", value="1.2 hrs", delta="-0.3 hrs")

st.markdown("---")


# 6. Main Dashboard Layout (Two Columns)
left_column, right_column = st.columns([1, 1])

with left_column:
    st.subheader("📥 Incoming Customer Message")
    customer_email = st.text_area(
        "Edit or paste raw customer inquiry:",
        value=(
            "Hi, I was charged twice for my subscription and now my account is"
            " locked out. Please help urgently!"
        ),
        height=150,
    )

    if run_button:
        # Simulate processing logic
        st.session_state.processed = True
        st.session_state.draft_text = (
            "Dear Customer,\n\nWe apologize for the double charge and the"
            " login issue. We have verified the duplicate transaction and"
            " initiated a full refund. Your account has also been manually"
            " unlocked.\n\nBest regards,\nSupport Team"
        )
        st.success("Ticket successfully analyzed and classified!")

with right_column:
    st.subheader("⚙️ Triage Results & Draft Review")

    if st.session_state.processed:
        # Badge-style categorization using markdown/HTML or st.markdown
        st.markdown(
            "**Department:** 💳 **Billing / Tech** &nbsp;&nbsp;&nbsp;&nbsp;"
            "**Priority:** 🔴 **Critical**"
        )
        st.markdown("**Sentiment:** 😠 **Frustrated** | **SLA Target:** 2 Hours")

        st.markdown("### Editable Response Draft")
        edited_draft = st.text_area(
            "Review and modify AI-generated response:",
            value=st.session_state.draft_text,
            height=150,
        )

        # Action Buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Approve & Send", type="primary", use_container_width=True):
                st.success("Response sent to customer and ticket resolved!")
        with col_btn2:
            if st.button("🔄 Regenerate Draft", use_container_width=True):
                st.info("Regenerating response draft...")
    else:
        st.info(
            "👈 Click **'Run Triage Pipeline'** in the sidebar to analyze the"
            " message."
        )