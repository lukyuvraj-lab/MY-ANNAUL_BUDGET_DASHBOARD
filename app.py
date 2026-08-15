import streamlit as st

from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate",
    page_icon="💰",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Remove Plotly chart toolbar from the entire app */
    .modebar-container {
        display: none !important;
    }

    .modebar {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# RESTORE SUPABASE SESSION
# =========================================================
try:

    session = supabase.auth.get_session()

    if session and session.user:

        st.session_state["user"] = session.user

        if session.access_token:
            st.session_state["access_token"] = (
                session.access_token
            )

        if session.refresh_token:
            st.session_state["refresh_token"] = (
                session.refresh_token
            )

except Exception:
    pass


# =========================================================
# SESSION CHECK
# =========================================================
user = st.session_state.get("user")


# =========================================================
# ROUTING
# =========================================================
if user:

    try:

        st.switch_page(
            "pages/Dashboard.py"
        )

    except Exception:

        st.title("💰 MoneyMate")
        st.success("Login successful.")
        st.info(
            "Dashboard could not be opened automatically."
        )

else:

    try:

        st.switch_page(
            "pages/Login.py"
        )

    except Exception:

        st.title("💰 MoneyMate")
        st.info(
            "Please log in to continue."
        )


# =========================================================
# FALLBACK
# =========================================================
st.stop()
