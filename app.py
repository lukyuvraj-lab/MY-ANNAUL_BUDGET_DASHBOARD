import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# SESSION CHECK
# =========================================================
user = st.session_state.get("user")


# =========================================================
# ROUTING
# =========================================================
if user:

    try:
        st.switch_page("pages/Dashboard.py")
    except Exception:
        st.title("💰 MoneyMate")
        st.success("Login successful.")
        st.info("Dashboard could not be opened automatically.")

else:

    try:
        st.switch_page("pages/Login.py")
    except Exception:
        st.title("💰 MoneyMate")
        st.info("Please log in to continue.")


# =========================================================
# FALLBACK
# =========================================================
st.stop()
