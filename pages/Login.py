import streamlit as st
from supabase import create_client


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Login",
    page_icon="🔐"
)


# =========================================================
# SUPABASE
# =========================================================
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTMzNzE5Nn0.aNB1owMWx2ddzqe9m1iDF9w3PLE0diBTEaMzMMHBJYY"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# TITLE
# =========================================================
st.title("🔐 MoneyMate Login")

email = st.text_input("Email")
password = st.text_input(
    "Password",
    type="password"
)

col1, col2 = st.columns(2)


# =========================================================
# LOGIN
# =========================================================
with col1:

    if st.button(
        "Login",
        use_container_width=True
    ):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = (
                    supabase.auth
                    .sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                )

                # Save user
                st.session_state["user"] = response.user

                # IMPORTANT:
                # Save Supabase authentication session
                st.session_state["access_token"] = (
                    response.session.access_token
                )

                st.session_state["refresh_token"] = (
                    response.session.refresh_token
                )

                st.success(
                    "✅ Login successful!"
                )

                st.switch_page(
                    "pages/Dashboard.py"
                )

            except Exception as e:

                st.error(
                    f"Login failed: {e}"
                )


# =========================================================
# SIGN UP
# =========================================================
with col2:

    if st.button(
        "Sign Up",
        use_container_width=True
    ):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = (
                    supabase.auth
                    .sign_up({
                        "email": email,
                        "password": password
                    })
                )

                st.success(
                    "✅ Account created! "
                    "Please check your email."
                )

            except Exception as e:

                st.error(
                    f"Sign Up failed: {e}"
                )
