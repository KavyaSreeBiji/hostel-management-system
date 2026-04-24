import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_mock_data, require_login

init_mock_data()
require_login()

st.set_page_config(page_title="User Dashboard", page_icon=":material/dashboard:", layout="wide")
st.title(":material/dashboard: User Dashboard", anchor=False)

user_id = st.session_state.current_user_id
student_data = st.session_state.students.get(user_id, {})
room_id = student_data.get("room_id")
room_data = st.session_state.rooms.get(room_id, {}) if room_id else {}
billing_data = st.session_state.billing.get(user_id, {})

user_complaints = [c for c in st.session_state.complaints if c["student_id"] == user_id]
pending_complaints = sum(1 for c in user_complaints if c["status"] == "Pending")
latest_complaint_status = user_complaints[-1]["status"] if user_complaints else "No complaints"

col1, col2 = st.columns(2)

with col1:
    st.subheader(":material/person: Basic Info", anchor=False)
    st.write(f"**Name:** {student_data.get('name', 'N/A')}")
    st.write(f"**Student ID:** {user_id}")
    st.write(f"**Email:** {student_data.get('email', 'N/A')}")
    st.write(f"**Phone:** {student_data.get('phone', 'N/A')}")

with col2:
    st.subheader(":material/meeting_room: Room Details", anchor=False)
    if room_id:
        st.write(f"**Room ID:** {room_id}")
        st.write(f"**Capacity:** {room_data.get('capacity', 'N/A')}")
        st.write(f"**Current Occupancy:** {room_data.get('occupancy', 'N/A')}")
        st.write(f"**Availability Status:** {room_data.get('status', 'N/A')}")
    else:
        st.info("You have not been allocated a room yet.")

st.divider()

st.subheader(":material/payments: Billing Summary", anchor=False)
b_col1, b_col2, b_col3, b_col4 = st.columns(4)
with b_col1:
    st.metric("Total Amount Due", f"₹{billing_data.get('total_due', 0)}")
with b_col2:
    st.metric("Last Bill Amount", f"₹{billing_data.get('last_bill', 0)}")
with b_col3:
    st.metric("Due Date", billing_data.get('due_date', 'N/A'))
with b_col4:
    status = billing_data.get('status', 'N/A')
    st.metric("Payment Status", status, delta="Paid" if status == "Paid" else "-Action needed" if status == "Pending" else None, delta_color="normal" if status == "Paid" else "inverse")

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
