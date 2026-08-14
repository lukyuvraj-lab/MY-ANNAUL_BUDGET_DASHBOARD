import streamlit as st
from utils.supabase_client import supabase
import os


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Login",
    page_icon="🔐",
    layout="centered"
)


# =========================================================
# IF ALREADY LOGGED IN
# =========================================================
if st.session_state.get("user"):

    st.success("You are already logged in.")

    if st.button(
        "🏠 Open Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )

    if st.button(
        "Logout",
        use_container_width=True
    ):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        for key in [
            "user",
            "access_token",
            "refresh_token"
        ]:

            st.session_state.pop(
                key,
                None
            )

        st.rerun()

    st.stop()

# =========================================================
# MONEY MATE LOGO & HEADER (SIDE-BY-SIDE)
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logo_candidates = [
    os.path.join(BASE_DIR, "assets", "moneymate_logo.png"),
    os.path.join(BASE_DIR, "assets", "moneymate_logo.jpg"),
    os.path.join(BASE_DIR, "assets", "logo.png"),
    os.path.join(BASE_DIR, "assets", "Logo.png"),
    os.path.join(BASE_DIR, "assets", "logo.jpg"),
]

logo_path = None

for path in logo_candidates:
    if os.path.exists(path):
        logo_path = path
        break

# Create two side-by-side columns
# [3, 1] means the text column is 3x wider than the logo column
col1, col2 = st.columns([3, 1], vertical_alignment="center")

with col1:
    st.title("🔐 MoneyMate")
    st.subheader("Login to your account")
    st.caption("Personal Finance Dashboard")

with col2:
    if logo_path:
        st.image(
            logo_path,
            use_container_width=True # Automatically scales to fit the column width
        )
    else:
        st.warning("No logo found.")



# =========================================================
# LOGIN FORM
# =========================================================
with st.form("login_form"):

    email = st.text_input(
        "Email",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login_clicked = st.form_submit_button(
        "🔐 Login",
        use_container_width=True
    )


# =========================================================
# LOGIN
# =========================================================
if login_clicked:

    email = email.strip()

    if not email or not password:

        st.warning(
            "Please enter your email and password."
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

            if not response.user:

                st.error(
                    "Login failed. User information was not returned."
                )

            elif not response.session:

                st.error(
                    "Login failed. Authentication session was not returned."
                )

            else:

                # -----------------------------------------
                # SAVE USER
                # -----------------------------------------
                st.session_state["user"] = (
                    response.user
                )

                # -----------------------------------------
                # SAVE AUTH TOKENS
                # -----------------------------------------
                st.session_state[
                    "access_token"
                ] = (
                    response.session.access_token
                )

                st.session_state[
                    "refresh_token"
                ] = (
                    response.session.refresh_token
                )

                st.success(
                    "✅ Login successful!"
                )

                st.switch_page(
                    "pages/Dashboard.py"
                )

        except Exception as e:

            error_message = str(e)

            if "Invalid login credentials" in error_message:

                st.error(
                    "❌ Invalid email or password."
                )

            elif "Email not confirmed" in error_message:

                st.error(
                    "📧 Please confirm your email before logging in."
                )

            else:

                st.error(
                    f"❌ Login failed: {error_message}"
                )


# =========================================================
# SIGN UP
# =========================================================
st.divider()

st.subheader(
    "🆕 New to MoneyMate?"
)

st.write(
    "Create a new account to start managing your finances."
)


if st.button(
    "📝 Create Account",
    use_container_width=True
):

    st.switch_page(
        "pages/SignUp.py"
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "💰 MoneyMate • Secure Personal Finance Management"
    )
