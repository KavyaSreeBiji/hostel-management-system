import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login
from db import fetch_student_profile, get_billing_by_student, fetch_student_complaints

require_login()

st.set_page_config(page_title="User Dashboard", page_icon=":material/dashboard:", layout="wide")
st.title(":material/dashboard: User Dashboard", anchor=False)

user_id = st.session_state.current_user_id
students_db_data = fetch_student_profile(user_id)
if not students_db_data:
    st.error("Engine failed to locate core identity profile.")
    st.stop()

student_data = students_db_data
room_id = student_data.get("Room_ID")

# Calculate nested billing securely
all_bills = get_billing_by_student(user_id) or []
total_amount_due = float(student_data.get('Total_Due') or 0.00)
last_bill = float(all_bills[0].get('Amount', 0.00)) if all_bills else 0.00
latest_due = all_bills[0].get('Due_Date', 'N/A') if all_bills else "N/A"
latest_status = all_bills[0].get('Status', 'N/A') if all_bills else "N/A"

# Fetch complaints
user_complaints = fetch_student_complaints(user_id) or []
pending_complaints = sum(1 for c in user_complaints if c.get("Status") == "Pending")
latest_complaint_status = user_complaints[0].get("Status", "No complaints") if user_complaints else "No complaints"

col1, col2 = st.columns(2)

with col1:
    st.subheader(":material/person: Basic Info", anchor=False)
    st.write(f"**Name:** {student_data.get('Name', 'N/A')}")
    st.write(f"**Student ID:** {user_id}")
    st.write(f"**Email:** {student_data.get('Email', 'N/A')}")
    st.write(f"**Phone:** {student_data.get('Phone', 'N/A')}")

with col2:
    st.subheader(":material/meeting_room: Room Details", anchor=False)
    if room_id:
        st.write(f"**Room ID:** {room_id}")
        st.write(f"**Capacity:** {student_data.get('Capacity', 'N/A')}")
        st.write(f"**Room Value:** ₹{student_data.get('Price', 0.00)}")
    else:
        st.info("You have not been allocated a room yet.")

st.divider()

st.subheader(":material/payments: Billing Summary", anchor=False)
b_col1, b_col2, b_col3, b_col4 = st.columns(4)
with b_col1:
    st.metric("Total Amount Due", f"₹{total_amount_due}")
with b_col2:
    st.metric("Latest Inbound Bill", f"₹{last_bill}")
with b_col3:
    st.metric("Next Due Date", str(latest_due))
with b_col4:
    st.metric("Latest Payment Status", latest_status, delta="Paid" if latest_status == "Paid" else "-Action needed" if latest_status == "Not Paid" else None, delta_color="normal" if latest_status == "Paid" else "inverse")

st.divider()

st.subheader(":material/campaign: Complaint Status", anchor=False)
c_col1, c_col2 = st.columns(2)
with c_col1:
    st.metric("Total Complaints Raised", len(user_complaints))
with c_col2:
    st.metric("Latest Complaint Status", latest_complaint_status, delta="Resolved" if latest_complaint_status == "Resolved" else None)

st.divider()

st.subheader(":material/bolt: Quick Actions", anchor=False)
st.info("Use the sidebar navigation on the left to view Full Billing, raise a Complaint, or edit your Profile.", icon=":material/arrow_back:")
