import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_mock_data, require_login

init_mock_data()
require_login()

st.set_page_config(page_title="Rooms", page_icon=":material/meeting_room:", layout="wide")
st.title(":material/meeting_room: Room Allocation", anchor=False)

rooms = st.session_state.rooms
students = st.session_state.students

# ------------------ SUMMARY ------------------
st.subheader(":material/insights: Room Summary", anchor=False)

total_rooms = len(rooms)
available_rooms = sum(1 for r in rooms.values() if r["status"] == "Available")
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
st.subheader(":material/table: Room Overview", anchor=False)

for room_id, room in rooms.items():
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

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
                options=available_students,
                format_func=lambda x: students[x]["name"],
                key=f"select_{room_id}"
            )

            if st.button("Allocate", key=f"btn_{room_id}"):
                students[selected]["room_id"] = room_id
                room["occupancy"] += 1

                if room["occupancy"] >= room["capacity"]:
                    room["status"] = "Full"

                st.success(f"{students[selected]['name']} assigned to Room {room_id}")
        else:
            st.caption("No action")

st.divider()

# ------------------ INFO ------------------
st.subheader(":material/info: Info", anchor=False)
st.info("Room allocation updates occupancy and availability dynamically.")
