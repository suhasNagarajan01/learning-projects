import streamlit as st
from triage_engine import classify_ticket
from response_generator import generate_response

st.set_page_config(page_title="Support Ticket Triage Agent", page_icon="🤖", layout="wide")

# Pre-defined test dataset matching assignment specifications
TEST_TICKETS = {
    "Ticket 1 (Billing / Critical)": (
        "I noticed an unauthorized charge of $499 on my credit card this morning from your platform. "
        "Cancel this immediately and refund my money before I contact my bank!"
    ),
    "Ticket 2 (Tech Support / High)": (
        "Our production REST API webhook returns HTTP 500 errors on every POST request since 8 AM. "
        "Our mobile app checkout is completely broken."
    ),
    "Ticket 3 (Security / Critical)": (
        "I received an email stating my two-factor authentication device was reset, but I did not request this. "
        "I think someone accessed my account."
    ),
    "Ticket 4 (General / Low)": (
        "Hi team, do you have a dark mode option available on the iOS app? Thanks!"
    )
}

st.title("🤖 Autonomous Customer Support & Ticket Routing Agent")
st.markdown("---")

# Data selection / input side
col_in, col_out = st.columns([1, 1])

with col_in:
    st.subheader("📥 Incoming Ticket")
    selected_preset = st.selectbox("Load Test Ticket Preset:", ["Custom"] + list(TEST_TICKETS.keys()))
    print("selected_preset:" , selected_preset)
    default_text = TEST_TICKETS[selected_preset] if selected_preset != "Custom" else ""
    print("default text:" , selected_preset)
    user_email = st.text_area("Customer Email Content:", value=default_text, height=200)
    
    run_btn = st.button("Run Triage Pipeline", type="primary", use_container_width=True)

if run_btn and user_email.strip():
    print("triage pipeline run initiated.")
    with st.spinner("Classifying ticket and generating draft..."):
        # Pipeline Execution
        triage_data = classify_ticket(user_email)
        print(triage_data)
        draft_reply = generate_response(user_email, triage_data)
        print(draft_reply)
        st.session_state['triage'] = triage_data
        st.session_state['draft'] = draft_reply

with col_out:
    st.subheader("⚙️ Routing & Auto-Draft Review")
    
    if 'triage' in st.session_state:
        tdata = st.session_state['triage']
        
        # Display Metrics / Badges
        c1, c2, c3 = st.columns(3)
        c1.metric("Department", tdata.get("department"))
        c2.metric("Priority", tdata.get("priority"))
        c3.metric("SLA Window", f"{tdata.get('sla_response_hours')} hrs")
        data = {
            "Department" : tdata.get("department"),
            "priority"  :tdata.get("priority"),
            "SLA Window" :  f"{tdata.get('sla_response_hours')} hrs"
        }

        print(data)
        
        st.info(f"**Customer Sentiment:** {tdata.get('sentiment')} | **Reasoning:** {tdata.get('reasoning')}")
        
        # Draft area
        edited_response = st.text_area("Review & Edit Draft Email:", value=st.session_state['draft'], height=220)
        
        if st.button("🚀 Approve & Send", type="primary"):
            st.success("Response dispatched to customer and ticket resolved successfully!")
    else:
        st.info("Select or enter a customer email and click **Run Triage Pipeline** to begin.")