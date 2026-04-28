import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import fetch_all_rooms, allocate_room, add_room, fetch_pending_requests, resolve_request, fetch_all_students, remove_student_from_room

st.set_page_config(page_title="Room Allocation", page_icon=":material/meeting_room:", layout="wide")
st.title(":material/meeting_room: Room Allocation (Database)", anchor=False)

rooms = fetch_all_rooms()
students = fetch_all_students() or []

if rooms is None:
    st.error("Failed to connect to the database. Ensure MySQL is running.")
    st.stop()

# ------------------ PENDING REQUESTS ------------------
st.subheader(":material/approval: Pending Room Requests", anchor=False)
requests = fetch_pending_requests()

if not requests:
    st.info("No pending requests to approve at this time.")
else:
    student_opts = {s["Student_ID"]: f"{s['Student_ID']} - {s['Name']}" for s in students}
    for req in requests:
        with st.container(border=True):
            rcol1, rcol2, rcol3 = st.columns([2, 1, 1])
            with rcol1:
                student_display = student_opts.get(req['Student_ID'], f"Student {req['Student_ID']}")
                st.write(f"**Request #{req['Request_ID']}** : **{student_display}** requested Room {req['Room_ID']}")
            with rcol2:
                if st.button("Approve", key=f"app_{req['Request_ID']}", type="primary"):
                    success, msg = resolve_request(req['Request_ID'], "Approve")
                    if success:
                        st.success("Request approved! Room successfully booked.")
                        st.rerun()
                    else:
                        st.error(msg)
            with rcol3:
                if st.button("Reject", key=f"rej_{req['Request_ID']}"):
                    success, msg = resolve_request(req['Request_ID'], "Reject")
                    if success:
                        st.success("Request rejected.")
                        st.rerun()
                    else:
                        st.error(msg)

st.divider()

# ------------------ ADD NEW ROOM ------------------
st.subheader(":material/add_circle: Add New Room", anchor=False)
with st.expander("Create a new room in the system"):
    capacity = st.number_input("Sharing Capacity (e.g., 2-sharing, 3-sharing)", min_value=1, max_value=10, value=2)
    price = st.number_input("Pricing per assignment (₹)", min_value=0.0, value=5000.0, step=500.0)
    
    if st.button("Add Room", type="primary"):
        if add_room(capacity, price):
            st.success("New room created successfully!")
            st.rerun()
        else:
            st.error("Failed to create room.")

# ------------------ SUMMARY ------------------
st.subheader(":material/insights: DB Room Summary", anchor=False)

total_rooms = len(rooms)
available_rooms = sum(1 for r in rooms if r["Availability_Status"] == "Available")
full_rooms = total_rooms - available_rooms

s1, s2, s3 = st.columns(3)

with s1:
    st.metric("Total Rooms", total_rooms)
with s2:
    st.metric("Available", available_rooms)
with s3:
    st.metric("Full", full_rooms)

st.divider()

# ------------------ ROOM TABLE ------------------
st.subheader(":material/table: Live Room Overview", anchor=False)

for room in rooms:
    room_id = room["Room_ID"]
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

    with col1:
        st.markdown(f"**Room {room_id}**")

    with col2:
        st.caption(f"Cap: {room['Capacity']}")

    with col3:
        st.caption(f"Occ: {room['Occupancy']}")
        st.caption(f"₹{room['Price']}")

    with col4:
        if room["Availability_Status"] == "Available":
            st.success("Available")
        else:
            st.error("Full")

    with col5:
        occupants = [s for s in students if s['Room_ID'] == room_id]
        if not occupants:
            st.caption("No occupants")
        else:
            with st.popover(f"View Occupants ({len(occupants)})"):
                for occ in occupants:
                    st.write(f"**{occ['Name']}** (ID: {occ['Student_ID']})")
                    if st.button("Remove", key=f"rem_{occ['Student_ID']}_{room_id}", type="primary"):
                        if remove_student_from_room(occ['Student_ID'], room_id):
                            st.success(f"Removed {occ['Name']} from Room {room_id}")
                            st.rerun()
                        else:
                            st.error("Failed to remove student.")
                    st.divider()

st.divider()
st.info("Live Database Synchronized. Updates will instantly flip Availability to 'Full' when capacity is met.")
