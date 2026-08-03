import streamlit as st
import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTMzNzE5Nn0.aNB1owMWx2ddzqe9m1iDF9w3PLE0diBTEaMzMMHBJYY"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Transactions", layout="wide")

st.title("📋 Transactions")

# Fetch data
response = supabase.table("transactions").select("*").execute()
data = response.data

if data:
    df = pd.DataFrame(data)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", ascending=False)

    st.subheader("All Transactions")
    st.dataframe(df, use_container_width=True)

    st.divider()

    st.subheader("🗑️ Delete Transaction")

    transaction_options = [
        f"{row['id']} | {row['type']} | ₹{row['amount']} | {row['category']}"
        for _, row in df.iterrows()
    ]

    selected = st.selectbox(
        "Select transaction to delete",
        transaction_options
    )

    if st.button("Delete Transaction", type="primary"):
        transaction_id = int(selected.split(" | ")[0])

        supabase.table("transactions").delete().eq("id", transaction_id).execute()

        st.success(f"Transaction {transaction_id} deleted successfully!")
        st.rerun()

else:
    st.info("No transactions found.")
