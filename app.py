import streamlit as st
import pandas as pd
from supabase import create_client

# -----------------------------
# Supabase Connection
# -----------------------------
SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"
SUPABASE_KEY = "PASTE_YOUR_ANON_KEY_HERE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="MoneyMate",
    page_icon="💰",
    layout="wide"
)

st.title("💰 MoneyMate - Personal Finance Dashboard")

# -----------------------------
# Add Transaction
# -----------------------------
st.header("➕ Add Transaction")

col1, col2 = st.columns(2)

with col1:
    date = st.date_input("Date")
    trans_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=1.0)

with col2:
    category = st.text_input("Category")
    account = st.selectbox(
        "Account",
        ["Cash", "Bank", "UPI", "Credit Card"]
    )
    note = st.text_area("Note")
    
if st.button("💾 Save Transaction"):

    data = {
        "date": str(date),
        "type": trans_type,
        "amount": amount,
        "category": category,
        "account": account,
        "note": note
    }

    supabase.table("transactions").insert(data).execute()

    st.success("✅ Transaction saved successfully!")

st.divider()

st.header("📋 Transactions")

response = (
    supabase.table("transactions")
    .select("*")
    .order("date", desc=True)
    .execute()
)

df = pd.DataFrame(response.data)

if not df.empty:
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    balance = total_income - total_expense

    c1, c2, c3 = st.columns(3)

    c1.metric("💰 Income", f"₹{total_income:,.2f}")
    c2.metric("💸 Expense", f"₹{total_expense:,.2f}")
    c3.metric("🏦 Balance", f"₹{balance:,.2f}")

    st.dataframe(df, use_container_width=True)
else:
    st.info("No transactions found.")
