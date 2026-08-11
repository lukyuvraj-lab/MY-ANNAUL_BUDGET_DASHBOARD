import streamlit as st

from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Sign Up",
    page_icon="📝",
    layout="centered"
)


# =========================================================
# HEADER
# =========================================================
st.title("📝 Create MoneyMate Account")

st.caption(
    "Start managing your income, expenses and budgets."
)


# =========================================================
# SIGN UP FORM
# =========================================================
with st.form("signup_form"):

    name = st.text_input(
        "Full Name",
        placeholder="Enter your name"
    )

    email = st.text_input(
        "Email",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password"
    )

    currency = st.selectbox(
        "Preferred Currency",
        [
            "₹ INR",
            "$ USD",
            "€ EUR",
            "£ GBP",
            "¥ JPY",
            "₩ KRW",
            "AED",
            "SGD"
        ]
    )

    signup_clicked = st.form_submit_button(
        "📝 Create Account",
        use_container_width=True
    )


# =========================================================
# SIGN UP
# =========================================================
if signup_clicked:

    name = name.strip()
    email = email.strip()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------
    if not name:

        st.warning(
            "Please enter your name."
        )

    elif not email:

        st.warning(
            "Please enter your email."
        )

    elif not password:

        st.warning(
            "Please create a password."
        )

    elif len(password) < 6:

        st.warning(
            "Password must contain at least 6 characters."
        )

    elif password != confirm_password:

        st.error(
            "❌ Passwords do not match."
        )

    else:

        try:

            # -------------------------------------------------
            # CREATE SUPABASE ACCOUNT
            # -------------------------------------------------
            response = (
                supabase.auth
                .sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "display_name": name,
                            "currency": currency,
                            "custom_categories": [],
                            "custom_accounts": []
                        }
                    }
                })
            )

            # -------------------------------------------------
            # CHECK RESPONSE
            # -------------------------------------------------
            if not response.user:

                st.error(
                    "❌ Account could not be created."
                )

            else:

                # -------------------------------------------------
                # IF EMAIL CONFIRMATION IS REQUIRED
                # -------------------------------------------------
                if response.session is None:

                    st.success(
                        "✅ Account created successfully!"
                    )

                    st.info(
                        "📧 Please check your email and "
                        "confirm your account before logging in."
                    )

                    if st.button(
                        "🔐 Go to Login",
                        use_container_width=True
                    ):

                        st.switch_page(
                            "pages/Login.py"
                        )

                # -------------------------------------------------
                # IF EMAIL CONFIRMATION IS NOT REQUIRED
                # -------------------------------------------------
                else:

                    st.success(
                        "✅ Account created successfully!"
                    )

                    st.session_state["user"] = (
                        response.user
                    )

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

                    st.switch_page(
                        "pages/Dashboard.py"
                    )

        except Exception as e:

            error_message = str(e)

            if "already registered" in error_message.lower():

                st.error(
                    "❌ This email is already registered."
                )

                st.info(
                    "Please use the Login page instead."
                )

            elif "User already registered" in error_message:

                st.error(
                    "❌ This email is already registered."
                )

            elif "invalid email" in error_message.lower():

                st.error(
                    "❌ Please enter a valid email address."
                )

            elif "password" in error_message.lower():

                st.error(
                    f"❌ Password error: {error_message}"
                )

            else:

                st.error(
                    f"❌ Sign Up failed: {error_message}"
                )


# =========================================================
# LOGIN LINK
# =========================================================
st.divider()

st.write(
    "Already have a MoneyMate account?"
)

if st.button(
    "🔐 Go to Login",
    use_container_width=True
):

    st.switch_page(
        "pages/Login.py"
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "💰 MoneyMate • Personal Finance Management"
          )
