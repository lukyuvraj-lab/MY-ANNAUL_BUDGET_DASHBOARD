import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.supabase_client import supabase

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="MoneyMate Dashboard",
    page_icon="💰",
    layout="wide"
)

# -------------------------------------------------
# LOGIN CHECK
# -------------------------------------------------
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

# Initialize local tracking if needed for fallback/manual addition
if "transactions" not in st.session_state:
    st.session_state["transactions"] = []

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Add Income", "Add Expense", "Transactions"]
)

# ============================================================
# DASHBOARD
# ============================================================
if menu == "Dashboard":
    st.title("💰 MoneyMate Dashboard")
    st.caption("Your financial overview")

    # LOAD TRANSACTIONS FROM SUPABASE
    response = (
        supabase
        .table("transactions")
        .select("*")
        .order("date", desc=True)
        .execute()
    )
    df = pd.DataFrame(response.data)

    # EMPTY DATA CHECK
    if df.empty:
        st.info("No transactions available yet.")
        st.stop()

    # CALCULATE TOTALS
    income = df.loc[df["type"].str.lower() == "income", "amount"].sum()
    expense = df.loc[df["type"].str.lower() == "expense", "amount"].sum()
    balance = income - expense
    savings = (balance / income) * 100 if income > 0 else 0

    # KPI CARDS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Income", f"₹{income:,.2f}")
    c2.metric("💸 Total Expense", f"₹{expense:,.2f}")
    c3.metric("🏦 Balance", f"₹{balance:,.2f}")
    c4.metric("📊 Savings %", f"{savings:.1f}%")

    st.divider()

    # EXPENSE BY CATEGORY
    st.subheader("🥧 Expense by Category")
    expense_df = df[df["type"].str.lower() == "expense"].copy()

    if expense_df.empty:
        st.info("No expense transactions yet.")
    else:
        category_expense = (
            expense_df
            .groupby("category", as_index=False)["amount"]
            .sum()
            .sort_values("amount", ascending=False)
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            fig = px.pie(category_expense, names="category", values="amount", hole=0.4)
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(category_expense, use_container_width=True, hide_index=True)

    st.divider()

    # RECENT TRANSACTIONS
    st.subheader("📋 Recent Transactions")
    display_columns = ["date", "type", "category", "account", "amount", "note"]
    available_columns = [col for col in display_columns if col in df.columns]
    recent_df = df.head(10)[available_columns].copy()

    st.dataframe(recent_df, use_container_width=True, hide_index=True)

# ============================================================
# ADD INCOME
# ============================================================
elif menu == "Add Income":
    st.title("💵 Add Income")

    with st.form("income_form"):
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        category = st.selectbox(
            "Category",
            ["Salary", "Business", "Freelance", "Investment", "Gift", "Other"]
        )
        description = st.text_input("Description")
        date = st.date_input("Date")
        submit = st.form_submit_button("➕ Add Income")

        if submit:
            if amount <= 0:
                st.error("Enter a valid amount.")
            else:
                st.session_state["transactions"].append({
                    "Date": str(date),
                    "Type": "Income",
                    "Category": category,
                    "Description": description,
                    "Amount": float(amount)
                })
                st.success("Income added successfully! ✅")
                st.rerun()

# ============================================================
# ADD EXPENSE
# ============================================================
elif menu == "Add Expense":
    st.title("💸 Add Expense")

    with st.form("expense_form"):
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        category = st.selectbox(
            "Category",
            [
                "Food", "Travel", "Shopping", "Bills", "Education", "Entertainment",
                "Medical", "Rent", "Groceries", "Fuel", "Electricity", "Mobile Recharge",
                "Internet", "Subscriptions", "Clothing", "Household", "Insurance",
                "Personal Care", "Gifts", "EMI / Loan", "Other"
            ]
        )
        description = st.text_input("Description")
        date = st.date_input("Date")
        submit = st.form_submit_button("➖ Add Expense")

        if submit:
            if amount <= 0:
                st.error("Enter a valid amount.")
            else:
                st.session_state["transactions"].append({
                    "Date": str(date),
                    "Type": "Expense",
                    "Category": category,
                    "Description": description,
                    "Amount": float(amount)
                })
                st.success("Expense added successfully! ✅")
                st.rerun()

# ============================================================
# TRANSACTIONS
# ============================================================
elif menu == "Transactions":
    st.title("📋 Manual Transactions")

    if st.session_state["transactions"]:
        st.dataframe(
            st.session_state["transactions"][::-1],
            use_container_width=True,
            hide_index=True
        )
        st.markdown("---")
        if st.button("🗑️ Clear All Transactions"):
            st.session_state["transactions"] = []
            st.success("Transactions cleared.")
            st.rerun()
    else:
        st.info("No manual transactions available.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption(
    f"MoneyMate Dashboard • "
    f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)
