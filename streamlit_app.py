"""Streamlit UI for ClaimFlow."""
import streamlit as st
import requests
from PIL import Image
import io
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="ClaimFlow - Instant Auto Claims",
    page_icon="🚗",
    layout="wide"
)

# Title
st.title("🚗 ClaimFlow - Instant Auto Claims Adjuster")
st.markdown("### Upload your damage photo and policy ID to get an instant claim decision")

# Sidebar
with st.sidebar:
    st.header("About ClaimFlow")
    st.info(
        "ClaimFlow uses AI agents to process your auto insurance claim instantly:\n\n"
        "1. **Vision Agent**: Analyzes damage photos\n"
        "2. **Policy Agent**: Checks your coverage\n"
        "3. **Finance Agent**: Calculates payout\n\n"
        "Get your decision in seconds!"
    )
    
    st.header("Sample Policy IDs")
    st.code("POL001 - $500 deductible")
    st.code("POL002 - $1000 deductible")
    st.code("POL003 - $250 deductible")

# Main form
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Claim Information")
    
    policy_id = st.text_input(
        "Policy ID",
        value="POL001",
        help="Enter your policy ID (e.g., POL001, POL002, POL003)"
    )
    
    email = st.text_input(
        "Email (optional)",
        help="Enter your email to receive notification"
    )
    
    uploaded_file = st.file_uploader(
        "Upload Damage Photo",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear photo of the damage"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Damage Photo", use_column_width=True)

with col2:
    st.subheader("📊 Claim Results")
    result_placeholder = st.empty()

# Submit button
if st.button("🚀 Process Claim", type="primary", use_container_width=True):
    if not policy_id:
        st.error("Please enter a Policy ID")
    elif uploaded_file is None:
        st.error("Please upload a damage photo")
    else:
        with st.spinner("Processing your claim... This may take a few seconds."):
            try:
                # Prepare the request
                files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"policy_id": policy_id}
                if email:
                    data["email"] = email
                
                # Make API request
                response = requests.post(
                    f"{API_URL}/api/claims/process",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results in the second column
                    with col2:
                        st.success("✅ Claim Processed Successfully!")
                        
                        # Claim ID
                        st.info(f"**Claim ID:** {result['claim_id']}")
                        
                        # Damage Analysis
                        st.markdown("### 🔍 Damage Analysis")
                        damage = result['damage_analysis']
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Damage Type", damage['damage_type'].title())
                            st.metric("Severity", damage['severity'].replace('_', ' ').title())
                        with col_b:
                            st.metric("Estimated Cost", f"${damage['estimated_cost']:,.2f}")
                            st.metric("Confidence", f"{damage['confidence']*100:.0f}%")
                        
                        # Policy Information
                        st.markdown("### 📄 Policy Information")
                        policy = result['policy_info']
                        
                        col_c, col_d = st.columns(2)
                        with col_c:
                            st.metric("Deductible", f"${policy['deductible']:,.2f}")
                            st.metric("Coverage Limit", f"${policy['coverage_limit']:,.2f}")
                        with col_d:
                            coverage_status = "✅ Covered" if policy['is_covered'] else "❌ Not Covered"
                            st.markdown(f"**Coverage Status:** {coverage_status}")
                            st.caption(policy['coverage_details'])
                        
                        # Payout Calculation
                        st.markdown("### 💰 Payout Calculation")
                        payout = result['payout_calculation']
                        
                        # Highlight payout amount
                        if payout['payout_amount'] > 0:
                            st.success(f"**Approved Payout: ${payout['payout_amount']:,.2f}**")
                        else:
                            st.error(f"**Status: {payout['status'].replace('_', ' ').title()}**")
                        
                        col_e, col_f, col_g = st.columns(3)
                        with col_e:
                            st.metric("Estimated Cost", f"${payout['estimated_cost']:,.2f}")
                        with col_f:
                            st.metric("Deductible", f"${payout['deductible']:,.2f}")
                        with col_g:
                            st.metric("Payout", f"${payout['payout_amount']:,.2f}")
                        
                        # PDF Download
                        if result.get('pdf_path'):
                            st.markdown("### 📥 Download Offer Letter")
                            pdf_url = f"{API_URL}/api/claims/{result['claim_id']}/pdf"
                            st.markdown(f"[📄 Download PDF Offer Letter]({pdf_url})")
                        
                        # Notification status
                        st.markdown("---")
                        st.caption("✉️ Notifications sent via Email and Slack (if configured)")
                
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to ClaimFlow API. "
                    "Please ensure the backend is running at " + API_URL
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "ClaimFlow - Instant Auto Claims Adjuster | Powered by AI Agents"
    "</div>",
    unsafe_allow_html=True
)
