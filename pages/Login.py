import streamlit as st
from supabase import create_client

# Supabase Connection
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Login", page_icon="🔐")

st.title("🔐 MoneyMate Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

col1, col2 = st.columns(2)

with col1:
    if st.button("Login"):
        try:
            supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )
            st.success("Login successful!")
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
            st.success("Account created! Please check your email if confirmation is enabled.")
        except Exception as e:
            st.error(f"Sign Up failed: {e}")
