import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login
from db import get_billing_by_student, process_payment

require_login()

st.set_page_config(page_title="Billing", page_icon=":material/payments:", layout="wide")
st.title(":material/payments: Billing Details", anchor=False)

user_id = st.session_state.current_user_id
billing_list = get_billing_by_student(user_id) or []
billing = billing_list[0] if billing_list else {}

# ------------------ OVERVIEW ------------------
st.subheader(":material/receipt_long: Billing Overview", anchor=False)

c1, c2, c3, c4 = st.columns(4)

with c1:
    total_due = sum(float(b['Amount']) for b in billing_list if b['Status'] == 'Not Paid')
    st.metric("Total Due", f"₹{total_due}")

with c2:
    st.metric("Latest Bill", f"₹{billing.get('Amount', 0)}")

with c3:
    st.metric("Due Date", str(billing.get("Due_Date", "N/A")))

with c4:
    status = billing.get("Status", "N/A")
    st.metric(
        "Status",
        status,
        delta="Paid" if status == "Paid" else "Action needed",
        delta_color="normal" if status == "Paid" else "inverse"
    )

st.divider()

# ------------------ HISTORY ------------------
st.subheader(":material/history: Payment History", anchor=False)

history = billing_list

if history:
    for bill in history:
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"**₹{bill['Amount']}** [ID: {bill['Bill_ID']}]")

        with col2:
            st.caption(f"Issued: {bill['Issue_Date']}")

        with col3:
            if bill["Status"] == "Paid":
                st.success("Paid")
            else:
                st.error("Not Paid")
else:
    st.info("No billing history available.")

st.divider()

# ------------------ QUICK ACTION ------------------
st.subheader(":material/bolt: Quick Action", anchor=False)

if billing.get("Status") == "Not Paid":
    if st.button("Pay Now"):
        success = process_payment(billing['Bill_ID'])
        if success:
            st.success("Payment marked as Paid successfully in Database!")
            st.rerun()
        else:
            st.error("Engine failed to process MySQL payment.")
else:
    st.info("All payments are up to date.")

