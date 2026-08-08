import streamlit as st
from supabase import create_client

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTM"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MoneyMate Login",
    page_icon="🔐"
)

# ============================================================
# LOGIN PAGE
# ============================================================

st.title("🔐 MoneyMate Login")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

col1, col2 = st.columns(2)

# ============================================================
# LOGIN
# ============================================================

with col1:

    if st.button("Login", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )

                # Save logged-in user
                st.session_state["user"] = response.user

                st.success("Login successful!")

                # Go to Dashboard
                st.switch_page(
                    "pages/Dashboard.py"
                )

            except Exception as e:

                st.error(
                    f"Login failed: {e}"
                )


# ============================================================
# SIGN UP
# ============================================================

with col2:

    if st.button("Sign Up", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password
                    }
                )

                st.success(
                    "Account created successfully! "
                    "Please check your email."
                )

            except Exception as e:

                st.error(
                    f"Sign Up failed: {e}"
                )import streamlit as st
from supabase import create_client

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"

SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MoneyMate Login",
    page_icon="🔐"
)

# ============================================================
# LOGIN PAGE
# ============================================================

st.title("🔐 MoneyMate Login")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

col1, col2 = st.columns(2)

# ============================================================
# LOGIN
# ============================================================

with col1:

    if st.button("Login", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )

                # Save logged-in user
                st.session_state["user"] = response.user

                st.success("Login successful!")

                # Go to Dashboard
                st.switch_page(
                    "pages/Dashboard.py"
                )

            except Exception as e:

                st.error(
                    f"Login failed: {e}"
                )


# ============================================================
# SIGN UP
# ============================================================

with col2:

    if st.button("Sign Up", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password
                    }
                )

                st.success(
                    "Account created successfully! "
                    "Please check your email."
                )

            except Exception as e:

                st.error(
                    f"Sign Up failed: {e}"
                )
