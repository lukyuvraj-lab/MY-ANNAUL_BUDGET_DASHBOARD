import streamlit as st
import pandas as pd
from datetime import date

from utils.supabase_client import supabase


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="MoneyMate Transactions",
    page_icon="📋",
    layout="wide"
)


# -----------------------------
# LOGIN CHECK
# -----------------------------
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state["user"]


# -----------------------------
# TITLE
# -----------------------------
st.title("📋 Transactions")
st.caption("Add and manage your transactions")


# -----------------------------
# ADD TRANSACTION
# -----------------------------
st.subheader("➕ Add Transaction")

with st.form("add_transaction_form"):

    col1, col2 = st.columns(2)

    with col1:
        trans_date = st.date_input(
            "Date",
            value=date.today()
        )

        trans_type = st.selectbox(
            "Type",
            ["Income", "Expense"]
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=100.0
        )

    with col2:
        category = st.text_input(
            "Category"
        )

        account = st.selectbox(
            "Account",
            [
                "Cash",
                "Bank",
                "UPI",
                "Credit Card"
            ]
        )

        note = st.text_input(
            "Note"
        )

    save = st.form_submit_button(
        "💾 Save Transaction",
        use_container_width=True
    )


# -----------------------------
# SAVE TRANSACTION
# -----------------------------
if save:

    if amount <= 0:
        st.error("Please enter an amount greater than 0.")

    elif not category.strip():
        st.error("Please enter a category.")

    else:

        try:

            supabase.table("transactions").insert({
                "user_id": user.id,
                "date": str(trans_date),
                "type": trans_type,
                "amount": amount,
                "category": category.strip(),
                "account": account,
                "note": note.strip()
            }).execute()

            st.success("✅ Transaction saved successfully!")

            st.rerun()

        except Exception as e:

            st.error(f"Save failed: {e}")


st.divider()


# -----------------------------
# LOAD TRANSACTIONS
# -----------------------------
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


# -----------------------------
# DISPLAY
# -----------------------------
if df.empty:

    st.info("📋 No transactions yet.")

else:

    st.subheader("📋 Your Transactions")

    display_columns = [
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

    if "amount" in display_df.columns:
        display_df["amount"] = display_df["amount"].apply(
            lambda x: f"₹{float(x):,.2f}"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------
# DELETE
# -----------------------------
if not df.empty:

    st.divider()

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

            supabase.table("transactions") \
                .delete() \
                .eq("id", selected_id) \
                .eq("user_id", user.id) \
                .execute()

            st.success("✅ Transaction deleted.")

            st.rerun()

        except Exception as e:

            st.error(f"Delete failed: {e}")
