import streamlit as st
import pandas as pd
from supabase import create_client

SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Transactions", layout="wide")

st.title("📋 Transactions")

response = supabase.table("transactions").select("*").execute()
data = response.data

if data:
    df = pd.DataFrame(data)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", ascending=False)

    st.dataframe(df, use_container_width=True)
else:
    st.info("No transactions found.")
