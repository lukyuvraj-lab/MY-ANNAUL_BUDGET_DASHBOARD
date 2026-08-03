import streamlit as st
import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTMzNzE5Nn0.aNB1owMWx2ddzqe9m1iDF9w3PLE0diBTEaMzMMHBJYY"


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
