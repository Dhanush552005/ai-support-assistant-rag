import sys
import os
import streamlit as st
import re

# Fix import path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from agents import run_agents

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SupportAI | Resolution Engine",
    page_icon="🤖",
    layout="wide", # Wider layout feels more like a professional dashboard
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextArea textarea { font-size: 1.1rem !important; }
    .status-box { border-radius: 10px; padding: 15px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ System Control")
    st.info("Current Model: `llama-3.1-8b-instant` (via Groq)")
    st.divider()
    st.markdown("### Support Metrics")
    st.metric(label="SLA Target", value="< 5s", delta="-1.2s")
    if st.button("Clear Cache & History"):
        st.cache_resource.clear()
        st.rerun()

# --- MAIN UI ---
st.title("🛒 E-commerce Support Resolution")
st.caption("Internal Agent Tool • Powered by RAG Multi-Agent Pipeline")

# Ticket Input Section
ticket = st.text_area(
    "Customer Ticket Inquiry", 
    placeholder="Example: 'My order arrived damaged, can I get refund?'",
    height=150
)

# Function to parse the structured output (assuming specific headers exist)
def parse_sections(text):
    sections = {}
    current_key = "General"
    # Logic to split based on "Header:" format
    lines = text.split('\n')
    for line in lines:
        if ":" in line and len(line.split(":")[0].split()) < 4:
            current_key = line.split(":")[0].strip()
            sections[current_key] = line.split(":", 1)[1].strip()
        else:
            sections[current_key] = sections.get(current_key, "") + "\n" + line
    return sections

if st.button("Generate Resolution", type="primary"):
    if not ticket.strip():
        st.warning("⚠️ Please enter a ticket description before proceeding.")
    else:
        # 1. Multi-Agent Status Tracking
        with st.status("🤖 AI Agents Collaborating...", expanded=True) as status:
            st.write("🔍 **Triage Agent:** Classifying issue intent...")
            # We'll call the actual function here
            # ✅ Add Order Context
            order_context = {
                "order_date": "2026-03-20",
                "delivery_date": "2026-03-25",
                "item_category": "perishable",
                "fulfillment_type": "first-party",
                "shipping_region": "India",
                "order_status": "delivered",
                "payment_method": "prepaid"
            }

            raw_response = run_agents(ticket, order_context)
            
            st.write("📚 **Retriever Agent:** Fetching policy documents...")
            st.write("⚖️ **Resolution Agent:** Drafting grounded response...")
            st.write("✅ **Compliance Agent:** Validating output structure...")
            status.update(label="Resolution Ready!", state="complete", expanded=False)

        # 2. Displaying the Resulting Sections professionally
        st.divider()
        data = parse_sections(raw_response)
        
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📝 Resolution Summary")
            # Highlight the Decision
            decision = data.get("Decision", "Review Required").upper()
            st.info(f"**Final Decision:** {decision}")
            
            with st.expander("Internal Rationale", expanded=True):
                st.write(data.get("Rationale", "No rationale provided."))

            st.subheader("💬 Prepared Customer Message")
            customer_reply = data.get("Customer Response", "Contact support.")
            st.text_area("Copy this to customer chat:", value=customer_reply, height=150)
            st.button("📋 Copy to Clipboard", on_click=lambda: st.write("Copied! (Mock)"))

        with col2:
            st.subheader("📌 Metadata & Citations")
            st.warning(f"**Category:** {data.get('Classification', 'Unclassified')}")
            
            with st.expander("View Policy Citations"):
                st.write(data.get("Citations", "No citations found."))
            
            with st.expander("Required Next Steps"):
                st.write(data.get("Next Steps", "Standard escalation."))

        # 3. Raw Logs (Hidden by default for devs)
        with st.expander("See Raw Model Output (Debug)"):
            st.code(raw_response)

else:
    st.info("💡 **Tip:** Mention specific details like 'damaged', 'late delivery', or 'missing item' for better policy matching.")