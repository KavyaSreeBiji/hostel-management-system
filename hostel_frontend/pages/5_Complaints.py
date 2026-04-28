import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login
from db import submit_complaint, fetch_student_complaints

require_login()

st.set_page_config(page_title="Complaints", page_icon=":material/campaign:", layout="centered")
st.title(":material/campaign: Complaints", anchor=False)

user_id = st.session_state.current_user_id

st.header("Raise a New Complaint", anchor=False)
with st.form("new_complaint_form"):
    category = st.selectbox("Category", ["Maintenance", "Cleaning", "Electrical", "Plumbing", "Internet", "Other"])
    description = st.text_area("Description", placeholder="Describe the issue in detail...")
    submitted = st.form_submit_button("Submit Complaint")
    
    if submitted:
        if not description.strip():
            st.error("Please provide a description.")
        else:
            success = submit_complaint(user_id, category, description)
            if success:
                st.success("Complaint submitted securely to Database successfully!")
                st.rerun()
            else:
                st.error("Failed to commit Complaint to Database.")

st.divider()

st.header("Your Past Complaints", anchor=False)
user_complaints = fetch_student_complaints(user_id) or []

if not user_complaints:
    st.info("You haven't raised any complaints yet.")
else:
    for c in user_complaints:
        with st.expander(f"[{c['Status']}] {c['Category']} - Complaint #{c['Complaint_ID']}"):
            st.write(f"**Description:** {c['Description']}")
            if c['Status'] == "Pending":
                st.warning("Status: Pending")
            elif c['Status'] == "Resolved":
                st.success("Status: Resolved")
