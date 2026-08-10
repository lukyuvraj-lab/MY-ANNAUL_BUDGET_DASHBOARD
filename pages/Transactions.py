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


# -----------------------------
# YOUR TRANSACTIONS
# -----------------------------
st.subheader("📋 Your Transactions")

display_columns = [
    "id",
    "date",
    "type",
    "amount",
    "category",
    "account",
    "note"
]

available_columns = [
    c for c in display_columns
    if c in df.columns
]

display_df = df[available_columns].copy()

# Rename ID to Transaction No.
display_df = display_df.rename(
    columns={
        "id": "Txn No.",
        "date": "Date",
        "type": "Type",
        "amount": "Amount",
        "category": "Category",
        "account": "Account",
        "note": "Note"
    }
)

# Format amount
if "Amount" in display_df.columns:
    display_df["Amount"] = display_df["Amount"].apply(
        lambda x: f"₹{float(x):,.2f}"
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# -----------------------------
# EDIT TRANSACTION
# -----------------------------
if not df.empty:

    st.divider()

    st.subheader("✏️ Edit Transaction")

    selected_edit_id = st.selectbox(
        "Select transaction to edit",
        df["id"].tolist(),
        key="edit_transaction"
    )

    selected_row = df[
        df["id"] == selected_edit_id
    ].iloc[0]

    edit_col1, edit_col2 = st.columns(2)

    with edit_col1:

        edit_date = st.date_input(
            "Date",
            value=pd.to_datetime(
                selected_row["date"]
            ).date(),
            key="edit_date"
        )

        edit_type = st.selectbox(
            "Type",
            ["Income", "Expense"],
            index=(
                0
                if selected_row["type"] == "Income"
                else 1
            ),
            key="edit_type"
        )

        edit_amount = st.number_input(
            "Amount",
            min_value=0.0,
            value=float(selected_row["amount"]),
            key="edit_amount"
        )

    with edit_col2:

        edit_category = st.text_input(
            "Category",
            value=str(selected_row["category"]),
            key="edit_category"
        )

        accounts = [
            "Cash",
            "Bank",
            "UPI",
            "Credit Card"
        ]

        current_account = str(
            selected_row["account"]
        )

        account_index = (
            accounts.index(current_account)
            if current_account in accounts
            else 0
        )

        edit_account = st.selectbox(
            "Account",
            accounts,
            index=account_index,
            key="edit_account"
        )

        edit_note = st.text_input(
            "Note",
            value=str(selected_row.get("note", "")),
            key="edit_note"
        )

    if st.button(
        "✏️ Update Transaction",
        use_container_width=True
    ):

        if edit_amount <= 0:
            st.error(
                "Amount must be greater than 0."
            )

        elif not edit_category.strip():
            st.error(
                "Please enter a category."
            )

        else:

            try:

                supabase.table("transactions") \
                    .update({
                        "date": str(edit_date),
                        "type": edit_type,
                        "amount": edit_amount,
                        "category": edit_category.strip(),
                        "account": edit_account,
                        "note": edit_note.strip()
                    }) \
                    .eq("id", selected_edit_id) \
                    .eq("user_id", user.id) \
                    .execute()

                st.success(
                    "✅ Transaction updated successfully!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Update failed: {e}"
                )


# -----------------------------
# DELETE TRANSACTION
# -----------------------------
if not df.empty:

    st.divider()

    st.subheader("🗑️ Delete Transaction")

    selected_delete_id = st.selectbox(
        "Select transaction to delete",
        df["id"].tolist(),
        key="delete_transaction"
    )

    if st.button(
        "🗑️ Delete Selected Transaction",
        use_container_width=True
    ):

        try:

            supabase.table("transactions") \
                .delete() \
                .eq("id", selected_delete_id) \
                .eq("user_id", user.id) \
                .execute()

            st.success(
                "✅ Transaction deleted."
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Delete failed: {e}"
            )
