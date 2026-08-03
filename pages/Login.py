import streamlit as st

st.set_page_config(page_title="Login", page_icon="🔐")

st.title("🔐 MoneyMate Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

col1, col2 = st.columns(2)

with col1:
    if st.button("Login"):
        st.success("Login feature will be connected to Supabase next.")

with col2:
    if st.button("Sign Up"):
        st.success("Sign Up feature will be connected to Supabase next.")
