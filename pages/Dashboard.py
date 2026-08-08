import streamlit as st
from supabase import create_client
from datetime import datetime

# ============================================================
# LOGIN CHECK
# ============================================================

if "user" not in st.session_state or st.session_state["user"] is None:
    st.switch_page("pages/Login.py")
    st.stop()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MoneyMate Dashboard",
    page_icon="💰",
    layout="wide"
)


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
# HEADER
# ============================================================

st.title("💰 MoneyMate Dashboard")

user = st.session_state["user"]

if hasattr(user, "email"):
    st.write(f"Welcome, **{user.email}** 👋")
else:
    st.write("Welcome to MoneyMate 👋")


# ============================================================
# LOGOUT
# ============================================================

with st.sidebar:
    st.header("💰 MoneyMate")

    if st.button("🚪 Logout", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.pop("user", None)
        st.switch_page("pages/Login.py")


# ============================================================
# DASHBOARD MENU
# ============================================================

st.sidebar.markdown("---")
st.sidebar.subheader("Menu")

menu = st.sidebar.radio(
    "Select",
    [
        "Dashboard",
        "Add Income",
        "Add Expense",
        "Transactions"
    ]
)


# ============================================================
# SESSION DATA
# ============================================================

if "transactions" not in st.session_state:
    st.session_state["transactions"] = []


# ============================================================
# DASHBOARD
# ============================================================

if menu == "Dashboard":

    st.subheader("📊 Financial Overview")

    transactions = st.session_state["transactions"]

    total_income = sum(
    float(t["Amount"])
    for t in transactions
    if t["Type"] == "Income"
)

total_expense = sum(
    float(t["Amount"])
    for t in transactions
    if t["Type"] == "Expense"
)

balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💵 Total Income",
            f"₹ {total_income:,.2f}"
        )

    with col2:
        st.metric(
            "💸 Total Expense",
            f"₹ {total_expense:,.2f}"
        )

    with col3:
        st.metric(
            "💰 Balance",
            f"₹ {balance:,.2f}"
        )

    st.markdown("---")

    if transactions:

        st.subheader("📋 Recent Transactions")

        st.dataframe(
            transactions,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No transactions available. "
            "Use 'Add Income' or 'Add Expense' from the sidebar."
        )


# ============================================================
# ADD INCOME
# ============================================================

elif menu == "Add Income":

    st.subheader("💵 Add Income")

    with st.form("income_form"):

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=100.0
        )

        category = st.selectbox(
            "Category",
            [
                "Salary",
                "Business",
                "Freelance",
                "Investment",
                "Other"
            ]
        )

        description = st.text_input(
            "Description"
        )

        date = st.date_input(
            "Date",
            datetime.today()
        )

        submitted = st.form_submit_button(
            "➕ Add Income"
        )

        if submitted:

            if amount <= 0:
                st.error("Please enter a valid amount.")

            else:

                transaction = {
                    "Date": str(date),
                    "Type": "Income",
                    "Category": category,
                    "Description": description,
                    "Amount": amount
                }

                st.session_state["transactions"].append(
                    transaction
                )

                st.success(
                    "Income added successfully! ✅"
                )

                st.rerun()


# ============================================================
# ADD EXPENSE
# ============================================================

elif menu == "Add Expense":

    st.subheader("💸 Add Expense")

    with st.form("expense_form"):

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=100.0
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Education",
                "Entertainment",
                "Medical",
                "Other"
            ]
        )

        description = st.text_input(
            "Description"
        )

        date = st.date_input(
            "Date",
            datetime.today()
        )

        submitted = st.form_submit_button(
            "➖ Add Expense"
        )

        if submitted:

            if amount <= 0:
                st.error("Please enter a valid amount.")

            else:

                transaction = {
                    "Date": str(date),
                    "Type": "Expense",
                    "Category": category,
                    "Description": description,
                    "Amount": amount
                }

                st.session_state["transactions"].append(
                    transaction
                )

                st.success(
                    "Expense added successfully! ✅"
                )

                st.rerun()


# ============================================================
# TRANSACTIONS
# ============================================================

elif menu == "Transactions":

    st.subheader("📋 All Transactions")

    transactions = st.session_state["transactions"]

    if transactions:

        st.dataframe(
            transactions,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        if st.button(
            "🗑️ Clear All Transactions"
        ):

            st.session_state["transactions"] = []

            st.success(
                "All transactions cleared."
            )

            st.rerun()

    else:

        st.info(
            "No transactions found."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    f"MoneyMate Dashboard • "
    f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)
