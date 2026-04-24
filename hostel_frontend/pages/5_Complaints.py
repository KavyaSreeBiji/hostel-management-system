import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_mock_data, require_login

init_mock_data()
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
            new_id = len(st.session_state.complaints) + 1
            st.session_state.complaints.append({
                "id": new_id,
                "student_id": user_id,
                "category": category,
                "description": description,
                "status": "Pending"
            })
            st.success("Complaint submitted successfully!")

st.divider()

st.header("Your Past Complaints", anchor=False)
user_complaints = [c for c in st.session_state.complaints if c["student_id"] == user_id]

if not user_complaints:
    st.info("You haven't raised any complaints yet.")
else:
    for c in reversed(user_complaints):
        with st.expander(f"[{c['status']}] {c['category']} - Complaint #{c['id']}"):
            st.write(f"**Description:** {c['description']}")
            if c['status'] == "Pending":
                st.warning("Status: Pending")
            elif c['status'] == "Resolved":
                st.success("Status: Resolved")
