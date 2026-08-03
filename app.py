import streamlit as st
import pandas as pd
from supabase import create_client

# -----------------------------
# Supabase Connection
# -----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

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

if st.button("💾        to_number(ys[f"Z{r}"].value)
    ])

    r += 1

year_df = pd.DataFrame(
    rows,
    columns=[
        "Year",
        "Income",
        "Expense",
        "Saving",
        "Spend %"
    ]
)

st.dataframe(year_df, use_container_width=True)
