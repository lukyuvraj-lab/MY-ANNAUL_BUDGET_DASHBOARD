import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTMzNzE5Nn0.aNB1owMWx2ddzqe9m1iDF9w3PLE0diBTEaMzMMHBJYY"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Login", page_icon="🔐")

st.title("🔐 MoneyMate Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

col1, col2 = st.columns(2)

with col1:
    if st.button("Login"):
        try:
            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )

st.session_state["user"] = response.user
st.success("Login successful!")
st.switch_page("pages/Dashboard.py")

        except Exception as e:
            st.error(f"Login failed: {e}")

with col2:
    if st.button("Sign Up"):
        try:
            supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                }
            )
            st.success("Account created! Check your email.")
        except Exception as e:
            st.error(f"Sign Up failed: {e}")
