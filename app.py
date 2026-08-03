import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import date
import streamlit as st

import streamlit as st

if "user" in st.session_state:
    st.switch_page("pages/Dashboard.py")
else:
    st.switch_page("pages/Login.py")
# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="MoneyMate",
    page_icon="💰",
    layout="wide"
)

# -----------------------------
# SUPABASE
# -----------------------------
SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTMzNzE5Nn0.aNB1owMWx2ddzqe9m1iDF9w3PLE0diBTEaMzMMHBJYY"

SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY")

# -----------------------------
# TITLE
# -----------------------------
st.title("💰 MoneyMate")
st.caption("Personal Finance Dashboard")

# -----------------------------
# ADD TRANSACTION
# -----------------------------
st.subheader("➕ Add Transaction")

c1, c2 = st.columns(2)

with c1:
    trans_date = st.date_input("Date", value=date.today())
    trans_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0)

with c2:
    category = st.text_input("Category")
    account = st.selectbox(
        "Account",
        ["Cash", "Bank", "UPI", "Credit Card"]
    )
    note = st.text_area("Note")

if st.button("💾 Save"):

    supabase.table("transactions").insert({
        "date": str(trans_date),
        "type": trans_type,
        "amount": amount,
        "category": category,
        "account": account,
        "note": note
    }).execute()

    st.success("Transaction Saved")

# -----------------------------
# LOAD DATA
# -----------------------------
response = (
    supabase.table("transactions")
    .select("*")
    .order("date", desc=True)
    .execute()
)

df = pd.DataFrame(response.data)

st.divider()

st.subheader("Dashboard")

if df.empty:
    st.info("No transactions yet.")
    st.stop()

income = df[df["type"] == "Income"]["amount"].sum()
expense = df[df["type"] == "Expense"]["amount"].sum()
balance = income - expense

a, b, c = st.columns(3)

a.metric("Income", f"₹{income:,.2f}")
b.metric("Expense", f"₹{expense:,.2f}")
c.metric("Balance", f"₹{balance:,.2f}")

st.divider()

st.subheader("Transactions")

st.dataframe(df, use_container_width=True)
