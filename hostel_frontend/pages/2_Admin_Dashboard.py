import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_mock_data, require_login

init_mock_data()
require_login()

st.set_page_config(page_title="Admin Dashboard", page_icon=":material/dashboard:", layout="wide")
st.title(":material/dashboard: Admin Dashboard", anchor=False)

# ------------------ LOAD DATA ------------------
students = st.session_state.students
rooms = st.session_state.rooms
billing = st.session_state.billing
complaints = st.session_state.complaints

# ------------------ TOP SUMMARY ------------------
st.subheader(":material/insights: System Overview", anchor=False)

total_students = len(students)
available_rooms = sum(1 for r in rooms.values() if r["status"] == "Available")
pending_complaints = sum(1 for c in complaints if c["status"] == "Pending")

total_revenue = sum(b.get("last_bill", 0) for b in billing.values())

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

for b in billing.values():
    if b.get("status") == "Paid":
        paid_count += 1
    else:
        pending_count += 1
        pending_amount += b.get("total_due", 0)

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
st.divider()
st.subheader(":material/table: Manage Room Allocation", anchor=False)

for room_id, room in rooms.items():
    col1, col2, col3, col4, col5 = st.columns([1, 1.2, 1.2, 1.2, 2])

    with col1:
        st.markdown(f"**{room_id}**")

    with col2:
        st.caption(f"Capacity: {room['capacity']}")

    with col3:
        st.caption(f"Occupancy: {room['occupancy']}")

    with col4:
        if room["status"] == "Available":
            st.success("Available")
        else:
            st.error("Full")

    with col5:
        available_students = [
            sid for sid, s in students.items() if not s.get("room_id")
        ]

        if available_students and room["status"] == "Available":
            selected = st.selectbox(
                "Assign Student",
                available_students,
                format_func=lambda x: students[x]["name"],
                key=f"admin_select_{room_id}"
            )

            if st.button("Allocate", key=f"admin_btn_{room_id}"):
                students[selected]["room_id"] = room_id
                room["occupancy"] += 1

                if room["occupancy"] >= room["capacity"]:
                    room["status"] = "Full"

                st.success(f"{students[selected]['name']} assigned to Room {room_id}")
        else:
            st.caption("No action")

# ------------------ QUICK INSIGHTS ------------------
st.divider()
st.subheader(":material/insights: System Insight", anchor=False)

if pending_count > 0:
    st.warning(f"{pending_count} payments are pending.")
else:
    st.success("All payments cleared.")

if available_rooms == 0:
    st.error("No rooms available.")
else:
    st.info(f"{available_rooms} rooms available for allocation.")
