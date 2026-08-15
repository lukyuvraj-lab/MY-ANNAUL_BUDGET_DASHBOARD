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
# RESTORE SUPABASE SESSION
# =========================================================
if (
    "access_token" in st.session_state
    and "refresh_token" in st.session_state
):
    try:
        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"]
        )
    except Exception:
        pass


# =========================================================
# LOGIN CHECK
# =========================================================
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state["user"]


# =========================================================
# DEFAULT CATEGORIES
# =========================================================
DEFAULT_INCOME_CATEGORIES = [
    "Salary",
    "Business",
    "Interest",
    "Balance Last Year",
    "Chit Fund",
    "Freelance",
    "Bonus",
    "Investment",
    "Rental",
    "Refunds",
    "Commission",
    "Sales",
    "Tax Refunds",
    "Other Income"
]

DEFAULT_EXPENSE_CATEGORIES = [
    "Bakery",
    "Beating",
    "Bike",
    "Bills",
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
    "Shopping",
    "Subscriptions",
    "Shop",
    "Travel",
    "Transport",
    "Trip",
    "Mobile",
    "Utensils",
    "Other Expense"
]

DEFAULT_ACCOUNTS = [
    "Cash",
    "Bank",
    "UPI",
    "Credit Card"
]


# =========================================================
# USER SETTINGS
# =========================================================
try:
    metadata = user.user_metadata or {}
except Exception:
    metadata = {}


settings_categories = metadata.get(
    "custom_categories",
    DEFAULT_EXPENSE_CATEGORIES
)

settings_accounts = metadata.get(
    "custom_accounts",
    DEFAULT_ACCOUNTS
)

settings_currency = metadata.get(
    "currency",
    "₹ INR"
)


if not isinstance(settings_categories, list):
    settings_categories = DEFAULT_EXPENSE_CATEGORIES.copy()

if not settings_categories:
    settings_categories = DEFAULT_EXPENSE_CATEGORIES.copy()

if not isinstance(settings_accounts, list):
    settings_accounts = DEFAULT_ACCOUNTS.copy()

if not settings_accounts:
    settings_accounts = DEFAULT_ACCOUNTS.copy()


# =========================================================
# COMBINE CUSTOM SETTINGS WITH INCOME CATEGORIES
# =========================================================
income_categories = list(dict.fromkeys(
    str(x).strip()
    for x in DEFAULT_INCOME_CATEGORIES
    if str(x).strip()
))

expense_categories = list(dict.fromkeys(
    str(x).strip()
    for x in settings_categories
    if str(x).strip()
))


# Income and Expense use separate category lists.
# Custom categories remain in the Expense list unless they are
# explicitly part of the default Income categories.


# =========================================================
# CURRENCY
# =========================================================
CURRENCY_SYMBOLS = {
    "₹ INR": "₹",
    "$ USD": "$",
    "€ EUR": "€",
    "£ GBP": "£",
    "¥ JPY": "¥",
    "₩ KRW": "₩",
    "AED": "AED ",
    "SGD": "SGD "
}

currency_symbol = CURRENCY_SYMBOLS.get(
    settings_currency,
    "₹"
)


def money(value):
    try:
        return f"{currency_symbol}{float(value):,.2f}"
    except Exception:
        return f"{currency_symbol}0.00"


# =========================================================
# TITLE
# =========================================================
st.title("📋 Transactions")
st.caption(
    "Add and manage your income and expenses"
)


# =========================================================
# LOAD TRANSACTIONS
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

    df = pd.DataFrame(
        response.data or []
    )

except Exception as e:

    st.error(
        f"Unable to load transactions: {e}"
    )
    st.stop()


# =========================================================
# CLEAN TRANSACTIONS
# =========================================================
if not df.empty:

    if "amount" in df.columns:

        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        ).fillna(0.0)

    if "type" in df.columns:

        df["type_clean"] = (
            df["type"]
            .astype(str)
            .str.strip()
            .str.casefold()
        )

else:

    df["amount"] = pd.Series(
        dtype="float64"
    )


# =========================================================
# CALCULATE BALANCE
# =========================================================
if df.empty:

    total_income = 0.0
    total_expense = 0.0
    balance = 0.0

else:

    total_income = float(
        df.loc[
            df["type_clean"] == "income",
            "amount"
        ].sum()
    )

    total_expense = float(
        df.loc[
            df["type_clean"] == "expense",
            "amount"
        ].sum()
    )

    balance = (
        total_income -
        total_expense
    )


# =========================================================
# BALANCE
# =========================================================
st.subheader("🏦 Current Balance")

k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        "Balance",
        money(balance)
    )

with k2:
    st.metric(
        "Total Income",
        money(total_income)
    )

with k3:
    st.metric(
        "Total Expense",
        money(total_expense)
    )


st.divider()


# =========================================================
# ADD TRANSACTION
# =========================================================
st.subheader("➕ Add Transaction")

st.caption("Income and Expense categories are kept separate.")

# Transaction type
trans_type = st.selectbox(
    "Type",
    ["Income", "Expense"],
    key="new_transaction_type"
)

# Keep Income Category and Expense Category completely separate.
if trans_type == "Income":
    income_category = st.selectbox(
        "Income Category",
        income_categories,
        key="new_income_category"
    )
    category = income_category
else:
    expense_category = st.selectbox(
        "Expense Category",
        expense_categories,
        key="new_expense_category"
    )
    category = expense_category

with st.form("add_transaction_form"):

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # LEFT
    # -----------------------------------------------------
    with col1:

        trans_date = st.date_input(
            "Date",
            value=date.today(),
            key="new_transaction_date"
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="new_transaction_amount"
        )

    # -----------------------------------------------------
    # RIGHT
    # -----------------------------------------------------
    with col2:

        account = st.selectbox(
            "Account",
            settings_accounts,
            key="new_transaction_account"
        )

        note = st.text_input(
            "Note",
            placeholder="Optional",
            key="new_transaction_note"
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

    elif not category.strip():

        st.error(
            "Please select a category."
        )

    elif not account.strip():

        st.error(
            "Please select an account."
        )

    else:

        try:

            (
                supabase
                .table("transactions")
                .insert({
                    "user_id": user.id,
                    "date": str(trans_date),
                    "type": trans_type,
                    "amount": amount,
                    "category": category.strip(),
                    "account": account.strip(),
                    "note": note.strip()
                })
                .execute()
            )

            st.success(
                "✅ Transaction saved successfully!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Save failed: {e}"
            )


# =========================================================
# TRANSACTION FILTER
# =========================================================
st.divider()
st.subheader("🔎 Filter Transactions")


filter_col1, filter_col2, filter_col3 = st.columns(3)


with filter_col1:

    filter_type = st.selectbox(
        "Type",
        [
            "All",
            "Income",
            "Expense"
        ],
        key="filter_type"
    )


with filter_col2:

    all_categories = sorted(
        set(
            df["category"].dropna().astype(str).tolist()
        )
        if not df.empty and "category" in df.columns
        else set()
    )

    filter_category = st.selectbox(
        "Category",
        ["All"] + all_categories,
        key="filter_category"
    )


with filter_col3:

    all_accounts = sorted(
        set(
            df["account"].dropna().astype(str).tolist()
        )
        if not df.empty and "account" in df.columns
        else set()
    )

    filter_account = st.selectbox(
        "Account",
        ["All"] + all_accounts,
        key="filter_account"
    )


filtered_df = df.copy()


if not filtered_df.empty:

    if filter_type != "All":

        filtered_df = filtered_df[
            filtered_df["type"].astype(str).str.casefold()
            == filter_type.casefold()
        ]

    if filter_category != "All":

        filtered_df = filtered_df[
            filtered_df["category"].astype(str)
            == filter_category
        ]

    if filter_account != "All":

        filtered_df = filtered_df[
            filtered_df["account"].astype(str)
            == filter_account
        ]


# =========================================================
# YOUR TRANSACTIONS
# =========================================================
st.subheader("📋 Your Transactions")


if filtered_df.empty:

    st.info(
        "No transactions found for the selected filters."
    )

else:

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
        column
        for column in display_columns
        if column in filtered_df.columns
    ]

    display_df = filtered_df[
        available_columns
    ].copy()

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

    if "Amount" in display_df.columns:

        display_df["Amount"] = display_df[
            "Amount"
        ].apply(money)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# EDIT TRANSACTION
# =========================================================
if not df.empty:

    st.divider()
    st.subheader("✏️ Edit Transaction")

    transaction_ids = df[
        "id"
    ].tolist()

    selected_edit_id = st.selectbox(
        "Select transaction to edit",
        transaction_ids,
        key="edit_transaction"
    )

    selected_rows = df[
        df["id"] == selected_edit_id
    ]

    if not selected_rows.empty:

        selected_row = (
            selected_rows.iloc[0]
        )

        edit_col1, edit_col2 = st.columns(2)

        # -------------------------------------------------
        # LEFT
        # -------------------------------------------------
        with edit_col1:

            try:
                current_date = pd.to_datetime(
                    selected_row["date"]
                ).date()
            except Exception:
                current_date = date.today()

            edit_date = st.date_input(
                "Date",
                value=current_date,
                key="edit_date"
            )

            current_type = str(
                selected_row.get(
                    "type",
                    "Expense"
                )
            ).strip().casefold()

            edit_type = st.selectbox(
                "Type",
                ["Income", "Expense"],
                index=(
                    0
                    if current_type == "income"
                    else 1
                ),
                key="edit_type"
            )

            edit_amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(
                    selected_row.get(
                        "amount",
                        0
                    )
                ),
                step=100.0,
                format="%.2f",
                key="edit_amount"
            )

        # -------------------------------------------------
        # RIGHT
        # -------------------------------------------------
        with edit_col2:

            if edit_type == "Income":
                edit_category_options = (
                    income_categories
                )
            else:
                edit_category_options = (
                    expense_categories
                )

            current_category = str(
                selected_row.get(
                    "category",
                    ""
                )
            )

            if (
                current_category
                in edit_category_options
            ):
                category_index = (
                    edit_category_options.index(
                        current_category
                    )
                )
            else:

                # Preserve an old category that
                # may no longer be in Settings.
                edit_category_options = (
                    [current_category]
                    + [
                        x
                        for x in edit_category_options
                        if x != current_category
                    ]
                )

                category_index = 0

            edit_category = st.selectbox(
                "Category",
                edit_category_options,
                index=category_index,
                key="edit_category"
            )

            current_account = str(
                selected_row.get(
                    "account",
                    ""
                )
            )

            edit_accounts = settings_accounts.copy()

            if (
                current_account
                and current_account not in edit_accounts
            ):
                edit_accounts.insert(
                    0,
                    current_account
                )

            if not edit_accounts:
                edit_accounts = [
                    "Cash"
                ]

            account_index = (
                edit_accounts.index(
                    current_account
                )
                if current_account in edit_accounts
                else 0
            )

            edit_account = st.selectbox(
                "Account",
                edit_accounts,
                index=account_index,
                key="edit_account"
            )

            current_note = str(
                selected_row.get(
                    "note",
                    ""
                )
            )

            edit_note = st.text_input(
                "Note",
                value=current_note,
                key="edit_note"
            )


        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------
        if st.button(
            "✏️ Update Transaction",
            use_container_width=True,
            key="update_transaction_button"
        ):

            if edit_amount <= 0:

                st.error(
                    "Amount must be greater than 0."
                )

            elif not edit_category.strip():

                st.error(
                    "Please select a category."
                )

            elif not edit_account.strip():

                st.error(
                    "Please select an account."
                )

            else:

                try:

                    (
                        supabase
                        .table("transactions")
                        .update({
                            "date": str(edit_date),
                            "type": edit_type,
                            "amount": edit_amount,
                            "category": edit_category.strip(),
                            "account": edit_account.strip(),
                            "note": edit_note.strip()
                        })
                        .eq(
                            "id",
                            selected_edit_id
                        )
                        .eq(
                            "user_id",
                            user.id
                        )
                        .execute()
                    )

                    st.success(
                        "✅ Transaction updated successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Update failed: {e}"
                    )


# =========================================================
# DELETE TRANSACTION
# =========================================================
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
        use_container_width=True,
        key="delete_transaction_button"
    ):

        try:

            (
                supabase
                .table("transactions")
                .delete()
                .eq(
                    "id",
                    selected_delete_id
                )
                .eq(
                    "user_id",
                    user.id
                )
                .execute()
            )

            st.success(
                "✅ Transaction deleted successfully!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Delete failed: {e}"
    )

