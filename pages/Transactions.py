import streamlit as st
import pandas as pd
from datetime import date

from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Transactions",
    page_icon="📋",
    layout="wide"
)


# =========================================================
# LOGIN CHECK
# =========================================================
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state["user"]


# =========================================================
# TITLE
# =========================================================
st.title("📋 Transactions")
st.caption("Add and manage your transactions")


# =========================================================
# LOAD USER TRANSACTIONS
# =========================================================
try:

    response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("user_id", user.id)
        .order("date", desc=True)
        .execute()
    )

    df = pd.DataFrame(response.data)

except Exception as e:

    st.error(f"Unable to load transactions: {e}")
    st.stop()


# =========================================================
# CALCULATE CURRENT BALANCE
# =========================================================
if df.empty:

    balance = 0.0

else:

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    ).fillna(0)

    df["type"] = (
        df["type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    total_income = df.loc[
        df["type"] == "income",
        "amount"
    ].sum()

    total_expense = df.loc[
        df["type"] == "expense",
        "amount"
    ].sum()

    balance = total_income - total_expense


# =========================================================
# BALANCE
# =========================================================
st.subheader("🏦 Current Balance")

st.metric(
    "Balance",
    f"₹{balance:,.2f}"
)


st.divider()


# =========================================================
# CATEGORY LIST
# =========================================================
categories = [
    "Bakery",
    "Beating",
    "Bike",
    "Bills",
    "Business Income",
    "Chiti",
    "Credit Card",
    "Entertainment",
    "Education",
    "Electricity",
    "EMI",
    "Gifts",
    "Groceries/vegetable's",
    "Investment",
    "Medical",
    "Home",
    "Hotel/Dhaba",
    "Insurance",
    "Internet",
    "Loan",
    "Fuel",
    "Rent",
    "Recharge",
    "Saloon",
    "Salary",
    "Shopping",
    "Subscriptions",
    "Shop",  
    "Travel",
    "Transport",
    "Trip",
    "Recharge",
    "Mobile",
    "Utensils",
    "Other"
]


# =========================================================
# ACCOUNT LIST
# =========================================================
accounts = [
    "Cash",
    "Bank",
    "UPI",
    "Credit Card"
]


# =========================================================
# ADD TRANSACTION
# =========================================================
st.subheader("➕ Add Transaction")

with st.form("add_transaction_form"):

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # LEFT
    # -----------------------------------------------------
    with col1:

        trans_date = st.date_input(
            "Date",
            value=date.today()
        )

        trans_type = st.selectbox(
            "Type",
            [
                "Income",
                "Expense"
            ]
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=100.0,
            format="%.2f"
        )

    # -----------------------------------------------------
    # RIGHT
    # -----------------------------------------------------
    with col2:

        category = st.selectbox(
            "Category",
            categories
        )

        account = st.selectbox(
            "Account",
            accounts
        )

        note = st.text_input(
            "Note",
            placeholder="Optional"
        )

    save = st.form_submit_button(
        "💾 Save Transaction",
        use_container_width=True
    )


# =========================================================
# SAVE TRANSACTION
# =========================================================
if save:

    if amount <= 0:

        st.error(
            "Please enter an amount greater than 0."
        )

    else:

        try:

            supabase.table("transactions").insert(
                {
                    "user_id": user.id,
                    "date": str(trans_date),
                    "type": trans_type,
                    "amount": amount,
                    "category": category,
                    "account": account,
                    "note": note.strip()
                }
            ).execute()

            st.success(
                "✅ Transaction saved successfully!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Save failed: {e}"
            )


st.divider()


# =========================================================
# TRANSACTION TABLE
# =========================================================
st.subheader("📋 Your Transactions")


if df.empty:

    st.info(
        "No transactions yet. Add your first transaction above."
    )

else:

    display_columns = [
        "date",
        "type",
        "category",
        "account",
        "amount",
        "note"
    ]

    available_columns = [
        column
        for column in display_columns
        if column in df.columns
    ]

    display_df = df[
        available_columns
    ].copy()

    if "amount" in display_df.columns:

        display_df["amount"] = (
            display_df["amount"]
            .apply(
                lambda x: f"₹{x:,.2f}"
            )
        )

    if "type" in display_df.columns:

        display_df["type"] = (
            display_df["type"]
            .astype(str)
            .str.title()
        )

    display_df = display_df.rename(
        columns={
            "date": "Date",
            "type": "Type",
            "category": "Category",
            "account": "Account",
            "amount": "Amount",
            "note": "Note"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# =========================================================
# DELETE TRANSACTION
# =========================================================
if not df.empty:

    st.subheader("🗑️ Delete Transaction")

    selected_id = st.selectbox(
        "Select transaction to delete",
        df["id"].tolist()
    )

    if st.button(
        "🗑️ Delete Selected Transaction",
        use_container_width=True
    ):

        try:

            (
                supabase
                .table("transactions")
                .delete()
                .eq("id", selected_id)
                .eq("user_id", user.id)
                .execute()
            )

            st.success(
                "✅ Transaction deleted successfully."
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Delete failed: {e}"
            )
