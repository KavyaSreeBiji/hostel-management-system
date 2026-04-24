import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_mock_data, require_login

init_mock_data()
require_login()

st.set_page_config(page_title="Billing", page_icon=":material/payments:", layout="wide")
st.title(":material/payments: Billing Details", anchor=False)

user_id = st.session_state.current_user_id
billing = st.session_state.billing.get(user_id, {})

# ------------------ OVERVIEW ------------------
st.subheader(":material/receipt_long: Billing Overview", anchor=False)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Due", f"₹{billing.get('total_due', 0)}")

with c2:
    st.metric("Last Bill", f"₹{billing.get('last_bill', 0)}")

with c3:
    st.metric("Due Date", billing.get("due_date", "N/A"))

with c4:
    status = billing.get("status", "N/A")
    st.metric(
        "Status",
        status,
        delta="Paid" if status == "Paid" else "Action needed",
        delta_color="normal" if status == "Paid" else "inverse"
    )

st.divider()

# ------------------ HISTORY ------------------
st.subheader(":material/history: Payment History", anchor=False)

history = billing.get("history", [])

if history:
    for bill in history:
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"**₹{bill['amount']}**")

        with col2:
            st.caption(bill["date"])

        with col3:
            if bill["status"] == "Paid":
                st.success("Paid")
            else:
                st.warning("Pending")
else:
    st.info("No billing history available.")

st.divider()

# ------------------ QUICK ACTION ------------------
st.subheader(":material/bolt: Quick Action", anchor=False)

if billing.get("status") == "Pending":
    if st.button("Pay Now"):
        billing["status"] = "Paid"
        st.success("Payment marked as Paid (demo)")
else:
    st.info("All payments are up to date.")

