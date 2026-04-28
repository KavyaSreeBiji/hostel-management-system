import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login
from db import fetch_all_students, fetch_all_rooms, fetch_all_billing, fetch_all_complaints

require_login()

st.set_page_config(page_title="Admin Dashboard", page_icon=":material/dashboard:", layout="wide")
st.title(":material/dashboard: Admin Dashboard", anchor=False)

# ------------------ LOAD DATA ------------------
students = fetch_all_students() or []
rooms = fetch_all_rooms() or []
billing = fetch_all_billing() or []
complaints = fetch_all_complaints() or []

# ------------------ TOP SUMMARY ------------------
st.subheader(":material/insights: System Overview", anchor=False)

total_students = len(students)
available_rooms = sum(1 for r in rooms if r.get("Availability_Status") == "Available")
pending_complaints = sum(1 for c in complaints if c.get("Status") == "Pending")

total_revenue = sum(float(b.get("Amount", 0)) for b in billing)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Students", total_students)
with c2:
    st.metric("Available Rooms", available_rooms)
with c3:
    st.metric("Pending Complaints", pending_complaints)
with c4:
    st.metric("Revenue", f"₹{total_revenue}")

# ------------------ BILLING OVERVIEW ------------------
st.divider()
st.subheader(":material/payments: Billing Overview", anchor=False)

pending_amount = 0
paid_count = 0
pending_count = 0

for b in billing:
    if b.get("Status") == "Paid":
        paid_count += 1
    else:
        pending_count += 1
        pending_amount += float(b.get("Amount", 0))

b1, b2, b3, b4 = st.columns(4)

with b1:
    st.metric("Total Revenue", f"₹{total_revenue}")
with b2:
    st.metric("Pending Amount", f"₹{pending_amount}")
with b3:
    st.metric("Paid Bills", paid_count)
with b4:
    st.metric("Pending Bills", pending_count)

# ------------------ ROOM SUMMARY ------------------
st.divider()
st.subheader(":material/meeting_room: Room Summary", anchor=False)

total_rooms = len(rooms)
full_rooms = total_rooms - available_rooms

r1, r2, r3 = st.columns(3)

with r1:
    st.metric("Total Rooms", total_rooms)
with r2:
    st.metric("Available", available_rooms)
with r3:
    st.metric("Full", full_rooms)

# ------------------ ROOM MANAGEMENT ------------------
st.info(f"{available_rooms} rooms available for allocation.")

# ------------------ COMPLAINTS MANAGER ------------------
st.divider()
st.subheader(":material/campaign: System Complaints", anchor=False)

if not complaints:
    st.info("No complaints submitted by students.")
else:
    for c in complaints:
        if c["Status"] == "Pending":
            with st.expander(f"[ACTION REQUIRED] {c['Category']} from {c['Name']} (ID: {c['Student_ID']})"):
                st.write(f"**Description:** {c['Description']}")
                if st.button("Mark as Resolved", key=f"res_{c['Complaint_ID']}", type="primary"):
                    from db import resolve_complaint
                    if resolve_complaint(c['Complaint_ID']):
                        st.success("Complaint resolved!")
                        st.rerun()
                    else:
                        st.error("Engine failed to resolve.")
